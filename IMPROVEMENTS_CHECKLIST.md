# Manchester United Daily News Bot — 개선 체크리스트

프로젝트 완성도를 높이기 위한 개선 항목입니다. 완료한 항목은 `[x]`로 표시하세요.

---

## 1. 안정성 · 운영

- [x] 시작 시 환경 변수 검증 (`DISCORD_TOKEN`, `DEEPSEEK_API_KEY`, `CHANNEL_ID` 누락/0 시 명확한 에러)
- [x] `logging` 모듈 도입 (RSS, AI, Discord 단계별 INFO/ERROR)
- [ ] GitHub Actions 실패 시 알림 (Discord 웹훅 또는 이메일)
- [x] `requirements.txt` 추가 및 패키지 버전 고정
- [x] README / Actions에서 `pip install -r requirements.txt`로 통일
- [x] 경기 분석 트리거를 `news_fetcher`의 `match_news` 기준으로 변경
- [x] `analyze_match`에 전체 뉴스가 아닌 경기 관련 블록만 전달

---

## 2. AI · 파싱 견고함

- [x] DeepSeek API 응답을 JSON / structured output으로 고정
- [x] `parse_articles` 실패 시 원문 링크 목록 fallback 전송
- [ ] `raw_news` 토큰·글자 수 상한 (기사 수 제한)
- [ ] 이미 전송한 URL 저장 (SQLite 또는 JSON) 후 중복 요약 방지
- [x] 프롬프트에 `today_kst` 날짜 반영 (오늘 기준 필터링 강화)
- [ ] AI 호출 실패 시 재시도 로그 및 사용자-facing 메시지 정리

---

## 3. Discord UX · API 제한

- [ ] Embed description 4096자 / title 256자 초과 시 잘림 처리
- [ ] 경기 분석 마크다운 길이 제한 또는 여러 Embed 분할
- [ ] 기사 수 많을 때 rate limit 대비 (딜레이, 배치, 상위 N건만)
- [ ] 카테고리별 단일 요약 Embed 옵션 검토
- [ ] 1티어 기사만 개별 Embed, 나머지는 묶음 전송 옵션
- [ ] `LoginFailure` 등 채널 접근 불가 시 `channel.send` 이중 실패 방지

---

## 4. 뉴스 수집 (`news_fetcher`)

- [ ] 피드별 실패 시 URL·예외 로그 남기기
- [ ] `socket.setdefaulttimeout` 대신 `requests` + per-request timeout
- [ ] 1티어 출처 판별을 제목 외 `source` / 본문까지 확장
- [ ] 제목 정규화 후 중복 제거 (`Man Utd` vs `Manchester United` 등)
- [ ] RSS URL·소스당 최대 기사 수를 환경 변수로 설정 가능하게

---

## 5. 테스트 · CI

- [ ] `news_fetcher` 단위 테스트 (mock feed, 중복, 경기 분류)
- [ ] `formatter` 테스트 (description 잘림, 빈 articles)
- [ ] `main` 통합 테스트 (Discord·OpenAI mock)
- [x] GitHub Actions에 `pytest` 단계 추가 (push / PR)
- [ ] `parse_match` / `analyze_*` mock 테스트

---

## 6. 배포 · 보안

- [ ] `.env`만 사용, `env` 폴더/파일 정리 및 `.gitignore` 확인
- [ ] README에 GitHub Secrets 설정 방법 문서화
- [ ] (선택) Discord Webhook으로 CI 전송 단순화
- [ ] Secrets·토큰이 로그/에러 메시지에 노출되지 않도록 점검

---

## 7. 기능 확장

- [ ] `--dry-run` 모드 (Discord 없이 콘솔/파일 출력)
- [ ] 테스트용 채널 ID 분리 (Secrets 또는 env)
- [ ] 스케줄 시간·RSS URL·최대 기사 수 환경 변수화
- [ ] (선택) 속보/1티어 즉시 알림용 별도 워크플로
- [ ] (선택) 슬래시 커맨드 `/news`로 수동 실행 (상시 봇)

---

## 8. 코드 · 문서 품질

- [ ] `ruff` 또는 `black` 포맷터 적용
- [ ] (선택) `mypy` 타입 검사
- [ ] README: Actions 수동 실행, 실패 시 체크리스트
- [ ] GitHub Actions `checkout@v4`, Python 3.12, pip 캐시
- [ ] 아키텍처/데이터 흐름 다이어그램 README 보강

---

## 추천 진행 순서

### 1주차 — 기반
- [x] 환경 변수 검증
- [x] `requirements.txt` + 버전 고정
- [x] CI에 `pytest`
- [x] 구조화된 로깅

### 2주차 — 핵심 품질
- [x] AI JSON 출력
- [x] 파싱 fallback
- [x] `match_news`만 경기 분석에 사용

### 3주차 — 전송·데이터
- [ ] Embed 길이 / rate limit 처리
- [ ] 중복 URL 저장

### 4주차 — (선택) 편의
- [ ] Webhook / dry-run
- [ ] 설정 env화

---

## 진행 요약

| 구역 | 완료 | 전체 |
|------|------|------|
| 1. 안정성 · 운영 | 6 | 7 |
| 2. AI · 파싱 | 3 | 6 |
| 3. Discord UX | 0 | 6 |
| 4. 뉴스 수집 | 0 | 5 |
| 5. 테스트 · CI | 1 | 5 |
| 6. 배포 · 보안 | 0 | 4 |
| 7. 기능 확장 | 0 | 5 |
| 8. 코드 · 문서 | 0 | 5 |
| **합계** | **12** | **43** |

> 표의 숫자는 체크리스트 항목 수에 맞게 직접 갱신하세요.
