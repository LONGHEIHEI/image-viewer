<template>
  <div v-if="segments.length" class="crumbs" :class="{ compact }">
    <span
      v-if="segments.length && rootText"
      class="crumb"
      @click="$emit('navigate', '')"
    >
      {{ rootText }}
    </span>
    <span
      v-for="(seg, idx) in segments"
      :key="idx"
      class="crumb"
      @click="$emit('navigate', segmentPath(idx))"
    >
      / {{ seg }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ path: string; rootLabel?: string; compact?: boolean }>()

const segments = computed(() =>
  props.path ? props.path.split(/[\\/]+/).filter(Boolean) : []
)

const rootText = computed(() => props.rootLabel || '')
const compact = computed(() => Boolean(props.compact))

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

.crumbs.compact {
  margin-bottom: 0;
}

.crumb {
  cursor: pointer;
  font-weight: 600;
}

.crumb:hover {
  color: var(--ink);
}
</style>
