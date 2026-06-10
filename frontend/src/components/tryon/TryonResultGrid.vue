<template>
  <section class="workbench-panel tryon-results">
    <div class="section-title">
      <div>
        <h3>换装结果</h3>
        <p v-if="job">{{ job.completedItems }} / {{ job.totalItems }} 已完成</p>
      </div>
      <div class="result-actions">
        <el-tag v-if="job">{{ formatStatus(job.status) }}</el-tag>
        <el-button v-if="downloadableItems.length" :icon="Download" @click="downloadAll">批量下载</el-button>
      </div>
    </div>

    <el-progress v-if="job" :percentage="job.progress" />

    <div v-if="items.length" class="tryon-results__grid">
      <article v-for="item in items" :key="item.id">
        <div class="tryon-results__thumb">
          <img v-if="item.outputImageUrl" :src="item.outputImageUrl" :alt="item.productAssetId" />
          <ImageIcon v-else :size="28" />
        </div>
        <div class="tryon-results__meta">
          <strong>{{ formatStatus(item.status) }}</strong>
          <span>{{ item.productAssetId }} × {{ item.modelAssetId }}</span>
        </div>
        <el-button v-if="item.outputImageUrl" size="small" :icon="Download" @click="downloadOne(item)">下载</el-button>
      </article>
    </div>

    <el-empty v-else description="上传模特图和衣服图后创建任务，这里会展示批量换装结果。" />
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Image as ImageIcon } from 'lucide-vue-next'

import type { TryonJob, TryonJobItem } from '@/types/task'
import { downloadImage, imageFilename } from '@/utils/download'
import { formatStatus } from '@/utils/format'

const props = defineProps<{
  job?: TryonJob
  items: TryonJobItem[]
}>()

const downloadableItems = computed(() => props.items.filter((item) => item.outputImageUrl))

async function downloadOne(item: TryonJobItem) {
  if (!item.outputImageUrl) return
  try {
    await downloadImage(item.outputImageUrl, imageFilename(`tryon-${item.productAssetId}`, item.outputImageUrl))
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '下载失败')
  }
}

async function downloadAll() {
  for (const item of downloadableItems.value) {
    await downloadOne(item)
  }
}
</script>

<style scoped lang="scss">
.tryon-results {
  display: grid;
  gap: 14px;
  padding: 16px;
}

.section-title {
  align-items: start;

  p {
    margin: 4px 0 0;
    color: var(--text-secondary);
    font-size: 12px;
  }
}

.result-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tryon-results__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;

  article {
    display: grid;
    gap: 8px;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 10px;
    background: #fff;
  }
}

.tryon-results__thumb {
  display: grid;
  overflow: hidden;
  min-height: 220px;
  place-items: center;
  border-radius: 8px;
  background: #f8fafc;

  img {
    width: 100%;
    height: 100%;
    min-height: 220px;
    object-fit: cover;
  }
}

.tryon-results__meta {
  display: grid;
  gap: 4px;

  span {
    overflow-wrap: anywhere;
    color: var(--text-secondary);
    font-size: 12px;
  }
}

@media (max-width: 760px) {
  .tryon-results__grid {
    grid-template-columns: 1fr;
  }
}
</style>
