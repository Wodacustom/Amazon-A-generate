<template>
  <div class="page home">
    <section class="home__workspace">
      <div class="home__primary">
        <HomeHeroPrompt
          v-model="prompt"
          v-model:link="productLink"
          @submit="submit"
          @upload="uploadReferenceImages"
          @use-tool="openTool"
        />
      </div>

      <aside class="home__today">
        <div class="home__today-head">
          <span>Today</span>
          <strong>生成准备度</strong>
        </div>
        <div class="home__readiness">
          <div v-for="item in readiness" :key="item.label" :class="{ active: item.active }">
            <component :is="item.icon" :size="18" />
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <button type="button" class="home__continue" @click="openTool('/aplus-detail')">
          <WandSparkles :size="18" />
          <span>打开 A+ 工作台</span>
        </button>
      </aside>
    </section>

    <section class="home__operations">
      <button
        v-for="feature in primaryFeatures"
        :key="feature.title"
        type="button"
        class="home__operation"
        @click="openTool(feature.to)"
      >
        <img :src="feature.image" :alt="feature.title" />
        <div>
          <span>{{ feature.label }}</span>
          <strong>{{ feature.title }}</strong>
          <p>{{ feature.description }}</p>
        </div>
      </button>
    </section>

    <section class="home__tool-strip" aria-label="常用工具">
      <button v-for="tool in tools" :key="tool.title" type="button" @click="openTool(tool.to)">
        <component :is="tool.icon" :size="19" />
        <span>{{ tool.title }}</span>
      </button>
    </section>

    <InspirationStrip @select="selectInspiration" />
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import {
  FileText,
  ImagePlus,
  Images,
  Link as LinkIcon,
  LayoutTemplate,
  Palette,
  Scissors,
  Shirt,
  Sparkles,
  UploadCloud,
  WandSparkles,
} from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import HomeHeroPrompt from '@/components/home/HomeHeroPrompt.vue'
import InspirationStrip from '@/components/home/InspirationStrip.vue'
import { useGenerationStore } from '@/stores/generation'
import { useProductStore } from '@/stores/product'
import { createLocalProductImage } from '@/utils/file'

const router = useRouter()
const product = useProductStore()
const generation = useGenerationStore()
const prompt = ref('')
const productLink = ref('')

const readiness = computed(() => [
  {
    label: '商品素材',
    value: product.images.length ? `${product.images.length} 张` : '待上传',
    active: Boolean(product.images.length),
    icon: UploadCloud,
  },
  {
    label: '生成草稿',
    value: prompt.value.trim() ? '已填写' : '空白',
    active: Boolean(prompt.value.trim()),
    icon: FileText,
  },
  {
    label: '商品链接',
    value: productLink.value.trim() ? '已粘贴' : '可选',
    active: Boolean(productLink.value.trim()),
    icon: LinkIcon,
  },
])

const primaryFeatures = [
  {
    label: 'AI 修图',
    title: '先整理商品主体',
    description: '抠图、换背景、局部重绘、统一光影，适合把杂乱素材整理成可生成输入。',
    to: '/continuous-edit',
    image: 'https://images.unsplash.com/photo-1616627561950-9f746e330187?auto=format&fit=crop&w=900&q=80',
  },
  {
    label: 'AI 生成',
    title: '生成 A+ 详情草稿',
    description: '从卖点、场景提示词到样机结构，直接进入可编辑的 A+ 工作台。',
    to: '/aplus-detail',
    image: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80',
  },
]

const tools = [
  { title: 'A+ 详情', to: '/aplus-detail', icon: WandSparkles },
  { title: '商品套图', to: '/product-images', icon: Images },
  { title: '样机模板', to: '/templates', icon: LayoutTemplate },
  { title: '智能抠图', to: '/continuous-edit', icon: Scissors },
  { title: '换背景', to: '/continuous-edit', icon: ImagePlus },
  { title: 'AI 试穿', to: '/tryon', icon: Shirt },
  { title: '品牌风格', to: '/style-memory', icon: Palette },
  { title: '灵感案例', to: '/templates', icon: Sparkles },
]

