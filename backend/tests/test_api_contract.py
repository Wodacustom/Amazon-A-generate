from fastapi.testclient import TestClient

from app.agents.mock_generation import MockGenerationAgent
from app.agents.mockup_recommendation import MockupRecommendationAgent
from app.core.config import settings
from app.main import create_app
from app.schemas.generation import CreateGenerationTaskRequest
from app.schemas.mockup import MockupRecommendationRequest
from app.schemas.product import ProductInfoRecommendationRequest
from app.services.in_memory import store
from app.services.gemini_image import GeminiImageGenerationClient
from app.services.product_info_recommendation import ProductInfoRecommendationAgent


client = TestClient(create_app())


def test_health_contract():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "aplus-agent-api",
        "version": "0.1.0",
    }


def test_prompt_options_are_grouped_for_frontend_selection():
    response = client.get("/api/prompt-option-groups")

    assert response.status_code == 200
    groups = response.json()["items"]
    keys = {group["key"] for group in groups}
    assert {"visual_style", "color", "composition", "copy_tone", "negative"}.issubset(keys)
    assert all(group["options"] for group in groups)


def test_file_upload_returns_stable_serving_url(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "local_storage_dir", str(tmp_path))

    upload_response = client.post(
        "/api/files/upload",
        files={"file": ("mockup.png", b"fake-image-bytes", "image/png")},
    )

    assert upload_response.status_code == 200
    uploaded = upload_response.json()
    assert uploaded["url"].startswith("/api/files/uploads/")

    file_response = client.get(uploaded["url"])
    assert file_response.status_code == 200
    assert file_response.content == b"fake-image-bytes"

    delete_response = client.delete(f"/api/files/{uploaded['id']}")
    assert delete_response.status_code == 200
    assert not (tmp_path / "uploads" / uploaded["storageKey"]).exists()


