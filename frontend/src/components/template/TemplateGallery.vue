<template>
  <div class="template-grid">
    <TemplateCard v-for="item in items" :key="item.id" :item="item" @use="$emit('use', $event)" />
  </div>
</template>

<script setup lang="ts">
import type { MockupTemplate } from '@/types/mockup'

import TemplateCard from './TemplateCard.vue'

defineProps<{
  items: MockupTemplate[]
}>()

defineEmits<{
  use: [template: MockupTemplate]
}>()
</script>

<style scoped lang="scss">
.template-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

@media (max-width: 1180px) {
  .template-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .template-grid {
    grid-template-columns: 1fr;
  }
}
</style>
