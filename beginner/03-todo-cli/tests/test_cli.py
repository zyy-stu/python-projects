"""通过真实 python -m 入口进行端到端验证。"""

import json
import os
import subprocess
import sys

import pytest


def invoke(db, *args):
    environment = dict(os.environ, TASKFLOW_DB=str(db), PYTHONUTF8="1")
    return subprocess.run(
        [sys.executable, "-m", "taskflow", *args],
        env=environment,
        capture_output=True,
        encoding="utf-8",
        timeout=15,
    )


def test_command_lifecycle(tmp_path):
    db = tmp_path / "tasks.db"
    result = invoke(db, "add", "学习 Python", "--priority", "high", "--due-date", "2030-01-01")
    assert result.returncode == 0
    task_id = str(json.loads(result.stdout)["id"])
    for args in [
        ("list",),
        ("show", task_id),
        ("update", task_id, "--title", "学习 Python 高级"),
        ("complete", task_id),
        ("complete", task_id),
        ("list", "--status", "completed"),
        ("reopen", task_id),
        ("list", "--status", "pending"),
        ("search", "Python"),
        ("list", "--priority", "high", "--due-before", "2030-01-01"),
        ("update", task_id, "--clear-due-date"),
        ("export", "--output", str(tmp_path / "tasks.csv")),
        ("delete", task_id),
    ]:
        response = invoke(db, *args)
        assert response.returncode == 0, response.stderr
        json.loads(response.stdout)
    assert invoke(db, "show", task_id).returncode == 1
    assert (tmp_path / "tasks.csv").exists()


@pytest.mark.parametrize(
    "args,code",
    [
        (("add", ""), 1),
        (("add", "x", "--priority", "wrong"), 2),
        (("show", "0"), 1),
        (("show", "999"), 1),
        (("add", "x", "--due-date", "2025-02-30"), 1),
        (("update", "1"), 1),
        (("--help",), 0),
    ],
)
def test_invalid_inputs(tmp_path, args, code):
    assert invoke(tmp_path / "isolated.db", *args).returncode == code


def test_protect_database_export(tmp_path):
    db = tmp_path / "tasks.db"
    assert invoke(db, "add", "保存").returncode == 0
    assert invoke(db, "export", "--output", str(db)).returncode == 1
    assert json.loads(invoke(db, "list").stdout)[0]["title"] == "保存"
