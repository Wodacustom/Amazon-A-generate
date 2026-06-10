<template>
  <div class="page">
    <div class="section-title">
      <div>
        <h2>样机库</h2>
        <p class="muted">管理可被 Agent 识别、评分和套用的商品样机模板。</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">新增样机</el-button>
    </div>

    <TemplateGalleryGrid :items="templates" @use="useTemplate" />

    <el-dialog v-model="dialogVisible" title="新增样机模板" width="760px">
      <el-form label-position="top">
        <div class="form-row">
          <el-form-item label="样机名称">
            <el-input v-model="draft.name" placeholder="例如 Outdoor Camping Table" />
          </el-form-item>
          <el-form-item label="构图">
            <el-select v-model="draft.composition">
              <el-option label="居中产品" value="center" />
              <el-option label="左侧产品" value="left-product" />
              <el-option label="右侧产品" value="right-product" />
              <el-option label="桌面摆拍" value="tabletop" />
              <el-option label="按模型理解融合" value="prompt-based" />
            </el-select>
          </el-form-item>
        </div>

        <el-form-item label="样机图片">
          <div class="upload-line">
            <el-upload
              :auto-upload="false"
              :show-file-list="false"
              accept="image/*"
              :on-change="handleImageSelected"
            >
              <el-button :loading="uploading">上传本地图片</el-button>
            </el-upload>
            <el-input v-model="draft.previewUrl" placeholder="也可以直接粘贴 https:// 图片 URL" />
          </div>
        </el-form-item>

        <div v-if="draft.previewUrl" class="mockup-preview">
          <img :src="draft.previewUrl" alt="样机预览" />
        </div>
        <div v-else class="mockup-empty">上传或粘贴一张样机图，Agent 会把它作为生图参考模板。</div>

        <el-form-item label="生图融合提示词">
          <el-input
            v-model="draft.mergePrompt"
            type="textarea"
            :rows="4"
            placeholder="例如：将我的原始产品替换到这张样机中的商品位置，保留产品外观、Logo、包装文字和比例，匹配样机的光影、透视、接触阴影和材质质感，生成真实电商 A+ 场景图。"
          />
        </el-form-item>

        <div class="form-row">
          <el-form-item label="类目标签">
            <el-input v-model="categoryText" placeholder="outdoor, drinkware" />
          </el-form-item>
          <el-form-item label="场景标签">
            <el-input v-model="sceneText" placeholder="camping, outdoor" />
          </el-form-item>
        </div>

        <div class="form-row">
          <el-form-item label="平台">
            <el-input v-model="platformText" placeholder="amazon, shopify" />
          </el-form-item>
          <el-form-item label="比例">
            <el-input v-model="ratioText" placeholder="platform_default, 4_5" />
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveTemplate">保存样机</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import type { UploadFile } from 'element-plus'
import { ElMessage } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { uploadFile } from '@/api/file'
import { createMockupTemplate, getMockupTemplates } from '@/api/mockup'
import TemplateGalleryGrid from '@/components/template/TemplateGallery.vue'
import { useGenerationStore } from '@/stores/generation'
import type { MockupTemplate } from '@/types/mockup'

const router = useRouter()
const generation = useGenerationStore()
const templates = ref<MockupTemplate[]>([])
const dialogVisible = ref(false)
const saving = ref(false)
const uploading = ref(false)
const categoryText = ref('outdoor, drinkware')
const sceneText = ref('camping, outdoor')
const platformText = ref('amazon')
const ratioText = ref('platform_default, 4_5')
const draft = reactive({
  name: '',
  previewUrl: '',
  composition: 'prompt-based',
  mergePrompt:
    'Use the uploaded mockup image as the scene template. Replace the product shown in the mockup with my original product image. Preserve my product shape, label, logo, packaging text, color, and proportions. Match the mockup perspective, lighting, contact shadow, material reflections, and depth of field. Keep the final image realistic, premium, and suitable for an ecommerce A+ detail page.',
})

onMounted(loadTemplates)

function openCreateDialog() {
  dialogVisible.value = true
}

async function loadTemplates() {
  templates.value = await getMockupTemplates()
}

async function useTemplate(template: MockupTemplate) {
  generation.setMockupPlan({
    sceneId: template.scenes[0] || 'full_mockup',
    templateId: template.id,
    template,
    matchScore: 100,
    scenePrompt: {
      positive: template.composition,
      negative: 'distorted product, changed logo, unreadable packaging text, wrong perspective',
      composition: 'Use the uploaded mockup as the complete A+ page composition.',
      productPlacement: 'Replace the product shown in the mockup with the uploaded product image.',
      supportingProps: [],
    },
    compositionNotes: `使用 ${template.name} 作为整页 A+ 样机结构，不再拆分单独模块。`,
  })
  await router.push('/aplus-detail')
}

async function handleImageSelected(upload: UploadFile) {
  if (!upload.raw) return
  uploading.value = true
  try {
    const response = await uploadFile(upload.raw)
    draft.previewUrl = response.url
    ElMessage.success('样机图片已上传')
  } finally {
    uploading.value = false
  }
}

async function saveTemplate() {
  if (!draft.name || !draft.previewUrl) {
    ElMessage.warning('请填写样机名称并上传或粘贴样机图片')
    return
  }

  saving.value = true
  try {
    await createMockupTemplate({
      name: draft.name,
      previewUrl: draft.previewUrl,
      category: splitTags(categoryText.value),
      scenes: splitTags(sceneText.value),
      platforms: splitTags(platformText.value),
      ratios: splitTags(ratioText.value),
      composition: draft.mergePrompt.trim() || draft.composition,
      replaceableAreas: [],
      tags: ['custom', 'prompt-replace'],
    })
    ElMessage.success('样机已加入 Agent 模板库')
    dialogVisible.value = false
    resetDraft()
    await loadTemplates()
  } finally {
    saving.value = false
  }
}

function resetDraft() {
  draft.name = ''
  draft.previewUrl = ''
  draft.composition = 'prompt-based'
  draft.mergePrompt =
    'Use the uploaded mockup image as the scene template. Replace the product shown in the mockup with my original product image. Preserve my product shape, label, logo, packaging text, color, and proportions. Match the mockup perspective, lighting, contact shadow, material reflections, and depth of field. Keep the final image realistic, premium, and suitable for an ecommerce A+ detail page.'
}

function splitTags(value: string) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}
</script>

<style scoped lang="scss">
.form-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.upload-line {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  width: 100%;
}

.mockup-preview,
.mockup-empty {
  margin: 2px 0 18px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: #f8fafc;
}

.mockup-preview {
  overflow: hidden;
  max-height: 420px;

  img {
    display: block;
    width: 100%;
    max-height: 420px;
    object-fit: contain;
    background: #f8fafc;
  }
}

.mockup-empty {
  display: flex;
  min-height: 220px;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  text-align: center;
  padding: 24px;
}

@media (max-width: 640px) {
  .form-row,
  .upload-line {
    grid-template-columns: 1fr;
  }
}
</style>
