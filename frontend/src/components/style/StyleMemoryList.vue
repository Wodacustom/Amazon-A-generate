<template>
  <div class="style-list">
    <article v-for="memory in memories" :key="memory.id" class="style-card">
      <div class="style-card__head">
        <div>
          <h3>{{ memory.name }}</h3>
          <span>{{ scopeLabel[memory.scope] }}</span>
        </div>
        <el-switch :model-value="memory.isActive" />
      </div>
      <div class="style-card__colors">
        <span v-for="color in memory.colors" :key="color" :style="{ background: color }" />
      </div>
      <p>{{ memory.copyTone }} · {{ memory.composition }}</p>
    </article>
  </div>
</template>

<script setup lang="ts">
import type { StyleMemory } from '@/types/user'

defineProps<{
  memories: StyleMemory[]
}>()

const scopeLabel = {
  user: '个人风格',
  company: '公司风格',
  brand: '品牌风格',
}
</script>

<style scoped lang="scss">
.style-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.style-card {
  display: grid;
  gap: 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 16px;

  h3,
  p {
    margin: 0;
  }

  p,
  span {
    color: var(--text-secondary);
  }
}

.style-card__head {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 12px;
}

.style-card__colors {
  display: flex;
  gap: 8px;

  span {
    width: 24px;
    height: 24px;
    border: 1px solid var(--line);
    border-radius: 50%;
  }
}

@media (max-width: 980px) {
  .style-list {
    grid-template-columns: 1fr;
  }
}
</style>
