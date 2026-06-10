from pydantic import BaseModel, ConfigDict, Field

from app.schemas.aliases import to_camel


class ProductInfo(BaseModel):
    product_name: str = ""
    core_selling_points: str = ""
    target_audience: str = ""
    use_scenes: str = ""
    specifications: str = ""
    brand_tone: str = ""
    forbidden_words: str = ""
    compliance_notes: str = ""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class ProductInfoRecommendationRequest(BaseModel):
    product_info: ProductInfo = Field(default_factory=ProductInfo)
    images: list[str] = Field(default_factory=list)
    platform: str = "amazon"
    country: str = "US"
    language: str = "zh-CN"
    design_style: str | None = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class ProductInfoRecommendationResponse(BaseModel):
    product_info: ProductInfo
    selling_points: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    source: str = "rule"

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
