# Manchester United Daily News Bot

이 프로젝트는 RSS 피드를 통해 맨체스터 유나이티드 관련 뉴스를 수집하고, DeepSeek AI를 활용하여 요약한 뒤 디스코드 채널에 전송하는 자동화 봇입니다.

## 주요 기능

* **뉴스 수집**: Google News, The Guardian, BBC Sport의 RSS 피드에서 맨유 관련 최신 24시간 뉴스를 가져옵니다.
* **AI 요약 및 분류**: DeepSeek 모델을 사용하여 뉴스를 속보, 이적, 경기, 일반 카테고리로 분류하고 한국어로 요약합니다.
* **1티어 소스 강조**: Fabrizio Romano, David Ornstein 등 공신력이 높은 1티어 출처의 기사를 식별하여 특별히 강조 표시합니다.
* **디스코드 임베드**: 카테고리별 이모지와 색상을 적용한 Discord Embed 형식으로 가독성 좋게 메시지를 전송합니다.
* **자동화**: GitHub Actions를 통해 한국 시간 기준 매일 오전 7시에 뉴스를 자동으로 전송합니다.

## 설치 및 환경 설정

1. 패키지를 설치합니다.
```
pip install discord.py openai python-dotenv feedparser pytz
```

2. `.env` 파일을 생성하고 아래 환경 변수를 설정합니다.

```env
DISCORD_TOKEN="YOUR_DISCORD_TOKEN"
DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY"
CHANNEL_ID="YOUR_CHANNEL_ID"
```

## 실행 방법

스크립트를 직접 실행하여 수동으로 뉴스를 가져오고 디스코드로 전송할 수 있습니다.

```
python main.py
```

## 테스트

`pytest`를 사용하여 작성된 단위 테스트를 실행할 수 있습니다.

```
pytest
```

