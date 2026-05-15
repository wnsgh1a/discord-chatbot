import re
from datetime import datetime
import pytz
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

KST = pytz.timezone('Asia/Seoul')

_NEWS_CATEGORIES = {
    "속보": 0xFF4444,
    "이적": 0xFF8800,
    "경기": 0x4488FF,
    "일반": 0x888888,
}


def _build_prompt(raw_news: str) -> str:
    today_kst = datetime.now(KST).strftime('%Y년 %m월 %d일')

    return f"""
너는 맨체스터 유나이티드 전문 뉴스 분석가야. 제공된 뉴스들 중 중요한 소식을 골라 한국어로 요약해줘.
특히 '[★1-Tier High Priority★]' 표시가 붙은 기사는 매우 공신력이 높으니 반드시 포함하고 비중 있게 다뤄줘.

결과는 반드시 각 기사마다 아래 형식을 '엄격히' 지켜서 '---' 기호로 구분해줘.

[형식]
카테고리: [속보/이적/경기/일반 중 하나]
언론사: [이름]
티어: [공신력 티어 - 1티어인 경우 '⭐최상위'로 표기]
제목: [한글 번역 제목]
내용: [2~3줄 요약]
날짜: [YYYY-MM-DD]
링크: [기사 링크]
---

[카테고리 분류 기준]
- 속보: 구단 공식 발표, 갑작스러운 사건, 감독 경질/선임
- 이적: 이적 루머, 영입/방출 계약 소식
- 경기: 경기 결과, 프리뷰, 리뷰, 선수 평점
- 일반: 인터뷰, 구단 소식, 부상 소식, 기타

뉴스 데이터:
{raw_news}
"""


def parse_articles(raw_text: str) -> list[dict]:
    articles_raw = [a.strip() for a in raw_text.split('---') if a.strip()]
    articles = []
    for article in articles_raw:
        lines = article.strip().split('\n')
        data = {}
        for line in lines:
            if ':' in line:
                key, _, value = line.partition(':')
                data[key.strip()] = value.strip()

        if not data.get("내용"):
            continue

        category = data.get("카테고리", "일반")
        is_tier1 = "⭐" in data.get("티어", "")
        color = 0xFFD700 if is_tier1 else _NEWS_CATEGORIES.get(category, _NEWS_CATEGORIES["일반"])

        articles.append({
            "category": category,
            "color": color,
            "title": data.get("제목", "뉴스 제목"),
            "source": data.get("언론사", "알 수 없음"),
            "tier": data.get("티어", "미분류"),
            "summary": data.get("내용", "내용 없음"),
            "link": data.get("링크", ""),
            "date": data.get("날짜", "-"),
        })
    return articles


def analyze_news(raw_news: str) -> list[dict]:
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = _build_prompt(raw_news)
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return parse_articles(response.text)
