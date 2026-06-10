<template>
  <el-button
    class="start-button"
    size="large"
    type="primary"
    :loading="loading"
    :icon="WandSparkles"
    @click="$emit('start')"
  >
    {{ loading ? '正在生成图片...' : '开始生成' }}
  </el-button>
</template>

<script setup lang="ts">
import { WandSparkles } from 'lucide-vue-next'

defineProps<{
  loading: boolean
}>()

defineEmits<{
  start: []
}>()
</script>

<style scoped lang="scss">
.start-button {
  width: 100%;
}
</style>
