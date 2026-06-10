<template>
  <el-dialog v-model="visible" title="导出结果" width="420px">
    <div class="export-options">
      <el-button :icon="ImageDown">导出长图</el-button>
      <el-button :icon="FileArchive">导出模块 ZIP</el-button>
      <el-button :icon="Copy">复制文案</el-button>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { Copy, FileArchive, ImageDown } from 'lucide-vue-next'

const visible = defineModel<boolean>({ required: true })
</script>

<style scoped lang="scss">
.export-options {
  display: grid;
  gap: 10px;
}
</style>
