<template>
  <section class="workbench-panel form-panel">
    <div class="section-title">
      <h3>生成设置</h3>
    </div>
    <el-form label-position="top">
      <el-form-item label="平台 / 国家">
        <div class="form-row">
          <el-select v-model="generation.settings.platform">
            <el-option label="Amazon" value="amazon" />
          </el-select>
          <el-select v-model="generation.settings.country">
            <el-option label="US" value="US" />
            <el-option label="UK" value="UK" />
            <el-option label="DE" value="DE" />
          </el-select>
        </div>
      </el-form-item>
      <el-form-item label="语言 / 质量">
        <div class="form-row">
          <el-select v-model="generation.settings.language">
            <el-option label="English" value="en" />
            <el-option label="中文" value="zh" />
          </el-select>
          <el-select v-model="generation.settings.qualityLevel">
            <el-option label="标准 A+" value="normal_a_plus" />
            <el-option label="高级 A+" value="premium_a_plus" />
          </el-select>
        </div>
      </el-form-item>
      <el-form-item label="生图模型 / 视觉风格">
        <div class="form-row">
          <el-select v-model="generation.settings.imageModel">
            <el-option
              v-for="model in imageModelOptions"
              :key="model.key"
              :label="model.label"
              :value="model.key"
            />
          </el-select>
          <el-select v-model="generation.settings.designStyle">
            <el-option label="简洁专业" value="minimal" />
            <el-option label="生活方式" value="lifestyle" />
            <el-option label="科技感" value="tech" />
          </el-select>
        </div>
        <p class="size-hint">{{ selectedImageModel?.description }}</p>
      </el-form-item>

      <el-form-item label="图片尺寸">
        <div class="form-row">
          <el-select v-model="generation.settings.imageRatio">
            <el-option label="Amazon 横图 16:9 · 建议 1600×900" value="platform_default" />
            <el-option label="正方形 1:1 · 建议 1600×1600" value="1_1" />
            <el-option label="竖图 4:5 · 建议 1600×2000" value="4_5" />
            <el-option label="宽屏 16:9 · 建议 1600×900" value="16_9" />
          </el-select>
        </div>
        <div class="size-card">
          <span>当前输出尺寸</span>
          <strong>{{ currentSize.label }}</strong>
          <p>{{ sizeHint }}</p>
        </div>
      </el-form-item>
    </el-form>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { imageModelOptions } from '@/data/options'
import { useGenerationStore } from '@/stores/generation'

const generation = useGenerationStore()

const selectedImageModel = computed(() => imageModelOptions.find((model) => model.key === generation.settings.imageModel))

const sizeHint = computed(() => {
  const hints: Record<string, string> = {
    platform_default: '默认适合 Amazon A+ 横向模块，建议下载后按平台需要二次裁切。',
    '1_1': '适合主图、方形卖点图和社媒复用。',
    '4_5': '适合移动端竖版浏览和高信息密度整页样机。',
    '16_9': '适合横向 A+ banner、首屏和宽版场景图。',
  }
  return hints[generation.settings.imageRatio] || hints.platform_default
})

const currentSize = computed(() => {
  const sizes: Record<string, { label: string; ratio: string; pixels: string }> = {
    platform_default: { label: '1600 × 900 px', ratio: '16:9', pixels: '1600x900' },
    '1_1': { label: '1600 × 1600 px', ratio: '1:1', pixels: '1600x1600' },
    '4_5': { label: '1600 × 2000 px', ratio: '4:5', pixels: '1600x2000' },
    '16_9': { label: '1600 × 900 px', ratio: '16:9', pixels: '1600x900' },
  }
  return sizes[generation.settings.imageRatio] || sizes.platform_default
})
</script>

<style scoped lang="scss">
.form-panel {
  padding: 16px;
}

.form-row {
  display: grid;
  width: 100%;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.size-card {
  display: grid;
  gap: 4px;
  margin: 8px 0 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff7ed;
  padding: 10px;

  span {
    color: var(--text-secondary);
    font-size: 12px;
  }

  strong {
    color: var(--text-primary);
    font-size: 18px;
  }

  p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 12px;
    line-height: 1.5;
  }
}

.size-hint {
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.5;
}
</style>
