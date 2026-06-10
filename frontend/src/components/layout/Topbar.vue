<template>
  <header class="topbar">
    <div class="topbar__links">
      <el-button text>灵感库</el-button>
      <el-button text>样机中心</el-button>
      <el-button text>使用指南</el-button>
    </div>
    <div class="topbar__actions">
      <CreditBadge />
      <el-button :icon="Bell" circle aria-label="通知" />
      <UserMenu />
    </div>
  </header>
</template>

<script setup lang="ts">
import { Bell } from 'lucide-vue-next'

import CreditBadge from './CreditBadge.vue'
import UserMenu from './UserMenu.vue'
</script>

<style scoped lang="scss">
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid var(--line);
  background: rgb(255 253 250 / 92%);
  padding: 12px 24px;
  backdrop-filter: blur(10px);
}

.topbar__links,
.topbar__actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

@media (max-width: 760px) {
  .topbar {
    padding: 10px 16px;
  }

  .topbar__links {
    display: none;
  }
}
</style>
