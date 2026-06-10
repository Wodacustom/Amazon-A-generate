<template>
  <div class="page result-page">
    <PreviewCanvas
      :result="result.currentResult"
      :active-module-id="result.activeModule?.id"
      @select-module="result.selectModule"
    />
    <aside class="result-page__side">
      <ModuleEditorPanel :module="result.activeModule" @update="result.updateActiveModule" />
      <ResultVersionPanel />
    </aside>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { getGenerationResult } from '@/api/generation'
import ModuleEditorPanel from '@/components/preview/ModuleEditorPanel.vue'
import PreviewCanvas from '@/components/preview/PreviewCanvas.vue'
import ResultVersionPanel from '@/components/preview/ResultVersionPanel.vue'
import { useResultStore } from '@/stores/result'

const result = useResultStore()
const route = useRoute()

onMounted(async () => {
  const taskId = typeof route.params.id === 'string' ? route.params.id : undefined
  if (!taskId || result.currentResult?.taskId === taskId) return

  const generationResult = await getGenerationResult(taskId)
  result.setResult(generationResult)
})
</script>

<style scoped lang="scss">
.result-page {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 18px;
}

.result-page__side {
  display: grid;
  align-content: start;
  gap: 14px;
}

@media (max-width: 980px) {
  .result-page {
    grid-template-columns: 1fr;
  }
}
</style>