def test_garment_library_stores_assets_separately(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "local_storage_dir", str(tmp_path))

    upload_response = client.post(
        "/api/garment-library/items",
        data={"name": "White Hoodie", "tags": "hoodie,winter"},
        files={"file": ("hoodie.png", b"fake-garment-bytes", "image/png")},
    )

    assert upload_response.status_code == 201
    uploaded = upload_response.json()
    assert uploaded["name"] == "White Hoodie"
    assert uploaded["url"].startswith("/api/files/garment-library/")
    assert uploaded["tags"] == ["hoodie", "winter"]
    assert (tmp_path / "garment-library" / uploaded["storageKey"]).exists()
    assert not (tmp_path / "uploads" / uploaded["storageKey"]).exists()

    list_response = client.get("/api/garment-library/items")
    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["id"] == uploaded["id"]

    file_response = client.get(uploaded["url"])
    assert file_response.status_code == 200
    assert file_response.content == b"fake-garment-bytes"

    delete_response = client.delete(f"/api/garment-library/items/{uploaded['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json()["ok"] is True
    assert not (tmp_path / "garment-library" / uploaded["storageKey"]).exists()


def test_garment_library_accepts_chinese_comma_tags(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "local_storage_dir", str(tmp_path))

    upload_response = client.post(
        "/api/garment-library/items",
        data={"tags": "连衣裙，夏季"},
        files={"file": ("dress.png", b"fake-garment-bytes", "image/png")},
    )

    assert upload_response.status_code == 201
    assert upload_response.json()["tags"] == ["连衣裙", "夏季"]


def test_tryon_job_accepts_model_and_garment_urls(monkeypatch):
    monkeypatch.setattr(settings, "image_generation_provider", "mock")
    payload = {
        "productAssetIds": ["garment-1", "garment-2"],
        "modelAssetIds": ["model-1"],
        "productImageUrls": ["/api/files/uploads/garment-1.png", "/api/files/uploads/garment-2.png"],
        "modelImageUrls": ["/api/files/uploads/model.png"],
        "prompt": "Keep the garment unchanged and put it on the reference model.",
        "outputCount": 1,
        "ratio": "4_5",
        "imageModel": "nanobanana_pro",
        "mode": "garment_preserve",
    }

    response = client.post("/api/tryon/jobs", json=payload)

    assert response.status_code == 201
    job = response.json()
    assert job["totalItems"] == 2

    items_response = client.get(f"/api/tryon/jobs/{job['id']}/items")
    assert items_response.status_code == 200
    items = items_response.json()["items"]
    assert len(items) == 2
    assert items[0]["prompt"].startswith("Keep the garment unchanged")
    assert items[0]["outputImageUrl"]


def test_tryon_job_can_be_created_for_async_batch_processing(monkeypatch):
    monkeypatch.setattr(settings, "image_generation_provider", "mock")
    payload = {
        "productAssetIds": ["garment-1", "garment-2", "garment-3"],
        "modelAssetIds": ["model-1"],
        "productImageUrls": [
            "/api/files/garment-library/garment-1.png",
            "/api/files/garment-library/garment-2.png",
            "/api/files/garment-library/garment-3.png",
        ],
        "modelImageUrls": ["/api/files/uploads/model.png"],
        "prompt": "Batch try-on preserving each garment.",
        "outputCount": 2,
        "ratio": "model_4_5",
        "imageModel": "nanobanana_pro",
        "mode": "garment_preserve",
        "asyncProcessing": True,
    }

    response = client.post("/api/tryon/jobs", json=payload)

    assert response.status_code == 201
    job = response.json()
    assert job["totalItems"] == 6
    assert job["status"] in {"queued", "running", "completed", "partial_success"}

    items_response = client.get(f"/api/tryon/jobs/{job['id']}/items")
    assert items_response.status_code == 200
    assert len(items_response.json()["items"]) == 6


def test_product_info_recommendation_returns_editable_draft(monkeypatch):
    monkeypatch.setattr(settings, "product_info_agent_provider", "rule")
    monkeypatch.setattr(settings, "generation_agent_provider", "mock")
    payload = {
        "productInfo": {
            "productName": "Portable Grinder",
            "coreSellingPoints": "USB-C charging; Easy to clean",
        },
        "images": ["blob:local-preview"],
        "platform": "amazon",
        "country": "US",
        "language": "zh-CN",
    }

    response = client.post("/api/products/recommend-info", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["productInfo"]["productName"] == "Portable Grinder"
    assert "USB-C charging" in body["productInfo"]["coreSellingPoints"]
    assert body["sellingPoints"]
    assert body["source"] == "rule"


def test_product_info_agent_can_attach_uploaded_image(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "local_storage_dir", str(tmp_path))
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    image_path = upload_dir / "product.png"
    image_path.write_bytes(b"fake-image-bytes")
    payload = ProductInfoRecommendationRequest(images=["/api/files/uploads/product.png"])

    parts = ProductInfoRecommendationAgent()._build_parts(payload)

    inline_parts = [part for part in parts if "inlineData" in part]
    assert inline_parts
    assert inline_parts[0]["inlineData"]["mimeType"] == "image/png"
    assert inline_parts[0]["inlineData"]["data"]


def test_gemini_image_client_can_attach_uploaded_product_image(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "local_storage_dir", str(tmp_path))
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    image_path = upload_dir / "product.webp"
    image_path.write_bytes(b"fake-webp-bytes")

    parts = GeminiImageGenerationClient()._build_parts(
        "Replace the mockup product with the uploaded product.",
        "hero",
        "4_5",
        ["/api/files/uploads/product.webp"],
    )

    inline_parts = [part for part in parts if "inlineData" in part]
    assert inline_parts
    assert inline_parts[0]["inlineData"]["mimeType"] == "image/webp"
    assert inline_parts[0]["inlineData"]["data"]


def test_gemini_image_client_can_attach_mockup_reference(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "local_storage_dir", str(tmp_path))
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    (upload_dir / "product.png").write_bytes(b"fake-product-bytes")
    (upload_dir / "mockup.png").write_bytes(b"fake-mockup-bytes")

    parts = GeminiImageGenerationClient()._build_parts(
        "Replace the mockup product with the uploaded product.",
        "hero",
        "4_5",
        ["/api/files/uploads/product.png"],
        "/api/files/uploads/mockup.png",
    )

    inline_parts = [part for part in parts if "inlineData" in part]
    assert len(inline_parts) == 2
    assert "Mockup reference URL" in parts[0]["text"]


def test_gemini_image_client_can_attach_garment_library_image(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "local_storage_dir", str(tmp_path))
    garment_dir = tmp_path / "garment-library"
    garment_dir.mkdir()
    (garment_dir / "garment.png").write_bytes(b"fake-garment-bytes")

    parts = GeminiImageGenerationClient()._build_parts(
        "Put the uploaded garment onto the reference model.",
        "tryon",
        "4_5",
        ["/api/files/garment-library/garment.png"],
    )

    inline_parts = [part for part in parts if "inlineData" in part]
    assert inline_parts
    assert inline_parts[0]["inlineData"]["mimeType"] == "image/png"


def test_gemini_image_client_supports_tryon_ratios():
    client = GeminiImageGenerationClient()

    assert client._aspect_ratio("9_16") == "9:16"
    assert client._target_size("9_16") == "1440x2560 px"
    assert client._aspect_ratio("model_3_4") == "3:4"
    assert client._target_size("model_3_4") == "1600x2133 px"
    assert client._resolve_model("nanobanana_pro") == settings.gemini_image_model


def test_generation_task_creates_mock_result_and_session(monkeypatch):
    monkeypatch.setattr(settings, "generation_agent_provider", "mock")
    monkeypatch.setattr(settings, "image_generation_provider", "mock")
    payload = {
        "productId": "product-local-1",
        "images": ["https://example.com/product.webp"],
        "platform": "amazon",
        "country": "US",
        "language": "en",
        "qualityLevel": "normal_a_plus",
        "imageRatio": "platform_default",
        "designStyle": "minimal",
        "productInfo": {
            "productName": "Portable Grinder",
            "coreSellingPoints": "Portable; Durable; Easy to clean",
            "targetAudience": "Coffee lovers",
            "useScenes": "Travel and office",
            "specifications": "USB-C, 250g",
            "brandTone": "Clean and professional",
            "forbiddenWords": "best",
            "complianceNotes": "Avoid absolute claims",
        },
        "modules": ["hero", "selling_points", "faq"],
        "promptConfig": {
            "visualStyle": ["minimal"],
            "color": ["white_background"],
            "composition": ["product_center"],
            "copyTone": ["professional"],
            "negative": ["no_exaggerated_claims"],
        },
        "styleMemory": {"mode": "none", "updateAfterGeneration": False},
    }

    create_response = client.post("/api/generation/tasks", json=payload)

    assert create_response.status_code == 201
    task = create_response.json()
    assert task["status"] == "completed"
    assert task["progress"] == 100
    assert task["currentStep"] == "生成完成"
    assert task["conversationSessionId"]

    result_response = client.get(f"/api/generation/results/{task['id']}")
    assert result_response.status_code == 200
    result = result_response.json()
    assert result["taskId"] == task["id"]
    assert [module["type"] for module in result["modules"]] == ["hero", "selling_points", "faq"]
    assert result["qualityScore"] >= 80

    versions_response = client.get(f"/api/generation/results/{result['id']}/versions")
    assert versions_response.status_code == 200
    versions = versions_response.json()["items"]
    assert len(versions) == 1
    assert versions[0]["label"] == "初始生成"
    assert versions[0]["modules"][0]["title"] == result["modules"][0]["title"]


def test_generation_result_versions_can_be_saved_and_restored(monkeypatch):
    monkeypatch.setattr(settings, "generation_agent_provider", "mock")
    monkeypatch.setattr(settings, "image_generation_provider", "mock")
    payload = {
        "productId": "product-version-1",
        "images": ["https://example.com/product.webp"],
        "platform": "amazon",
        "country": "US",
        "language": "en",
        "qualityLevel": "normal_a_plus",
        "imageRatio": "platform_default",
        "imageModel": "mock",
        "designStyle": "minimal",
        "productInfo": {
            "productName": "Versioned Grinder",
            "coreSellingPoints": "Portable; Durable",
        },
        "modules": ["hero"],
        "promptConfig": {
            "visualStyle": ["minimal"],
            "color": [],
            "composition": [],
            "copyTone": [],
            "negative": [],
        },
        "styleMemory": {"mode": "none", "updateAfterGeneration": False},
    }

    task = client.post("/api/generation/tasks", json=payload).json()
    result = client.get(f"/api/generation/results/{task['id']}").json()
    original_title = result["modules"][0]["title"]

    patched = {
        "modules": [{**result["modules"][0], "title": "Edited hero title"}],
        "versionLabel": "标题微调",
    }
    update_response = client.put(f"/api/generation/results/{result['id']}", json=patched)

    assert update_response.status_code == 200
    assert update_response.json()["modules"][0]["title"] == "Edited hero title"

    versions = client.get(f"/api/generation/results/{result['id']}/versions").json()["items"]
    assert [item["label"] for item in versions] == ["初始生成", "标题微调"]

    restore_response = client.post(f"/api/generation/results/{result['id']}/versions/{versions[0]['id']}/restore")

    assert restore_response.status_code == 200
    assert restore_response.json()["modules"][0]["title"] == original_title

    restored_versions = client.get(f"/api/generation/results/{result['id']}/versions").json()["items"]
    assert restored_versions[-1]["label"] == "恢复版本 1"


def test_generation_agent_can_use_gemini_structured_output(monkeypatch):
    class FakeGeminiGenerationClient:
        def generate(self, payload):
            return {
                "productAnalysis": {
                    "category": "coffee grinder",
                    "positioning": "Portable grinder for travel coffee routines",
                },
                "modules": [
                    {
                        "type": "hero",
                        "title": "Grind Fresh Anywhere",
                        "subtitle": "Portable coffee grinder",
                        "description": "Compact grinding for travel, office, and daily brewing. Built for clean handling and easy storage.",
                        "layout": "full",
                        "visualPrompt": "Premium ecommerce hero image, portable coffee grinder on clean desk",
                    },
                    {
                        "type": "faq",
                        "title": "Easy Daily Care",
                        "subtitle": "FAQ",
                        "description": "Designed for simple cleaning and practical everyday use without exaggerated claims.",
                        "layout": "left-image",
                        "visualPrompt": "Clean FAQ module image with grinder details and text-safe area",
                    },
                ],
                "visualPrompts": [
                    {"moduleType": "hero", "prompt": "Premium ecommerce hero image"},
                    {"moduleType": "faq", "prompt": "Clean FAQ module image"},
                ],
                "qualityNotes": ["Avoid absolute claims"],
            }

    monkeypatch.setattr(settings, "generation_agent_provider", "gemini")
    monkeypatch.setattr(settings, "image_generation_provider", "mock")
    payload = {
        "productId": "product-local-2",
        "images": ["https://example.com/product.webp"],
        "platform": "amazon",
        "country": "US",
        "language": "en",
        "qualityLevel": "normal_a_plus",
        "imageRatio": "platform_default",
        "designStyle": "minimal",
        "productInfo": {
            "productName": "Portable Grinder",
            "coreSellingPoints": "Portable; Durable; Easy to clean",
            "targetAudience": "Coffee lovers",
            "useScenes": "Travel and office",
            "specifications": "USB-C, 250g",
            "brandTone": "Clean and professional",
            "forbiddenWords": "best",
            "complianceNotes": "Avoid absolute claims",
        },
        "modules": ["hero", "faq"],
        "promptConfig": {
            "visualStyle": ["minimal"],
            "color": ["white_background"],
            "composition": ["product_center"],
            "copyTone": ["professional"],
            "negative": ["no_exaggerated_claims"],
        },
        "styleMemory": {"mode": "none", "updateAfterGeneration": False},
    }

    task, result, _session = MockGenerationAgent(gemini_client=FakeGeminiGenerationClient()).run(
        CreateGenerationTaskRequest.model_validate(payload)
    )

    assert task["status"] == "completed"
    assert result["modules"][0]["title"] == "Grind Fresh Anywhere"
    assert result["modules"][0]["visualPrompt"] == "Premium ecommerce hero image, portable coffee grinder on clean desk"
    assert result["modules"][1]["description"].startswith("Designed for simple cleaning")
    assert result["metadata"]["productAnalysis"]["category"] == "coffee grinder"
    assert result["metadata"]["visualPrompts"][0]["moduleType"] == "hero"


def test_generation_agent_can_use_image_provider(monkeypatch):
    class FakeGeminiGenerationClient:
        def generate(self, payload):
            return {
                "productAnalysis": {"category": "outdoor"},
                "modules": [
                    {
                        "type": "hero",
                        "title": "Outdoor Ready",
                        "subtitle": "Hero",
                        "description": "A clean outdoor ecommerce hero module.",
                        "layout": "full",
                        "visualPrompt": "Outdoor camping bottle on a wood table",
                    }
                ],
                "visualPrompts": [{"moduleType": "hero", "prompt": "Outdoor camping bottle on a wood table"}],
                "qualityNotes": [],
            }

    class FakeImageClient:
        def generate_module_image(
            self,
            prompt,
            module_type,
            image_ratio,
            product_image_urls,
            mockup_image_url=None,
            image_model=None,
        ):
            assert module_type == "hero"
            assert image_ratio == "4_5"
            assert product_image_urls == ["https://example.com/bottle.webp"]
            assert mockup_image_url is None
            assert image_model == "nanobanana_pro"
            assert "camping bottle" in prompt
            return "/api/files/generated/fake.png"

    monkeypatch.setattr(settings, "generation_agent_provider", "gemini")
    monkeypatch.setattr(settings, "image_generation_provider", "gemini")
    payload = CreateGenerationTaskRequest.model_validate(
        {
            "productId": "product-local-3",
            "images": ["https://example.com/bottle.webp"],
            "platform": "amazon",
            "country": "US",
            "language": "en",
            "qualityLevel": "normal_a_plus",
            "imageRatio": "4_5",
            "imageModel": "nanobanana_pro",
            "designStyle": "lifestyle",
            "productInfo": {
                "productName": "Insulated Bottle",
                "coreSellingPoints": "Portable; Leakproof",
                "targetAudience": "Campers",
                "useScenes": "Camping",
                "specifications": "24oz",
                "brandTone": "",
                "forbiddenWords": "",
                "complianceNotes": "",
            },
            "modules": ["hero"],
            "promptConfig": {
                "visualStyle": ["lifestyle"],
                "color": [],
                "composition": [],
                "copyTone": [],
                "negative": [],
            },
            "styleMemory": {"mode": "none", "updateAfterGeneration": False},
        }
    )

    _task, result, _session = MockGenerationAgent(
        gemini_client=FakeGeminiGenerationClient(),
        image_client=FakeImageClient(),
    ).run(payload)

    assert result["modules"][0]["imageUrl"] == "/api/files/generated/fake.png"


def test_generation_agent_passes_mockup_reference_to_image_provider(monkeypatch):
    class FakeGeminiGenerationClient:
        def generate(self, payload):
            return {
                "productAnalysis": {"category": "outdoor"},
                "modules": [
                    {
                        "type": "full_aplus_mockup",
                        "title": "Outdoor Ready",
                        "subtitle": "Hero",
                        "description": "A clean outdoor ecommerce hero module.",
                        "layout": "full",
                        "visualPrompt": "Replace the mockup product with the uploaded bottle",
                    }
                ],
                "visualPrompts": [],
                "qualityNotes": [],
            }

    class FakeImageClient:
        def generate_module_image(
            self,
            prompt,
            module_type,
            image_ratio,
            product_image_urls,
            mockup_image_url=None,
            image_model=None,
        ):
            assert module_type == "full_aplus_mockup"
            assert product_image_urls == ["/api/files/uploads/product.png"]
            assert mockup_image_url == "/api/files/uploads/mockup.png"
            assert image_model == "nanobanana_pro"
            return "/api/files/generated/mockup-fused.png"

    monkeypatch.setattr(settings, "generation_agent_provider", "gemini")
    monkeypatch.setattr(settings, "image_generation_provider", "gemini")
    payload = CreateGenerationTaskRequest.model_validate(
        {
            "productId": "product-local-4",
            "images": ["/api/files/uploads/product.png"],
            "platform": "amazon",
            "country": "US",
            "language": "en",
            "qualityLevel": "normal_a_plus",
            "imageRatio": "4_5",
            "imageModel": "nanobanana_pro",
            "designStyle": "lifestyle",
            "productInfo": {
                "productName": "Insulated Bottle",
                "coreSellingPoints": "Portable; Leakproof",
            },
            "modules": ["full_aplus_mockup"],
            "promptConfig": {"visualStyle": [], "color": [], "composition": [], "copyTone": [], "negative": []},
            "styleMemory": {"mode": "none", "updateAfterGeneration": False},
            "mockupPlan": {
                "sceneId": "camping",
                "templateId": "custom-mockup",
                "template": {
                    "id": "custom-mockup",
                    "name": "Custom Mockup",
                    "category": ["outdoor"],
                    "scenes": ["camping"],
                    "platforms": ["amazon"],
                    "ratios": ["4_5"],
                    "composition": "Replace the mockup product with my original product.",
                    "replaceableAreas": [],
                    "previewUrl": "/api/files/uploads/mockup.png",
                    "sourceUrl": "mockup://custom-mockup",
                    "tags": ["custom"],
                },
                "matchScore": 90,
                "scenePrompt": {
                    "positive": "Outdoor bottle hero",
                    "negative": "distorted product",
                    "composition": "Use mockup composition",
                    "productPlacement": "Replace product in mockup",
                    "supportingProps": [],
                },
                "compositionNotes": "Use mockup as scene template.",
            },
        }
    )

    _task, result, _session = MockGenerationAgent(
        gemini_client=FakeGeminiGenerationClient(),
        image_client=FakeImageClient(),
    ).run(payload)

    assert [module["type"] for module in result["modules"]] == ["full_aplus_mockup"]
    assert result["modules"][0]["imageUrl"] == "/api/files/generated/mockup-fused.png"


def test_mockup_recommendation_returns_scene_prompts_and_templates(monkeypatch):
    monkeypatch.setattr(settings, "scene_agent_provider", "rule")
    payload = {
        "productInfo": {
            "productName": "Insulated Camping Bottle",
            "coreSellingPoints": "Portable; Leakproof; Long lasting insulation",
            "targetAudience": "Hikers and campers",
            "useScenes": "Camping and road trips",
            "specifications": "24oz stainless steel",
            "brandTone": "Outdoor and reliable",
            "forbiddenWords": "best",
            "complianceNotes": "Avoid absolute claims",
        },
        "images": ["https://example.com/bottle.webp"],
        "platform": "amazon",
        "country": "US",
        "language": "en",
        "imageRatio": "4_5",
        "designStyle": "lifestyle",
    }

    response = client.post("/api/mockups/recommend", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["productCategory"] == "outdoor"
    assert body["scenes"]
    assert body["matchedMockups"]
    assert body["selectedPlan"]["scenePrompt"]["positive"]
    assert "replaceableAreas" in body["matchedMockups"][0]["template"]


def test_mockup_template_can_be_created_and_used_for_matching(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "scene_agent_provider", "rule")
    monkeypatch.setattr(settings, "local_storage_dir", str(tmp_path))
    store.mockup_templates.clear()
    create_payload = {
        "name": "Custom Camping Flatlay",
        "category": ["outdoor", "drinkware"],
        "scenes": ["camping"],
        "platforms": ["amazon"],
        "ratios": ["4_5"],
        "composition": "center",
        "replaceableAreas": [],
        "previewUrl": "https://example.com/custom-camping.jpg",
        "tags": ["custom", "camping"],
    }

    create_response = client.post("/api/mockups/templates", json=create_payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"].startswith("custom-")
    assert created["replaceableAreas"] == []

    detail_response = client.get(f"/api/mockups/templates/{created['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["name"] == "Custom Camping Flatlay"

    recommend_response = client.post(
        "/api/mockups/recommend",
        json={
            "productInfo": {
                "productName": "Insulated Camping Bottle",
                "coreSellingPoints": "Portable; Leakproof",
                "targetAudience": "Campers",
                "useScenes": "Camping",
                "specifications": "24oz",
                "brandTone": "",
                "forbiddenWords": "",
                "complianceNotes": "",
            },
            "platform": "amazon",
            "country": "US",
            "language": "en",
            "imageRatio": "4_5",
            "designStyle": "lifestyle",
        },
    )
    template_ids = [item["template"]["id"] for item in recommend_response.json()["matchedMockups"]]
    assert created["id"] in template_ids

    store.mockup_templates.clear()
    persisted_detail_response = client.get(f"/api/mockups/templates/{created['id']}")

    assert persisted_detail_response.status_code == 200
    assert persisted_detail_response.json()["id"] == created["id"]
    assert (tmp_path / "mockup_templates.json").exists()
    store.mockup_templates.clear()


def test_mockup_recommendation_can_use_qwen_scene_output(monkeypatch):
    class FakeQwenClient:
        def recommend(self, payload):
            return {
                "productCategory": "beauty",
                "scenes": [
                    {
                        "id": "vanity",
                        "name": "梳妆台护理场景",
                        "category": "beauty",
                        "audience": "Beauty shoppers",
                        "reason": "突出精致护理氛围",
                        "riskNotes": ["避免医疗化表述"],
                        "prompt": {
                            "positive": "Premium beauty vanity product photography, clean A+ composition",
                            "negative": "medical claim, distorted logo",
                            "composition": "Text-safe area on the right.",
                            "productPlacement": "Place product on vanity table with natural shadow.",
                            "supportingProps": ["mirror", "towel"],
                        },
                    }
                ],
            }

    monkeypatch.setattr(settings, "scene_agent_provider", "qwen")
    payload = MockupRecommendationRequest(
        productInfo={
            "productName": "Beauty Device",
            "coreSellingPoints": "Portable; Gentle care",
            "targetAudience": "Beauty shoppers",
            "useScenes": "Vanity",
            "specifications": "",
            "brandTone": "",
            "forbiddenWords": "",
            "complianceNotes": "",
        },
        platform="amazon",
        country="US",
        language="en",
    )

    body = MockupRecommendationAgent(qwen_client=FakeQwenClient()).run(payload)

    assert body["productCategory"] == "beauty"
    assert body["scenes"][0]["id"] == "vanity"
    assert body["matchedMockups"][0]["template"]["id"] == "beauty-vanity-premium"


def test_mockup_recommendation_can_use_gemini_scene_output(monkeypatch):
    class FakeGeminiClient:
        def recommend(self, payload):
            return {
                "productCategory": "electronics",
                "scenes": [
                    {
                        "id": "office",
                        "name": "办公桌面场景",
                        "category": "electronics",
                        "audience": "Office workers",
                        "reason": "突出效率和专业感",
                        "riskNotes": ["避免夸大性能"],
                        "prompt": {
                            "positive": "Premium office desk ecommerce product photography",
                            "negative": "distorted logo, exaggerated claim",
                            "composition": "Right product with text-safe area.",
                            "productPlacement": "Place product on desk with natural shadow.",
                            "supportingProps": ["laptop", "notebook"],
                        },
                    }
                ],
            }

    monkeypatch.setattr(settings, "scene_agent_provider", "gemini")
    payload = MockupRecommendationRequest(
        productInfo={
            "productName": "Wireless Earbuds",
            "coreSellingPoints": "Bluetooth; Long battery life",
            "targetAudience": "Office workers",
            "useScenes": "Office",
            "specifications": "",
            "brandTone": "",
            "forbiddenWords": "",
            "complianceNotes": "",
        },
        platform="amazon",
        country="US",
        language="en",
    )

    body = MockupRecommendationAgent(gemini_client=FakeGeminiClient()).run(payload)

    assert body["productCategory"] == "electronics"
    assert body["scenes"][0]["id"] == "office"
    assert body["matchedMockups"][0]["template"]["id"] == "office-desk-productivity"


def test_tryon_job_contract_supports_mock_subtasks_and_cancel():
    payload = {
        "productAssetIds": ["asset-product-1"],
        "modelAssetIds": ["asset-model-1", "asset-model-2"],
        "outputCount": 1,
        "ratio": "4_5",
        "mode": "fast",
    }

    create_response = client.post("/api/tryon/jobs", json=payload)

    assert create_response.status_code == 201
    job = create_response.json()
    assert job["totalItems"] == 2
    assert job["status"] == "completed"

    items_response = client.get(f"/api/tryon/jobs/{job['id']}/items")
    assert items_response.status_code == 200
    assert len(items_response.json()["items"]) == 2

    cancel_response = client.post(f"/api/tryon/jobs/{job['id']}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] in {"completed", "cancelled", "partial_success"}
