from fastapi import APIRouter

from app.agents.mockup_recommendation import MockupRecommendationAgent
from app.schemas.mockup import (
    CreateMockupTemplateRequest,
    MockupRecommendationRequest,
    MockupRecommendationResponse,
    MockupTemplate,
)
from app.services.mockup_repository import create_mockup_template, get_mockup_template, list_mockup_templates as list_templates

router = APIRouter()
agent = MockupRecommendationAgent()


@router.get("/templates", response_model=list[MockupTemplate])
def list_mockup_templates() -> list[dict]:
    return list_templates()


@router.post("/templates", response_model=MockupTemplate, status_code=201)
def create_template(payload: CreateMockupTemplateRequest) -> dict:
    return create_mockup_template(payload)


@router.get("/templates/{template_id}", response_model=MockupTemplate)
def get_template(template_id: str) -> dict:
    template = get_mockup_template(template_id)
    if not template:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Mockup template not found")
    return template


@router.post("/recommend", response_model=MockupRecommendationResponse)
def recommend_mockups(payload: MockupRecommendationRequest) -> dict:
    return agent.run(payload)
