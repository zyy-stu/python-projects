"""命令解析与可读 JSON 输出。"""

import argparse
import json
import logging
import sqlite3
import sys
from dataclasses import asdict
from pathlib import Path

from .config import Config
from .database import Database
from .exceptions import TaskFlowError, ValidationError
from .exporters import export_csv
from .models import PRIORITIES, STATUSES
from .repository import TaskRepository
from .services import TaskService


def parser() -> argparse.ArgumentParser:
    """构造命令定义，配置选项置于子命令之前。"""
    root = argparse.ArgumentParser(description="TaskFlow 命令行任务管理")
    root.add_argument("--db", help="SQLite 路径，覆盖 TASKFLOW_DB")
    root.add_argument("--verbose", action="store_true", help="记录操作日志")
    commands = root.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="新增任务")
    add.add_argument("title")
    add.add_argument("--description", default="")
    add.add_argument("--priority", choices=PRIORITIES, default="normal")
    add.add_argument("--due-date")
    listing = commands.add_parser("list", help="列出任务")
    listing.add_argument("--status", choices=STATUSES)
    listing.add_argument("--priority", choices=PRIORITIES)
    listing.add_argument("--due-before", help="包含该日的截止日期上界")
    for name in ("show", "delete", "complete", "reopen"):
        commands.add_parser(name).add_argument("id", type=int)
    update = commands.add_parser("update")
    update.add_argument("id", type=int)
    for name in ("title", "description", "due-date"):
        update.add_argument("--" + name)
    update.add_argument("--priority", choices=PRIORITIES)
    update.add_argument("--clear-due-date", action="store_true")
    commands.add_parser("search").add_argument("keyword")
    export = commands.add_parser("export")
    export.add_argument("--output", required=True, type=Path)
    return root


def main(argv: list[str] | None = None) -> int:
    """把可预见错误变成退出码 1，解析错误由 argparse 返回 2。"""
    args = parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    try:
        config = Config.load(args.db)
        if args.command == "export" and args.output.expanduser().resolve() == config.database:
            raise ValidationError("导出路径不能与数据库相同")
        repository = TaskRepository(Database(config.database))
        service = TaskService(repository)
        if args.command == "add":
            result = service.add(args.title, args.description, args.priority, args.due_date)
        elif args.command == "list":
            result = repository.list(
                status=args.status, priority=args.priority, due_before=args.due_before
            )
        elif args.command == "show":
            result = repository.get(args.id)
        elif args.command == "update":
            if args.clear_due_date and args.due_date is not None:
                raise ValidationError("不能同时设置和清除截止日期")
            changes = {
                key: getattr(args, key)
                for key in ("title", "description", "priority", "due_date")
                if getattr(args, key) is not None
            }
            if args.clear_due_date:
                changes["due_date"] = None
            if not changes:
                raise ValidationError("至少提供一个要修改的字段")
            result = repository.update(args.id, changes)
        elif args.command in ("complete", "reopen"):
            result = service.set_completed(args.id, args.command == "complete")
        elif args.command == "delete":
            repository.delete(args.id)
            result = {"deleted": args.id}
        elif args.command == "search":
            result = service.search(args.keyword)
        else:
            count = export_csv(repository.list(), args.output)
            result = {"exported": count, "output": str(args.output)}
        if isinstance(result, list):
            payload = [asdict(task) for task in result]
        elif isinstance(result, dict):
            payload = result
        else:
            payload = asdict(result)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except (TaskFlowError, sqlite3.Error, OSError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
