<template>
  <section v-if="loading || task || error" class="workbench-panel task-progress">
    <div class="task-progress__head">
      <div>
        <strong>{{ title }}</strong>
        <span>{{ subtitle }}</span>
      </div>
      <el-tag v-if="loading" type="warning">生成中</el-tag>
      <el-tag v-else-if="task?.status === 'completed'" type="success">完成</el-tag>
      <el-tag v-else-if="task?.status === 'failed' || error" type="danger">异常</el-tag>
    </div>

    <el-progress :percentage="visibleProgress" :status="progressStatus" />

    <div v-if="loading && visibleSteps.length" class="task-progress__steps">
      <div
        v-for="step in visibleSteps"
        :key="step.key"
        class="task-progress__step"
        :class="{ active: currentStep?.key === step.key, done: visibleProgress >= step.percentage }"
      >
        <span />
        <div>
          <strong>{{ step.label }}</strong>
          <small>{{ step.detail }}</small>
        </div>
      </div>
    </div>

    <p v-if="task?.errorMessage || error">{{ task?.errorMessage || error }}</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { GenerationProgressStep, GenerationTask } from '@/types/generation'
import { formatStatus } from '@/utils/format'

const props = defineProps<{
  task?: GenerationTask
  error?: string
  loading?: boolean
  progress?: number
  currentStep?: GenerationProgressStep
  steps?: GenerationProgressStep[]
}>()

const visibleProgress = computed(() => {
  if (props.loading) return Math.round(props.progress || 0)
  return props.task?.progress || 0
})

const title = computed(() => {
  if (props.loading) return props.currentStep?.label || '生成中'
  if (props.task) return formatStatus(props.task.status)
  return '生成异常'
})

const subtitle = computed(() => {
  if (props.loading) return props.currentStep?.detail || '正在处理图片生成任务。'
  return props.task?.currentStep || props.error || ''
})

const progressStatus = computed(() => {
  if (props.task?.status === 'failed' || props.error) return 'exception'
  if (!props.loading && props.task?.status === 'completed') return 'success'
  return undefined
})

const visibleSteps = computed(() => props.steps || [])
</script>

<style scoped lang="scss">
.task-progress {
  display: grid;
  gap: 12px;
  padding: 16px;
}

.task-progress__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;

  div {
    display: grid;
    gap: 4px;
  }

  span {
    color: var(--text-secondary);
    font-size: 12px;
    line-height: 1.5;
  }
}

.task-progress__steps {
  display: grid;
  gap: 8px;
}

.task-progress__step {
  display: grid;
  align-items: start;
  grid-template-columns: 12px minmax(0, 1fr);
  gap: 8px;
  color: var(--text-muted);

  > span {
    width: 10px;
    height: 10px;
    margin-top: 4px;
    border: 1px solid var(--line);
    border-radius: 50%;
    background: #fff;
  }

  div {
    display: grid;
    gap: 2px;
  }

  strong {
    color: inherit;
    font-size: 13px;
  }

  small {
    font-size: 12px;
    line-height: 1.45;
  }

  &.done {
    color: var(--text-secondary);

    > span {
      border-color: #22c55e;
      background: #22c55e;
    }
  }

  &.active {
    color: var(--text-primary);

    > span {
      border-color: #fb923c;
      background: #fb923c;
      box-shadow: 0 0 0 4px rgba(251, 146, 60, 0.16);
    }
  }
}

p {
  margin: 0;
  color: var(--danger);
}
</style>
