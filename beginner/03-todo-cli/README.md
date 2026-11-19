# TaskFlow CLI

使用 Python 3.11+、标准库 argparse 和 SQLite。argparse 随 Python 提供，能生成帮助、校验选项，并减少运行依赖。

## 安装与检查

在本项目目录执行：

```bash
python -m pip install -e .
python -m taskflow --help
python -m pip install pytest==9.2.0 ruff==0.11.13
python -m pytest
python -m ruff check .
python -m ruff format --check .
```

运行时只有标准库依赖。默认数据库为用户目录的 `.taskflow/tasks.db`。可以用环境变量 `TASKFLOW_DB`，或将 `--db ./demo.db` 放在子命令之前覆盖配置。演练时选择独立数据库。

## 核心命令

```bash
python -m taskflow --db demo.db add "学习 Python" --priority high --due-date 2030-01-01
python -m taskflow --db demo.db list
python -m taskflow --db demo.db show 1
python -m taskflow --db demo.db update 1 --title "学习 Python 高级"
python -m taskflow --db demo.db complete 1
python -m taskflow --db demo.db reopen 1
python -m taskflow --db demo.db list --status pending --priority high --due-before 2030-01-01
python -m taskflow --db demo.db search "Python"
python -m taskflow --db demo.db export --output tasks.csv
python -m taskflow --db demo.db delete 1
```

`update --clear-due-date` 清除日期。状态更新幂等，同名标题允许多条，每条有独立 ID。标题去除两端空白，长度 1–200；描述上限 10000；日期严格为 YYYY-MM-DD。截止日期筛选包含上界，无截止日期的任务不会匹配该筛选。按 ID 升序显示，关键词按字面查找，英文大小写不敏感。

## 日志与错误

`--verbose` 在 stderr 打印操作日志，仅记录 ID 与状态。参数错误退出码为 2，业务或存储错误为 1，成功为 0。CSV 使用 UTF-8 BOM，保留标题与描述的原文，使用表格程序打开时按文本导入。导出先写临时文件再替换目标，不能导出到数据库本身。

文件写入失败先检查路径与权限，数据库忙时检查其他程序是否长期占用事务。

[完整教程](docs/README.md) · [需求](docs/requirements.md) · [架构](docs/architecture.md) · [数据库](docs/database-design.md) · [练习](exercises/README.md)
