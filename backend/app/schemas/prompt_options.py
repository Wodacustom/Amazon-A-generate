from pydantic import BaseModel


class PromptOption(BaseModel):
    key: str
    label: str
    prompt: str
    negative: bool = False


class PromptOptionGroup(BaseModel):
    key: str
    label: str
    selection: str = "multiple"
    options: list[PromptOption]


class PromptOptionGroupList(BaseModel):
    items: list[PromptOptionGroup]
