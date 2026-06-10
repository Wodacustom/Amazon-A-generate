<template>
  <section class="workbench-panel prompt-selector">
    <div class="section-title">
      <h3>模块化提示词</h3>
      <el-button text size="small" :loading="loading" @click="loadOptions">刷新</el-button>
    </div>

    <div v-if="groups.length" class="prompt-selector__groups">
      <div v-for="group in groups" :key="group.key" class="prompt-group">
        <strong>{{ group.label }}</strong>
        <div class="prompt-group__options">
          <el-check-tag
            v-for="option in group.options"
            :key="option.key"
            :checked="generation.promptConfig[group.key].includes(option.key)"
            @change="toggle(group.key, option.key, group.selection)"
          >
            {{ option.label }}
          </el-check-tag>
        </div>
      </div>
    </div>
    <el-empty v-else description="提示词选项暂未加载" />
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getPromptOptionGroups } from '@/api/prompt'
import { useGenerationStore } from '@/stores/generation'
import type { PromptConfig, PromptOptionGroup } from '@/types/generation'

const generation = useGenerationStore()
const groups = ref<PromptOptionGroup[]>([])
const loading = ref(false)

onMounted(loadOptions)

async function loadOptions() {
  loading.value = true
  try {
    groups.value = await getPromptOptionGroups()
  } catch {
    groups.value = fallbackGroups
  } finally {
    loading.value = false
  }
}

function toggle(groupKey: keyof PromptConfig, optionKey: string, selection: string) {
  const values = generation.promptConfig[groupKey]
  if (values.includes(optionKey)) {
    generation.promptConfig[groupKey] = values.filter((value) => value !== optionKey)
    return
  }
  generation.promptConfig[groupKey] = selection === 'single' ? [optionKey] : [...values, optionKey]
}

const fallbackGroups: PromptOptionGroup[] = [
  {
    key: 'visualStyle',
    label: '视觉风格',
    selection: 'multiple',
    options: [
      { key: 'minimal', label: '简洁专业', prompt: 'Clean and professional', negative: false },
      { key: 'lifestyle', label: '生活方式', prompt: 'Lifestyle product scene', negative: false },
    ],
  },
  {
    key: 'negative',
    label: '禁用元素',
    selection: 'multiple',
    options: [{ key: 'no_exaggerated_claims', label: '避免夸大宣传', prompt: 'Avoid exaggerated claims', negative: true }],
  },
]
</script>

<style scoped lang="scss">
.prompt-selector {
  padding: 16px;
}

.prompt-selector__groups {
  display: grid;
  gap: 14px;
}

.prompt-group {
  display: grid;
  gap: 8px;
}

.prompt-group__options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
