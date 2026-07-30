"""ontology_users / ontology_jobs 를 Neo4j 그래프로 적재한다.

(:User)-[:HAS_JOB]->(:Job) 이고 company 는 Job 의 속성이다.
드라이버 세션을 주입받아 테스트 시 가짜 세션을 넣을 수 있게 한다.
"""

from __future__ import annotations

from collections.abc import Sequence

CONSTRAINT_STATEMENTS: tuple[str, ...] = (
    "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
    "CREATE CONSTRAINT job_id_unique IF NOT EXISTS FOR (j:Job) REQUIRE j.id IS UNIQUE",
)

MERGE_USER = "MERGE (u:User {id: $id}) SET u.name = $name, u.email = $email, u.age = $age"

MERGE_JOB = "MERGE (j:Job {id: $id}) SET j.title = $title, j.company = $company"

# 두 패턴을 한 MATCH 에 쉼표로 나열하면 Neo4j 가 cartesian product 경고를 낸다.
# MATCH 를 나눠 쓰면 순차 조회로 해석돼 경고 없이 같은 결과를 얻는다.
MERGE_HAS_JOB = (
    "MATCH (u:User {id: $userid}) "
    "MATCH (j:Job {id: $jobid}) "
    "MERGE (u)-[:HAS_JOB]->(j)"
)


def write_graph(
    session,
    users: Sequence[dict],
    jobs: Sequence[dict],
) -> None:
    """제약 → 노드 → 관계 순으로 적재한다. MERGE 라 재실행해도 중복되지 않는다."""
    for statement in CONSTRAINT_STATEMENTS:
        session.run(statement)

    for user in users:
        session.run(
            MERGE_USER,
            id=user["id"],
            name=user["name"],
            email=user["email"],
            age=user["age"],
        )

    for job in jobs:
        session.run(
            MERGE_JOB,
            id=job["id"],
            title=job["title"],
            company=job["company"],
        )

    for job in jobs:
        session.run(MERGE_HAS_JOB, userid=job["userid"], jobid=job["id"])
