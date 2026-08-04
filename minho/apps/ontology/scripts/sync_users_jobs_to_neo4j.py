#!/usr/bin/env python3
"""Postgres 의 ontology_users / ontology_jobs 를 Neo4j 그래프로 동기화한다.

Postgres 가 정본이고 Neo4j 는 파생이다. 단방향이며 MERGE 라 재실행이 안전하다.

실행 (backend 컨테이너, 작업 디렉터리 /app):
    docker exec pmhllll12-all-backend-1 \
        python apps/ontology/scripts/sync_users_jobs_to_neo4j.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

_ONTOLOGY_ROOT = Path(__file__).resolve().parents[1]
_APPS_ROOT = _ONTOLOGY_ROOT.parent
_MINHO_ROOT = _APPS_ROOT.parent
for _path in (str(_MINHO_ROOT), str(_APPS_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("sync_users_jobs_to_neo4j")

from neo4j import GraphDatabase  # noqa: E402
from ontology.adapter.outbound.neo4j_users_jobs_writer import write_graph  # noqa: E402
from sqlalchemy import text  # noqa: E402

from database import AsyncSessionLocal  # noqa: E402


async def _load_rows() -> tuple[list[dict], list[dict]]:
    async with AsyncSessionLocal() as session:
        users = (
            (
                await session.execute(
                    text("SELECT id, name, email, age FROM ontology_users ORDER BY id")
                )
            )
            .mappings()
            .all()
        )
        jobs = (
            (
                await session.execute(
                    text("SELECT id, title, company, userid FROM ontology_jobs ORDER BY id")
                )
            )
            .mappings()
            .all()
        )
    return [dict(r) for r in users], [dict(r) for r in jobs]


def main() -> int:
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    if not (uri and user and password):
        logger.error("NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD 가 필요합니다.")
        return 1

    if AsyncSessionLocal is None:
        logger.error("DATABASE_URL 이 없어 DB 세션을 만들 수 없습니다.")
        return 1

    users, jobs = asyncio.run(_load_rows())
    logger.info("Postgres 에서 users=%d jobs=%d 읽음", len(users), len(jobs))

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            write_graph(session, users, jobs)
            counts = session.run(
                "MATCH (u:User) WITH count(u) AS users "
                "MATCH (j:Job) WITH users, count(j) AS jobs "
                "MATCH ()-[r:HAS_JOB]->() "
                "RETURN users, jobs, count(r) AS rels"
            ).single()
        logger.info(
            "Neo4j 적재 완료 — User=%d Job=%d HAS_JOB=%d",
            counts["users"],
            counts["jobs"],
            counts["rels"],
        )
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
