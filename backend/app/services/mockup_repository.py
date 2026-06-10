from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.schemas.mockup import CreateMockupTemplateRequest
from app.services.in_memory import store
from app.services.mockup_catalog import MOCKUP_TEMPLATES


def _custom_templates_path() -> Path:
    return Path(settings.local_storage_dir) / "mockup_templates.json"


def _load_custom_templates() -> dict[str, dict]:
    path = _custom_templates_path()
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if not isinstance(payload, list):
        return {}

    templates = {}
    for item in payload:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            templates[item["id"]] = item
    return templates


def _persist_custom_templates(templates: dict[str, dict]) -> None:
    path = _custom_templates_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = sorted(templates.values(), key=lambda item: item["id"])
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(path)


def _custom_templates() -> dict[str, dict]:
    persisted = _load_custom_templates()
    if persisted:
        store.mockup_templates.update(persisted)
    return {**persisted, **store.mockup_templates}


def list_mockup_templates() -> list[dict]:
    return [*MOCKUP_TEMPLATES, *_custom_templates().values()]


def get_mockup_template(template_id: str) -> dict | None:
    return next((item for item in list_mockup_templates() if item["id"] == template_id), None)


def create_mockup_template(payload: CreateMockupTemplateRequest) -> dict:
    template_id = f"custom-{uuid4()}"
    template = {
        "id": template_id,
        "name": payload.name,
        "category": payload.category,
        "scenes": payload.scenes,
        "platforms": payload.platforms,
        "ratios": payload.ratios,
        "composition": payload.composition,
        "replaceableAreas": [area.model_dump(by_alias=True) for area in payload.replaceable_areas],
        "previewUrl": payload.preview_url,
        "sourceUrl": payload.source_url or f"mockup://{template_id}",
        "tags": payload.tags,
    }
    store.mockup_templates[template_id] = template
    _persist_custom_templates(_custom_templates())
    return template
