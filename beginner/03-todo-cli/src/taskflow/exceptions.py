"""可向用户展示的业务错误。"""


class TaskFlowError(Exception):
    """统一业务异常。"""


class ValidationError(TaskFlowError):
    """输入未满足约束。"""


class TaskNotFound(TaskFlowError):
    """目标任务不存在。"""
