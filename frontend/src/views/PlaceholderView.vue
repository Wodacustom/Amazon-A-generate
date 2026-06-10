<template>
  <section class="placeholder">
    <h2>{{ title }}</h2>
    <p>{{ description }}</p>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description: string
}>()
</script>

<style scoped lang="scss">
.placeholder {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  padding: 28px;

  h2 {
    margin-top: 0;
  }

  p {
    margin-bottom: 0;
    color: var(--text-secondary);
  }
}
</style>
