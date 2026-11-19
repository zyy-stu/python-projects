"""为每项测试隔离数据库。"""

import pytest
from taskflow.database import Database
from taskflow.repository import TaskRepository


@pytest.fixture
def repository(tmp_path):
    return TaskRepository(Database(tmp_path / "test.db"))
