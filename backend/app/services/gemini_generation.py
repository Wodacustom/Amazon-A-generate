from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.generation import CreateGenerationTaskRequest

MODULE_COPY: dict[str, tuple[str, str]] = {
    "full_aplus_mockup": ("整页 A+ 样机图", "基于选中的完整样机版式，将商品图融合进去，生成一张完整 A+ 页面图。"),
    "hero": ("首屏主视觉", "突出产品核心价值、品牌可信度和首屏转化重点。"),
    "selling_points": ("核心卖点图", "拆解材质、性能、体验和差异化优势。"),
    "usage_scene": ("使用场景图", "结合目标人群的真实使用场景建立代入感。"),
    "multi_angle": ("多角度图", "展示外观结构、细节和包装，降低购买疑虑。"),
    "atmosphere": ("场景氛围图", "统一光影、色彩和场景语言，增强品牌感。"),
    "specs": ("产品参数图", "把尺寸、材质、重量等参数转化为清晰信息图。"),
    "comparison": ("对比图", "用对比表呈现升级点和选择理由。"),
    "faq": ("FAQ 图文", "回答安装、保养、适配和售后等常见问题。"),
    "brand_story": ("品牌故事", "通过品牌理念和服务承诺提升信任。"),
}

LAYOUTS = ["full", "left-image", "right-image", "grid", "comparison"]


class GeminiAPlusGenerationClient:
    def generate(self, payload: CreateGenerationTaskRequest) -> dict[str, Any] | None:
        if not settings.gemini_api_key:
            return None

        response_text = self._generate_content(payload)
        data = self._parse_json(response_text)
        if not data:
            return None
        return self._normalize(data, payload)

    def _generate_content(self, payload: CreateGenerationTaskRequest) -> str:
        model = settings.gemini_model.strip().removeprefix("models/")
        url = f"{settings.gemini_base_url.rstrip('/')}/models/{model}:generateContent"
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                "你是跨境电商 Amazon A+ 详情页生成 Agent。"
                                "请基于商品信息、模块选择、提示词配置和样机计划，生成结构化 A+ 页面草稿。"
                                "只输出严格 JSON，不要输出 Markdown，不要输出解释。\n\n"
                                f"{self._build_prompt(payload)}"
                            )
                        }
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.35,
                "responseMimeType": "application/json",
            },
        }
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": settings.gemini_api_key.get_secret_value(),
        }

        with httpx.Client(timeout=settings.gemini_timeout_seconds) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()

        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        return "".join(str(part.get("text", "")) for part in parts)

    def _build_prompt(self, payload: CreateGenerationTaskRequest) -> str:
        info = payload.product_info
        return json.dumps(
            {
                "task": "generate ecommerce Amazon A+ page draft",
                "outputSchema": {
                    "productAnalysis": {
                        "category": "product category",
                        "positioning": "one sentence positioning",
                        "targetAudience": "audience summary",
                        "sellingPoints": ["3 to 5 concise selling points"],
                        "complianceNotes": ["risk notes"],
                    },
                    "modules": [
                        {
                            "type": "must match requested module type",
                            "title": "short A+ module title",
                            "subtitle": "short supporting subtitle",
                            "description": "2 to 4 sentence module copy",
                            "visualPrompt": "English prompt for image generation or mockup composition",
                            "layout": "one of full, left-image, right-image, grid, comparison",
                        }
                    ],
                    "qualityNotes": ["short QA notes"],
                },
                "rules": [
                    "如果 requestedModules 只有 full_aplus_mockup，必须只返回一个模块；该模块代表整张 A+ 页面图，不要再拆分 hero、selling_points、faq 等子模块。",
                    "full_aplus_mockup 的 visualPrompt 必须说明：使用 mockupPlan.template.previewUrl 作为完整 A+ 版式参考，将用户产品图替换/融合到样机中的商品位置，并保留样机里的整体模块构成。",
                    "必须按 requestedModules 的顺序返回模块",
                    "文案语言遵循 language 字段",
                    "避免绝对化、医疗化、夸大功效和平台禁词",
                    "visualPrompt 使用英文，强调真实电商摄影、产品主体清晰、Logo 不变形、文字安全区",
                    "如果信息不足，用保守表达，不编造认证、测试数据或竞品事实",
                ],
                "settings": {
                    "platform": payload.platform,
                    "country": payload.country,
                    "language": payload.language,
                    "qualityLevel": payload.quality_level,
                    "imageRatio": payload.image_ratio,
                    "designStyle": payload.design_style,
                },
                "requestedModules": payload.modules,
                "promptConfig": payload.prompt_config.model_dump(by_alias=True),
                "styleMemory": payload.style_memory.model_dump(by_alias=True),
                "mockupPlan": payload.mockup_plan.model_dump(by_alias=True) if payload.mockup_plan else None,
                "product": {
                    "name": info.product_name,
                    "sellingPoints": info.core_selling_points,
                    "targetAudience": info.target_audience,
                    "useScenes": info.use_scenes,
                    "specifications": info.specifications,
                    "brandTone": info.brand_tone,
                    "forbiddenWords": info.forbidden_words,
                    "complianceNotes": info.compliance_notes,
                    "imageCount": len(payload.images),
                },
            },
            ensure_ascii=False,
        )

    def _parse_json(self, content: str) -> dict[str, Any] | None:
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None

    def _normalize(self, data: dict[str, Any], payload: CreateGenerationTaskRequest) -> dict[str, Any]:
        raw_modules = data.get("modules") if isinstance(data.get("modules"), list) else []
        raw_by_type = {str(item.get("type")): item for item in raw_modules if isinstance(item, dict)}

        modules = []
        visual_prompts = []
        for index, module_type in enumerate(payload.modules):
            fallback_title, fallback_description = MODULE_COPY.get(module_type, ("详情模块", "商品详情页模块文案。"))
            raw = raw_by_type.get(module_type, {})
            visual_prompt = str(raw.get("visualPrompt") or raw.get("visual_prompt") or "")
            modules.append(
                {
                    "type": module_type,
                    "title": str(raw.get("title") or fallback_title),
                    "subtitle": str(raw.get("subtitle") or fallback_title),
                    "description": str(raw.get("description") or fallback_description),
                    "layout": self._valid_layout(str(raw.get("layout") or LAYOUTS[index % len(LAYOUTS)]), index),
                    "visualPrompt": visual_prompt,
                }
            )
            visual_prompts.append({"moduleType": module_type, "prompt": visual_prompt})

        return {
            "productAnalysis": data.get("productAnalysis") if isinstance(data.get("productAnalysis"), dict) else {},
            "modules": modules,
            "visualPrompts": visual_prompts,
            "qualityNotes": data.get("qualityNotes") if isinstance(data.get("qualityNotes"), list) else [],
        }

    def _valid_layout(self, layout: str, index: int) -> str:
        if layout in LAYOUTS:
            return layout
        return LAYOUTS[index % len(LAYOUTS)]
