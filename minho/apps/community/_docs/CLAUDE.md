---
type: spoke
app: community
links:
  - star_craft
---

# community 앱 — n8n + EXAONE Gmail 이메일 에이전트

스타 토폴로지의 **스포크**. 주제를 받아 EXAONE가 이메일 본문을 작성하고 n8n 워크플로우를 통해 Gmail로 발송한다.

---

## 헥사고날 레이어

```
apps/community/
├── domain/
│   └── email_message.py        # EmailMessage 값 객체 (to_email, topic)
├── app/
│   ├── dtos/
│   │   └── send_email_dto.py   # SendEmailCommand / SendEmailResult
│   ├── ports/input/
│   │   └── send_email_use_case.py   # SendEmailUseCase (abstract)
│   ├── ports/output/
│   │   └── email_client_port.py     # EmailClientPort (abstract)
│   └── use_cases/
│       └── send_email_interactor.py # SendEmailInteractor
├── adapter/
│   ├── inbound/
│   │   └── api/
│   │       ├── __init__.py          # community_router 노출
│   │       ├── schemas/__init__.py  # EmailSendRequest / EmailSendResponse
│   │       └── v1/
│   │           └── email_router.py  # POST /api/community/email/send
│   └── outbound/
│       └── n8n_email_client.py      # EmailClientPort 구현 — n8n Webhook 호출
├── dependencies/
│   └── providers.py                 # get_send_email_use_case()
└── tests/
    ├── domain/
    │   └── test_email_message.py
    └── app/use_cases/
        └── test_send_email_interactor.py
```

**의존성 방향:** `adapter` → `app` → `domain`

---

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/api/community/email/send` | 주제 → EXAONE 작성 → Gmail 발송 |

### 요청 본문

```json
{
  "to_email": "recipient@example.com",
  "topic": "이메일 주제 또는 내용 힌트"
}
```

---

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `N8N_COMMUNITY_EMAIL_WEBHOOK_URL` | `http://localhost:5678/webhook/community-email` | n8n 웹훅 URL |

---

## n8n 워크플로우 연동

1. n8n에서 `POST /webhook/community-email` 웹훅 트리거 생성
2. 수신 페이로드: `{ "to_email": "...", "topic": "..." }`
3. EXAONE (Ollama) 노드로 이메일 본문 생성
4. Gmail 노드로 발송

---

## TDD

```bash
cd minho
python -m pytest apps/community/tests/ -v
```
