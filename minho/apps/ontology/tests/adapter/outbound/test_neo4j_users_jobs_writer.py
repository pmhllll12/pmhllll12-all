from __future__ import annotations

from ontology.adapter.outbound.neo4j_users_jobs_writer import (
    CONSTRAINT_STATEMENTS,
    MERGE_HAS_JOB,
    MERGE_JOB,
    MERGE_USER,
    write_graph,
)


class _FakeSession:
    def __init__(self):
        self.runs: list[tuple[str, dict]] = []

    def run(self, query, **params):
        self.runs.append((query, params))


def test_constraints_cover_user_and_job():
    joined = " ".join(CONSTRAINT_STATEMENTS)
    assert "u:User" in joined
    assert "j:Job" in joined
    assert joined.count("IF NOT EXISTS") == 2


def test_merge_statements_use_merge_not_create():
    for query in (MERGE_USER, MERGE_JOB, MERGE_HAS_JOB):
        assert "MERGE" in query
        assert "CREATE (" not in query


def test_write_graph_runs_constraints_then_nodes_then_relationships():
    session = _FakeSession()
    users = [{"id": 1, "name": "김민준", "email": "minjun.kim@example.com", "age": 32}]
    jobs = [{"id": 1, "title": "백엔드 개발자", "company": "카카오", "userid": 1}]

    write_graph(session, users, jobs)

    queries = [q for q, _ in session.runs]
    assert len(queries) == 2 + 1 + 1 + 1  # 제약 2 + user 1 + job 1 + 관계 1
    assert queries[0] in CONSTRAINT_STATEMENTS
    assert queries[1] in CONSTRAINT_STATEMENTS
    assert queries[2] == MERGE_USER
    assert queries[3] == MERGE_JOB
    assert queries[4] == MERGE_HAS_JOB


def test_write_graph_passes_row_values_as_parameters():
    session = _FakeSession()
    users = [{"id": 7, "name": "정하은", "email": "haeun.jung@example.com", "age": 35}]
    jobs = [{"id": 9, "title": "머신러닝 엔지니어", "company": "라인", "userid": 7}]

    write_graph(session, users, jobs)

    _, user_params = session.runs[2]
    assert user_params == {
        "id": 7,
        "name": "정하은",
        "email": "haeun.jung@example.com",
        "age": 35,
    }
    _, rel_params = session.runs[4]
    assert rel_params == {"userid": 7, "jobid": 9}
