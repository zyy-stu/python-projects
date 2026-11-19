"""CRUD 和筛选行为。"""

import pytest
from taskflow.exceptions import TaskNotFound, ValidationError


def test_crud_and_duplicate_titles(repository):
    first = repository.create("重复")
    second = repository.create("重复")
    assert first.id != second.id
    updated = repository.update(first.id, {"title": "新标题", "due_date": "2030-01-01"})
    assert updated.title == "新标题"
    assert updated.updated_at >= updated.created_at
    repository.delete(second.id)
    with pytest.raises(TaskNotFound):
        repository.get(second.id)


def test_filters_and_literal_search(repository):
    first = repository.create("Python 100%", priority="high", due_date="2030-01-01")
    second = repository.create("其他", due_date="2030-02-01")
    repository.update(second.id, {"status": "completed"})
    assert [t.id for t in repository.list(status="pending", priority="high")] == [first.id]
    assert [t.id for t in repository.list(keyword="%")] == [first.id]
    assert [t.id for t in repository.list(due_before="2030-01-01")] == [first.id]
    assert repository.list(keyword="' OR 1=1 --") == []


def test_unknown_update_and_missing_delete(repository):
    with pytest.raises(ValidationError):
        repository.update(1, {"id": 2})
    with pytest.raises(TaskNotFound):
        repository.delete(99)
