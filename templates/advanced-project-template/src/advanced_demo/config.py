"""显式配置对象。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    name: str = "学习者"
