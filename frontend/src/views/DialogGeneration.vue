<template>
  <div class="dialog-page">
    <section class="dialog-header">
      <div>
        <h1>对话生成</h1>
        <p>用提示词和参考图对话式生成商品视觉图。</p>
      </div>
      <el-button :icon="RefreshCcw" @click="clearConversation">清空对话</el-button>
    </section>

    <section class="workbench-panel conversation-panel">
      <div class="conversation-list">
        <el-empty v-if="!messages.length" description="上传图片或输入提示词开始生成" />
        <article v-for="message in messages" :key="message.id" :class="['message', `message--${message.role}`]">
          <div class="message__body">
            <div class="message__meta">
              <strong>{{ message.role === 'user' ? '你' : '生成结果' }}</strong>
              <span>{{ message.time }}</span>
            </div>

            <p v-if="message.prompt" class="message__prompt">{{ message.prompt }}</p>

            <div v-if="message.attachments?.length" class="attachment-list">
              <figure v-for="attachment in message.attachments" :key="attachment.id" class="attachment">
                <img :src="attachment.url" :alt="attachment.name" />
                <figcaption>{{ attachment.label }}</figcaption>
              </figure>
            </div>

            <div v-if="message.results?.length" class="result-grid">
              <article v-for="item in message.results" :key="item.file_id" class="result-card">
                <img :src="item.image_url" alt="generated image" />
                <div class="result-card__meta">
                  <el-tag size="small">{{ item.operation }}</el-tag>
                  <span>{{ item.provider || 'unknown' }} / {{ item.model || 'unknown' }}</span>
                  <small>链接有效 {{ Math.round(item.expires_in / 3600) }} 小时</small>
                </div>
              </article>
            </div>

            <el-alert
              v-if="message.error"
              :title="message.error"
              type="error"
              show-icon
              :closable="false"
            />
          </div>
        </article>
      </div>

      <div class="composer">
        <div class="composer__uploads">
          <div v-if="imagePreview" class="upload-preview">
            <img :src="imagePreview.url" :alt="imagePreview.name" />
            <span>参考图</span>
            <el-button text :icon="X" aria-label="移除参考图" @click="clearImage" />
          </div>
          <div v-if="maskPreview" class="upload-preview">
            <img :src="maskPreview.url" :alt="maskPreview.name" />
            <span>Mask</span>
            <el-button text :icon="X" aria-label="移除 Mask" @click="clearMask" />
          </div>
        </div>

        <el-input
          v-model="form.prompt"
          type="textarea"
          :rows="4"
          resize="none"
          placeholder="描述要生成的图片。上传参考图后会按图片编辑模式生成。"
          @keydown.ctrl.enter.prevent="submit"
        />

        <div class="composer__actions">
          <div class="upload-actions">
            <el-upload :auto-upload="false" :show-file-list="false" accept="image/*" :on-change="selectImage">
              <el-button :icon="ImagePlus">参考图</el-button>
            </el-upload>
            <el-upload :auto-upload="false" :show-file-list="false" accept="image/*" :on-change="selectMask">
              <el-button :icon="Layers">Mask</el-button>
            </el-upload>
          </div>
          <el-button type="primary" :icon="Send" :loading="submitting" @click="submit">发送生成</el-button>
        </div>

        <el-collapse class="advanced" accordion>
          <el-collapse-item title="高级设置" name="advanced">
            <div class="advanced-grid">
              <el-form-item label="业务 role">
                <el-input v-model="form.role" />
              </el-form-item>
              <el-form-item label="模型 Profile ID">
                <el-input-number v-model="form.modelProfileId" :min="1" />
              </el-form-item>
              <el-form-item label="尺寸">
                <el-select v-model="form.size">
                  <el-option label="1024x1024" value="1024x1024" />
                  <el-option label="1536x1024" value="1536x1024" />
                  <el-option label="1024x1536" value="1024x1536" />
                  <el-option label="auto" value="auto" />
                </el-select>
              </el-form-item>
              <el-form-item label="数量">
                <el-input-number v-model="form.n" :min="1" :max="10" />
              </el-form-item>
            </div>
            <el-form-item label="扩展参数 JSON">
              <el-input
                v-model="form.optionsText"
                type="textarea"
                :rows="4"
                placeholder='例如：{"quality":"high","response_format":"b64_json"}'
              />
            </el-form-item>
          </el-collapse-item>
        </el-collapse>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { ImagePlus, Layers, RefreshCcw, Send, X } from 'lucide-vue-next'
import { computed, onBeforeUnmount, reactive, ref } from 'vue'

import { generateImage, type GeneratedImageItem } from '@/api/imageGeneration'

interface AttachmentPreview {
  id: string
  file: File
  name: string
  label: string
  url: string
}

interface ConversationMessage {
  id: string
  role: 'user' | 'assistant'
  time: string
  prompt?: string
  attachments?: AttachmentPreview[]
  results?: GeneratedImageItem[]
  error?: string
}

const messages = ref<ConversationMessage[]>([])
const submitting = ref(false)
const imagePreview = ref<AttachmentPreview | null>(null)
const maskPreview = ref<AttachmentPreview | null>(null)

const form = reactive({
  prompt: '',
  role: 'image_generation',
  modelProfileId: undefined as number | undefined,
  size: '1024x1024',
  n: 1,
  optionsText: '{}',
})

const activeAttachments = computed(() => [imagePreview.value, maskPreview.value].filter(Boolean) as AttachmentPreview[])

function selectImage(upload: UploadFile) {
  if (!upload.raw) return
  replacePreview(imagePreview, upload.raw, '参考图')
}

