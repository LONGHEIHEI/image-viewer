<template>
  <div class="grid">
    <n-card
      v-for="folder in folders"
      :key="folder.path"
      class="card folder-card"
      :bordered="false"
      :content-style="{ padding: 0 }"
      @click="$emit('open-folder', folder.path)"
    >
      <div class="thumb" v-if="folderThumb">
        <img
          :src="folderThumb(folder.path)"
          :alt="folder.name"
          loading="lazy"
          @error="onThumbError"
        />
        <div class="thumb-fallback">目录</div>
      </div>
      <div class="icon" v-else>目录</div>
      <div class="label-area">
        <div class="label">{{ folder.name }}</div>
      </div>
    </n-card>
    <n-card
      v-for="archive in archives"
      :key="archive.path"
      class="card folder-card"
      :bordered="false"
      :content-style="{ padding: 0 }"
      @click="$emit('open-archive', archive.path)"
    >
      <div class="thumb" v-if="archiveThumb">
        <img
          :src="archiveThumb(archive.path)"
          :alt="archive.name"
          loading="lazy"
          @error="onThumbError"
        />
        <div class="thumb-fallback">压缩包</div>
      </div>
      <div class="icon" v-else>压缩包</div>
      <div class="label-area">
        <div class="label">{{ archive.name }}</div>
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { NCard } from 'naive-ui'
import type { FolderItem } from '../api/client'

defineProps<{
  folders: FolderItem[]
  archives: FolderItem[]
  folderThumb?: (path: string) => string
  archiveThumb?: (path: string) => string
}>()

function onThumbError(event: Event) {
  const target = event.target as HTMLImageElement | null
  if (!target) return
  target.classList.add('hidden')
}
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 14px;
}

.card {
  cursor: pointer;
  border-radius: 16px;
  border: 1px solid var(--stroke);
  box-shadow: var(--shadow-soft);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.folder-card {
  overflow: hidden;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 26px rgba(20, 25, 35, 0.12);
}

.icon {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent-2);
  font-weight: 700;
}

.thumb {
  position: relative;
  overflow: hidden;
  background: #f0f2f4;
  aspect-ratio: 4 / 3;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.thumb img.hidden {
  display: none;
}

.thumb-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent-2);
  font-weight: 700;
}

.thumb img:not(.hidden) ~ .thumb-fallback {
  opacity: 0;
}

.label-area {
  padding: 12px 14px 14px;
  min-width: 0;
}

.label {
  font-weight: 700;
  font-family: 'Space Grotesk', Arial, sans-serif;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
