-- 初始化 MVP 数据库结构。
-- 本脚本保持幂等：容器重启时重复执行不会删除或覆盖已有数据。

CREATE EXTENSION IF NOT EXISTS vector;

DROP INDEX IF EXISTS ix_files_object_key;
DROP INDEX IF EXISTS ix_agent_runs_status;
DROP INDEX IF EXISTS ix_agent_results_run_id;
DROP INDEX IF EXISTS ix_vector_documents_source_type;
DROP INDEX IF EXISTS ix_vector_documents_source_id;
DROP INDEX IF EXISTS ix_vector_documents_embedding;
DROP INDEX IF EXISTS uk_user_username;
DROP INDEX IF EXISTS ix_model_profiles_name;
DROP INDEX IF EXISTS ix_model_routes_role;
DROP INDEX IF EXISTS ix_model_request_templates_role;

CREATE TABLE IF NOT EXISTS files (
    id uuid PRIMARY KEY,
    object_key text NOT NULL UNIQUE,
    bucket varchar(255) NOT NULL,
    original_filename text,
    content_type varchar(255),
    size_bytes bigint NOT NULL,
    url text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz
);

COMMENT ON TABLE files IS '文件对象元数据表，记录 RustFS/S3 中对象的元数据信息';
COMMENT ON COLUMN files.id IS '文件记录唯一 ID';
COMMENT ON COLUMN files.object_key IS '对象存储中的文件 key';
COMMENT ON COLUMN files.bucket IS '对象所在 bucket 名称';
COMMENT ON COLUMN files.original_filename IS '用户上传时的原始文件名';
COMMENT ON COLUMN files.content_type IS '文件 MIME 类型';
COMMENT ON COLUMN files.size_bytes IS '文件大小，单位字节';
COMMENT ON COLUMN files.url IS '后端提供的文件访问 URL';
COMMENT ON COLUMN files.created_at IS '记录创建时间';
COMMENT ON COLUMN files.updated_at IS '记录更新时间';

CREATE TABLE IF NOT EXISTS products (
    id uuid PRIMARY KEY,
    name varchar(255) NOT NULL,
    platform varchar(50) NOT NULL,
    country varchar(50) NOT NULL,
    language varchar(50) NOT NULL,
    selling_points jsonb NOT NULL,
    specs jsonb NOT NULL,
    description text,
    file_ids jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz
);

COMMENT ON TABLE products IS '产品草稿表，保存智能体生成所需的产品输入';
COMMENT ON COLUMN products.id IS '产品唯一 ID';
COMMENT ON COLUMN products.name IS '产品名称';
COMMENT ON COLUMN products.platform IS '目标销售平台，例如 amazon';
COMMENT ON COLUMN products.country IS '目标国家或地区';
COMMENT ON COLUMN products.language IS '内容生成语言';
COMMENT ON COLUMN products.selling_points IS '产品卖点列表';
COMMENT ON COLUMN products.specs IS '产品规格参数';
COMMENT ON COLUMN products.description IS '产品描述';
COMMENT ON COLUMN products.file_ids IS '关联文件 ID 列表';
COMMENT ON COLUMN products.created_at IS '记录创建时间';
COMMENT ON COLUMN products.updated_at IS '记录更新时间';

CREATE TABLE IF NOT EXISTS agent_runs (
    id uuid PRIMARY KEY,
    product_id uuid REFERENCES products(id) ON DELETE SET NULL,
    status varchar(50) NOT NULL,
    progress integer NOT NULL,
    current_step varchar(100),
    input_snapshot jsonb NOT NULL,
    error_message text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz
);

COMMENT ON TABLE agent_runs IS '智能体运行记录表，保存每次 LangGraph 执行状态';
COMMENT ON COLUMN agent_runs.id IS '智能体运行唯一 ID';
COMMENT ON COLUMN agent_runs.product_id IS '关联产品 ID，产品删除后置空';
COMMENT ON COLUMN agent_runs.status IS '运行状态，例如 queued、running、completed、failed';
COMMENT ON COLUMN agent_runs.progress IS '运行进度，范围 0 到 100';
COMMENT ON COLUMN agent_runs.current_step IS '当前执行步骤';
COMMENT ON COLUMN agent_runs.input_snapshot IS '本次运行的输入快照';
COMMENT ON COLUMN agent_runs.error_message IS '失败时的错误信息';
COMMENT ON COLUMN agent_runs.created_at IS '记录创建时间';
COMMENT ON COLUMN agent_runs.updated_at IS '记录更新时间';

