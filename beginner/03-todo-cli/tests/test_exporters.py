"""验证 CSV 与失败时原子性。"""

import csv

import pytest
from taskflow.exporters import export_csv


def test_export_unicode_and_empty(repository, tmp_path):
    task = repository.create('中文,"任务"', description="第一行\n第二行")
    output = tmp_path / "tasks.csv"
    assert export_csv([task], output) == 1
    with output.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["title"] == task.title
    assert rows[0]["description"] == task.description
    assert export_csv([], output) == 0
    assert len(output.read_text(encoding="utf-8-sig").splitlines()) == 1


def test_export_failure_preserves_original(repository, tmp_path):
    output = tmp_path / "tasks.csv"
    output.write_text("旧数据", encoding="utf-8")
    task = repository.create("新数据")

    def failing_rows():
        yield task
        raise RuntimeError("模拟中断")

    with pytest.raises(RuntimeError):
        export_csv(failing_rows(), output)
    assert output.read_text(encoding="utf-8") == "旧数据"
    assert list(tmp_path.glob(".taskflow-*")) == []
