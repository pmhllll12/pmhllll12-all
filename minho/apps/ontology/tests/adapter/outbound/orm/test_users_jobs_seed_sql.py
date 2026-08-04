from __future__ import annotations

from pathlib import Path

_SEED_FILE = (
    Path(__file__).resolve().parents[4] / "resources" / "users_jobs_seed_data.sql"
)


def test_seed_file_exists():
    assert _SEED_FILE.is_file()


def test_seed_has_five_users_and_five_jobs():
    sql = _SEED_FILE.read_text(encoding="utf-8")
    assert sql.count("INSERT INTO ontology_users") == 1
    assert sql.count("INSERT INTO ontology_jobs") == 1
    # 각 INSERT 의 VALUES 행 수 = 5
    users_block = sql.split("INSERT INTO ontology_users")[1].split(";")[0]
    jobs_block = sql.split("INSERT INTO ontology_jobs")[1].split(";")[0]
    assert users_block.count("(") - users_block.count("(id") == 5
    assert jobs_block.count("(") - jobs_block.count("(id") == 5


def test_seed_uses_reserved_example_domain():
    sql = _SEED_FILE.read_text(encoding="utf-8")
    assert sql.count("@example.com") == 5


def test_seed_resets_both_sequences():
    sql = _SEED_FILE.read_text(encoding="utf-8")
    assert "ontology_users_id_seq" in sql
    assert "ontology_jobs_id_seq" in sql