function selectInspiration(value: string) {
  prompt.value = value
  product.applyPromptDraft(value)
}

function uploadReferenceImages(files: File[]) {
  product.addImages(files.map((file, index) => createLocalProductImage(file, 'reference', product.images.length + index)))
  ElMessage.success('参考图片已加入生成草稿')
}

async function submit() {
  if (!prompt.value.trim()) {
    ElMessage.warning('请先输入产品卖点或营销信息')
    return
  }
  product.applyPromptDraft(prompt.value)
  generation.setHomeDraft(prompt.value)
  await router.push({ path: '/aplus-detail', query: productLink.value ? { link: productLink.value } : {} })
}

async function openTool(path: string) {
  await router.push(path)
}
</script>

<style scoped lang="scss">
.home {
  min-height: calc(100vh - 80px);
  max-width: 1200px;
  margin: 0 auto;
  padding: 18px 0 32px;
}

.home__workspace {
  display: grid;
  align-items: stretch;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 18px;
}

.home__primary,
.home__today {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgb(255 255 255 / 78%);
}

.home__primary {
  padding: 26px;
}

.home__today {
  display: grid;
  align-content: start;
  gap: 14px;
  padding: 18px;
}

.home__today-head {
  display: grid;
  gap: 4px;

  span {
    color: var(--brand);
    font-size: 12px;
    font-weight: 800;
  }

  strong {
    font-size: 22px;
  }
}

.home__readiness {
  display: grid;
  gap: 8px;
}

.home__readiness div {
  display: grid;
  align-items: center;
  grid-template-columns: 28px minmax(0, 1fr) auto;
  gap: 8px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 10px;
  color: var(--text-secondary);

  svg {
    color: var(--text-muted);
  }

  span,
  strong {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  strong {
    color: var(--text-primary);
    font-size: 13px;
  }

  &.active {
    border-color: #d8b9a4;
    background: var(--brand-soft);

    svg {
      color: var(--brand);
    }
  }
}

.home__continue {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  border: 0;
  border-radius: var(--radius);
  background: var(--text-primary);
  color: #fff;
  padding: 12px;
  cursor: pointer;
  font-weight: 700;
}

.home__operations {
  display: grid;
  grid-template-columns: minmax(0, 0.88fr) minmax(0, 1.12fr);
  gap: 14px;
  margin-top: 18px;
}

.home__operation {
  display: grid;
  grid-template-columns: 140px minmax(0, 1fr);
  gap: 14px;
  align-items: stretch;
  min-height: 156px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 10px;
  color: var(--text-primary);
  text-align: left;
  cursor: pointer;

  img {
    width: 100%;
    height: 100%;
    min-height: 136px;
    border-radius: 6px;
    object-fit: cover;
  }

  div {
    display: grid;
    align-content: center;
    gap: 7px;
    min-width: 0;
    padding: 8px;
  }

  span {
    width: fit-content;
    border-radius: var(--radius);
    background: var(--accent-soft);
    color: var(--brand-dark);
    padding: 5px 8px;
    font-size: 12px;
    font-weight: 800;
  }

  strong {
    font-size: 22px;
    line-height: 1.18;
  }

  p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.6;
  }

  &:hover {
    border-color: #d8b9a4;
    box-shadow: var(--shadow-soft);
  }
}

.home__tool-strip {
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  gap: 10px;
  margin-top: 16px;
}

.home__tool-strip button {
  display: grid;
  min-height: 86px;
  place-items: center;
  gap: 7px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgb(255 255 255 / 84%);
  color: var(--text-primary);
  cursor: pointer;

  svg {
    color: var(--brand);
  }

  span {
    font-size: 13px;
    font-weight: 700;
  }

  &:hover {
    border-color: #d8b9a4;
    background: var(--brand-soft);
  }
}

@media (max-width: 1080px) {
  .home__workspace,
  .home__operations {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1180px) {
  .home__tool-strip {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .home {
    padding-bottom: 16px;
  }

  .home__primary,
  .home__today {
    padding: 16px;
  }

  .home__operation {
    grid-template-columns: 1fr;
  }

  .home__tool-strip {
    grid-template-columns: 1fr;
  }
}
</style>
