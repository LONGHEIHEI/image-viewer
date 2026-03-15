<template>
  <div class="sidebar">
    <div class="header">
      <div>
        <div class="title">目录树</div>
        <div class="subtitle">文件夹与压缩包</div>
      </div>
      <button class="ghost" @click="$emit('refresh')">刷新</button>
    </div>

    <div v-if="loading" class="loading">正在加载目录...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="tree" class="tree">
      <TreeNode :node="tree" :level="0" @open-folder="$emit('open-folder', $event)" @open-archive="$emit('open-archive', $event)" />
    </div>
    <div v-else class="empty">目录为空。</div>
  </div>
</template>

<script setup lang="ts">
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
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--stroke);
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 12px 24px rgba(20, 25, 35, 0.08);
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

.subtitle {
  font-size: 12px;
  color: var(--muted);
}

.loading,
.error,
.empty {
  font-size: 12px;
  color: var(--muted);
}

.ghost {
  background: transparent;
  border: 1px solid var(--stroke);
  border-radius: 999px;
  padding: 4px 10px;
  cursor: pointer;
}
</style>
