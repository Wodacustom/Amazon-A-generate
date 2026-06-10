<template>
  <div class="page">
    <div class="section-title">
      <div>
        <h2>品牌风格</h2>
        <p class="muted">管理个人、公司、品牌三个层级的风格记忆。</p>
      </div>
      <el-button type="primary">新增风格</el-button>
    </div>
    <StyleMemoryList :memories="memories" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import StyleMemoryList from '@/components/style/StyleMemoryList.vue'
import type { StyleMemory } from '@/types/user'

const memories = ref<StyleMemory[]>([
  {
    id: 'style-1',
    name: '简洁白底科技感',
    scope: 'brand',
    colors: ['#ffffff', '#111827', '#f97316'],
    copyTone: '专业、简洁、克制',
    composition: '产品居中，关键卖点围绕展示',
    forbiddenElements: ['夸张医疗声明'],
    isActive: true,
    usageCount: 12,
  },
  {
    id: 'style-2',
    name: '户外生活方式',
    scope: 'company',
    colors: ['#f8fafc', '#166534', '#f59e0b'],
    copyTone: '自然、可信、场景化',
    composition: '人物与产品在真实场景中结合',
    forbiddenElements: ['过度暗色滤镜'],
    isActive: true,
  },
])
</script>
