<template>
  <article class="template-card">
    <div class="template-card__preview">
      <img v-if="item.previewUrl" :src="item.previewUrl" :alt="item.name" />
      <LayoutTemplate v-else :size="34" />
    </div>
    <div class="template-card__body">
      <div class="template-card__tags">
        <el-tag v-for="tag in item.category.slice(0, 2)" :key="tag" size="small">{{ tag }}</el-tag>
      </div>
      <h3>{{ item.name }}</h3>
      <p>{{ item.scenes.join(' / ') || '未设置场景' }}</p>
      <small>{{ item.composition }} · 提示词融合</small>
      <el-button type="primary" @click="$emit('use', item)">用于整页 A+</el-button>
    </div>
  </article>
</template>

<script setup lang="ts">
import { LayoutTemplate } from 'lucide-vue-next'

import type { MockupTemplate } from '@/types/mockup'

defineProps<{
  item: MockupTemplate
}>()

defineEmits<{
  use: [template: MockupTemplate]
}>()
</script>

<style scoped lang="scss">
.template-card {
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
}

.template-card__preview {
  display: grid;
  height: 132px;
  place-items: center;
  background: linear-gradient(135deg, #f1f5f9, #ffedd5);
  color: var(--brand-dark);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.template-card__body {
  display: grid;
  gap: 10px;
  padding: 16px;

  h3,
  p {
    margin: 0;
  }

  p {
    color: var(--text-secondary);
  }

  small {
    color: var(--text-muted);
    font-size: 12px;
  }
}

.template-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
