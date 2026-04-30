"""
应用异常体系。

继承 FastAPI HTTPException，统一错误响应格式。
所有业务层抛出的异常均从 AppException 派生，便于全局异常处理器统一捕获。
"""
from fastapi import HTTPException, status


class AppException(HTTPException):
    """所有应用级异常的基类。"""


class NotFoundError(AppException):
    """资源不存在（HTTP 404）。"""

    def __init__(self, msg: str = "资源不存在") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=msg)


class UnauthorizedError(AppException):
    """未登录或令牌已过期（HTTP 401）。"""

    def __init__(self, msg: str = "未登录或登录已过期") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)


class ForbiddenError(AppException):
    """权限不足（HTTP 403）。"""

    def __init__(self, msg: str = "无权限执行此操作") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=msg)


class BadRequestError(AppException):
    """请求参数错误（HTTP 400）。"""

    def __init__(self, msg: str = "请求参数错误") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


class ConflictError(AppException):
    """资源冲突，如重复注册（HTTP 409）。"""

    def __init__(self, msg: str = "资源已存在") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=msg)


class UnprocessableError(AppException):
    """业务逻辑无法处理（HTTP 422）。"""

    def __init__(self, msg: str = "请求内容无法处理") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg
        )
