from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.schemas.product import ProductInfo, ProductInfoRecommendationRequest
from app.services.file_storage import storage_dir


class ProductInfoRecommendationAgent:
    def recommend(self, payload: ProductInfoRecommendationRequest) -> dict[str, Any]:
        if self._should_use_gemini():
            try:
                result = self._recommend_with_gemini(payload)
                if result:
                    return result
            except (httpx.HTTPError, ValueError, KeyError, TypeError):
                pass
        return self._recommend_with_rules(payload)

    def _should_use_gemini(self) -> bool:
        provider = settings.product_info_agent_provider.lower()
        return bool(settings.gemini_api_key) and (provider == "gemini" or settings.generation_agent_provider.lower() == "gemini")

    def _recommend_with_gemini(self, payload: ProductInfoRecommendationRequest) -> dict[str, Any] | None:
        model = settings.gemini_model.strip().removeprefix("models/")
        url = f"{settings.gemini_base_url.rstrip('/')}/models/{model}:generateContent"
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": self._build_parts(payload),
                }
            ],
            "generationConfig": {"temperature": 0.35, "responseMimeType": "application/json"},
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
        content = "".join(str(part.get("text", "")) for part in parts)
        parsed = self._parse_json(content)
        if not parsed:
            return None
        product_info = self._normalize_product_info(parsed.get("productInfo") or parsed, payload.product_info)
        selling_points = parsed.get("sellingPoints")
        assumptions = parsed.get("assumptions")
        return {
            "productInfo": product_info.model_dump(by_alias=True),
            "sellingPoints": selling_points if isinstance(selling_points, list) else self._split_points(product_info.core_selling_points),
            "assumptions": assumptions if isinstance(assumptions, list) else [],
            "source": "gemini",
        }

    def _build_parts(self, payload: ProductInfoRecommendationRequest) -> list[dict[str, Any]]:
        parts: list[dict[str, Any]] = [
            {
                "text": (
                    "你是跨境电商商品信息与卖点提炼 Agent。"
                    "请同时观察用户上传的商品图片和已有文字信息，补全适合 Amazon A+ 详情页生成的商品资料。"
                    "如果图片中可以看出商品类型、材质、结构、配件、包装文字或使用方式，请优先利用图片信息。"
                    "只输出严格 JSON，不要 Markdown，不要解释。\n\n"
                    f"{self._build_prompt(payload)}"
                )
            }
        ]
        for image_url in payload.images[:4]:
            image_part = self._image_part_from_url(image_url)
            if image_part:
                parts.append(image_part)
        return parts

    def _image_part_from_url(self, image_url: str) -> dict[str, Any] | None:
        path = self._local_image_path(image_url)
        if not path or not path.exists() or not path.is_file():
            return None
        mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
        if not mime_type.startswith("image/"):
            return None
        return {
            "inlineData": {
                "mimeType": mime_type,
                "data": base64.b64encode(path.read_bytes()).decode("ascii"),
            }
        }

    def _local_image_path(self, image_url: str) -> Path | None:
        parsed = urlparse(image_url)
        path = parsed.path if parsed.scheme else image_url
        prefixes = {
            "/api/files/uploads/": storage_dir("uploads"),
            "/api/files/generated/": storage_dir("generated"),
            "/api/files/garment-library/": storage_dir("garment-library"),
        }
        for prefix, directory in prefixes.items():
            if path.startswith(prefix):
                filename = path.removeprefix(prefix)
                if "/" in filename or "\\" in filename or not filename:
                    return None
                return directory / filename
        return None

    def _build_prompt(self, payload: ProductInfoRecommendationRequest) -> str:
        info = payload.product_info
        return json.dumps(
            {
                "outputSchema": {
                    "productInfo": {
                        "productName": "short product name",
                        "coreSellingPoints": "3 to 6 selling points separated by semicolon",
                        "targetAudience": "target users",
                        "useScenes": "main usage scenes",
                        "specifications": "known specs only; if unknown, write conservative placeholders",
                        "brandTone": "brand tone for A+ content",
                        "forbiddenWords": "platform/compliance words to avoid",
                        "complianceNotes": "risk notes and conservative claims",
                    },
                    "sellingPoints": ["concise selling point 1", "concise selling point 2"],
                    "assumptions": ["what was inferred because source info was incomplete"],
                },
                "rules": [
                    "不要编造认证、测试数据、医疗功效、专利或竞品事实。",
                    "卖点要适合电商美工转成 A+ 模块图，不要写空泛营销词。",
                    "图片可见信息优先级高于用户未确认的文字推断；看不清的规格不要编造。",
                    "如果商品名称或类目不明确，基于已有文字做保守推断，并在 assumptions 中说明。",
                    "coreSellingPoints 使用分号分隔，方便前端继续编辑。",
                    "输出语言遵循 language 字段。",
                ],
                "context": {
                    "platform": payload.platform,
                    "country": payload.country,
                    "language": payload.language,
                    "designStyle": payload.design_style,
                    "imageCount": len(payload.images),
                    "currentProductInfo": info.model_dump(by_alias=True),
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
        return json.loads(text[start : end + 1])

    def _normalize_product_info(self, raw: Any, current: ProductInfo) -> ProductInfo:
        data = raw if isinstance(raw, dict) else {}
        return ProductInfo(
            product_name=str(data.get("productName") or data.get("product_name") or current.product_name or "新商品"),
            core_selling_points=str(
                data.get("coreSellingPoints") or data.get("core_selling_points") or current.core_selling_points
            ),
            target_audience=str(data.get("targetAudience") or data.get("target_audience") or current.target_audience),
            use_scenes=str(data.get("useScenes") or data.get("use_scenes") or current.use_scenes),
            specifications=str(data.get("specifications") or current.specifications),
            brand_tone=str(data.get("brandTone") or data.get("brand_tone") or current.brand_tone),
            forbidden_words=str(
                data.get("forbiddenWords")
                or data.get("forbidden_words")
                or current.forbidden_words
                or "避免绝对化、医疗化、夸大功效和未经证实的认证表述"
            ),
            compliance_notes=str(
                data.get("complianceNotes")
                or data.get("compliance_notes")
                or current.compliance_notes
                or "保持描述基于可见信息；不要编造测试数据、认证或医疗功效。"
            ),
        )

    def _recommend_with_rules(self, payload: ProductInfoRecommendationRequest) -> dict[str, Any]:
        current = payload.product_info
        product_name = current.product_name or self._infer_name(current.core_selling_points) or "新商品"
        points = self._split_points(current.core_selling_points)
        if not points:
            points = ["突出产品核心功能", "展示材质与做工细节", "强调日常使用便利性", "匹配真实使用场景"]
        product_info = ProductInfo(
            product_name=product_name,
            core_selling_points="; ".join(points[:6]),
            target_audience=current.target_audience or "关注品质、便利性和真实使用体验的电商消费者",
            use_scenes=current.use_scenes or "家庭日常、办公室、户外或礼品场景，需根据商品类目进一步确认",
            specifications=current.specifications or "请补充尺寸、材质、容量、重量、兼容型号等可验证规格",
            brand_tone=current.brand_tone or "专业、清晰、可信赖",
            forbidden_words=current.forbidden_words or "避免绝对化、医疗化、夸大功效和未经证实的认证表述",
            compliance_notes=current.compliance_notes or "卖点需基于真实资料；不要编造测试数据、认证、排名或竞品对比事实。",
        )
        return {
            "productInfo": product_info.model_dump(by_alias=True),
            "sellingPoints": points[:6],
            "assumptions": ["当前信息不足，已生成保守可编辑草稿。"],
            "source": "rule",
        }

    def _infer_name(self, text: str) -> str:
        cleaned = text.replace("\n", " ").strip()
        if not cleaned:
            return ""
        return cleaned.split(";")[0].split("，")[0].split(",")[0][:32]

    def _split_points(self, text: str) -> list[str]:
        normalized = text.replace("\n", ";").replace("；", ";")
        return [item.strip() for item in normalized.split(";") if item.strip()]
