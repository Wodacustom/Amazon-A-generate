<template>
  <section class="workbench-panel tryon-panel">
    <div class="section-title">
      <h3>批量模特换装</h3>
      <el-tag type="info">{{ selectedGarments.length }} 件样衣</el-tag>
    </div>

    <el-form label-position="top">
      <el-form-item label="参考模特图">
        <el-upload :auto-upload="false" :show-file-list="false" accept="image/*" :on-change="uploadModel">
          <el-button :loading="modelUploading">上传模特图</el-button>
        </el-upload>
        <div v-if="modelImage" class="asset-preview">
          <img :src="modelImage.url" :alt="modelImage.name" />
          <div>
            <span>{{ modelImage.name }}</span>
            <small>{{ modelImage.width }} x {{ modelImage.height }} · {{ modelRatioLabel }}</small>
          </div>
        </div>
      </el-form-item>

      <el-form-item label="样衣库">
        <div class="library-actions">
          <el-upload
            multiple
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            :on-change="uploadGarment"
          >
            <el-button :loading="garmentUploading">上传样衣入库</el-button>
          </el-upload>
          <el-button :icon="FolderOpen" :loading="folderUploading" @click="selectGarmentFolder">
            导入衣服文件夹
          </el-button>
          <el-button :loading="libraryLoading" @click="loadLibrary">刷新样衣库</el-button>
          <input
            ref="folderInput"
            class="folder-input"
            type="file"
            accept="image/*"
            multiple
            webkitdirectory
            @change="uploadGarmentFolder"
          />
        </div>
        <p v-if="folderUploading" class="folder-progress">
          正在导入文件夹：{{ folderUploadProgress.done }} / {{ folderUploadProgress.total }}
        </p>

        <div v-if="garmentLibrary.length" class="garment-library">
          <div
            v-for="garment in garmentLibrary"
            :key="garment.id"
            class="garment-card"
            :class="{ 'is-selected': selectedGarmentIds.includes(garment.id) }"
            @click="toggleGarment(garment.id)"
          >
            <img :src="garment.url" :alt="garment.name" />
            <div class="garment-card__meta">
              <span>{{ garment.name }}</span>
              <small>{{ garment.filename }}</small>
            </div>
            <div class="garment-card__actions">
              <el-checkbox :model-value="selectedGarmentIds.includes(garment.id)" />
              <el-button text type="danger" @click.stop="removeLibraryGarment(garment.id)">删除</el-button>
            </div>
          </div>
        </div>
        <el-empty v-else class="library-empty" description="还没有样衣底板，上传后会保存到独立样衣库。" />
      </el-form-item>

      <el-form-item label="换装提示词">
        <el-input v-model="payload.prompt" type="textarea" :rows="7" />
      </el-form-item>

      <el-form-item label="输出数量 / 输出比例">
        <div class="form-row">
          <el-input-number v-model="payload.outputCount" :min="1" :max="4" />
          <el-select v-model="payload.ratio">
            <el-option
              :disabled="!modelImage"
              :label="modelImage ? `跟随模特图 · ${modelRatioLabel}` : '跟随模特图 · 上传后自动识别'"
              :value="modelRatioValue"
            />
            <el-option label="9:16 竖屏全身图" value="9_16" />
            <el-option label="3:4 竖版模特图" value="3_4" />
            <el-option label="2:3 服装电商图" value="2_3" />
            <el-option label="4:5 电商竖图" value="4_5" />
            <el-option label="1:1 方图" value="1_1" />
            <el-option label="16:9 横图" value="16_9" />
          </el-select>
        </div>
        <p class="ratio-hint">{{ ratioHint }}</p>
      </el-form-item>

      <el-form-item label="生图模型">
        <el-select v-model="payload.imageModel">
          <el-option
            v-for="model in imageModelOptions"
            :key="model.key"
            :label="model.label"
            :value="model.key"
          />
        </el-select>
        <p class="ratio-hint">{{ selectedImageModel?.description }}</p>
      </el-form-item>

      <el-alert
        type="info"
        :closable="false"
        show-icon
        title="可以一次导入整个衣服图片文件夹。样衣会进入独立样衣库，生成时会异步创建批量任务并持续刷新结果。"
      />

      <el-button class="submit-button" type="primary" :loading="loading" @click="submit">创建批量换装任务</el-button>
    </el-form>
  </section>
</template>

<script setup lang="ts">
import type { UploadFile } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { FolderOpen } from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'

import { uploadFile } from '@/api/file'
import { deleteGarmentLibraryItem, listGarmentLibraryItems, uploadGarmentLibraryItem } from '@/api/garmentLibrary'
import { imageModelOptions } from '@/data/options'
import type { GarmentLibraryItem } from '@/types/garmentLibrary'
import type { CreateTryonJobPayload } from '@/types/task'

interface UploadedAsset {
  id: string
  name: string
  url: string
}

interface UploadedModel extends UploadedAsset {
  width: number
  height: number
}

const emit = defineEmits<{
  submit: [payload: CreateTryonJobPayload]
}>()

defineProps<{
  loading: boolean
}>()

