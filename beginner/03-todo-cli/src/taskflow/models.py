"""任务数据与输入约束。"""

from dataclasses import dataclass
from datetime import date, datetime

from .exceptions import ValidationError

PRIORITIES = ("low", "normal", "high")
STATUSES = ("pending", "completed")


def validate_fields(fields: dict[str, object]) -> dict[str, object]:
    """校验并规范字段，拒绝未知列。"""
    allowed = {"title", "description", "priority", "status", "due_date"}
    if set(fields) - allowed:
        raise ValidationError("存在未知字段")
    result = dict(fields)
    if "title" in result:
        title = result["title"]
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 200:
            raise ValidationError("标题去空白后必须为 1 到 200 个字符")
        result["title"] = title.strip()
    if "description" in result:
        if not isinstance(result["description"], str) or len(result["description"]) > 10000:
            raise ValidationError("描述必须为不超过 10000 字的文本")
    if "priority" in result and result["priority"] not in PRIORITIES:
        raise ValidationError("优先级应为 low、normal 或 high")
    if "status" in result and result["status"] not in STATUSES:
        raise ValidationError("状态应为 pending 或 completed")
    if "due_date" in result and result["due_date"] is not None:
        try:
            value = result["due_date"]
            if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
                raise ValueError
        except (ValueError, TypeError):
            raise ValidationError("日期应为 YYYY-MM-DD") from None
    return result


def validate_id(task_id: int) -> None:
    """任务 ID 必须是正整数。"""
    if type(task_id) is not int or task_id < 1:
        raise ValidationError("任务 ID 必须为正整数")


@dataclass(frozen=True)
class Task:
    """持久化任务快照，时间为 UTC ISO 格式。"""

    id: int
    title: str
    description: str
    priority: str
    status: str
    due_date: str | None
    created_at: str
    updated_at: str

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_fields(
            {
                "title": self.title,
                "description": self.description,
                "priority": self.priority,
                "status": self.status,
                "due_date": self.due_date,
            }
        )
        for value in (self.created_at, self.updated_at):
            try:
                timestamp = datetime.fromisoformat(value)
                if timestamp.tzinfo is None:
                    raise ValueError
            except ValueError:
                raise ValidationError("时间必须包含时区") from None
