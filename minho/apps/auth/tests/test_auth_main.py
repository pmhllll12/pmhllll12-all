from __future__ import annotations

from fastapi.testclient import TestClient


def test_auth_main_boots_without_jwt_private_key(monkeypatch):
    """auth_main.py를 import만 해도 JWT_PRIVATE_KEY 없이 에러가 나면 안 된다 —
    실제 발급 호출 시점에만 키가 필요하다(core/security.py의 지연 로딩 설계)."""
    monkeypatch.delenv("JWT_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("JWT_PUBLIC_KEY", raising=False)
    import importlib

    import auth_main

    importlib.reload(auth_main)
    client = TestClient(auth_main.app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_main_app_boots_without_jwt_private_key(monkeypatch):
    """main:app(백엔드)은 검증부만 쓰므로 JWT_PRIVATE_KEY 없이도 import/기동돼야 한다.

    `apps/main.py`(cd apps && python main.py용 쉘)와 이름이 겹쳐 `import main`이
    pytest.ini의 pythonpath(apps가 .보다 먼저) 순서상 잘못된 쪽을 집을 수 있어,
    backend root의 main.py를 파일 경로로 직접 로드한다.
    """
    import importlib.util
    from pathlib import Path

    monkeypatch.delenv("JWT_PRIVATE_KEY", raising=False)

    main_path = Path(__file__).resolve().parents[3] / "main.py"
    spec = importlib.util.spec_from_file_location("_auth_test_main", main_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert any(getattr(route, "path", "") == "/ping" for route in module.app.routes)

