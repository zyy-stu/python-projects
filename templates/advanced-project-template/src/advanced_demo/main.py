"""高级模板入口，读取配置并注入具体服务。"""

import logging
import os

from .config import Config
from .exceptions import ApplicationError
from .service import TextGreeter, run


def greeting(name: str) -> str:
    """验证并输出问候，保持公共函数契约。"""
    try:
        return run(Config(name), TextGreeter())
    except ApplicationError as error:
        raise ValueError(str(error)) from error


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    print(greeting(os.environ.get("DEMO_NAME", "学习者")))


if __name__ == "__main__":
    main()
