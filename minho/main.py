import asyncio
import logging
import os
import re
import sys
from pathlib import Path

# `backend/` 에서 실행: `main` 모듈은 이 파일, `adapters`·`titanic` 등은 `apps/` 에 있음
_BACKEND_ROOT = Path(__file__).resolve().parent
_APPS_ROOT = _BACKEND_ROOT / "apps"
_CORE_ROOT = _BACKEND_ROOT / "core"
_backend_str = str(_BACKEND_ROOT)
_apps_str = str(_APPS_ROOT)
_core_str = str(_CORE_ROOT)
if _backend_str not in sys.path:
    sys.path.insert(0, _backend_str)
if _apps_str not in sys.path:
    sys.path.append(_apps_str)
# `core/matrix/` → 최상위 패키지 이름이 `matrix` 이므로 `backend/core` 를 path 에 넣음
if _core_str not in sys.path:
    sys.path.append(_core_str)

# Windows: NumPy/BLAS·MKL 이 기본 멀티스레드일 때 일부 환경에서 프로세스가 네이티브 크래시로
# 종료되는 경우가 있어, pandas/numpy 로드 전에 스레드 수를 1로 제한합니다.
if sys.platform == "win32":
    for _k in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        os.environ.setdefault(_k, "1")

from _import_aliases import install_secom_aliases  # noqa: E402

install_secom_aliases()

# Windows: psycopg 비동기는 ProactorEventLoop 와 호환되지 않음
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

from adapters.db_health_adapter import DbHealthAdapter
from adapters.weather_adapter import fetch_seoul_weather
from community.adapter.inbound.api import community_router
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from silicon_valley.adapter.inbound.api import silicon_valley_router
from silicon_valley.adapter.inbound.mcp.piper_bighetti_hr_tools import mcp as bighetti_mcp
from silicon_valley.adapter.inbound.mcp.piper_dinesh_dash_tools import mcp as dinesh_mcp
from silicon_valley.adapter.inbound.mcp.piper_dunn_coo_tools import mcp as dunn_mcp
from silicon_valley.adapter.inbound.mcp.piper_gilfoyle_system_tools import mcp as gilfoyle_mcp
from silicon_valley.adapter.inbound.mcp.piper_hendricks_ceo_tools import mcp as hendricks_mcp
from silicon_valley.dependencies.providers import get_n8n_client
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from titanic.adapter.inbound.api import titanic_router
from vision.adapter.inbound.api import vision_router

from core.matrix.vault_keymaker_secret_manager import (
    MissingApiKeyError,
    format_gemini_error,
    keymaker,
)
from database import dispose_engine, get_db

# 캐릭터별 MCP 서버 — 마운트 경로(prefix), FastMCP 인스턴스, Streamable HTTP ASGI 앱
_SILICON_VALLEY_MCP_SERVERS = tuple(
    (prefix, server, server.streamable_http_app())
    for prefix, server in (
        ("/mcp/hendricks", hendricks_mcp),
        ("/mcp/bighetti", bighetti_mcp),
        ("/mcp/dinesh", dinesh_mcp),
        ("/mcp/gilfoyle", gilfoyle_mcp),
        ("/mcp/dunn", dunn_mcp),
    )
)

try:
    from secom.app.controllers.user_controller import UserController, register_secom_routes
    from secom.app.repositories.user_repository import UserRepository
    from secom.app.services.user_service import UserService
    from secom.schemas.user_schemas import UserSchemas
except ModuleNotFoundError:
    SECOM_AVAILABLE = False

    def register_secom_routes(app: FastAPI) -> None:  # noqa: ARG001
        """secom 패키지가 없으면 회원가입·secom 라우트를 등록하지 않습니다."""
        logger = logging.getLogger(__name__)
        logger.warning("secom 모듈 없음 — register_secom_routes 생략")

    UserController = None  # type: ignore[assignment, misc]
    UserRepository = None  # type: ignore[assignment, misc]
    UserSchemas = None  # type: ignore[assignment, misc]
    UserService = None  # type: ignore[assignment, misc]
else:
    SECOM_AVAILABLE = True
from logging_config import get_uvicorn_log_config, setup_app_logging

