from __future__ import annotations

import logging

import httpx

from community.app.ports.output.email_client_port import EmailClientPort

logger = logging.getLogger(__name__)


class N8nEmailClient(EmailClientPort):
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    async def deliver(self, to_email: str, topic: str) -> bool:
        """n8n Webhook으로 { to_email, topic } 전송 — 콘텐츠 생성·발송은 n8n이 처리."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.webhook_url,
                    json={"to_email": to_email, "topic": topic},
                )
                logger.info("[N8nEmailClient] to=%s status=%s", to_email, response.status_code)
                return response.status_code == 200
            except Exception as exc:
                logger.error("[N8nEmailClient] 전송 실패 to=%s error=%s", to_email, exc)
                return False
