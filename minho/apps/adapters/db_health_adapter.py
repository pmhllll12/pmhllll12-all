"""DB 연결·시간 점검."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DbHealthAdapter:
    _NOW_SQL = text("SELECT NOW();")

    @classmethod
    async def neon_time_check(cls, session: AsyncSession) -> dict[str, object]:
        try:
            result = await session.execute(cls._NOW_SQL)
            now = result.scalar()
            return {"status": "success", "neon_time": now}
        except Exception as e:
            return {"status": "error", "message": str(e)}
