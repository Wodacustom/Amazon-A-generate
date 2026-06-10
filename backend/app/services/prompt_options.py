from app.schemas.prompt_options import PromptOption, PromptOptionGroup
from app.services.prompt_option_catalog import PROMPT_OPTION_GROUPS


def get_prompt_option_groups() -> list[PromptOptionGroup]:
    return [
        PromptOptionGroup(
            key=group["key"],
            label=group["label"],
            options=[PromptOption(**option) for option in group["options"]],
        )
        for group in PROMPT_OPTION_GROUPS
    ]
