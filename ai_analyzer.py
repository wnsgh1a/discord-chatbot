import json
import logging
import time
from datetime import datetime

import pytz
from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL, MAX_NEWS_BLOCKS_FOR_AI, MAX_RAW_NEWS_CHARS
from news_fetcher import extract_links_from_raw, is_tier1_text, truncate_raw_news

logger = logging.getLogger(__name__)

KST = pytz.timezone("Asia/Seoul")
MAX_RETRIES = 3
RETRY_DELAY = 2
VALID_CATEGORIES = ("속보", "이적", "경기", "일반")

_NEWS_CATEGORIES = {
    "속보": 0xFF4444,
    "이적": 0xFF8800,
    "경기": 0x4488FF,
    "일반": 0x888888,
}


class AIAnalysisError(Exception):
    """사용자에게 표시할 메시지를 포함한 AI 분석 오류."""

    def __init__(self, user_message: str, *, cause: Exception | None = None):
        self.user_message = user_message
        self.cause = cause
        super().__init__(user_message)


def _get_client():
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com", timeout=30)


def _today_kst() -> str:
    return datetime.now(KST).strftime("%Y년 %m월 %d일")


def _limit_raw_news(raw_news: str) -> str:
    return truncate_raw_news(
        raw_news,
        max_chars=MAX_RAW_NEWS_CHARS,
        max_blocks=MAX_NEWS_BLOCKS_FOR_AI,
    )


def _build_json_prompt(raw_news: str) -> str:
    today = _today_kst()
    limited = _limit_raw_news(raw_news)
    return f"""
너는 맨체스터 유나이티드 전문 뉴스 분석가야.
오늘 날짜(KST): {today}
제공된 뉴스 중 {today} 기준으로 중요하고 최신인 소식만 골라 한국어로 요약해줘.
'[★1-Tier High Priority★]' 표시 기사는 반드시 포함하고 비중 있게 다뤄줘.

반드시 아래 JSON 스키마만 출력하세요. 다른 텍스트나 마크다운 코드블록은 금지합니다.

{{
  "articles": [
    {{
      "category": "속보|이적|경기|일반 중 하나",
      "source": "언론사명",
      "tier": "⭐최상위 또는 일반",
      "title": "한글 번역 제목",
      "summary": "2~3줄 요약",
      "date": "YYYY-MM-DD",
      "link": "기사 URL"
    }}
  ]
}}

카테고리 기준:
- 속보: 구단 공식 발표, 갑작스러운 사건, 감독 경질/선임
- 이적: 이적 루머, 영입/방출 계약
- 경기: 경기 결과, 프리뷰, 리뷰, 선수 평점
- 일반: 인터뷰, 구단 소식, 부상, 기타

뉴스 데이터:
{limited}
"""


def _build_match_json_prompt(raw_match: str) -> str:
    today = _today_kst()
    limited = _limit_raw_news(raw_match)
    return f"""
너는 맨체스터 유나이티드 전문 축구 분석가야. 오늘 날짜(KST): {today}
아래 경기 관련 뉴스만 읽고 분석하세요.

반드시 아래 JSON만 출력하세요.

{{
  "has_match": true,
  "analysis_text": "마크다운 형식 경기 분석 (대회명, 스코어, 경기 요약, 주요 기록, 총평 포함)"
}}

경기 정보가 불충분하면 {{"has_match": false, "analysis_text": ""}} 를 반환하세요.

경기 뉴스 데이터:
{limited}
"""


def _call_api_json(prompt: str) -> dict | None:
    client = _get_client()
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            logger.info("DeepSeek API JSON 호출 (시도 %d/%d)", attempt + 1, MAX_RETRIES)
            response = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Respond with valid JSON only. No markdown fences or extra text.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                timeout=30,
            )
            content = response.choices[0].message.content
            if not content:
                last_error = AIAnalysisError("AI가 빈 응답을 반환했습니다.")
                continue
            return json.loads(content)
        except json.JSONDecodeError as exc:
            last_error = exc
            logger.warning("JSON 디코드 실패 (시도 %d/%d)", attempt + 1, MAX_RETRIES)
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                logger.warning("API 호출 실패, %ds 후 재시도: %s", RETRY_DELAY * (attempt + 1), exc)
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                logger.error("API 호출 최종 실패: %s", exc)

    raise AIAnalysisError(
        "AI 뉴스 분석에 실패했습니다. 잠시 후 다시 시도하거나 RSS fallback 링크를 확인해 주세요.",
        cause=last_error,
    )


