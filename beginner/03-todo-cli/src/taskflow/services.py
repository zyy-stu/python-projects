"""任务业务操作。"""

import logging

from .models import Task
from .repository import TaskRepository

logger = logging.getLogger(__name__)


class TaskService:
    """状态操作保持幂等，日志只记录操作与 ID。"""

    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def add(
        self,
        title: str,
        description: str = "",
        priority: str = "normal",
        due_date: str | None = None,
    ) -> Task:
        task = self.repository.create(title, description, priority, due_date)
        logger.info("创建任务 id=%s", task.id)
        return task

    def set_completed(self, task_id: int, completed: bool) -> Task:
        task = self.repository.get(task_id)
        status = "completed" if completed else "pending"
        if task.status == status:
            return task
        updated = self.repository.update(task_id, {"status": status})
        logger.info("修改状态 id=%s status=%s", task_id, status)
        return updated

    def search(self, keyword: str) -> list[Task]:
        return self.repository.list(keyword=keyword)
