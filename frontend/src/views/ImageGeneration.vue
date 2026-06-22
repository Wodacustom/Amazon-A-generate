<template>
  <div class="image-page">
    <section class="image-header">
      <div>
        <h1>生图测试</h1>
        <p>上传可选参考图和 mask，输入提示词后发起 OpenAI/NewAPI 图片协议请求。</p>
      </div>
      <el-button type="primary" :loading="submitting" @click="submit">生成图片</el-button>
    </section>

    <div class="image-grid">
      <section class="workbench-panel image-panel">
        <div class="section-title">
          <h3>请求参数</h3>
        </div>
        <el-form label-position="top">
          <el-form-item label="提示词">
            <el-input v-model="form.prompt" type="textarea" :rows="7" placeholder="描述要生成或编辑的图片" />
          </el-form-item>

          <div class="form-row">
            <el-form-item label="业务 role">
              <el-input v-model="form.role" />
            </el-form-item>
            <el-form-item label="模型 Profile ID（可选）">
              <el-input-number v-model="form.modelProfileId" :min="1" />
            </el-form-item>
          </div>

          <div class="form-row">
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

          <div class="upload-row">
            <el-upload :auto-upload="false" :show-file-list="false" accept="image/*" :on-change="selectImage">
              <el-button>上传参考图</el-button>
            </el-upload>
            <span class="file-name">{{ imageFile?.name || '无参考图时走 generations' }}</span>
          </div>

          <div class="upload-row">
            <el-upload :auto-upload="false" :show-file-list="false" accept="image/*" :on-change="selectMask">
              <el-button>上传 Mask</el-button>
            </el-upload>
            <span class="file-name">{{ maskFile?.name || '可选，仅 edits 使用' }}</span>
          </div>

          <el-form-item label="扩展参数 JSON">
            <el-input
              v-model="form.optionsText"
              type="textarea"
              :rows="5"
              placeholder='例如：{"quality":"high","response_format":"b64_json"}'
            />
          </el-form-item>
        </el-form>
      </section>

      <section class="workbench-panel image-panel">
        <div class="section-title">
          <h3>生成结果</h3>
          <el-tag v-if="result">{{ result.items.length }} 张</el-tag>
        </div>

        <el-empty v-if="!result" description="等待生成结果" />
        <div v-else class="result-list">
          <article v-for="item in result.items" :key="item.file_id" class="result-item">
            <img :src="item.image_url" alt="generated image" />
            <div class="result-meta">
              <el-tag>{{ item.operation }}</el-tag>
              <span>{{ item.provider }} / {{ item.model }}</span>
              <small>链接有效 {{ Math.round(item.expires_in / 3600) }} 小时</small>
            </div>
          </article>
        </div>

        <pre v-if="result" class="metadata">{{ JSON.stringify(result.metadata, null, 2) }}</pre>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { reactive, ref } from 'vue'

import { generateImage, type ImageGenerationResponse } from '@/api/imageGeneration'

const imageFile = ref<File | null>(null)
const maskFile = ref<File | null>(null)
const submitting = ref(false)
const result = ref<ImageGenerationResponse | null>(null)

const form = reactive({
  prompt: '',
  role: 'image_generation',
  modelProfileId: undefined as number | undefined,
  size: '1024x1024',
  n: 1,
  optionsText: '{}',
})

function selectImage(upload: UploadFile) {
  imageFile.value = upload.raw || null
}

function selectMask(upload: UploadFile) {
  maskFile.value = upload.raw || null
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
  if (maskFile.value && !imageFile.value) {
    ElMessage.warning('Mask 需要和参考图一起上传')
    return
  }
  const options = parseOptions()
  if (!options) return

  submitting.value = true
  try {
    result.value = await generateImage({
      prompt: form.prompt,
      role: form.role || 'image_generation',
      modelProfileId: form.modelProfileId,
      size: form.size,
      n: form.n,
      image: imageFile.value,
      mask: maskFile.value,
      options,
    })
    ElMessage.success('图片已生成')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
.image-page {
  display: grid;
  gap: 16px;
}

.image-header {
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

.image-grid {
  display: grid;
  grid-template-columns: minmax(360px, 420px) minmax(0, 1fr);
  gap: 16px;
}

.image-panel {
  padding: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.upload-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.file-name {
  min-width: 0;
  color: var(--text-secondary);
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
}

.result-item {
  display: grid;
  gap: 10px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 10px;

  img {
    width: 100%;
    aspect-ratio: 1;
    border-radius: 6px;
    object-fit: contain;
    background: #f6f6f6;
  }
}

.result-meta {
  display: grid;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 13px;
}

.metadata {
  margin: 16px 0 0;
  overflow: auto;
  border-radius: 6px;
  background: #f7f7f7;
  padding: 10px;
  font-size: 12px;
}

@media (max-width: 980px) {
  .image-header,
  .upload-row {
    align-items: stretch;
    flex-direction: column;
  }

  .image-grid,
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
