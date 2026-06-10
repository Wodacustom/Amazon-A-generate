<template>
  <aside class="workbench-panel editor">
    <div class="section-title">
      <h3>模块编辑</h3>
      <el-button :icon="Download" text :disabled="!module?.imageUrl" @click="downloadCurrentImage">下载图片</el-button>
    </div>

    <template v-if="module">
      <div v-if="mockupPlan?.template" class="editor__mockup">
        <img :src="mockupPlan.template.previewUrl" :alt="mockupPlan.template.name" />
        <div>
          <span>Agent 选用样机</span>
          <strong>{{ mockupPlan.template.name }}</strong>
          <small>{{ mockupPlan.matchScore || 0 }} 分 · {{ mockupPlan.template.composition }}</small>
        </div>
      </div>

      <el-form label-position="top">
        <el-form-item label="标题">
          <el-input :model-value="module.title" @update:model-value="update({ title: String($event) })" />
        </el-form-item>
        <el-form-item label="副标题">
          <el-input :model-value="module.subtitle" @update:model-value="update({ subtitle: String($event) })" />
        </el-form-item>
        <el-form-item label="描述文案">
          <el-input
            :model-value="module.description"
            type="textarea"
            :rows="5"
            @update:model-value="update({ description: String($event) })"
          />
        </el-form-item>
        <el-form-item label="视觉提示词">
          <el-input
            :model-value="module.visualPrompt"
            type="textarea"
            :rows="4"
            @update:model-value="update({ visualPrompt: String($event) })"
          />
        </el-form-item>
      </el-form>

      <div class="editor__actions">
        <el-button :icon="RefreshCw">局部重新生成</el-button>
        <el-button :icon="Save">保存为风格参考</el-button>
      </div>
    </template>
    <el-empty v-else description="选择一个模块后进行编辑" />

  </aside>
</template>

<script setup lang="ts">
import { Download, RefreshCw, Save } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { computed } from 'vue'

import type { GeneratedModule } from '@/types/result'
import type { MockupGenerationPlan } from '@/types/mockup'

import { downloadImage, imageFilename } from '@/utils/download'

const props = defineProps<{
  module?: GeneratedModule
  resultMetadata?: Record<string, unknown>
}>()

const emit = defineEmits<{
  update: [patch: Partial<GeneratedModule>]
}>()

const mockupPlan = computed(() => props.resultMetadata?.mockupPlan as MockupGenerationPlan | undefined)

function update(patch: Partial<GeneratedModule>) {
  emit('update', patch)
}

async function downloadCurrentImage() {
  if (!props.module?.imageUrl) return
  try {
    await downloadImage(props.module.imageUrl, imageFilename(props.module.title, props.module.imageUrl))
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '图片下载失败')
  }
}
</script>

<style scoped lang="scss">
.editor {
  display: grid;
  align-content: start;
  gap: 14px;
  padding: 16px;
}

.editor__actions {
  display: grid;
  gap: 10px;
}

.editor__mockup {
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 8px;

  img {
    width: 82px;
    height: 62px;
    border-radius: 6px;
    object-fit: cover;
  }

  div {
    display: grid;
    gap: 3px;
    min-width: 0;
  }

  span,
  small {
    color: var(--text-secondary);
    font-size: 12px;
  }

  strong,
  small {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
