<template>
  <section class="workbench-panel preview">
    <div class="section-title">
      <h2>A+ 详情预览</h2>
      <el-tag v-if="result">质量分 {{ result.qualityScore }}</el-tag>
    </div>

    <TaskProgress
      :task="task"
      :error="error"
      :loading="loading"
      :progress="progress"
      :current-step="currentStep"
      :steps="steps"
    />

    <div v-if="result" class="preview__modules">
      <ResultModuleCard
        v-for="module in result.modules"
        :key="module.id"
        :module="module"
        :active="module.id === activeModuleId"
        @select="$emit('select-module', module.id)"
      />
    </div>
    <div v-else class="preview__empty">
      <div class="preview__empty-icon">
        <ImageIcon :size="30" />
      </div>
      <div>
        <h3>等待生成预览</h3>
        <p>生成完成后，A+ 模块图、标题文案和质量分会在这里集中展示。</p>
      </div>
      <div class="preview__empty-grid">
        <span>商品素材</span>
        <span>场景样机</span>
        <span>模块草稿</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Image as ImageIcon } from 'lucide-vue-next'

import TaskProgress from '@/components/task/TaskProgress.vue'
import type { GenerationProgressStep, GenerationTask } from '@/types/generation'
import type { GenerationResult } from '@/types/result'

import ResultModuleCard from './ResultModuleCard.vue'

defineProps<{
  result?: GenerationResult
  task?: GenerationTask
  error?: string
  activeModuleId?: string
  loading?: boolean
  progress?: number
  currentStep?: GenerationProgressStep
  steps?: GenerationProgressStep[]
}>()

defineEmits<{
  'select-module': [moduleId: string]
}>()
</script>

<style scoped lang="scss">
.preview {
  display: grid;
  align-content: start;
  gap: 14px;
  min-height: 620px;
  padding: 18px;
}

.preview__modules {
  display: grid;
  gap: 14px;
}

.preview__empty {
  display: grid;
  place-items: center;
  gap: 14px;
  min-height: 440px;
  border: 1px dashed var(--line-strong);
  border-radius: var(--radius);
  background:
    linear-gradient(180deg, rgb(255 255 255 / 86%), rgb(255 255 255 / 96%)),
    repeating-linear-gradient(90deg, #f2f4f7 0, #f2f4f7 1px, transparent 1px, transparent 36px);
  padding: 28px;
  text-align: center;

  h3 {
    margin: 0 0 6px;
    font-size: 20px;
  }

  p {
    max-width: 360px;
    margin: 0;
    color: var(--text-secondary);
    line-height: 1.6;
  }
}

.preview__empty-icon {
  display: grid;
  width: 60px;
  height: 60px;
  place-items: center;
  border: 1px solid #d8b9a4;
  border-radius: var(--radius);
  background: var(--brand-soft);
  color: var(--brand);
}

.preview__empty-grid {
  display: grid;
  width: min(360px, 100%);
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;

  span {
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: #fff;
    padding: 9px 6px;
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 700;
  }
}

@media (max-width: 640px) {
  .preview__empty {
    min-height: 320px;
    padding: 20px;
  }

  .preview__empty-grid {
    grid-template-columns: 1fr;
  }
}
</style>
