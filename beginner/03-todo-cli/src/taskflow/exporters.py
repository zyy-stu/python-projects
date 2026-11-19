"""以原子替换方式导出 CSV。"""

import csv
import os
import tempfile
from collections.abc import Iterable
from dataclasses import asdict, fields
from pathlib import Path

from .models import Task


def export_csv(tasks: Iterable[Task], output: Path) -> int:
    """导出 UTF-8 CSV，失败时清理临时文件并保留旧输出。"""
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    count = 0
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            newline="",
            dir=output.parent,
            prefix=".taskflow-",
            delete=False,
        ) as stream:
            temporary = stream.name
            writer = csv.DictWriter(stream, fieldnames=[field.name for field in fields(Task)])
            writer.writeheader()
            for task in tasks:
                writer.writerow(asdict(task))
                count += 1
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
        return count
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)
