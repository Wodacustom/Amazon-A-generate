<template>
  <div class="composer">
    <div class="composer__toolbar">
      <div>
        <button type="button" class="active">文字生成</button>
        <button type="button">参考图</button>
        <button type="button">商品链接</button>
      </div>
      <span>草稿会带入 A+ 工作台</span>
    </div>
    <el-input
      v-model="prompt"
      type="textarea"
      :autosize="{ minRows: 5, maxRows: 8 }"
      :maxlength="limit"
      resize="none"
      show-word-limit
      placeholder="例如：露营保温水壶，Amazon US，突出防漏、长效保温、便携挂扣，需要一套户外 A+ 详情图。"
    />
    <div class="composer__footer">
      <el-input v-model="link" :prefix-icon="LinkIcon" placeholder="商品链接，可选" />
      <el-upload :auto-upload="false" :show-file-list="false" multiple :on-change="handleChange">
        <el-button :icon="ImagePlus">上传参考图片</el-button>
      </el-upload>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UploadFile } from 'element-plus'
import { ImagePlus, Link as LinkIcon } from 'lucide-vue-next'

defineProps<{
  limit: number
}>()

const prompt = defineModel<string>({ required: true })
const link = defineModel<string>('link', { required: true })

const emit = defineEmits<{
  upload: [files: File[]]
}>()

function handleChange(file: UploadFile) {
  if (file.raw) {
    emit('upload', [file.raw])
  }
}
</script>

<style scoped lang="scss">
.composer {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 14px;
  box-shadow: var(--shadow-soft);
}

.composer__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 13px;

  div {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  button {
    border: 0;
    border-radius: 999px;
    background: transparent;
    color: var(--text-secondary);
    padding: 6px 10px;
    cursor: pointer;
  }

  button.active {
    background: var(--brand-soft);
    color: var(--brand);
    font-weight: 700;
  }
}

.composer__footer {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  margin-top: 12px;
}

@media (max-width: 640px) {
  .composer__toolbar {
    display: grid;
  }

  .composer__footer {
    grid-template-columns: 1fr;
  }
}
</style>
