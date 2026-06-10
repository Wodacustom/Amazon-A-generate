<template>
  <div class="app-shell">
    <AppSidebar />
    <div class="app-shell__body">
      <Topbar />
      <main class="app-shell__content">
        <RouterView />
      </main>
    </div>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'

import AppSidebar from './AppSidebar.vue'
import MobileNav from './MobileNav.vue'
import Topbar from './Topbar.vue'
</script>

<style scoped lang="scss">
.app-shell {
  display: grid;
  min-height: 100vh;
  grid-template-columns: 252px minmax(0, 1fr);
}

.app-shell__body {
  min-width: 0;
}

.app-shell__content {
  min-width: 0;
  padding: 24px;
}

@media (max-width: 760px) {
  .app-shell {
    display: block;
    padding-bottom: 68px;
  }

  .app-shell__content {
    padding: 16px;
  }
}
</style>
