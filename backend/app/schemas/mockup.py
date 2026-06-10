from pydantic import BaseModel, ConfigDict, Field

from app.schemas.aliases import to_camel
from app.schemas.product import ProductInfo


class ReplaceableArea(BaseModel):
    id: str
    type: str
    x: int
    y: int
    width: int
    height: int

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class MockupTemplate(BaseModel):
    id: str
    name: str
    category: list[str]
    scenes: list[str]
    platforms: list[str]
    ratios: list[str]
    composition: str
    replaceable_areas: list[ReplaceableArea]
    preview_url: str
    source_url: str
    tags: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class CreateMockupTemplateRequest(BaseModel):
    name: str
    category: list[str] = Field(default_factory=list)
    scenes: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=lambda: ["amazon"])
    ratios: list[str] = Field(default_factory=lambda: ["platform_default"])
    composition: str = "center"
    replaceable_areas: list[ReplaceableArea] = Field(default_factory=list)
    preview_url: str
    source_url: str | None = None
    tags: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class ScenePrompt(BaseModel):
    positive: str
    negative: str
    composition: str
    product_placement: str
    supporting_props: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class SceneRecommendation(BaseModel):
    id: str
    name: str
    category: str
    audience: str
    reason: str
    risk_notes: list[str] = Field(default_factory=list)
    prompt: ScenePrompt

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class MatchedMockup(BaseModel):
    template: MockupTemplate
    scene_id: str
    score: int
    reason: str

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class MockupGenerationPlan(BaseModel):
    scene_id: str
    template_id: str
    template: MockupTemplate | None = None
    match_score: int | None = None
    scene_prompt: ScenePrompt
    composition_notes: str

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class MockupRecommendationRequest(BaseModel):
    product_info: ProductInfo
    images: list[str] = Field(default_factory=list)
    platform: str = "amazon"
    country: str = "US"
    language: str = "en"
    image_ratio: str | None = None
    design_style: str | None = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class MockupRecommendationResponse(BaseModel):
    product_category: str
    scenes: list[SceneRecommendation]
    matched_mockups: list[MatchedMockup]
    selected_plan: MockupGenerationPlan | None = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
