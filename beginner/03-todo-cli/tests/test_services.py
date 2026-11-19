"""状态幂等与搜索规则。"""

import pytest
from taskflow.exceptions import TaskNotFound
from taskflow.services import TaskService


def test_complete_reopen_and_search(repository):
    service = TaskService(repository)
    task = service.add("Python 学习")
    done = service.set_completed(task.id, True)
    assert done.status == "completed"
    assert service.set_completed(task.id, True).updated_at == done.updated_at
    assert service.set_completed(task.id, False).status == "pending"
    assert service.search("python")[0].id == task.id


def test_missing_task(repository):
    with pytest.raises(TaskNotFound):
        TaskService(repository).set_completed(999, True)
