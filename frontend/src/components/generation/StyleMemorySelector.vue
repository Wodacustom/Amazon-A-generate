<template>
  <section class="workbench-panel style-selector">
    <div class="section-title">
      <h3>风格记忆</h3>
    </div>
    <el-segmented v-model="generation.styleMemory.mode" :options="modeOptions" />
    <el-checkbox v-model="generation.styleMemory.updateAfterGeneration">生成满意后沉淀为风格参考</el-checkbox>
  </section>
</template>

<script setup lang="ts">
import { useGenerationStore } from '@/stores/generation'

const generation = useGenerationStore()
const modeOptions = [
  { label: '不使用', value: 'none' },
  { label: '个人', value: 'user' },
  { label: '公司', value: 'company' },
  { label: '品牌', value: 'brand' },
]
</script>

<style scoped lang="scss">
.style-selector {
  display: grid;
  gap: 12px;
  padding: 16px;
}
</style>
