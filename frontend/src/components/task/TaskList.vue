<template>
  <div class="task-list">
    <article v-for="task in tasks" :key="task.id" class="task-list__item">
      <div>
        <h3>{{ task.productName }}</h3>
        <span>{{ task.id }} · {{ formatDateTime(task.createdAt) }}</span>
      </div>
      <el-tag>{{ formatStatus(task.status) }}</el-tag>
      <el-progress :percentage="task.progress" />
    </article>
  </div>
</template>

<script setup lang="ts">
import type { GenerationTask } from '@/types/generation'
import { formatDateTime, formatStatus } from '@/utils/format'

defineProps<{
  tasks: GenerationTask[]
}>()
</script>

<style scoped lang="scss">
.task-list {
  display: grid;
  gap: 12px;
}

.task-list__item {
  display: grid;
  align-items: center;
  grid-template-columns: minmax(0, 1fr) auto 180px;
  gap: 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 14px;

  h3 {
    margin: 0 0 4px;
  }

  span {
    color: var(--text-secondary);
    font-size: 13px;
  }
}

@media (max-width: 760px) {
  .task-list__item {
    grid-template-columns: 1fr;
  }
}
</style>
