<template>
  <div class="page">
    <div class="section-title">
      <div>
        <h2>历史记录</h2>
        <p class="muted">查看生成任务、进度和失败恢复入口。</p>
      </div>
      <el-input v-model="keyword" class="task-search" placeholder="搜索商品名称或任务 ID" clearable />
    </div>
    <TaskList :tasks="filteredTasks" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import TaskList from '@/components/task/TaskList.vue'
import { useGenerationStore } from '@/stores/generation'

const generation = useGenerationStore()
const keyword = ref('')

const filteredTasks = computed(() => {
  const tasks = generation.task ? [generation.task] : []
  if (!keyword.value) return tasks
  return tasks.filter((task) => `${task.productName} ${task.id}`.includes(keyword.value))
})
</script>

<style scoped lang="scss">
.task-search {
  max-width: 320px;
}
</style>
