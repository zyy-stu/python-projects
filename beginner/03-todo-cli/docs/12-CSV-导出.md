# 12 CSV 导出

## 本章目标

先在目标目录写临时文件，flush 和 fsync 后原子替换。finally 清理中断的临时文件，CLI 拒绝导出覆盖数据库本身。

## 前置知识

能够使用 Python 函数、包导入、异常和上下文管理器。先阅读[项目安装与命令](../README.md)，运行最小新增和查询，再学习本章。

## 设计思路

先在目标目录写临时文件，flush 和 fsync 后原子替换。finally 清理中断的临时文件，CLI 拒绝导出覆盖数据库本身。 本项目对任务创建允许相同标题，使用 ID 区分。持久化时间以 UTC 记录，截止日期按 YYYY-MM-DD 验证。

## 核心代码

下面摘自当前实际实现 [exporters.py](../src/taskflow/exporters.py)。

```python
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
```

## 代码解释

csv.DictWriter 保持字段顺序，UTF-8 BOM 便于中文表格读取。临时文件与目标同目录，替换前先完成写入；抛异常后旧输出仍在。

## 运行方法

在项目目录执行编辑安装：

```bash
python -m pip install -e .
python -m taskflow --db demo.db add "学习 Python" --priority high
python -m taskflow --db demo.db export --output demo-tasks.csv
```

首次演练从新数据库开始，已有数据库时按实际新增返回的 ID 替换示例中的 1。正常查询打印 JSON；不存在任务打印错误到 stderr 并返回 1。帮助命令不创建数据库。

## 测试方法

安装开发依赖后运行相关测试和完整测试：

```bash
python -m pip install pytest==9.2.0 ruff==0.11.13
python -m pytest tests/test_exporters.py -q
python -m pytest -q
```

核对[实际测试文件](../tests/test_exporters.py)的断言。测试数据放在 tmp_path，CLI 测试通过 TASKFLOW_DB 指向临时文件。测试运行结果以关联提交的 CI 为准。

## 常见问题

- 找不到 taskflow 时检查当前解释器是否完成编辑安装。
- 日期错误时用完整的 YYYY-MM-DD，空标题和大于 200 字的标题也会被拒绝。
- 数据不一致时检查 --db 与 TASKFLOW_DB，确认调用的是同一数据库。
- CSV 按文本导入；导出内容保留原文，不对标题自动改写。

## 本章总结

先在目标目录写临时文件，flush 和 fsync 后原子替换。finally 清理中断的临时文件，CLI 拒绝导出覆盖数据库本身。 修改时同步验证相关成功、异常和边界场景，再核对实际命令输出。

[教程目录](README.md) · [扩展练习](../exercises/README.md)
