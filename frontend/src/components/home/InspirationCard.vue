<template>
  <button class="card" type="button" @click="$emit('select')">
    <div class="card__thumb" :style="{ backgroundImage: `url(${props.item.imageUrl})` }">
      <component :is="icon" :size="22" />
    </div>
    <strong>{{ item.title }}</strong>
    <span>{{ item.prompt }}</span>
    <em>做同款</em>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Dumbbell, Headphones, PawPrint, Sparkles, TentTree } from 'lucide-vue-next'

const props = defineProps<{
  item: { title: string; prompt: string; imageUrl?: string }
}>()

defineEmits<{
  select: []
}>()

const icon = computed(() => {
  if (itemTitle.value.includes('耳机')) return Headphones
  if (itemTitle.value.includes('宠物')) return PawPrint
  if (itemTitle.value.includes('瑜伽')) return Dumbbell
  if (itemTitle.value.includes('户外')) return TentTree
  return Sparkles
})

const itemTitle = computed(() => props.item.title)
</script>

<style scoped lang="scss">
.card {
  display: grid;
  min-height: 176px;
  align-content: start;
  gap: 9px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 12px;
  color: inherit;
  text-align: left;
  cursor: pointer;

  strong,
  span {
    overflow-wrap: anywhere;
  }

  span {
    display: -webkit-box;
    overflow: hidden;
    color: var(--text-secondary);
    font-size: 13px;
    line-height: 1.5;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
  }

  &:hover {
    border-color: #d8b9a4;
    box-shadow: var(--shadow-soft);
  }
}

.card__thumb {
  position: relative;
  display: grid;
  height: 76px;
  place-items: center;
  border-radius: 7px;
  background:
    linear-gradient(135deg, rgb(251 240 223 / 82%), rgb(247 235 229 / 80%)),
    #f8fafc;
  background-position: center;
  background-size: cover;
  color: #fff;
  overflow: hidden;

  &::after {
    position: absolute;
    inset: 0;
    background: rgb(15 23 42 / 28%);
    content: '';
  }

  svg {
    position: relative;
    z-index: 1;
  }
}

.card em {
  margin-top: auto;
  color: var(--brand);
  font-size: 12px;
  font-style: normal;
  font-weight: 700;
}
</style>