function selectMask(upload: UploadFile) {
  if (!upload.raw) return
  replacePreview(maskPreview, upload.raw, 'Mask')
}

function replacePreview(target: typeof imagePreview, file: File, label: string) {
  if (target.value) {
    URL.revokeObjectURL(target.value.url)
  }
  target.value = {
    id: crypto.randomUUID(),
    file,
    name: file.name,
    label,
    url: URL.createObjectURL(file),
  }
}

function clearImage() {
  if (imagePreview.value) URL.revokeObjectURL(imagePreview.value.url)
  imagePreview.value = null
}

function clearMask() {
  if (maskPreview.value) URL.revokeObjectURL(maskPreview.value.url)
  maskPreview.value = null
}

function parseOptions() {
  try {
    const parsed = JSON.parse(form.optionsText || '{}')
    if (!parsed || Array.isArray(parsed) || typeof parsed !== 'object') {
      throw new Error('扩展参数必须是 JSON 对象')
    }
    return parsed as Record<string, unknown>
  } catch (error) {
    const message = error instanceof Error ? error.message : '扩展参数 JSON 格式错误'
    ElMessage.error(message)
    return null
  }
}

async function submit() {
  if (!form.prompt.trim()) {
    ElMessage.warning('请填写提示词')
    return
  }
  if (maskPreview.value && !imagePreview.value) {
    ElMessage.warning('Mask 需要和参考图一起上传')
    return
  }
  const options = parseOptions()
  if (!options) return

  const userMessage: ConversationMessage = {
    id: crypto.randomUUID(),
    role: 'user',
    time: currentTime(),
    prompt: form.prompt.trim(),
    attachments: activeAttachments.value.map((attachment) => ({ ...attachment })),
  }
  messages.value.push(userMessage)

  submitting.value = true
  try {
    const response = await generateImage({
      prompt: userMessage.prompt || '',
      role: form.role || 'image_generation',
      modelProfileId: form.modelProfileId,
      size: form.size,
      n: form.n,
      image: imagePreview.value?.file || null,
      mask: maskPreview.value?.file || null,
      options,
    })
    messages.value.push({
      id: crypto.randomUUID(),
      role: 'assistant',
      time: currentTime(),
      results: response.items,
    })
    form.prompt = ''
    ElMessage.success('图片已生成')
  } catch (error) {
    const message = error instanceof Error ? error.message : '图片生成失败'
    messages.value.push({
      id: crypto.randomUUID(),
      role: 'assistant',
      time: currentTime(),
      error: message,
    })
  } finally {
    submitting.value = false
  }
}

function clearConversation() {
  messages.value = []
}

function currentTime() {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

onBeforeUnmount(() => {
  clearImage()
  clearMask()
})
</script>

<style scoped lang="scss">
.dialog-page {
  display: grid;
  gap: 16px;
  min-height: calc(100vh - 112px);
}

.dialog-header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 12px;

  h1 {
    margin: 0 0 4px;
  }

  p {
    margin: 0;
    color: var(--text-secondary);
  }
}

.conversation-panel {
  display: grid;
  min-height: 0;
  grid-template-rows: minmax(320px, 1fr) auto;
  overflow: hidden;
}

.conversation-list {
  display: grid;
  align-content: start;
  gap: 14px;
  min-height: 0;
  max-height: calc(100vh - 372px);
  overflow: auto;
  padding: 16px;
}

.message {
  display: flex;

  &--user {
    justify-content: flex-end;

    .message__body {
      background: var(--brand-soft);
    }
  }

  &--assistant {
    justify-content: flex-start;
  }
}

.message__body {
  display: grid;
  gap: 10px;
  max-width: min(820px, 92%);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 12px;
}

.message__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 12px;

  strong {
    color: var(--text-primary);
  }
}

.message__prompt {
  margin: 0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.attachment-list,
.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
}

.attachment {
  display: grid;
  gap: 6px;
  margin: 0;

  img {
    width: 100%;
    aspect-ratio: 1;
    border-radius: 6px;
    object-fit: cover;
    background: #f6f6f6;
  }

  figcaption {
    color: var(--text-secondary);
    font-size: 12px;
  }
}

.result-card {
  display: grid;
  gap: 8px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 8px;

  img {
    width: 100%;
    aspect-ratio: 1;
    border-radius: 6px;
    object-fit: contain;
    background: #f6f6f6;
  }
}

.result-card__meta {
  display: grid;
  gap: 5px;
  color: var(--text-secondary);
  font-size: 12px;
}

.composer {
  display: grid;
  gap: 10px;
  border-top: 1px solid var(--line);
  background: #fff;
  padding: 14px;
}

.composer__uploads {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.upload-preview {
  display: grid;
  align-items: center;
  grid-template-columns: 44px minmax(80px, 1fr) 28px;
  gap: 8px;
  max-width: 220px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 6px;

  img {
    width: 44px;
    height: 44px;
    border-radius: 6px;
    object-fit: cover;
  }

  span {
    min-width: 0;
    color: var(--text-secondary);
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.composer__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.upload-actions {
  display: flex;
  gap: 8px;
}

.advanced {
  border-top: 1px solid var(--line);
  padding-top: 4px;
}

.advanced-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

@media (max-width: 980px) {
  .dialog-header,
  .composer__actions {
    align-items: stretch;
    flex-direction: column;
  }

  .advanced-grid {
    grid-template-columns: 1fr;
  }

  .message__body {
    max-width: 100%;
  }
}
</style>
