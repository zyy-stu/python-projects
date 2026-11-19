# CSV 导出

## 本章目标与前置知识

同目录临时文件写入完成后原子替换，失败时清理临时文件。 需要了解 Python 函数、模块和异常。

## 设计思路、核心代码与解释

从[exporters.py](../src/taskflow/exporters.py)中的 `export_csv` 开始阅读。同目录临时文件写入完成后原子替换，失败时清理临时文件。
导出先 flush 和 fsync，再 os.replace。finally 在失败路径移除临时文件，原目标不会被部分覆盖。

## 运行和测试

在项目目录安装 `python -m pip install -e .`。按[使用演练](../examples/usage.md)执行相关命令，再运行 `python -m pytest`。检查过程中使用 `--db demo.db` 指定演练数据库。

## 常见问题与总结

导入错误时确认已经完成编辑安装；数据不符合预期时先确认环境变量或命令行覆盖后的数据库路径。同目录临时文件写入完成后原子替换，失败时清理临时文件。

[教程目录](README.md)
