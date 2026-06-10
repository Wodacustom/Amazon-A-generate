<template>
  <nav class="mobile-nav">
    <RouterLink v-for="item in items" :key="item.to" :to="item.to">
      <component :is="item.icon" :size="18" />
      <span>{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { Brush, Clock3, Home, WandSparkles } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

const items = [
  { to: '/', label: '首页', icon: Home },
  { to: '/aplus-detail', label: '生成', icon: WandSparkles },
  { to: '/style-memory', label: '风格', icon: Brush },
  { to: '/tasks', label: '历史', icon: Clock3 },
]
</script>

<style scoped lang="scss">
.mobile-nav {
  position: fixed;
  z-index: 20;
  right: 0;
  bottom: 0;
  left: 0;
  display: none;
  grid-template-columns: repeat(4, 1fr);
  border-top: 1px solid var(--line);
  background: #fff;

  a {
    display: grid;
    justify-items: center;
    gap: 4px;
    padding: 9px 4px;
    color: var(--text-secondary);
    font-size: 12px;
  }

  .router-link-active {
    color: var(--brand-dark);
    font-weight: 700;
  }
}

@media (max-width: 760px) {
  .mobile-nav {
    display: grid;
  }
}
</style>
