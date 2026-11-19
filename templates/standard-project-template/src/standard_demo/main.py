"""打印问候的最小可运行入口。"""

import logging
import os


def greeting(name: str) -> str:
    """返回规范化问候，空输入失败。"""
    if not name.strip():
        raise ValueError("姓名不能为空")
    return f"你好，{name.strip()}"


def main() -> None:
    """读取配置并输出结果。"""
    logging.basicConfig(level=logging.INFO)
    name = os.environ.get("DEMO_NAME", "学习者")
    print(greeting(name))


if __name__ == "__main__":
    main()
