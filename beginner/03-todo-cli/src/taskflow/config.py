"""用户环境配置。"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """命令行覆盖环境变量，再使用默认路径。"""

    database: Path

    @classmethod
    def load(cls, database: str | None = None) -> "Config":
        selected = database or os.environ.get("TASKFLOW_DB")
        path = Path(selected).expanduser() if selected else Path.home() / ".taskflow/tasks.db"
        return cls(path.resolve())