def _article_dict(
    category: str,
    source: str,
    tier: str,
    title: str,
    summary: str,
    link: str,
    date: str,
) -> dict:
    if category not in VALID_CATEGORIES:
        category = "일반"
    is_tier1 = "⭐" in tier
    color = 0xFFD700 if is_tier1 else _NEWS_CATEGORIES.get(category, _NEWS_CATEGORIES["일반"])
    return {
        "category": category,
        "color": color,
        "title": title,
        "source": source,
        "tier": tier,
        "summary": summary,
        "link": link,
        "date": date,
    }


def parse_articles_json(data: dict) -> list[dict]:
    articles = []
    for item in data.get("articles", []):
        summary = (item.get("summary") or "").strip()
        if not summary:
            continue
        articles.append(
            _article_dict(
                category=item.get("category", "일반"),
                source=item.get("source", "알 수 없음"),
                tier=item.get("tier", "미분류"),
                title=item.get("title", "뉴스 제목"),
                summary=summary,
                link=item.get("link", ""),
                date=item.get("date", "-"),
            )
        )
    return articles


def parse_articles(raw_text: str) -> list[dict]:
    articles_raw = [a.strip() for a in raw_text.split("---") if a.strip()]
    articles = []
    for article in articles_raw:
        lines = article.strip().split("\n")
        data = {}
        for line in lines:
            if ":" in line:
                key, _, value = line.partition(":")
                data[key.strip()] = value.strip()

        if not data.get("내용"):
            continue

        articles.append(
            _article_dict(
                category=data.get("카테고리", "일반"),
                source=data.get("언론사", "알 수 없음"),
                tier=data.get("티어", "미분류"),
                title=data.get("제목", "뉴스 제목"),
                summary=data.get("내용", "내용 없음"),
                link=data.get("링크", ""),
                date=data.get("날짜", "-"),
            )
        )
    return articles


def build_fallback_articles(raw_news: str) -> list[dict]:
    articles = []
    for item in extract_links_from_raw(raw_news):
        tier = "⭐최상위" if is_tier1_text(item["title"]) else "일반"
        articles.append(
            _article_dict(
                category="일반",
                source="RSS 원문",
                tier=tier,
                title=item["title"],
                summary="AI 요약에 실패하여 원문 링크만 제공합니다.",
                link=item["link"],
                date=item["date"],
            )
        )
    return articles


def parse_match_json(data: dict) -> dict | None:
    if not data.get("has_match"):
        return None
    text = (data.get("analysis_text") or "").strip()
    if not text:
        return None
    return {"type": "match", "text": text, "color": 0x44AA44}


def parse_match(raw_text: str) -> dict | None:
    if not raw_text or "경기 요약" not in raw_text:
        return None
    return {"type": "match", "text": raw_text, "color": 0x44AA44}


def analyze_news(raw_news: str) -> list[dict]:
    try:
        data = _call_api_json(_build_json_prompt(raw_news))
    except AIAnalysisError:
        raise
    articles = parse_articles_json(data)
    logger.info("뉴스 JSON 파싱 결과: %d건", len(articles))
    return articles


def analyze_match(raw_match: str) -> dict | None:
    if not raw_match.strip():
        return None
    try:
        data = _call_api_json(_build_match_json_prompt(raw_match))
    except AIAnalysisError as exc:
        logger.warning("경기 분석 실패, 건너뜀: %s", exc.user_message)
        return None
    result = parse_match_json(data)
    if result:
        logger.info("경기 분석 JSON 파싱 완료")
    return result
