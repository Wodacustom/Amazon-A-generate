from fastapi import APIRouter


def test_schema_package_exports_public_contracts():
    from app.schemas import (
        CreateGenerationTaskRequest,
        CreateTryonJobRequest,
        AuthTokenResponse,
        CreditAccountResponse,
        CreditRedemptionCodeList,
        CreditRedemptionCodeResponse,
        GarmentLibraryItem,
        GarmentLibraryList,
        GeneratedModule,
        GenerationResultResponse,
        GenerationTaskResponse,
        LoginRequest,
        MockupGenerationPlan,
        MockupRecommendationRequest,
        MockupRecommendationResponse,
        MockupTemplate,
        ProductInfo,
        PromptConfig,
        PromptOptionGroupList,
        RegisterRequest,
        RedeemCreditCodeRequest,
        StyleMemorySelection,
        TryonJobItemList,
        TryonJobResponse,
        UserProfileResponse,
        UserListResponse,
    )

    assert ProductInfo
    assert PromptConfig
    assert StyleMemorySelection
    assert CreateGenerationTaskRequest
    assert AuthTokenResponse
    assert CreditAccountResponse
    assert CreditRedemptionCodeList
    assert CreditRedemptionCodeResponse
    assert LoginRequest
    assert RegisterRequest
    assert RedeemCreditCodeRequest
    assert UserProfileResponse
    assert UserListResponse
    assert GenerationTaskResponse
    assert GenerationResultResponse
    assert GeneratedModule
    assert MockupGenerationPlan
    assert MockupRecommendationRequest
    assert MockupRecommendationResponse
    assert MockupTemplate
    assert PromptOptionGroupList
    assert CreateTryonJobRequest
    assert GarmentLibraryItem
    assert GarmentLibraryList
    assert TryonJobResponse
    assert TryonJobItemList


def test_route_package_exports_domain_routers():
    from app.api.routes import (
        auth_router,
        conversations_router,
        files_router,
        garment_library_router,
        generation_router,
        health_router,
        mockups_router,
        products_router,
        prompt_options_router,
        style_memories_router,
        tryon_router,
    )

    routers = [
        auth_router,
        conversations_router,
        files_router,
        garment_library_router,
        generation_router,
        health_router,
        mockups_router,
        products_router,
        prompt_options_router,
        style_memories_router,
        tryon_router,
    ]

    assert all(isinstance(router, APIRouter) for router in routers)


def test_service_and_agent_packages_export_entrypoints():
    from app.agents import MockGenerationAgent, MockupRecommendationAgent
    from app.memory import summarize_context
    from app.services import get_prompt_option_groups, store
    from app.tryon import create_mock_tryon_job, create_queued_tryon_job, estimate_item_count, process_queued_tryon_job
    from app.workers import run_generation_task, run_tryon_item

    assert MockGenerationAgent
    assert MockupRecommendationAgent
    assert get_prompt_option_groups
    assert store
    assert summarize_context([{"content": "test"}])["latestInstruction"] == "test"
    assert estimate_item_count(["p1"], ["m1", "m2"], 2) == 4
    job, items = create_mock_tryon_job(["p1"], ["m1"], 1, "4_5", "fast")
    assert job["totalItems"] == 1
    assert len(items) == 1
    queued_job, queued_items = create_queued_tryon_job(["p1"], ["m1"], 1, "4_5", "fast")
    assert queued_job["status"] == "queued"
    assert queued_items[0]["status"] == "queued"
    assert process_queued_tryon_job
    assert run_generation_task("task-1") == "task-1"
    assert run_tryon_item("item-1") == "item-1"
