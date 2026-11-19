"""入口配置到接口实现的集成验证。"""

from advanced_demo.config import Config
from advanced_demo.service import run


class FakeGreeter:
    def greet(self, name: str) -> str:
        return f"测试:{name}"


def test_service_injection():
    assert run(Config("小林"), FakeGreeter()) == "测试:小林"
