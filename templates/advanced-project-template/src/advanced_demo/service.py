"""可替换的问候接口与实现。"""

from typing import Protocol

from .config import Config
from .exceptions import ApplicationError


class Greeter(Protocol):
    """由入口依赖的最小契约。"""

    def greet(self, name: str) -> str: ...


class TextGreeter:
    """文本实现。"""

    def greet(self, name: str) -> str:
        if not name.strip():
            raise ApplicationError("姓名不能为空")
        return f"你好，{name.strip()}"


def run(config: Config, greeter: Greeter) -> str:
    """通过注入的接口执行用例。"""
    return greeter.greet(config.name)
