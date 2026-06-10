<template>
  <section class="home-hero">
    <div class="home-hero__headline">
      <span>AI 电商美工 Agent</span>
      <h1>今天要生产哪组商品内容</h1>
      <p>把商品图、链接和卖点放进同一个入口，后续会进入 A+ 生成工作台继续细化。</p>
    </div>

    <PromptComposer v-model="prompt" v-model:link="productLink" :limit="500" @upload="$emit('upload', $event)" />

    <div class="home-hero__shortcuts">
      <button v-for="item in shortcuts" :key="item.label" type="button" @click="$emit('useTool', item.to)">
        <component :is="item.icon" :size="17" />
        <span>{{ item.label }}</span>
      </button>
    </div>

    <div class="home-hero__actions">
      <el-button size="large" type="primary" :icon="WandSparkles" @click="$emit('submit')">进入生成工作台</el-button>
      <el-button size="large" :icon="ClipboardPaste" @click="pasteLink">粘贴商品链接</el-button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ClipboardPaste, Images, LayoutTemplate, Scissors, WandSparkles } from 'lucide-vue-next'

import PromptComposer from './PromptComposer.vue'

const prompt = defineModel<string>({ required: true })
const productLink = defineModel<string>('link', { required: true })

defineEmits<{
  submit: []
  upload: [files: File[]]
  useTool: [path: string]
}>()

const shortcuts = [
  { label: '图片编辑', to: '/continuous-edit', icon: Scissors },
  { label: '创建设计', to: '/aplus-detail', icon: WandSparkles },
  { label: '商品套图', to: '/product-images', icon: Images },
  { label: '样机模板', to: '/templates', icon: LayoutTemplate },
]

async function pasteLink() {
  try {
    const text = await navigator.clipboard.readText()
    productLink.value = text
  } catch {
    productLink.value = ''
  }
}
</script>

<style scoped lang="scss">
.home-hero {
  display: grid;
  gap: 16px;

  h1 {
    max-width: 680px;
    margin: 6px 0 0;
    font-size: clamp(34px, 5vw, 56px);
    line-height: 1.02;
  }

  p {
    max-width: 560px;
    margin: 12px 0 0;
    color: var(--text-secondary);
    font-size: 16px;
    line-height: 1.65;
  }
}

.home-hero__headline span {
  color: var(--brand);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0;
}

.home-hero__shortcuts,
.home-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.home-hero__shortcuts {
  width: 100%;
}

.home-hero__shortcuts button {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  color: var(--text-primary);
  padding: 9px 12px;
  cursor: pointer;

  svg {
    color: var(--brand);
  }

  &:hover {
    border-color: #d8b9a4;
    background: var(--brand-soft);
  }
}

@media (max-width: 760px) {
  .home-hero {
    align-items: stretch;
  }

  .home-hero__shortcuts,
  .home-hero__actions {
    justify-content: flex-start;
  }
}
</style>