CREATE TABLE IF NOT EXISTS agent_results (
    id uuid PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    product_id uuid REFERENCES products(id) ON DELETE SET NULL,
    content_modules jsonb NOT NULL,
    image_prompts jsonb NOT NULL,
    model_metadata jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz
);

COMMENT ON TABLE agent_results IS '智能体结果表，保存生成后的 A+ 内容和图片提示词';
COMMENT ON COLUMN agent_results.id IS '结果唯一 ID';
COMMENT ON COLUMN agent_results.run_id IS '关联智能体运行 ID，运行删除后级联删除';
COMMENT ON COLUMN agent_results.product_id IS '关联产品 ID，产品删除后置空';
COMMENT ON COLUMN agent_results.content_modules IS '生成的 A+ 内容模块列表';
COMMENT ON COLUMN agent_results.image_prompts IS '生成的图片提示词列表';
COMMENT ON COLUMN agent_results.model_metadata IS '模型、分析和检索上下文等元数据';
COMMENT ON COLUMN agent_results.created_at IS '记录创建时间';
COMMENT ON COLUMN agent_results.updated_at IS '记录更新时间';

CREATE TABLE IF NOT EXISTS vector_documents (
    id uuid PRIMARY KEY,
    source_type varchar(80) NOT NULL,
    source_id varchar(80) NOT NULL,
    content text NOT NULL,
    metadata jsonb NOT NULL,
    embedding vector(1536) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz
);

COMMENT ON TABLE vector_documents IS '向量文档表，统一保存产品、结果和记忆文本的 embedding';
COMMENT ON COLUMN vector_documents.id IS '向量文档唯一 ID';
COMMENT ON COLUMN vector_documents.source_type IS '来源类型，例如 product 或 agent_result';
COMMENT ON COLUMN vector_documents.source_id IS '来源记录 ID';
COMMENT ON COLUMN vector_documents.content IS '参与向量化和检索的文本内容';
COMMENT ON COLUMN vector_documents.metadata IS '文档附加元数据';
COMMENT ON COLUMN vector_documents.embedding IS 'pgvector 向量字段，默认真实 embedding 维度为 1536';
COMMENT ON COLUMN vector_documents.created_at IS '记录创建时间';
COMMENT ON COLUMN vector_documents.updated_at IS '记录更新时间';

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_attribute attribute
        JOIN pg_class class ON class.oid = attribute.attrelid
        WHERE class.relname = 'vector_documents'
          AND attribute.attname = 'embedding'
          AND format_type(attribute.atttypid, attribute.atttypmod) <> 'vector(1536)'
    ) THEN
        TRUNCATE TABLE vector_documents;
        ALTER TABLE vector_documents
        ALTER COLUMN embedding TYPE vector(1536)
        USING NULL::vector(1536);
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS system_users (
    id bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    username varchar(64) NOT NULL UNIQUE,
    password varchar(128) NOT NULL,
    role varchar(32) NOT NULL,
    avatar varchar(128),
    create_time timestamptz DEFAULT now(),
    update_time timestamptz,
    deleted smallint DEFAULT 0
);

COMMENT ON TABLE system_users IS '系统用户表';
COMMENT ON COLUMN system_users.id IS '主键ID';
COMMENT ON COLUMN system_users.username IS '用户名，唯一';
COMMENT ON COLUMN system_users.password IS '密码哈希';
COMMENT ON COLUMN system_users.role IS '角色：admin/user';
COMMENT ON COLUMN system_users.avatar IS '用户头像';
COMMENT ON COLUMN system_users.create_time IS '创建时间';
COMMENT ON COLUMN system_users.update_time IS '更新时间';
COMMENT ON COLUMN system_users.deleted IS '是否删除 0：正常 1：删除';

INSERT INTO system_users (username, password, role, avatar, deleted)
VALUES ('admin', 'pbkdf2_sha256$120000$Y29kZXgtZGVmYXVsdC1zYWx0$6gi6P1LeAy874W3ZeMMT7cgsYa-LetblKwj9TUBeY4I=', 'admin', NULL, 0)
ON CONFLICT (username) DO NOTHING;

