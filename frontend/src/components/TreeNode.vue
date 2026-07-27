<template>
  <div>
    <div class="node" :style="{ paddingLeft: `${level * 12}px` }" @click="handleClick">
      <span class="tag" :class="node.type">{{ typeLabel }}</span>
      <span class="name">{{ displayName }}</span>
    </div>
    <TreeNode
      v-for="child in node.children || []"
      :key="child.path"
      :node="child"
      :level="level + 1"
      @open-folder="$emit('open-folder', $event)"
      @open-archive="$emit('open-archive', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TreeNode as TreeNodeType } from '../api/client'

const props = defineProps<{ node: TreeNodeType; level: number }>()
const emit = defineEmits<{
  (e: 'open-folder', path: string): void
  (e: 'open-archive', path: string): void
}>()

const displayName = computed(() => props.node.name || '')
const typeLabel = computed(() => (props.node.type === 'archive' ? '压缩包' : '目录'))

function handleClick() {
  if (props.node.type === 'archive') {
    emit('open-archive', props.node.path)
  } else {
    emit('open-folder', props.node.path)
  }
}
</script>

<style scoped>
.node {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 6px;
  border-radius: 8px;
  cursor: pointer;
}

.node:hover {
  background: rgba(27, 30, 39, 0.06);
}

.tag {
  text-transform: uppercase;
  font-size: 10px;
  letter-spacing: 0.08em;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 999px;
}

.tag.folder {
  background: rgba(47, 143, 124, 0.12);
  color: var(--accent-2);
}

.tag.archive {
  background: rgba(194, 101, 75, 0.12);
  color: var(--accent);
}

.name {
  font-size: 13px;
  color: var(--ink);
  word-break: break-all;
}
</style>
