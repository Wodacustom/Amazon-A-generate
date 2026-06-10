<template>
  <div class="page workbench">
    <section class="workbench__header">
      <div class="workbench__intro">
        <span>A+ Detail Workspace</span>
        <h1>A+ 详情页生成工作台</h1>
        <p>围绕商品素材、场景样机和模块编辑组织生成流程，减少来回切换。</p>
      </div>

      <div class="workbench__status" aria-label="生成状态概览">
        <div>
          <span>可用素材</span>
          <strong>{{ readyImageCount }}/{{ product.images.length }}</strong>
          <small>{{ readyImageCount ? '已准备' : '待上传' }}</small>
        </div>
        <div>
          <span>生成模式</span>
          <strong>{{ generationModeLabel }}</strong>
          <small>{{ generation.mockupPlan ? '已匹配样机' : '常规模块' }}</small>
        </div>
        <div>
          <span>当前结果</span>
          <strong>{{ resultStatus }}</strong>
          <small>{{ result.currentResult ? '可编辑' : '等待生成' }}</small>
        </div>
      </div>
    </section>

    <section class="workbench__flow" aria-label="A+ 生成流程">
      <div v-for="step in workflowSteps" :key="step.label" :class="['workbench__step', step.state]">
        <span>{{ step.index }}</span>
        <div>
          <strong>{{ step.label }}</strong>
          <small>{{ step.detail }}</small>
        </div>
      </div>
    </section>

    <section class="workbench__config">
      <ProductUploader />
      <SellingPointEditor />
      <SceneRecommendationPanel />
      <GenerationSettings />
      <PromptOptionSelector />
      <StyleMemorySelector />
      <ModuleSelector />
      <StartGenerateButton :loading="generation.loading" @start="startGenerate" />
    </section>

    <PreviewCanvas
      class="workbench__preview"
      :result="result.currentResult"
      :task="generation.task"
      :error="generation.error"
      :loading="generation.loading"
      :progress="generation.progress"
      :current-step="generation.progressStep"
      :steps="generation.progressSteps"
      :active-module-id="result.activeModule?.id"
      @select-module="result.selectModule"
    />

    <aside class="workbench__editor-stack">
      <ModuleEditorPanel
        :module="result.activeModule"
        :result-metadata="result.currentResult?.metadata"
        @update="result.updateActiveModule"
      />
      <ResultVersionPanel />
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed } from 'vue'

import GenerationSettings from '@/components/generation/GenerationSettings.vue'
import ModuleSelector from '@/components/generation/ModuleSelector.vue'
import PromptOptionSelector from '@/components/generation/PromptOptionSelector.vue'
import SceneRecommendationPanel from '@/components/generation/SceneRecommendationPanel.vue'
import StartGenerateButton from '@/components/generation/StartGenerateButton.vue'
import StyleMemorySelector from '@/components/generation/StyleMemorySelector.vue'
import SellingPointEditor from '@/components/generation/SellingPointEditor.vue'
import ModuleEditorPanel from '@/components/preview/ModuleEditorPanel.vue'
import PreviewCanvas from '@/components/preview/PreviewCanvas.vue'
import ResultVersionPanel from '@/components/preview/ResultVersionPanel.vue'
import ProductUploader from '@/components/upload/ProductUploader.vue'
import { useGenerationStore } from '@/stores/generation'
import { useProductStore } from '@/stores/product'
import { useResultStore } from '@/stores/result'
import { validateGenerationDraft } from '@/utils/validation'

const generation = useGenerationStore()
const product = useProductStore()
const result = useResultStore()

