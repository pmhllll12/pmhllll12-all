# dependencies/providers.py (예시)

from admin.adapter.outbound.client.n8n_client import N8nClient

# 실제 환경에서는 환경 변수(os.environ)에서 URL을 가져옵니다.
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/notify"


def get_n8n_client() -> N8nClient:
    return N8nClient(webhook_url=N8N_WEBHOOK_URL)
