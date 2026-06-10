<template>
  <section class="inspiration">
    <div class="section-title">
      <h2>最近常用模板</h2>
      <span class="muted">点击后生成同款方向</span>
    </div>
    <div class="inspiration__grid">
      <InspirationCard v-for="item in inspirationItems" :key="item.title" :item="item" @select="$emit('select', item.prompt)" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { inspirationItems } from '@/data/options'

import InspirationCard from './InspirationCard.vue'

defineEmits<{
  select: [prompt: string]
}>()
</script>

<style scoped lang="scss">
.inspiration {
  margin-top: 22px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgb(255 255 255 / 70%);
  padding: 16px;
}

.inspiration__grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

@media (max-width: 1180px) {
  .inspiration__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .inspiration__grid {
    grid-template-columns: 1fr;
  }
}
</style>
