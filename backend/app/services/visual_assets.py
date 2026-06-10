from app.services.mockup_repository import list_mockup_templates


MODULE_IMAGE_URLS: dict[str, str] = {
    "full_aplus_mockup": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
    "hero": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
    "selling_points": "https://images.unsplash.com/photo-1581090464777-f3220bbe1b8b?auto=format&fit=crop&w=1200&q=80",
    "usage_scene": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
    "multi_angle": "https://images.unsplash.com/photo-1587614382346-4ec70e388b28?auto=format&fit=crop&w=1200&q=80",
    "atmosphere": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=80",
    "specs": "https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?auto=format&fit=crop&w=1200&q=80",
    "comparison": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80",
    "faq": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&w=1200&q=80",
    "brand_story": "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1200&q=80",
}


def select_module_image_url(module_type: str, template_id: str | None, visual_prompt: str, index: int) -> str:
    template = next((item for item in list_mockup_templates() if item["id"] == template_id), None)
    prompt = visual_prompt.lower()

    if template and module_type in {"full_aplus_mockup", "hero", "usage_scene", "atmosphere"}:
        return template["previewUrl"]
    if "camp" in prompt or "outdoor" in prompt or "hiking" in prompt:
        return _template_url("outdoor-camping-table")
    if "office" in prompt or "desk" in prompt or "productivity" in prompt:
        return _template_url("office-desk-productivity")
    if "beauty" in prompt or "vanity" in prompt:
        return _template_url("beauty-vanity-premium")
    if "pet" in prompt:
        return _template_url("pet-home-cozy")
    if "fitness" in prompt or "gym" in prompt:
        return _template_url("fitness-studio-action")

    return f"{MODULE_IMAGE_URLS.get(module_type, MODULE_IMAGE_URLS['hero'])}&sig={index}"


def _template_url(template_id: str) -> str:
    template = next((item for item in list_mockup_templates() if item["id"] == template_id), None)
    return template["previewUrl"] if template else MODULE_IMAGE_URLS["hero"]
