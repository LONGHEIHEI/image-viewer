<template>
  <n-card class="panel sidebar" :bordered="false">
    <div class="header">
      <div class="title">目录树</div>
      <n-button size="small" @click="$emit('refresh')">刷新</n-button>
    </div>

    <div v-if="loading" class="loading">正在加载目录...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="tree" class="tree">
      <TreeNode
        :node="tree"
        :level="0"
        @open-folder="$emit('open-folder', $event)"
        @open-archive="$emit('open-archive', $event)"
      />
    </div>
    <div v-else class="empty">目录为空。</div>
  </n-card>
</template>

<script setup lang="ts">
import { NCard, NButton } from 'naive-ui'
import type { TreeNode as TreeNodeType } from '../api/client'
import TreeNode from './TreeNode.vue'

defineProps<{ tree: TreeNodeType | null; loading: boolean; error: string }>()

defineEmits<{
  (e: 'open-folder', path: string): void
  (e: 'open-archive', path: string): void
  (e: 'refresh'): void
}>()
</script>

<style scoped>
.sidebar {
  max-height: calc(100vh - 220px);
  overflow: auto;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 10px;
}

.title {
  font-size: 16px;
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-weight: 700;
}

.loading,
.error,
.empty {
  font-size: 12px;
  color: var(--muted);
}
</style>