const modelUploading = ref(false)
const garmentUploading = ref(false)
const folderUploading = ref(false)
const libraryLoading = ref(false)
const folderInput = ref<HTMLInputElement>()
const folderUploadProgress = reactive({ done: 0, total: 0 })
const modelImage = ref<UploadedModel>()
const garmentLibrary = ref<GarmentLibraryItem[]>([])
const selectedGarmentIds = ref<string[]>([])
const modelRatioValue = ref('model_4_5')
const payload = reactive({
  outputCount: 1,
  ratio: 'model_4_5',
  imageModel: 'nanobanana_pro',
  mode: 'garment_preserve',
  prompt:
    'Use the reference model image as the fixed model, pose, face, body shape, camera angle, background, and lighting reference. Put the uploaded garment onto the model. Preserve the garment exactly as provided: do not change the clothing silhouette, fabric texture, color, print, pattern, logo, buttons, zipper, seams, collar, sleeves, hem, pockets, labels, embroidery, decorations, accessories attached to the clothing, or any visible design element. Keep the garment proportions faithful to the source clothing image. Fit the garment naturally on the model body with realistic drape, folds, occlusion, contact shadows, and fabric tension. The final image should look like the original garment is truly worn by the reference model. Do not redesign the clothing, do not simplify the pattern, do not invent new logos, do not change sleeve length or neckline, and do not alter any text or graphic printed on the garment.',
})

const selectedGarments = computed(() => garmentLibrary.value.filter((item) => selectedGarmentIds.value.includes(item.id)))

const modelRatioLabel = computed(() => {
  if (!modelImage.value) return '4:5'
  const [width, height] = ratioFromSize(modelImage.value.width, modelImage.value.height)
  return `${width}:${height}`
})

const ratioHint = computed(() => {
  if (payload.ratio.startsWith('model_')) {
    return modelImage.value ? `将按参考模特图原始比例生成：${modelRatioLabel.value}` : '上传模特图后会自动读取原图比例。'
  }
  const labels: Record<string, string> = {
    '9_16': '适合手机竖屏、全身模特展示和短视频封面。',
    '3_4': '适合常见电商服装模特图。',
    '2_3': '适合较高的服装详情图。',
    '4_5': '适合移动端商品展示和社媒平台。',
    '1_1': '适合方形商品卡片。',
    '16_9': '适合横向 banner 或场景展示。',
  }
  return labels[payload.ratio] || '将按所选比例生成。'
})

const selectedImageModel = computed(() => imageModelOptions.find((model) => model.key === payload.imageModel))

onMounted(loadLibrary)

async function loadLibrary() {
  libraryLoading.value = true
  try {
    garmentLibrary.value = await listGarmentLibraryItems()
    selectedGarmentIds.value = selectedGarmentIds.value.filter((id) => garmentLibrary.value.some((item) => item.id === id))
  } finally {
    libraryLoading.value = false
  }
}

async function uploadModel(file: UploadFile) {
  if (!file.raw) return
  modelUploading.value = true
  try {
    const size = await readImageSize(file.raw)
    const uploaded = await uploadFile(file.raw)
    modelImage.value = { id: uploaded.id, name: uploaded.filename, url: uploaded.url, ...size }
    const [ratioWidth, ratioHeight] = ratioFromSize(size.width, size.height)
    modelRatioValue.value = `model_${ratioWidth}_${ratioHeight}`
    payload.ratio = modelRatioValue.value
    ElMessage.success(`模特图已上传，已自动设置比例 ${ratioWidth}:${ratioHeight}`)
  } finally {
    modelUploading.value = false
  }
}

async function uploadGarment(file: UploadFile) {
  if (!file.raw) return
  garmentUploading.value = true
  try {
    const uploaded = await uploadGarmentLibraryItem(file.raw)
    garmentLibrary.value = [uploaded, ...garmentLibrary.value.filter((item) => item.id !== uploaded.id)]
    selectedGarmentIds.value = [...selectedGarmentIds.value, uploaded.id]
    ElMessage.success('样衣已保存到样衣库，并加入本次批量任务')
  } finally {
    garmentUploading.value = false
  }
}

function selectGarmentFolder() {
  folderInput.value?.click()
}

async function uploadGarmentFolder(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || []).filter(isImageFile)
  if (!files.length) {
    ElMessage.warning('文件夹中没有可用的图片文件')
    input.value = ''
    return
  }

  folderUploading.value = true
  folderUploadProgress.done = 0
  folderUploadProgress.total = files.length
  try {
    const uploadedItems: GarmentLibraryItem[] = []
    for (const file of files) {
      const name = relativeFileName(file)
      const uploaded = await uploadGarmentLibraryItem(file, { name, tags: 'folder-import' })
      uploadedItems.push(uploaded)
      folderUploadProgress.done += 1
    }
    const uploadedIds = uploadedItems.map((item) => item.id)
    garmentLibrary.value = [
      ...uploadedItems,
      ...garmentLibrary.value.filter((item) => !uploadedIds.includes(item.id)),
    ]
    selectedGarmentIds.value = Array.from(new Set([...selectedGarmentIds.value, ...uploadedIds]))
    ElMessage.success(`已导入 ${uploadedItems.length} 张衣服图，并加入本次批量任务`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '衣服文件夹导入失败')
  } finally {
    folderUploading.value = false
    input.value = ''
  }
}

