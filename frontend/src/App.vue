<template>
  <AppLayout />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import AppLayout from '@/components/layout/AppLayout.vue'
import { useUserStore } from '@/stores/user'

const user = useUserStore()

onMounted(() => {
  user.restoreSession()
})
</script>
