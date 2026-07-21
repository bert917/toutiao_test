from pydantic import BaseModel, Field
from typing import Any, Optional


class ResponseModel(BaseModel):
    """统一 API 响应模型。"""

    code: int = Field(200, description="状态码，200 表示成功")
    message: str = Field("success", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
