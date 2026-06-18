-- 初始化 MVP 数据库结构。
-- 本脚本保持幂等：容器重启时重复执行不会删除或覆盖已有数据。

CREATE EXTENSION IF NOT EXISTS vector;

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

COMMENT ON TABLE files IS '文件对象元数据表，记录 RustFS/S3 中对象的索引信息';
COMMENT ON COLUMN files.id IS '文件记录唯一 ID';
COMMENT ON COLUMN files.object_key IS '对象存储中的文件 key';
COMMENT ON COLUMN files.bucket IS '对象所在 bucket 名称';
COMMENT ON COLUMN files.original_filename IS '用户上传时的原始文件名';
COMMENT ON COLUMN files.content_type IS '文件 MIME 类型';
COMMENT ON COLUMN files.size_bytes IS '文件大小，单位字节';
COMMENT ON COLUMN files.url IS '后端提供的文件访问 URL';
COMMENT ON COLUMN files.created_at IS '记录创建时间';
COMMENT ON COLUMN files.updated_at IS '记录更新时间';

CREATE INDEX IF NOT EXISTS ix_files_object_key ON files (object_key);

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

CREATE INDEX IF NOT EXISTS ix_agent_runs_status ON agent_runs (status);

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

CREATE INDEX IF NOT EXISTS ix_agent_results_run_id ON agent_results (run_id);

CREATE TABLE IF NOT EXISTS vector_documents (
    id uuid PRIMARY KEY,
    source_type varchar(80) NOT NULL,
    source_id varchar(80) NOT NULL,
    content text NOT NULL,
    metadata jsonb NOT NULL,
    embedding vector(8) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz
);

COMMENT ON TABLE vector_documents IS '向量文档表，统一保存产品、结果和记忆文本的 embedding';
COMMENT ON COLUMN vector_documents.id IS '向量文档唯一 ID';
COMMENT ON COLUMN vector_documents.source_type IS '来源类型，例如 product 或 agent_result';
COMMENT ON COLUMN vector_documents.source_id IS '来源记录 ID';
COMMENT ON COLUMN vector_documents.content IS '参与向量化和检索的文本内容';
COMMENT ON COLUMN vector_documents.metadata IS '文档附加元数据';
COMMENT ON COLUMN vector_documents.embedding IS 'pgvector 向量字段，MVP 阶段维度为 8';
COMMENT ON COLUMN vector_documents.created_at IS '记录创建时间';
COMMENT ON COLUMN vector_documents.updated_at IS '记录更新时间';

CREATE INDEX IF NOT EXISTS ix_vector_documents_source_type ON vector_documents (source_type);
CREATE INDEX IF NOT EXISTS ix_vector_documents_source_id ON vector_documents (source_id);

-- ivfflat 用于 pgvector 余弦距离检索；MVP 阶段固定 embedding 维度为 8。
CREATE INDEX IF NOT EXISTS ix_vector_documents_embedding
ON vector_documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
