<template>
  <div class="page tryon-page">
    <TryonJobPanel :loading="loading" @submit="submit" />
    <TryonResultGrid :job="job" :items="items" />
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { onBeforeUnmount } from 'vue'
import { ref } from 'vue'

import { createTryonJob, getTryonJob, listTryonJobItems } from '@/api/tryon'
import TryonJobPanel from '@/components/tryon/TryonJobPanel.vue'
import TryonResultGrid from '@/components/tryon/TryonResultGrid.vue'
import type { CreateTryonJobPayload, TryonJob, TryonJobItem } from '@/types/task'

const loading = ref(false)
const job = ref<TryonJob>()
const items = ref<TryonJobItem[]>([])
let pollingTimer: number | undefined

async function submit(payload: CreateTryonJobPayload) {
  loading.value = true
  stopPolling()
  try {
    job.value = await createTryonJob({ ...payload, asyncProcessing: true })
    items.value = await listTryonJobItems(job.value.id)
    ElMessage.success('批量换装任务已创建，正在后台生成')
    startPolling(job.value.id)
  } catch (event) {
    ElMessage.error(event instanceof Error ? event.message : '套图任务失败')
  } finally {
    loading.value = false
  }
}

function startPolling(jobId: string) {
  pollingTimer = window.setInterval(async () => {
    try {
      job.value = await getTryonJob(jobId)
      items.value = await listTryonJobItems(jobId)
      if (['completed', 'failed', 'cancelled', 'partial_success'].includes(job.value.status)) {
        stopPolling()
      }
    } catch {
      stopPolling()
    }
  }, 1800)
}

function stopPolling() {
  if (pollingTimer) {
    window.clearInterval(pollingTimer)
    pollingTimer = undefined
  }
}

onBeforeUnmount(stopPolling)
</script>

<style scoped lang="scss">
.tryon-page {
  display: grid;
  grid-template-columns: 380px minmax(0, 1fr);
  gap: 18px;
}

@media (max-width: 980px) {
  .tryon-page {
    grid-template-columns: 1fr;
  }
}
</style>
