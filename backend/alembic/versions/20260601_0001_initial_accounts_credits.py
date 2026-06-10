"""initial accounts credits and generation schema

Revision ID: 20260601_0001
Revises:
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=True),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("plan", sa.String(length=50), nullable=False),
        sa.Column("credits", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_status", "users", ["status"])

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("access_token", sa.String(length=128), nullable=False),
        sa.Column("token_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_access_token", "auth_sessions", ["access_token"], unique=True)
    op.create_index("ix_auth_sessions_status", "auth_sessions", ["status"])

    op.create_table(
        "companies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "brands",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("company_id", sa.Uuid(), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("owner_user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "credit_accounts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("balance", sa.Integer(), nullable=False),
        sa.Column("lifetime_earned", sa.Integer(), nullable=False),
        sa.Column("lifetime_spent", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_credit_accounts_user_id", "credit_accounts", ["user_id"], unique=True)
    op.create_index("ix_credit_accounts_status", "credit_accounts", ["status"])

    op.create_table(
        "credit_transactions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "account_id",
            sa.Uuid(),
            sa.ForeignKey("credit_accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("related_entity_type", sa.String(length=80), nullable=True),
        sa.Column("related_entity_id", sa.String(length=80), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_credit_transactions_account_id", "credit_transactions", ["account_id"])
    op.create_index("ix_credit_transactions_user_id", "credit_transactions", ["user_id"])
    op.create_index("ix_credit_transactions_transaction_type", "credit_transactions", ["transaction_type"])

    op.create_table(
        "credit_redemption_codes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("redeemed_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_credit_redemption_codes_code", "credit_redemption_codes", ["code"], unique=True)
    op.create_index("ix_credit_redemption_codes_status", "credit_redemption_codes", ["status"])
    op.create_index("ix_credit_redemption_codes_created_by_user_id", "credit_redemption_codes", ["created_by_user_id"])
    op.create_index("ix_credit_redemption_codes_redeemed_by_user_id", "credit_redemption_codes", ["redeemed_by_user_id"])

    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("brand_id", sa.Uuid(), sa.ForeignKey("brands.id"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=True),
        sa.Column("country", sa.String(length=50), nullable=True),
        sa.Column("language", sa.String(length=50), nullable=True),
        sa.Column("selling_points", sa.JSON(), nullable=False),
        sa.Column("specs", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_products_user_id", "products", ["user_id"])

    op.create_table(
        "generation_tasks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("current_step", sa.String(length=100), nullable=True),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_generation_tasks_user_id", "generation_tasks", ["user_id"])
    op.create_index("ix_generation_tasks_status", "generation_tasks", ["status"])

    op.create_table(
        "generation_results",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "task_id",
            sa.Uuid(),
            sa.ForeignKey("generation_tasks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("modules", sa.JSON(), nullable=False),
        sa.Column("preview_url", sa.Text(), nullable=True),
        sa.Column("export_urls", sa.JSON(), nullable=False),
        sa.Column("quality_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_generation_results_task_id", "generation_results", ["task_id"])

    op.create_table(
        "product_images",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=True),
        sa.Column("image_type", sa.String(length=50), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_product_images_product_id", "product_images", ["product_id"])

    op.create_table(
        "conversation_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("task_id", sa.Uuid(), sa.ForeignKey("generation_tasks.id"), nullable=True),
        sa.Column("current_result_id", sa.Uuid(), sa.ForeignKey("generation_results.id"), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("context", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_conversation_sessions_user_id", "conversation_sessions", ["user_id"])

    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(),
            sa.ForeignKey("conversation_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("message_type", sa.String(length=50), nullable=False),
        sa.Column("related_image_version_id", sa.Uuid(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_conversation_messages_session_id", "conversation_messages", ["session_id"])

    op.create_table(
        "image_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(),
            sa.ForeignKey("conversation_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("parent_image_version_id", sa.Uuid(), sa.ForeignKey("image_versions.id"), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("edit_instruction", sa.Text(), nullable=True),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_image_versions_session_id", "image_versions", ["session_id"])

    op.create_table(
        "style_memories",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_type", sa.String(length=20), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("style_name", sa.String(length=255), nullable=False),
        sa.Column("style_summary", sa.Text(), nullable=True),
        sa.Column("visual_keywords", sa.JSON(), nullable=False),
        sa.Column("color_palette", sa.JSON(), nullable=False),
        sa.Column("layout_preferences", sa.JSON(), nullable=False),
        sa.Column("copywriting_tone", sa.JSON(), nullable=False),
        sa.Column("negative_preferences", sa.JSON(), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_style_memories_owner_type", "style_memories", ["owner_type"])
    op.create_index("ix_style_memories_owner_id", "style_memories", ["owner_id"])

    op.create_table(
        "style_memory_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "style_memory_id",
            sa.Uuid(),
            sa.ForeignKey("style_memories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_result_id", sa.Uuid(), sa.ForeignKey("generation_results.id"), nullable=True),
        sa.Column("user_feedback", sa.Text(), nullable=True),
        sa.Column("extracted_style_delta", sa.JSON(), nullable=False),
        sa.Column("update_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_style_memory_events_style_memory_id", "style_memory_events", ["style_memory_id"])

    op.create_table(
        "tryon_assets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_type", sa.String(length=30), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("original_filename", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tryon_assets_user_id", "tryon_assets", ["user_id"])
    op.create_index("ix_tryon_assets_asset_type", "tryon_assets", ["asset_type"])

    op.create_table(
        "tryon_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("total_items", sa.Integer(), nullable=False),
        sa.Column("completed_items", sa.Integer(), nullable=False),
        sa.Column("failed_items", sa.Integer(), nullable=False),
        sa.Column("cancelled_items", sa.Integer(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tryon_jobs_user_id", "tryon_jobs", ["user_id"])
    op.create_index("ix_tryon_jobs_status", "tryon_jobs", ["status"])

    op.create_table(
        "tryon_job_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("tryon_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_asset_id", sa.Uuid(), sa.ForeignKey("tryon_assets.id"), nullable=False),
        sa.Column("model_asset_id", sa.Uuid(), sa.ForeignKey("tryon_assets.id"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("output_image_url", sa.Text(), nullable=True),
        sa.Column("output_storage_key", sa.Text(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("worker_id", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tryon_job_items_job_id", "tryon_job_items", ["job_id"])
    op.create_index("ix_tryon_job_items_user_id", "tryon_job_items", ["user_id"])
    op.create_index("ix_tryon_job_items_status", "tryon_job_items", ["status"])


def downgrade() -> None:
    for table_name in [
        "tryon_job_items",
        "tryon_jobs",
        "tryon_assets",
        "style_memory_events",
        "style_memories",
        "image_versions",
        "conversation_messages",
        "conversation_sessions",
        "product_images",
        "generation_results",
        "generation_tasks",
        "products",
        "credit_redemption_codes",
        "credit_transactions",
        "credit_accounts",
        "brands",
        "companies",
        "auth_sessions",
        "users",
    ]:
        op.drop_table(table_name)

