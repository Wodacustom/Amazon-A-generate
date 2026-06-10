<template>
  <article class="module-card" :class="{ active }" @click="$emit('select')">
    <div class="module-card__media">
      <img v-if="module.imageUrl" :src="module.imageUrl" :alt="module.title" />
      <ImageIcon v-else :size="34" />
    </div>
    <div class="module-card__content">
      <el-tag size="small">{{ module.type }}</el-tag>
      <h3>{{ module.title }}</h3>
      <p>{{ module.description || module.subtitle }}</p>
      <div class="module-card__actions">
        <small v-if="module.visualPrompt">AI visual prompt ready</small>
        <el-button v-if="module.imageUrl" size="small" :icon="Download" @click.stop="downloadCurrentImage">
          下载图片
        </el-button>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { Download, Image as ImageIcon } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'

import type { GeneratedModule } from '@/types/result'
import { downloadImage, imageFilename } from '@/utils/download'

const props = defineProps<{
  module: GeneratedModule
  active: boolean
}>()

defineEmits<{
  select: []
}>()

async function downloadCurrentImage() {
  if (!props.module.imageUrl) return
  try {
    await downloadImage(props.module.imageUrl, imageFilename(props.module.title, props.module.imageUrl))
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '图片下载失败')
  }
}
</script>

<style scoped lang="scss">
.module-card {
  display: grid;
  grid-template-columns: minmax(120px, 30%) minmax(0, 1fr);
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  cursor: pointer;

  &.active {
    border-color: #fb923c;
    box-shadow: 0 0 0 2px rgb(249 115 22 / 12%);
  }
}

.module-card__media {
  display: grid;
  min-height: 152px;
  place-items: center;
  background: linear-gradient(135deg, #f8fafc, #fff7ed);
  color: var(--brand-dark);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.module-card__content {
  display: grid;
  align-content: center;
  gap: 8px;
  padding: 18px;

  h3,
  p {
    margin: 0;
    overflow-wrap: anywhere;
  }

  p {
    color: var(--text-secondary);
    line-height: 1.6;
  }

}

.module-card__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;

  small {
    color: var(--brand-dark);
    font-size: 12px;
    font-weight: 700;
  }
}

@media (max-width: 640px) {
  .module-card {
    grid-template-columns: 1fr;
  }
}
</style>
