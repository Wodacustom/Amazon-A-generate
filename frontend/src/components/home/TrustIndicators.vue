<template>
  <section class="trust">
    <div v-for="item in items" :key="item.label" class="trust__item">
      <component :is="item.icon" :size="18" />
      <span>{{ item.label }}</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { BadgeCheck, ShieldCheck, Zap } from 'lucide-vue-next'

const items = [
  { label: '数据安全', icon: ShieldCheck },
  { label: '秒级生成', icon: Zap },
  { label: '专业设计标准', icon: BadgeCheck },
]
</script>

<style scoped lang="scss">
.trust {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}

.trust__item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

@media (max-width: 760px) {
  .trust {
    justify-content: flex-start;
  }
}
</style>
