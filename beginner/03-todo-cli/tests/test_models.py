"""模型输入与时间校验。"""

from datetime import datetime

import pytest
from taskflow.exceptions import ValidationError
from taskflow.models import Task, validate_fields, validate_id


@pytest.mark.parametrize(
    "fields",
    [
        {"title": ""},
        {"title": " "},
        {"title": "a" * 201},
        {"priority": "urgent"},
        {"status": "other"},
        {"due_date": "2025-02-30"},
        {"due_date": "20251102"},
        {"unknown": "x"},
        {"description": "a" * 10001},
    ],
)
def test_invalid_fields(fields):
    with pytest.raises(ValidationError):
        validate_fields(fields)


@pytest.mark.parametrize("value", [0, -1, True, "1"])
def test_invalid_ids(value):
    with pytest.raises(ValidationError):
        validate_id(value)


def test_task_time(repository):
    task = repository.create(" 学习 ")
    assert isinstance(task, Task)
    assert task.title == "学习"
    assert datetime.fromisoformat(task.created_at).tzinfo is not None
    assert task.created_at == task.updated_at
