from datetime import UTC, datetime
from uuid import uuid4

from app.agents.generation_templates import LAYOUTS, MODULE_COPY
from app.core.config import settings
from app.schemas.generation import CreateGenerationTaskRequest
from app.services.gemini_generation import GeminiAPlusGenerationClient
from app.services.gemini_image import GeminiImageGenerationClient
from app.services.visual_assets import select_module_image_url


class MockGenerationAgent:
    def __init__(
        self,
        gemini_client: GeminiAPlusGenerationClient | None = None,
        image_client: GeminiImageGenerationClient | None = None,
    ) -> None:
        self.gemini_client = gemini_client or GeminiAPlusGenerationClient()
        self.image_client = image_client or GeminiImageGenerationClient()

    def run(self, payload: CreateGenerationTaskRequest) -> tuple[dict, dict, dict]:
        now = datetime.now(UTC).isoformat()
        task_id = str(uuid4())
        session_id = str(uuid4())
        product_id = payload.product_id or str(uuid4())
        product_name = payload.product_info.product_name or "未命名商品"
        generated = self._generate_with_llm(payload)

        modules = []
        for index, module_type in enumerate(payload.modules):
            fallback_title, fallback_description = MODULE_COPY.get(module_type, ("详情模块", "商品详情页模块文案。"))
            generated_module = self._module_from_generated(generated, module_type)
            visual_prompt = generated_module.get("visualPrompt") or generated_module.get("visual_prompt") or ""
            template_id = payload.mockup_plan.template_id if payload.mockup_plan else None
            image_url = self._generate_image_url(payload, module_type, template_id, visual_prompt, index)
            modules.append(
                {
                    "id": str(uuid4()),
                    "type": module_type,
                    "title": generated_module.get("title") or (f"{product_name} 核心卖点" if index == 0 else fallback_title),
                    "subtitle": generated_module.get("subtitle") or fallback_title,
                    "description": generated_module.get("description") or fallback_description,
                    "imageUrl": image_url,
                    "visualPrompt": visual_prompt or None,
                    "layout": generated_module.get("layout") or LAYOUTS[index % len(LAYOUTS)],
                    "sortOrder": index,
                }
            )

        task = {
            "id": task_id,
            "productName": product_name,
            "status": "completed",
            "progress": 100,
            "currentStep": "生成完成",
            "createdAt": now,
            "conversationSessionId": session_id,
        }
        result = {
            "id": str(uuid4()),
            "taskId": task_id,
            "productId": product_id,
            "modules": modules,
            "previewUrl": None,
            "exportUrls": {},
            "qualityScore": 91.0,
            "metadata": {
                "promptConfig": payload.prompt_config.model_dump(by_alias=True),
                "styleMemory": payload.style_memory.model_dump(by_alias=True),
                "mockupPlan": payload.mockup_plan.model_dump(by_alias=True) if payload.mockup_plan else None,
                "targetSize": self._target_size(payload.image_ratio),
                "imageModel": payload.image_model or settings.default_image_model,
                "agentProvider": settings.generation_agent_provider,
                "productAnalysis": generated.get("productAnalysis") if generated else None,
                "visualPrompts": generated.get("visualPrompts") if generated else [],
                "qualityNotes": generated.get("qualityNotes") if generated else [],
            },
        }
        session = {
            "id": session_id,
            "taskId": task_id,
            "productId": product_id,
            "status": "active",
            "context": {"latestResultId": result["id"], "moduleCount": len(modules)},
            "createdAt": now,
        }
        return task, result, session

    def _target_size(self, image_ratio: str | None) -> dict[str, str]:
        mapping = {
            "1_1": {"ratio": "1:1", "pixels": "1600x1600"},
            "2_3": {"ratio": "2:3", "pixels": "1600x2400"},
            "3_4": {"ratio": "3:4", "pixels": "1600x2133"},
            "4_5": {"ratio": "4:5", "pixels": "1600x2000"},
            "9_16": {"ratio": "9:16", "pixels": "1440x2560"},
            "16_9": {"ratio": "16:9", "pixels": "1600x900"},
            "platform_default": {"ratio": "16:9", "pixels": "1600x900"},
        }
        if image_ratio and image_ratio.startswith("model_"):
            parts = image_ratio.split("_")
            if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
                return {"ratio": f"{int(parts[1])}:{int(parts[2])}", "pixels": "follow_model_ratio"}
        return mapping.get(image_ratio or "", mapping["platform_default"])

    def _generate_with_llm(self, payload: CreateGenerationTaskRequest) -> dict | None:
        if settings.generation_agent_provider != "gemini":
            return None
        try:
            return self.gemini_client.generate(payload)
        except Exception:
            return None

    def _module_from_generated(self, generated: dict | None, module_type: str) -> dict:
        if not generated:
            return {}
        modules = generated.get("modules")
        if not isinstance(modules, list):
            return {}
        return next((item for item in modules if isinstance(item, dict) and item.get("type") == module_type), {})

    def _generate_image_url(
        self,
        payload: CreateGenerationTaskRequest,
        module_type: str,
        template_id: str | None,
        visual_prompt: str,
        index: int,
    ) -> str:
        fallback_url = select_module_image_url(module_type, template_id, visual_prompt, index)
        if settings.image_generation_provider != "gemini":
            return fallback_url
        try:
            mockup_image_url = None
            if payload.mockup_plan and payload.mockup_plan.template:
                mockup_image_url = payload.mockup_plan.template.preview_url
            return (
                self.image_client.generate_module_image(
                    visual_prompt,
                    module_type,
                    payload.image_ratio,
                    payload.images,
                    mockup_image_url,
                    payload.image_model,
                )
                or fallback_url
            )
        except Exception:
            return fallback_url
