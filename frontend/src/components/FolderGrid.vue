<template>
  <div class="grid">
    <div v-for="folder in folders" :key="folder.path" class="card" @click="$emit('open-folder', folder.path)">
      <div class="icon">目录</div>
      <div class="label">{{ folder.name }}</div>
      <div class="meta">浏览文件夹</div>
    </div>
    <div v-for="archive in archives" :key="archive.path" class="card" @click="$emit('open-archive', archive.path)">
      <div class="icon">压缩包</div>
      <div class="label">{{ archive.name }}</div>
      <div class="meta">打开压缩包</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FolderItem } from '../api/client'

defineProps<{ folders: FolderItem[]; archives: FolderItem[] }>()
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 14px;
}

.card {
  background: var(--panel);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid var(--stroke);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  box-shadow: 0 10px 18px rgba(20, 25, 35, 0.08);
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 26px rgba(20, 25, 35, 0.16);
}

.icon {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent-2);
  font-weight: 700;
}

.label {
  margin-top: 10px;
  font-weight: 700;
  font-family: 'Space Grotesk', Arial, sans-serif;
}

.meta {
  margin-top: 6px;
  font-size: 12px;
  color: var(--muted);
}
</style>
