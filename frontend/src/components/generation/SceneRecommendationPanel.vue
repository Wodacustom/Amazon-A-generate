<template>
  <section class="workbench-panel scene-panel">
    <div class="section-title">
      <h3>场景样机</h3>
      <el-button size="small" :loading="generation.mockupLoading" @click="handleRecommend">
        <Search :size="15" />
        分析
      </el-button>
    </div>

    <div v-if="generation.mockupRecommendation" class="scene-panel__content">
      <div class="scene-panel__meta">
        <span>类目：{{ generation.mockupRecommendation.productCategory }}</span>
        <span>{{ generation.mockupRecommendation.matchedMockups.length }} 个样机</span>
      </div>

      <div class="scene-list">
        <button
          v-for="scene in generation.mockupRecommendation.scenes"
          :key="scene.id"
          type="button"
          :class="{ selected: scene.id === selectedSceneId }"
          @click="selectScene(scene.id)"
        >
          <strong>{{ scene.name }}</strong>
          <span>{{ scene.reason }}</span>
        </button>
      </div>

      <div v-if="selectedScene" class="prompt-box">
        <span>场景提示词</span>
        <p>{{ selectedScene.prompt.positive }}</p>
      </div>

      <div class="mockup-list">
        <button
          v-for="match in visibleMockups"
          :key="match.template.id"
          type="button"
          :class="{ selected: match.template.id === generation.mockupPlan?.templateId }"
          @click="selectMockup(match)"
        >
          <img :src="match.template.previewUrl" :alt="match.template.name" />
          <div>
            <strong>{{ match.template.name }}</strong>
            <span>{{ match.score }} 分 · {{ match.template.composition }}</span>
          </div>
          <Check v-if="match.template.id === generation.mockupPlan?.templateId" :size="16" />
        </button>
      </div>
    </div>

    <p v-else class="scene-panel__empty">上传商品图并填写卖点后，可先分析产品场景与样机方向。</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Search } from 'lucide-vue-next'

import { useGenerationStore } from '@/stores/generation'
import { useProductStore } from '@/stores/product'
import type { MatchedMockup } from '@/types/mockup'

const generation = useGenerationStore()
const product = useProductStore()

const selectedSceneId = computed(() => generation.mockupPlan?.sceneId || generation.mockupRecommendation?.scenes[0]?.id)
const selectedScene = computed(() =>
  generation.mockupRecommendation?.scenes.find((scene) => scene.id === selectedSceneId.value),
)
const visibleMockups = computed(() => {
  const matches = generation.mockupRecommendation?.matchedMockups || []
  return matches.filter((match) => match.sceneId === selectedSceneId.value).length
    ? matches.filter((match) => match.sceneId === selectedSceneId.value)
    : matches
})

async function handleRecommend() {
  if (!product.productInfo.productName || !product.productInfo.coreSellingPoints) {
    ElMessage.warning('请先填写商品名称和核心卖点')
    return
  }

  try {
    await generation.recommendMockups(product.readyImages, product.productInfo)
    ElMessage.success('场景样机已推荐')
  } catch {
    ElMessage.error(generation.error || '场景样机推荐失败')
  }
}

function selectScene(sceneId: string) {
  const match =
    generation.mockupRecommendation?.matchedMockups.find((item) => item.sceneId === sceneId) ||
    generation.mockupRecommendation?.matchedMockups[0]
  if (match) {
    selectMockup(match, sceneId)
  }
}

function selectMockup(match: MatchedMockup, sceneId = match.sceneId) {
  const scene = generation.mockupRecommendation?.scenes.find((item) => item.id === sceneId)
  if (!scene) return

  generation.setMockupPlan({
    sceneId,
    templateId: match.template.id,
    template: match.template,
    matchScore: match.score,
    scenePrompt: scene.prompt,
    compositionNotes: `使用 ${match.template.name} 的 ${match.template.composition} 构图，产品保持正面可见并统一光影。`,
  })
}
</script>

<style scoped lang="scss">
.scene-panel {
  display: grid;
  gap: 12px;
  padding: 16px;
}

.scene-panel__content {
  display: grid;
  gap: 12px;
}

.scene-panel__meta {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 12px;
}

.scene-list,
.mockup-list {
  display: grid;
  gap: 8px;
}

.scene-list button,
.mockup-list button {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  text-align: left;
  cursor: pointer;
}

.scene-list button {
  display: grid;
  gap: 4px;
  padding: 10px;

  span {
    color: var(--text-secondary);
    font-size: 12px;
    line-height: 1.45;
  }
}

.scene-list button.selected,
.mockup-list button.selected {
  border-color: #fb923c;
  background: var(--brand-soft);
}

.prompt-box {
  display: grid;
  gap: 6px;
  border: 1px dashed var(--line);
  border-radius: var(--radius);
  padding: 10px;
  background: #fff;

  span {
    color: var(--text-secondary);
    font-size: 12px;
  }

  p {
    margin: 0;
    color: var(--text-primary);
    font-size: 12px;
    line-height: 1.5;
  }
}

.mockup-list button {
  display: grid;
  align-items: center;
  grid-template-columns: 64px minmax(0, 1fr) 18px;
  gap: 10px;
  padding: 8px;

  img {
    width: 64px;
    height: 48px;
    border-radius: 6px;
    object-fit: cover;
  }

  div {
    display: grid;
    gap: 3px;
    min-width: 0;
  }

  strong,
  span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  span {
    color: var(--text-secondary);
    font-size: 12px;
  }
}

.scene-panel__empty {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.5;
}
</style>