const readyImageCount = computed(() => product.readyImages.length)
const selectedModuleCount = computed(() => (generation.isFullMockupMode ? 1 : generation.modules.length))
const generationModeLabel = computed(() =>
  generation.isFullMockupMode ? '整页样机' : `${selectedModuleCount.value} 个模块`,
)
const resultStatus = computed(() => {
  if (generation.loading) return '生成中'
  if (result.currentResult) return `质量分 ${result.currentResult.qualityScore}`
  return '未生成'
})
const workflowSteps = computed(() => [
  {
    index: '01',
    label: '素材',
    detail: readyImageCount.value ? `${readyImageCount.value} 张图片可用` : '等待商品图',
    state: readyImageCount.value ? 'done' : 'active',
  },
  {
    index: '02',
    label: '配置',
    detail: generation.mockupPlan ? '样机与场景已选定' : `${selectedModuleCount.value} 个模块待生成`,
    state: readyImageCount.value && generation.modules.length ? (generation.mockupPlan ? 'done' : 'active') : 'pending',
  },
  {
    index: '03',
    label: '生成与编辑',
    detail: result.currentResult ? '选择模块微调文案' : '等待生成结果',
    state: result.currentResult ? 'active' : 'pending',
  },
])

async function startGenerate() {
  const validation = validateGenerationDraft(product.productInfo, product.images, generation.modules)
  if (!validation.ok) {
    ElMessage.warning(validation.messages[0])
    return
  }

  try {
    if (!generation.mockupPlan) {
      await generation.recommendMockups(product.readyImages, product.productInfo)
    }
    const generated = await generation.run(product.productId, product.readyImages, product.productInfo)
    result.setResult(generated)
    ElMessage.success('生成完成')
  } catch {
    ElMessage.error(generation.error || '生成失败')
  }
}
</script>

<style scoped lang="scss">
.workbench {
  display: grid;
  align-items: start;
  grid-template-columns: minmax(280px, 360px) minmax(0, 1fr) minmax(280px, 360px);
  gap: 18px;
}

.workbench__header,
.workbench__flow {
  grid-column: 1 / -1;
}

.workbench__header {
  display: grid;
  align-items: end;
  grid-template-columns: minmax(0, 1fr) minmax(420px, 520px);
  gap: 20px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 20px;
}

.workbench__intro {
  display: grid;
  gap: 6px;

  span {
    color: var(--brand-dark);
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
  }

  h1 {
    margin: 0;
    font-size: 26px;
    line-height: 1.2;
  }

  p {
    max-width: 640px;
    margin: 0;
    color: var(--text-secondary);
    line-height: 1.6;
  }
}

.workbench__status {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;

  div {
    display: grid;
    gap: 4px;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: #f8fafc;
    padding: 12px;
  }

  span,
  small {
    color: var(--text-secondary);
    font-size: 12px;
  }

  strong {
    overflow: hidden;
    color: var(--text-primary);
    font-size: 18px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.workbench__flow {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.workbench__step {
  display: grid;
  align-items: center;
  grid-template-columns: 38px minmax(0, 1fr);
  gap: 10px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 12px;

  > span {
    display: grid;
    width: 38px;
    height: 38px;
    place-items: center;
    border-radius: var(--radius);
    background: #f2f4f7;
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 800;
  }

  div {
    display: grid;
    gap: 3px;
    min-width: 0;
  }

  strong,
  small {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  small {
    color: var(--text-secondary);
    font-size: 12px;
  }

  &.active {
    border-color: #d8b9a4;
    background: var(--brand-soft);

    > span {
      background: var(--brand);
      color: #fff;
    }
  }

  &.done > span {
    background: var(--mint-soft);
    color: var(--mint);
  }
}

.workbench__config {
  display: grid;
  gap: 14px;
}

.workbench__preview,
.workbench__editor-stack {
  position: sticky;
  top: 86px;
}

.workbench__editor-stack {
  display: grid;
  gap: 14px;
}

@media (max-width: 1320px) {
  .workbench {
    grid-template-columns: minmax(280px, 360px) minmax(0, 1fr);
  }

  .workbench__header {
    grid-template-columns: 1fr;
  }

  .workbench__editor-stack {
    position: static;
    grid-column: 1 / -1;
  }
}

@media (max-width: 980px) {
  .workbench {
    grid-template-columns: 1fr;
  }

  .workbench__status,
  .workbench__flow {
    grid-template-columns: 1fr;
  }

  .workbench__preview {
    position: static;
  }
}

@media (max-width: 640px) {
  .workbench__header {
    padding: 16px;
  }

  .workbench__intro h1 {
    font-size: 22px;
  }
}
</style>
