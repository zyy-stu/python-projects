"""验证正常及空配置行为。"""

import pytest
from basic_demo.main import greeting


def test_greeting():
    assert greeting(" 小林 ") == "你好，小林"


def test_empty_name():
    with pytest.raises(ValueError):
        greeting(" ")
