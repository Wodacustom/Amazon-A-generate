<template>
  <div v-if="images.length" class="image-list">
    <div v-for="image in images" :key="image.id" class="image-list__item">
      <img :src="image.url" :alt="image.name" />
      <div>
        <strong>{{ image.name }}</strong>
        <span>{{ image.type }} · {{ Math.ceil(image.size / 1024) }} KB</span>
      </div>
      <el-button :icon="Trash2" text circle aria-label="删除图片" @click="$emit('remove', image.id)" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Trash2 } from 'lucide-vue-next'

import type { ProductImage } from '@/types/product'

defineProps<{
  images: ProductImage[]
}>()

defineEmits<{
  remove: [imageId: string]
}>()
</script>

<style scoped lang="scss">
.image-list {
  display: grid;
  gap: 10px;
  margin-top: 12px;
}

.image-list__item {
  display: grid;
  align-items: center;
  grid-template-columns: 54px minmax(0, 1fr) auto;
  gap: 10px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 8px;

  img {
    width: 54px;
    height: 54px;
    border-radius: 6px;
    object-fit: cover;
  }

  strong,
  span {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  span {
    color: var(--text-secondary);
    font-size: 12px;
  }
}
</style>