CREATE TABLE IF NOT EXISTS model_profiles (
    id bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name varchar(80) NOT NULL UNIQUE,
    model_type varchar(32) NOT NULL,
    provider varchar(64) NOT NULL,
    model varchar(128) NOT NULL,
    base_url varchar(512),
    encrypted_api_key text,
    timeout_seconds double precision NOT NULL DEFAULT 60,
    temperature double precision,
    dimensions integer,
    config jsonb NOT NULL DEFAULT '{}'::jsonb,
    enabled boolean NOT NULL DEFAULT true,
    create_time timestamptz DEFAULT now(),
    update_time timestamptz,
    deleted integer NOT NULL DEFAULT 0
);

COMMENT ON TABLE model_profiles IS '模型档案表，保存可调用模型的供应商、模型名、地址、密钥和运行参数';
COMMENT ON COLUMN model_profiles.id IS '主键ID';
COMMENT ON COLUMN model_profiles.name IS '模型档案名称，唯一，例如 mock_chat 或 qwen_copywriter';
COMMENT ON COLUMN model_profiles.model_type IS '模型类型：chat、embedding 或 image';
COMMENT ON COLUMN model_profiles.provider IS '模型供应商或协议适配器：mock/openai/qwen/gemini/vllm/newapi';
COMMENT ON COLUMN model_profiles.model IS '供应商侧模型名称';
COMMENT ON COLUMN model_profiles.base_url IS '模型接口基础地址';
COMMENT ON COLUMN model_profiles.encrypted_api_key IS '加密后的模型 API Key';
COMMENT ON COLUMN model_profiles.timeout_seconds IS '模型请求超时时间，单位秒';
COMMENT ON COLUMN model_profiles.temperature IS '聊天模型采样温度';
COMMENT ON COLUMN model_profiles.dimensions IS 'embedding 向量维度，chat/image 模型为空';
COMMENT ON COLUMN model_profiles.config IS '模型扩展配置 JSON';
COMMENT ON COLUMN model_profiles.enabled IS '是否启用该模型档案';
COMMENT ON COLUMN model_profiles.create_time IS '创建时间';
COMMENT ON COLUMN model_profiles.update_time IS '更新时间';
COMMENT ON COLUMN model_profiles.deleted IS '是否删除 0：正常 1：删除';

CREATE TABLE IF NOT EXISTS model_routes (
    id bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    role varchar(80) NOT NULL UNIQUE,
    primary_profile_id bigint NOT NULL REFERENCES model_profiles(id),
    fallback_profile_id bigint REFERENCES model_profiles(id),
    enabled boolean NOT NULL DEFAULT true,
    create_time timestamptz DEFAULT now(),
    update_time timestamptz,
    deleted integer NOT NULL DEFAULT 0
);

COMMENT ON TABLE model_routes IS '模型路由表，保存业务场景 role 到主模型和备用模型的映射';
COMMENT ON COLUMN model_routes.id IS '主键ID';
COMMENT ON COLUMN model_routes.role IS '业务模型角色，唯一，例如 a_plus_content/image_prompt/retrieval_embedding/image_generation';
COMMENT ON COLUMN model_routes.primary_profile_id IS '主模型档案 ID';
COMMENT ON COLUMN model_routes.fallback_profile_id IS '备用模型档案 ID，主模型失败时降级使用';
COMMENT ON COLUMN model_routes.enabled IS '是否启用该路由';
COMMENT ON COLUMN model_routes.create_time IS '创建时间';
COMMENT ON COLUMN model_routes.update_time IS '更新时间';
COMMENT ON COLUMN model_routes.deleted IS '是否删除 0：正常 1：删除';

CREATE TABLE IF NOT EXISTS model_request_templates (
    id bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    role varchar(80) NOT NULL,
    name varchar(120) NOT NULL,
    version varchar(40) NOT NULL DEFAULT 'v1',
    system_prompt text NOT NULL,
    user_template text NOT NULL,
    response_contract varchar(120) NOT NULL,
    enabled boolean NOT NULL DEFAULT true,
    create_time timestamptz DEFAULT now(),
    update_time timestamptz,
    deleted integer NOT NULL DEFAULT 0
);

