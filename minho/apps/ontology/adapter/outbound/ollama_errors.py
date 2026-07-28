from __future__ import annotations


class OllamaUnavailableError(RuntimeError):
    """Ollama 서버(채팅·임베딩 모델 포함)에 연결할 수 없을 때."""
