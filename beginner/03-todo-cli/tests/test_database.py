"""SQL 约束和事务。"""

import sqlite3

import pytest
from taskflow.database import Database


def test_initialization_is_repeatable(tmp_path):
    path = tmp_path / "task.db"
    Database(path)
    database = Database(path)
    with database.connect() as conn:
        assert conn.execute("SELECT count(*) FROM tasks").fetchone()[0] == 0


def test_transaction_rolls_back(repository):
    task = repository.create("保留")
    with pytest.raises(RuntimeError), repository.database.connect() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task.id,))
        raise RuntimeError("回滚")
    assert repository.get(task.id).title == "保留"


def test_database_constraint(repository):
    task = repository.create("合法")
    with pytest.raises(sqlite3.IntegrityError), repository.database.connect() as conn:
        conn.execute("UPDATE tasks SET priority='wrong' WHERE id=?", (task.id,))
    assert repository.get(task.id).priority == "normal"
