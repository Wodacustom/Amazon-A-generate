<template>
  <section class="workbench-panel uploader">
    <div class="section-title">
      <h3>商品图片</h3>
      <el-tag type="info">{{ product.images.length }} 张</el-tag>
    </div>
    <el-upload drag multiple :auto-upload="false" :show-file-list="false" :on-change="handleChange">
      <UploadCloud :size="26" />
      <div class="uploader__text">{{ uploading ? '图片上传中...' : '拖拽或点击上传商品图 / 参考图' }}</div>
    </el-upload>
    <UploadedImageList :images="product.images" @remove="product.removeImage" />
  </section>
</template>

<script setup lang="ts">
import type { UploadFile } from 'element-plus'
import { ElMessage } from 'element-plus'
import { UploadCloud } from 'lucide-vue-next'
import { ref } from 'vue'

import { uploadFile } from '@/api/file'
import { useProductStore } from '@/stores/product'

import UploadedImageList from './UploadedImageList.vue'

const product = useProductStore()
const uploading = ref(false)

async function handleChange(file: UploadFile) {
  if (!file.raw) return
  uploading.value = true
  try {
    const response = await uploadFile(file.raw)
    product.addImages([
      {
        id: response.id,
        url: response.url,
        type: 'main',
        name: response.filename,
        size: file.raw.size,
        sortOrder: product.images.length,
        uploadStatus: 'success',
        uploadProgress: 100,
      },
    ])
    ElMessage.success('商品图已上传，可用于 AI 看图识别')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '商品图上传失败')
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped lang="scss">
.uploader {
  padding: 16px;
}

.uploader__text {
  margin-top: 8px;
  color: var(--text-secondary);
}
</style>
