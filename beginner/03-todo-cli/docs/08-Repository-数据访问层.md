# 08 Repository 数据访问层

## 本章目标

列名仅来自白名单，值使用占位参数。update 在写事务内查询刚更新的行；缺失记录转成业务异常。

## 前置知识

能够使用 Python 函数、包导入、异常和上下文管理器。先阅读[项目安装与命令](../README.md)，运行最小新增和查询，再学习本章。

## 设计思路

列名仅来自白名单，值使用占位参数。update 在写事务内查询刚更新的行；缺失记录转成业务异常。 本项目对任务创建允许相同标题，使用 ID 区分。持久化时间以 UTC 记录，截止日期按 YYYY-MM-DD 验证。

## 核心代码

下面摘自当前实际实现 [repository.py](../src/taskflow/repository.py)。

```python
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
```

## 代码解释

创建、更新、删除在各自连接事务内执行。筛选将 SQL 条件与参数列表同步构造；keyword 使用 instr，避免把百分号当通配符。

## 运行方法

在项目目录执行编辑安装：

```bash
python -m pip install -e .
python -m taskflow --db demo.db add "学习 Python" --priority high
python -m taskflow --db demo.db update 1 --title "新标题"
```

首次演练从新数据库开始，已有数据库时按实际新增返回的 ID 替换示例中的 1。正常查询打印 JSON；不存在任务打印错误到 stderr 并返回 1。帮助命令不创建数据库。

## 测试方法

安装开发依赖后运行相关测试和完整测试：

```bash
python -m pip install pytest==9.2.0 ruff==0.11.13
python -m pytest tests/test_repository.py -q
python -m pytest -q
```

核对[实际测试文件](../tests/test_repository.py)的断言。测试数据放在 tmp_path，CLI 测试通过 TASKFLOW_DB 指向临时文件。测试运行结果以关联提交的 CI 为准。

## 常见问题

- 找不到 taskflow 时检查当前解释器是否完成编辑安装。
- 日期错误时用完整的 YYYY-MM-DD，空标题和大于 200 字的标题也会被拒绝。
- 数据不一致时检查 --db 与 TASKFLOW_DB，确认调用的是同一数据库。
- CSV 按文本导入；导出内容保留原文，不对标题自动改写。

## 本章总结

列名仅来自白名单，值使用占位参数。update 在写事务内查询刚更新的行；缺失记录转成业务异常。 修改时同步验证相关成功、异常和边界场景，再核对实际命令输出。

[教程目录](README.md) · [扩展练习](../exercises/README.md)
