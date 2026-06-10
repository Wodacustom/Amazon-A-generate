<template>
  <button class="credit" type="button" @click="refresh">
    <Coins :size="16" />
    <span>{{ user.profile.credits }} 积分</span>
  </button>
</template>

<script setup lang="ts">
import { Coins } from 'lucide-vue-next'

import { useUserStore } from '@/stores/user'

const user = useUserStore()

async function refresh() {
  await user.refreshCredits()
}
</script>

<style scoped lang="scss">
.credit {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #fed7aa;
  border-radius: 999px;
  background: #fff7ed;
  color: var(--brand-dark);
  padding: 7px 10px;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
}
</style>
