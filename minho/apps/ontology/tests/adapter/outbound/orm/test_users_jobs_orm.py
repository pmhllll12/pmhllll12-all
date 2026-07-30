from __future__ import annotations

from ontology.adapter.outbound.orm.job_orm import JobOrm
from ontology.adapter.outbound.orm.user_orm import UserOrm


def test_user_table_name_and_columns():
    assert UserOrm.__tablename__ == "ontology_users"
    columns = UserOrm.__table__.columns
    assert set(columns.keys()) == {"id", "name", "email", "age", "embedding"}
    assert columns["id"].primary_key is True
    assert columns["email"].unique is True
    assert columns["name"].nullable is False
    assert columns["age"].nullable is True


def test_job_table_name_and_columns():
    assert JobOrm.__tablename__ == "ontology_jobs"
    columns = JobOrm.__table__.columns
    assert set(columns.keys()) == {"id", "title", "company", "userid", "embedding"}
    assert columns["userid"].nullable is False


def test_job_userid_is_fk_to_users_with_cascade():
    fk = next(iter(JobOrm.__table__.columns["userid"].foreign_keys))
    assert fk.column.table.name == "ontology_users"
    assert fk.column.name == "id"
    assert fk.ondelete == "CASCADE"


def test_embedding_columns_are_768_dim_and_nullable():
    for orm in (UserOrm, JobOrm):
        column = orm.__table__.columns["embedding"]
        assert column.nullable is True
        assert column.type.dim == 768
