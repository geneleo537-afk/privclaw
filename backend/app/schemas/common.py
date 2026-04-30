"""
通用响应 Schema。

Response[T]：统一包装所有 API 响应，code=0 表示成功。
PageData[T] + PageResponse[T]：分页列表响应。
"""
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """统一 API 响应包装器。"""

    code: int = 0
    message: str = "ok"
    data: Optional[T] = None

    @classmethod
    def ok(cls, data: T = None, message: str = "ok") -> "Response[T]":
        """构造成功响应的便捷方法。"""
        return cls(code=0, message=message, data=data)

    @classmethod
    def fail(cls, message: str, code: int = 1) -> "Response[None]":
        """构造失败响应的便捷方法。"""
        return cls(code=code, message=message, data=None)


class PageData(BaseModel, Generic[T]):
    """分页数据载体。"""

    items: List[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """总页数（向上取整）。"""
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size


class PageResponse(Response[PageData[T]], Generic[T]):
    """分页列表响应。"""
