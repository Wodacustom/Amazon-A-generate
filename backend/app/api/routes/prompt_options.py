from fastapi import APIRouter

from app.schemas.prompt_options import PromptOptionGroupList
from app.services.prompt_options import get_prompt_option_groups

router = APIRouter()


@router.get("/prompt-option-groups", response_model=PromptOptionGroupList)
def list_prompt_option_groups() -> PromptOptionGroupList:
    return PromptOptionGroupList(items=get_prompt_option_groups())


@router.get("/prompt-options")
def list_prompt_options() -> dict[str, list[dict]]:
    options = [option.model_dump() for group in get_prompt_option_groups() for option in group.options]
    return {"items": options}
