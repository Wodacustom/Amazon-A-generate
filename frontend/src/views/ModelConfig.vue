<template>
  <div class="model-page">
    <section class="model-header">
      <div>
        <h1>模型配置</h1>
        <p>维护业务可调用模型的 base_url、api_key、模型名和厂商配置。</p>
      </div>
      <div class="header-actions">
        <el-button :loading="loading" @click="loadProfiles">刷新</el-button>
        <el-button type="primary" @click="openCreate">新增模型</el-button>
      </div>
    </section>

    <section class="workbench-panel model-panel">
      <div class="section-title">
        <h3>可调用模型</h3>
        <el-tag>{{ profiles.length }} 个</el-tag>
      </div>

      <el-table v-loading="loading" :data="profiles" height="560">
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            <el-tag :type="modelTypeTag(row.model_type)" effect="plain">
              {{ row.model_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="厂商" width="120">
          <template #default="{ row }">
            <el-tag effect="plain">{{ row.provider }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="模型" min-width="180" show-overflow-tooltip />
        <el-table-column prop="base_url" label="Base URL" min-width="260" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="muted">{{ row.base_url || '未配置' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="API Key" width="150">
          <template #default="{ row }">
            <span>{{ row.masked_api_key || (row.api_key_configured ? '已配置' : '未配置') }}</span>
          </template>
        </el-table-column>
        <el-table-column label="超时" width="90">
          <template #default="{ row }">{{ row.timeout_seconds }}s</template>
        </el-table-column>
        <el-table-column label="启用" width="90">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="(value: boolean) => updateEnabled(row, value)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="removeProfile(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <el-drawer v-model="drawerVisible" :title="drawerTitle" size="520px" destroy-on-close>
      <el-form label-position="top" class="model-form">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="例如：主聊天模型" />
        </el-form-item>

        <div class="form-row">
          <el-form-item label="模型类型">
            <el-select v-model="form.model_type">
              <el-option label="Chat" value="chat" />
              <el-option label="Embedding" value="embedding" />
              <el-option label="Image" value="image" />
            </el-select>
          </el-form-item>
          <el-form-item label="厂商">
            <el-select v-model="form.provider">
              <el-option v-for="provider in providerOptions" :key="provider" :label="provider" :value="provider" />
            </el-select>
          </el-form-item>
        </div>

        <el-form-item label="模型名">
          <el-input v-model="form.model" placeholder="例如：gpt-4o-mini / qwen-plus" />
        </el-form-item>

        <el-form-item label="Base URL">
          <el-input v-model="form.base_url" placeholder="例如：https://api.openai.com/v1" />
        </el-form-item>

        <el-form-item label="API Key">
          <el-input
            v-model="form.api_key"
            :placeholder="editingProfileId ? '留空则不修改当前密钥' : '可留空，例如 mock 模型'"
            show-password
          />
        </el-form-item>

        <div class="form-row">
          <el-form-item label="超时时间（秒）">
            <el-input-number v-model="form.timeout_seconds" :min="1" :max="600" />
          </el-form-item>
          <el-form-item label="温度">
            <el-input-number v-model="form.temperature" :min="0" :max="2" :step="0.1" />
          </el-form-item>
        </div>

        <div class="form-row">
          <el-form-item label="Embedding 维度">
            <el-input-number v-model="form.dimensions" :min="1" :max="65536" />
          </el-form-item>
          <el-form-item label="是否启用">
            <el-switch v-model="form.enabled" />
          </el-form-item>
        </div>

        <el-form-item label="扩展配置 JSON">
          <el-input
            v-model="form.configText"
            type="textarea"
            :rows="8"
            placeholder='例如：{"extra_headers":{"x-provider":"custom"}}'
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="drawer-footer">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="submitProfile">保存</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import {
  createModelProfile,
  deleteModelProfile,
  listModelProfiles,
  updateModelProfile,
  type ModelProfile,
  type ModelProfilePayload,
  type ModelProvider,
  type ModelType,
} from '@/api/modelConfig'

interface ModelFormState {
  name: string
  model_type: ModelType
  provider: ModelProvider
  model: string
  base_url: string
  api_key: string
  timeout_seconds: number
  temperature: number | undefined
  dimensions: number | undefined
  configText: string
  enabled: boolean
}

const providerOptions: ModelProvider[] = ['mock', 'openai', 'qwen', 'gemini', 'vllm', 'newapi']
const profiles = ref<ModelProfile[]>([])
const loading = ref(false)
const saving = ref(false)
const drawerVisible = ref(false)
const editingProfileId = ref<number | null>(null)

const form = reactive<ModelFormState>(createEmptyForm())
const drawerTitle = computed(() => (editingProfileId.value ? '编辑模型' : '新增模型'))

function createEmptyForm(): ModelFormState {
  return {
    name: '',
    model_type: 'chat',
    provider: 'openai',
    model: '',
    base_url: '',
    api_key: '',
    timeout_seconds: 60,
    temperature: 0.7,
    dimensions: undefined,
    configText: '{}',
    enabled: true,
  }
}

function modelTypeTag(modelType: ModelType) {
  if (modelType === 'chat') return 'primary'
  if (modelType === 'embedding') return 'success'
  return 'warning'
}

function resetForm(next: ModelFormState) {
  Object.assign(form, next)
}

async function loadProfiles() {
  loading.value = true
  try {
    profiles.value = await listModelProfiles()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingProfileId.value = null
  resetForm(createEmptyForm())
  drawerVisible.value = true
}

function openEdit(profile: ModelProfile) {
  editingProfileId.value = profile.id
  resetForm({
    name: profile.name,
    model_type: profile.model_type,
    provider: profile.provider,
    model: profile.model,
    base_url: profile.base_url || '',
    api_key: '',
    timeout_seconds: profile.timeout_seconds,
    temperature: profile.temperature ?? undefined,
    dimensions: profile.dimensions ?? undefined,
    configText: JSON.stringify(profile.config || {}, null, 2),
    enabled: profile.enabled,
  })
  drawerVisible.value = true
}

function parseConfig() {
  try {
    const parsed = JSON.parse(form.configText || '{}')
    if (!parsed || Array.isArray(parsed) || typeof parsed !== 'object') {
      throw new Error('扩展配置必须是 JSON 对象')
    }
    return parsed as Record<string, unknown>
  } catch (error) {
    const message = error instanceof Error ? error.message : '扩展配置 JSON 格式错误'
    ElMessage.error(message)
    return null
  }
}

function buildPayload(config: Record<string, unknown>) {
  const payload: ModelProfilePayload = {
    name: form.name.trim(),
    model_type: form.model_type,
    provider: form.provider,
    model: form.model.trim(),
    base_url: form.base_url.trim() || null,
    timeout_seconds: form.timeout_seconds,
    temperature: form.temperature ?? null,
    dimensions: form.dimensions ?? null,
    config,
    enabled: form.enabled,
  }
  // 编辑时空 api_key 表示不覆盖密钥；新增时也允许 mock 等模型不配置密钥。
  if (form.api_key.trim()) {
    payload.api_key = form.api_key.trim()
  }
  return payload
}

async function submitProfile() {
  if (!form.name.trim() || !form.model.trim()) {
    ElMessage.warning('请填写名称和模型名')
    return
  }
  const config = parseConfig()
  if (!config) return

  saving.value = true
  try {
    const payload = buildPayload(config)
    if (editingProfileId.value) {
      await updateModelProfile(editingProfileId.value, payload)
      ElMessage.success('模型已更新')
    } else {
      await createModelProfile(payload)
      ElMessage.success('模型已创建')
    }
    drawerVisible.value = false
    await loadProfiles()
  } finally {
    saving.value = false
  }
}

async function updateEnabled(profile: ModelProfile, enabled: boolean) {
  try {
    await updateModelProfile(profile.id, { enabled })
    ElMessage.success(enabled ? '模型已启用' : '模型已停用')
  } catch (error) {
    profile.enabled = !enabled
    throw error
  }
}

async function removeProfile(profile: ModelProfile) {
  await ElMessageBox.confirm(`确认删除模型「${profile.name}」？删除后仅做逻辑删除。`, '删除模型', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await deleteModelProfile(profile.id)
  ElMessage.success('模型已删除')
  await loadProfiles()
}

onMounted(loadProfiles)
</script>

<style scoped lang="scss">
.model-page {
  display: grid;
  gap: 16px;
}

.model-header {
  display: grid;
  align-items: end;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;

  h1 {
    margin: 0 0 4px;
  }

  p {
    margin: 0;
    color: var(--text-secondary);
  }
}

.header-actions {
  display: flex;
  gap: 8px;
}

.model-panel {
  padding: 16px;
}

.muted {
  color: var(--text-secondary);
}

.model-form {
  padding-right: 4px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 980px) {
  .model-header,
  .form-row {
    grid-template-columns: 1fr;
  }

  .header-actions {
    justify-content: flex-start;
  }
}
</style>