setup_app_logging()
logger = logging.getLogger(__name__)
API_PORT = int(os.getenv("API_PORT", "8000"))
# 폰·다른 PC에서 `http://<이_PC_LAN_IP>:8000` 으로 직접 호출할 때는 0.0.0.0 (보안: 신뢰 네트워크에서만)
API_HOST = os.getenv("API_HOST", "127.0.0.1").strip() or "127.0.0.1"
_SIGNUP_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class SignupRequest(BaseModel):
    """회원가입 POST 본문."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "newuser01",
                "email": "newuser@example.com",
                "nickname": "홍길동",
                "phone": "01012345678",
                "password": "password12",
                "password_confirm": "password12",
            }
        }
    )

    user_id: str = Field(
        ...,
        min_length=2,
        max_length=64,
        description="로그인 아이디",
        examples=["newuser01"],
    )
    email: str = Field(
        ...,
        min_length=3,
        max_length=320,
        description="도메인에 점(.)이 있는 이메일 (예: user@example.com)",
        examples=["newuser@example.com"],
    )
    nickname: str = Field(
        ...,
        min_length=1,
        max_length=64,
        examples=["홍길동"],
    )
    phone: str = Field(
        ...,
        min_length=9,
        max_length=32,
        description="숫자만 또는 하이픈 포함 (예: 010-1234-5678)",
        examples=["01012345678"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=512,
        examples=["password12"],
    )
    password_confirm: str = Field(
        ...,
        min_length=6,
        max_length=512,
        examples=["password12"],
    )


class SignupResponse(BaseModel):
    ok: bool
    message: str
    email: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_app_logging()
    if SECOM_AVAILABLE:
        from secom.app.bootstrap import init_engine

        await init_engine()
    else:
        logger.warning("secom 모듈 없음 — init_engine 생략")
    logger.info(
        "API 준비 port=%s — docs http://127.0.0.1:%s/docs | ping http://127.0.0.1:%s/ping",
        API_PORT,
        API_PORT,
        API_PORT,
    )
    logger.info(
        "프론트는 별도 터미널에서 저장소 루트 `npm run dev` 또는 `frontend` 에서 `npm run dev` 로 실행하세요. "
        "해당 터미널을 닫거나 Ctrl+C 하면 http://localhost:3000 은 연결 거부(ERR_CONNECTION_REFUSED)가 됩니다. "
        "자세한 안내: frontend/DEV_SERVER.md"
    )
    try:
        async with AsyncExitStack() as mcp_stack:
            for _prefix, server, _http_app in _SILICON_VALLEY_MCP_SERVERS:
                await mcp_stack.enter_async_context(server.session_manager.run())
            yield
    finally:
        await dispose_engine()


app = FastAPI(title="TJ Watson Main Page", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_secom_routes(app)

app.include_router(titanic_router)
app.include_router(silicon_valley_router)
app.include_router(community_router)
app.include_router(vision_router)

for _mcp_prefix, _mcp_server, _mcp_http_app in _SILICON_VALLEY_MCP_SERVERS:
    app.mount(_mcp_prefix, _mcp_http_app)


@app.middleware("http")
async def log_http_requests(request: Request, call_next):
    logger.info("HTTP >>> %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("HTTP <<< %s %s status=%s", request.method, request.url.path, response.status_code)
    return response


@app.get("/ping")
def ping() -> dict[str, bool]:
    """브라우저에서 열면 요청 로그가 찍히는지 확인용."""
    logger.info("[ping] 요청 수신 — 로깅 정상")
    return {"ok": True}


@app.get("/")
def read_root():
    return {"message": "FAST API 메인 페이지 ", "docs": "/docs"}


@app.post("/signup", response_model=SignupResponse)
async def signup(
    body: SignupRequest,
    db: AsyncSession = Depends(get_db),
) -> SignupResponse:
    """회원가입 — 검증 후 secom 레이어(controller → service → repository)로 저장합니다."""
    if not SECOM_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="이 설치에는 secom(회원가입) 패키지가 포함되어 있지 않습니다.",
        )
    assert UserSchemas is not None

    email = body.email.strip()
    if not _SIGNUP_EMAIL_RE.match(email):
        logger.warning(
            "[/signup] 이메일 형식 거부 — email=%r (save_user 미호출)",
            email,
        )
        raise HTTPException(status_code=422, detail="올바른 이메일 형식이 아닙니다.")
    if body.password != body.password_confirm:
        logger.warning(
            "[/signup] 비밀번호 불일치 — email=%r (save_user 미호출)",
            email,
        )
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    logger.info(
        "[/signup] 요청 수신 — user_id=%s email=%s nickname=%s phone=%s",
        body.user_id.strip(),
        email,
        body.nickname.strip(),
        body.phone.strip(),
    )

    user_schemas = UserSchemas(
        user_id=body.user_id.strip(),
        email=body.email,
        nickname=body.nickname.strip(),
        phone=body.phone.strip(),
        password=body.password,
        password_confirm=body.password_confirm,
        role="user",
    )
    try:
        user_service = UserService(UserRepository(db))
        await UserController(user_service).save_user(user_schemas)
    except ValueError as exc:
        if db.in_transaction():
            await db.rollback()
        logger.warning("[/signup] 검증 실패 — %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IntegrityError as exc:
        if db.in_transaction():
            await db.rollback()
        logger.warning("[/signup] 중복 데이터 — %s", exc.orig)
        raise HTTPException(
            status_code=409,
            detail="이미 사용 중인 아이디 또는 이메일입니다.",
        ) from exc
    except SQLAlchemyError as exc:
        if db.in_transaction():
            await db.rollback()
        logger.exception("[/signup] DB 오류")
        raise HTTPException(
            status_code=503,
            detail="데이터베이스 연결 오류입니다. 잠시 후 다시 시도하세요.",
        ) from exc

    await get_n8n_client().send_event(
        {"message": f"새 회원가입: user_id={body.user_id.strip()} email={email}"}
    )

    return SignupResponse(
        ok=True,
        message="회원가입 요청이 접수되었습니다.",
        email=email,
    )


class ChatRequest(BaseModel):
    """클라이언트가 보내는 사용자 메시지."""

    message: str = Field(..., min_length=1, max_length=100_000)


class ChatResponse(BaseModel):
    """Gemini 모델의 텍스트 응답."""

    reply: str
    model: str


class WeatherResponse(BaseModel):
    """서울 현재 날씨."""

    city: str
    temp: int
    description: str
    icon: str


def _extract_text(response: Any) -> str:
    try:
        text = (response.text or "").strip()
    except ValueError:
        text = ""
    if text:
        return text
    if response.candidates:
        parts = response.candidates[0].content.parts
        chunks = [getattr(p, "text", "") or "" for p in parts]
        return "".join(chunks).strip()
    return ""


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    """JSON `{"message": "..."}` 를 받아 Gemini 답변을 JSON으로 반환합니다."""
    def _generate():
        return keymaker.generate_content(body.message)

    try:
        response, model_used = await asyncio.to_thread(_generate)
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        status, detail = format_gemini_error(exc)
        raise HTTPException(status_code=status, detail=detail) from exc

    reply = _extract_text(response)
    if not reply:
        raise HTTPException(status_code=502, detail="모델이 비어 있는 응답을 반환했습니다.")
    return ChatResponse(reply=reply, model=model_used)


@app.get("/weather", response_model=WeatherResponse)
async def weather() -> WeatherResponse:
    """서울 현재 온도·날씨 아이콘 코드(OpenWeatherMap)."""

    def _fetch():
        return fetch_seoul_weather()

    try:
        data = await asyncio.to_thread(_fetch)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return WeatherResponse(**data)


@app.get("/db-check")
async def check_db(db: AsyncSession = Depends(get_db)):
    return await DbHealthAdapter.neon_time_check(db)


@app.get("/doro/data")
def read_doro_data():
    doro_director = DoroDirector()
    df = doro_director.get_data()

    return df.to_dict(orient="records")


if __name__ == "__main__":
    import uvicorn

    # 주의: `python main.py` 는 반드시 `minho/` 디렉터리에서 실행하세요.
    # 브라우저 주소는 반드시 `http://` 로 시작해야 합니다 (https 아님).
    # Windows 에서 `localhost` 가 IPv6(::1)만 가면 연결이 안 될 수 있어 기본은 127.0.0.1 입니다.
    # 다른 PC·휴대폰에서 접속하려면 API_HOST=0.0.0.0 환경 변수를 설정하세요.
    _reload_default = "0" if sys.platform == "win32" else "1"
    use_reload = os.getenv("UVICORN_RELOAD", _reload_default).lower() in (
        "1",
        "true",
        "yes",
    )
    if use_reload:
        logger.info("uvicorn reload=ON (코드 저장 시 재시작)")
    else:
        logger.info(
            "uvicorn reload=OFF — 안정 실행. 자동 재시작은 UVICORN_RELOAD=1"
        )
    _uvicorn_kwargs = dict(
        host=API_HOST,
        port=API_PORT,
        log_level="info",
        log_config=get_uvicorn_log_config(),
        access_log=True,
    )
    logger.info(
        "브라우저에서 열 주소: http://127.0.0.1:%s/docs 또는 http://127.0.0.1:%s/ping",
        API_PORT,
        API_PORT,
    )
    if use_reload:
        uvicorn.run(
            "main:app",
            reload=True,
            reload_dirs=[str(_BACKEND_ROOT), str(_APPS_ROOT)],
            **_uvicorn_kwargs,
        )
    else:
        uvicorn.run(app, **_uvicorn_kwargs)
