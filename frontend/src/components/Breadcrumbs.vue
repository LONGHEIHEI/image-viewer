<template>
  <div class="crumbs">
    <span class="crumb" @click="$emit('navigate', '')">根目录</span>
    <span v-for="(seg, idx) in segments" :key="idx" class="crumb" @click="$emit('navigate', segmentPath(idx))">
      / {{ seg }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ path: string }>()

const segments = computed(() =>
  props.path ? props.path.split(/[\\/]+/).filter(Boolean) : []
)

function segmentPath(index: number) {
  return segments.value.slice(0, index + 1).join('/')
}
</script>

<style scoped>
.crumbs {
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--muted);
}

.crumb {
  cursor: pointer;
  font-weight: 600;
}

.crumb:hover {
  color: var(--ink);
}
</style>
