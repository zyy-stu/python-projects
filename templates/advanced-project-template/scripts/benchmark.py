"""手动执行轻量性能基线，不设置机器相关的通过阈值。"""

from timeit import timeit

from advanced_demo.main import greeting

if __name__ == "__main__":
    print(timeit(lambda: greeting("学习者"), number=1000))
