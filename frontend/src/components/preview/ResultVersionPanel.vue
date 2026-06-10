<template>
  <section class="workbench-panel version-panel">
    <div class="section-title">
      <h3>版本历史</h3>
      <el-button
        size="small"
        type="primary"
        :icon="Save"
        :loading="result.versionLoading"
        :disabled="!result.currentResult"
        @click="saveVersion"
      >
        保存版本
      </el-button>
    </div>

    <div v-if="result.currentResult" class="version-panel__list">
      <article v-for="version in latestVersions" :key="version.id" class="version-panel__item">
        <div>
          <strong>V{{ version.version }} · {{ version.label }}</strong>
          <span>{{ formatDateTime(version.createdAt) }} · {{ version.modules.length }} 个模块</span>
        </div>
        <el-button
          size="small"
          text
          :icon="RotateCcw"
          :loading="result.versionLoading"
          @click="restore(version.id)"
        >
          恢复
        </el-button>
      </article>

      <p v-if="!result.versions.length" class="version-panel__empty">当前结果还没有版本快照。</p>
    </div>
    <p v-else class="version-panel__empty">生成结果后可保存和恢复编辑版本。</p>
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { RotateCcw, Save } from 'lucide-vue-next'
import { computed, watch } from 'vue'

import { useResultStore } from '@/stores/result'
import { formatDateTime } from '@/utils/format'

const result = useResultStore()

const latestVersions = computed(() => [...result.versions].reverse())

watch(
  () => result.currentResult?.id,
  (resultId) => {
    if (resultId) {
      void result.loadVersions(resultId)
    }
  },
  { immediate: true },
)

async function saveVersion() {
  try {
    await result.saveCurrentVersion(`编辑版本 ${result.versions.length + 1}`)
    ElMessage.success('版本已保存')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '版本保存失败')
  }
}

async function restore(versionId: string) {
  try {
    await result.restoreVersion(versionId)
    ElMessage.success('版本已恢复')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '版本恢复失败')
  }
}
</script>

<style scoped lang="scss">
.version-panel {
  display: grid;
  gap: 12px;
  padding: 16px;
}

.version-panel__list {
  display: grid;
  gap: 8px;
}

.version-panel__item {
  display: grid;
  align-items: center;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 10px;

  div {
    display: grid;
    gap: 4px;
    min-width: 0;
  }

  strong,
  span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  strong {
    color: var(--text-primary);
    font-size: 13px;
  }

  span {
    color: var(--text-secondary);
    font-size: 12px;
  }
}

.version-panel__empty {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.5;
}
</style>