function toggleGarment(id: string) {
  selectedGarmentIds.value = selectedGarmentIds.value.includes(id)
    ? selectedGarmentIds.value.filter((item) => item !== id)
    : [...selectedGarmentIds.value, id]
}

async function removeLibraryGarment(id: string) {
  await ElMessageBox.confirm('删除后该样衣底板会从样衣库移除，本地文件也会删除。', '删除样衣', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteGarmentLibraryItem(id)
  garmentLibrary.value = garmentLibrary.value.filter((item) => item.id !== id)
  selectedGarmentIds.value = selectedGarmentIds.value.filter((item) => item !== id)
  ElMessage.success('样衣已删除')
}

function submit() {
  if (!modelImage.value) {
    ElMessage.warning('请先上传参考模特图')
    return
  }
  if (!selectedGarments.value.length) {
    ElMessage.warning('请至少从样衣库选择一张样衣')
    return
  }

  emit('submit', {
    productAssetIds: selectedGarments.value.map((item) => item.id),
    modelAssetIds: [modelImage.value.id],
    productImageUrls: selectedGarments.value.map((item) => item.url),
    modelImageUrls: [modelImage.value.url],
    prompt: payload.prompt,
    outputCount: payload.outputCount,
    ratio: payload.ratio,
    imageModel: payload.imageModel,
    mode: payload.mode,
    asyncProcessing: true,
  })
}

function isImageFile(file: File) {
  return file.type.startsWith('image/') || /\.(png|jpe?g|webp|gif|bmp)$/i.test(file.name)
}

function relativeFileName(file: File) {
  const maybeRelative = file as File & { webkitRelativePath?: string }
  return maybeRelative.webkitRelativePath || file.name
}

function readImageSize(file: File) {
  return new Promise<{ width: number; height: number }>((resolve, reject) => {
    const objectUrl = URL.createObjectURL(file)
    const image = new Image()
    image.onload = () => {
      resolve({ width: image.naturalWidth, height: image.naturalHeight })
      URL.revokeObjectURL(objectUrl)
    }
    image.onerror = () => {
      URL.revokeObjectURL(objectUrl)
      reject(new Error('无法读取图片尺寸'))
    }
    image.src = objectUrl
  })
}

function ratioFromSize(width: number, height: number): [number, number] {
  const divisor = gcd(width, height)
  const ratioWidth = Math.round(width / divisor)
  const ratioHeight = Math.round(height / divisor)
  if (ratioWidth > 40 || ratioHeight > 40) {
    return closestStandardRatio(width / height)
  }
  return [ratioWidth, ratioHeight]
}

function closestStandardRatio(value: number): [number, number] {
  const ratios: Array<[number, number]> = [
    [9, 16],
    [2, 3],
    [3, 4],
    [4, 5],
    [1, 1],
    [16, 9],
  ]
  return ratios.reduce((best, item) =>
    Math.abs(item[0] / item[1] - value) < Math.abs(best[0] / best[1] - value) ? item : best,
  )
}

function gcd(left: number, right: number): number {
  return right === 0 ? left : gcd(right, left % right)
}
</script>

<style scoped lang="scss">
.tryon-panel {
  padding: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.library-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  width: 100%;
}

.folder-input {
  display: none;
}

.folder-progress {
  width: 100%;
  margin: 8px 0 0;
  color: var(--text-secondary);
  font-size: 12px;
}

.asset-preview {
  display: grid;
  align-items: center;
  grid-template-columns: 54px minmax(0, 1fr) auto;
  gap: 8px;
  width: 100%;
  margin-top: 8px;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 8px;
  background: #fff;

  img {
    width: 54px;
    height: 54px;
    border-radius: 6px;
    object-fit: cover;
  }

  div {
    display: grid;
    gap: 2px;
    min-width: 0;
  }

  span,
  small {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  small {
    color: var(--text-secondary);
    font-size: 12px;
  }
}

.garment-library {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
  width: 100%;
  max-height: 360px;
  overflow: auto;
  margin-top: 10px;
}

.garment-card {
  display: grid;
  gap: 8px;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 8px;
  background: #fff;
  cursor: pointer;

  &.is-selected {
    border-color: var(--el-color-primary);
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.14);
  }

  img {
    width: 100%;
    aspect-ratio: 1;
    border-radius: 6px;
    object-fit: cover;
    background: #f5f7fb;
  }
}

.garment-card__meta {
  display: grid;
  gap: 2px;
  min-width: 0;

  span,
  small {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  small {
    color: var(--text-secondary);
    font-size: 12px;
  }
}

.garment-card__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.library-empty {
  width: 100%;
  padding: 18px 0 4px;
}

.ratio-hint {
  margin: 8px 0 0;
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.5;
}

.submit-button {
  width: 100%;
  margin-top: 12px;
}
</style>
