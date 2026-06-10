<template>
  <section class="workbench-panel module-selector">
    <div class="section-title">
      <h3>详情页模块</h3>
    </div>

    <div v-if="generation.isFullMockupMode" class="full-mockup-mode">
      <strong>整页样机模式</strong>
      <span>已选择样机：{{ generation.mockupPlan?.template?.name }}</span>
      <p>该样机将作为完整 A+ 图结构，生成时不再拆分选择单独模块。</p>
    </div>

    <div v-else class="module-selector__grid">
      <button
        v-for="module in moduleOptions"
        :key="module.key"
        type="button"
        :class="{ selected: generation.modules.includes(module.key) }"
        @click="generation.selectModule(module.key, !generation.modules.includes(module.key))"
      >
        <strong>{{ module.label }}</strong>
        <span>{{ module.description }}</span>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { moduleOptions } from '@/data/options'
import { useGenerationStore } from '@/stores/generation'

const generation = useGenerationStore()
</script>

<style scoped lang="scss">
.module-selector {
  padding: 16px;
}

.module-selector__grid {
  display: grid;
  gap: 8px;

  button {
    display: grid;
    gap: 4px;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: #fff;
    padding: 10px;
    text-align: left;
    cursor: pointer;

    span {
      color: var(--text-secondary);
      font-size: 12px;
      line-height: 1.45;
    }

    &.selected {
      border-color: #fb923c;
      background: var(--brand-soft);
    }
  }
}

.full-mockup-mode {
  display: grid;
  gap: 6px;
  border: 1px solid #fb923c;
  border-radius: var(--radius);
  background: var(--brand-soft);
  padding: 12px;

  span,
  p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 12px;
    line-height: 1.5;
  }
}
</style>
