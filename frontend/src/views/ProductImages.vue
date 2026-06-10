<template>
  <div class="page placeholder-workspace">
    <div>
      <h2>商品套图</h2>
      <p class="muted">用于主图、场景图、细节图和模特图的批量生成入口。</p>
    </div>
    <RouterLink to="/tryon">
      <el-button type="primary">进入套图自动化</el-button>
    </RouterLink>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped lang="scss">
.placeholder-workspace {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 22px;
}
</style>