COMMENT ON TABLE model_request_templates IS '模型请求模板表，保存不同业务角色的 system prompt 和用户请求模板';
COMMENT ON COLUMN model_request_templates.id IS '主键ID';
COMMENT ON COLUMN model_request_templates.role IS '业务模型角色';
COMMENT ON COLUMN model_request_templates.name IS '模板名称';
COMMENT ON COLUMN model_request_templates.version IS '模板版本';
COMMENT ON COLUMN model_request_templates.system_prompt IS '模型 system prompt 模板';
COMMENT ON COLUMN model_request_templates.user_template IS '模型 user message 请求体模板';
COMMENT ON COLUMN model_request_templates.response_contract IS '响应契约名称，对应后端 Pydantic 校验模型';
COMMENT ON COLUMN model_request_templates.enabled IS '是否启用该模板';
COMMENT ON COLUMN model_request_templates.create_time IS '创建时间';
COMMENT ON COLUMN model_request_templates.update_time IS '更新时间';
COMMENT ON COLUMN model_request_templates.deleted IS '是否删除 0：正常 1：删除';

CREATE TABLE IF NOT EXISTS model_config_audit_logs (
    id bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    actor_user_id bigint,
    action varchar(80) NOT NULL,
    target_type varchar(80) NOT NULL,
    target_id varchar(80),
    detail jsonb NOT NULL DEFAULT '{}'::jsonb,
    create_time timestamptz DEFAULT now()
);

COMMENT ON TABLE model_config_audit_logs IS '模型配置审计日志表，记录模型档案、路由和模板的管理操作';
COMMENT ON COLUMN model_config_audit_logs.id IS '主键ID';
COMMENT ON COLUMN model_config_audit_logs.actor_user_id IS '操作人用户 ID';
COMMENT ON COLUMN model_config_audit_logs.action IS '操作类型';
COMMENT ON COLUMN model_config_audit_logs.target_type IS '操作对象类型';
COMMENT ON COLUMN model_config_audit_logs.target_id IS '操作对象 ID 或业务标识';
COMMENT ON COLUMN model_config_audit_logs.detail IS '操作详情 JSON，不记录明文密钥';
COMMENT ON COLUMN model_config_audit_logs.create_time IS '创建时间';

INSERT INTO model_profiles (name, model_type, provider, model, dimensions, enabled)
VALUES
    ('mock_chat', 'chat', 'mock', 'mock-a-plus-v1', NULL, true),
    ('mock_embedding', 'embedding', 'mock', 'mock-hash-v1', 1536, true),
    ('mock_image', 'image', 'mock', 'mock-image-v1', NULL, true)
ON CONFLICT (name) DO NOTHING;

INSERT INTO model_routes (role, primary_profile_id, enabled)
SELECT 'a_plus_content', id, true FROM model_profiles WHERE name = 'mock_chat'
ON CONFLICT (role) DO NOTHING;

INSERT INTO model_routes (role, primary_profile_id, enabled)
SELECT 'image_prompt', id, true FROM model_profiles WHERE name = 'mock_chat'
ON CONFLICT (role) DO NOTHING;

INSERT INTO model_routes (role, primary_profile_id, enabled)
SELECT 'retrieval_embedding', id, true FROM model_profiles WHERE name = 'mock_embedding'
ON CONFLICT (role) DO NOTHING;

INSERT INTO model_routes (role, primary_profile_id, enabled)
SELECT 'image_generation', id, true FROM model_profiles WHERE name = 'mock_image'
ON CONFLICT (role) DO NOTHING;

INSERT INTO model_request_templates (role, name, version, system_prompt, user_template, response_contract, enabled)
VALUES
    ('a_plus_content', 'default_a_plus_content', 'v1', 'You generate Amazon A+ content drafts. Return only JSON with a content_modules array.', '{payload}', 'APlusContentResponse', true),
    ('image_prompt', 'default_image_prompt', 'v1', 'You write image prompts for Amazon A+ modules. Return only JSON with an image_prompts array.', '{payload}', 'ImagePromptResponse', true)
ON CONFLICT DO NOTHING;
