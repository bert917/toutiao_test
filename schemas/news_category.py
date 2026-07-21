from pydantic import BaseModel, Field


class NewsCategoryResponse(BaseModel):
    """新闻分类响应模型。"""

    id: int = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称")
    sort_order: int = Field(..., description="排序序号")

    model_config = {"from_attributes": True}
