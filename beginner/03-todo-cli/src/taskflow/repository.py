"""参数化 SQL 数据访问。"""

from datetime import UTC, datetime

from .database import Database
from .exceptions import TaskNotFound
from .models import Task, validate_fields, validate_id


class TaskRepository:
    """提供数据库 CRUD，约束动态列名及输入。"""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        title: str,
        description: str = "",
        priority: str = "normal",
        due_date: str | None = None,
    ) -> Task:
        fields = validate_fields(
            {
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date,
            }
        )
        now = datetime.now(UTC).isoformat(timespec="microseconds")
        with self.database.connect() as connection:
            cursor = connection.execute(
                """INSERT INTO tasks
                (title, description, priority, status, due_date, created_at, updated_at)
                VALUES (?, ?, ?, 'pending', ?, ?, ?)""",
                (fields["title"], description, priority, due_date, now, now),
            )
            task_id = cursor.lastrowid
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return Task(**dict(row))

    def get(self, task_id: int) -> Task:
        validate_id(task_id)
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise TaskNotFound(f"任务 {task_id} 不存在")
        return Task(**dict(row))

    def list(
        self,
        status: str | None = None,
        priority: str | None = None,
        keyword: str | None = None,
        due_before: str | None = None,
    ) -> list[Task]:
        filters, parameters = [], []
        validate_fields(
            {
                k: v
                for k, v in {
                    "status": status,
                    "priority": priority,
                    "due_date": due_before,
                }.items()
                if v is not None
            }
        )
        for name, value in (("status", status), ("priority", priority)):
            if value is not None:
                filters.append(f"{name} = ?")
                parameters.append(value)
        if keyword is not None:
            # instr 按字面搜索，百分号和下划线不作为通配符。
            filters.append(
                "(instr(lower(title), lower(?)) > 0 OR instr(lower(description), lower(?)) > 0)"
            )
            parameters.extend([keyword, keyword])
        if due_before is not None:
            filters.append("due_date <= ?")
            parameters.append(due_before)
        clause = " WHERE " + " AND ".join(filters) if filters else ""
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM tasks" + clause + " ORDER BY id", parameters
            ).fetchall()
        return [Task(**dict(row)) for row in rows]

    def update(self, task_id: int, fields: dict[str, object]) -> Task:
        validate_id(task_id)
        fields = validate_fields(fields)
        if not fields:
            return self.get(task_id)
        fields["updated_at"] = datetime.now(UTC).isoformat(timespec="microseconds")
        assignments = ", ".join(f"{name} = ?" for name in fields)
        with self.database.connect() as connection:
            cursor = connection.execute(
                f"UPDATE tasks SET {assignments} WHERE id = ?", (*fields.values(), task_id)
            )
            if cursor.rowcount != 1:
                raise TaskNotFound(f"任务 {task_id} 不存在")
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return Task(**dict(row))

    def delete(self, task_id: int) -> None:
        validate_id(task_id)
        with self.database.connect() as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            if cursor.rowcount != 1:
                raise TaskNotFound(f"任务 {task_id} 不存在")
