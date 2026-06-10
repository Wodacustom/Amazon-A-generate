import importlib

from app.db.base import Base
from app.models import (
    AuthSession,
    Brand,
    Company,
    ConversationMessage,
    ConversationSession,
    CreditAccount,
    CreditRedemptionCode,
    CreditTransaction,
    GenerationResult,
    GenerationTask,
    ImageVersion,
    Product,
    ProductImage,
    StyleMemory,
    StyleMemoryEvent,
    TryonAsset,
    TryonJob,
    TryonJobItem,
    User,
)


def test_models_are_split_by_domain_modules():
    module_names = [
        "app.models.mixins",
        "app.models.user",
        "app.models.product",
        "app.models.generation",
        "app.models.conversation",
        "app.models.style_memory",
        "app.models.tryon",
    ]

    for module_name in module_names:
        importlib.import_module(module_name)


def test_models_package_exports_all_table_classes():
    exported_models = [
        AuthSession,
        Brand,
        Company,
        ConversationMessage,
        ConversationSession,
        CreditAccount,
        CreditRedemptionCode,
        CreditTransaction,
        GenerationResult,
        GenerationTask,
        ImageVersion,
        Product,
        ProductImage,
        StyleMemory,
        StyleMemoryEvent,
        TryonAsset,
        TryonJob,
        TryonJobItem,
        User,
    ]

    assert {model.__tablename__ for model in exported_models}.issubset(Base.metadata.tables)
