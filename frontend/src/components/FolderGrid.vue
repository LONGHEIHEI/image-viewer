<template>
  <div class="grid" :style="gridStyle">
    <button
      v-for="folder in folders"
      :key="folder.path"
      type="button"
      class="card folder-card"
      @click="handleFolderClick(folder.path)"
    >
      <div :class="['thumb', { 'thumb--private': privacyEnabled && !isRevealed(`folder:${folder.path}`) }]" v-if="folderThumb">
        <img
          :src="folderThumb(folder.path)"
          :alt="folder.name"
          loading="lazy"
          @error="onThumbError"
        />
        <div class="thumb-fallback">目录</div>
        <div v-if="privacyEnabled && !isRevealed(`folder:${folder.path}`)" class="privacy-mask"></div>
      </div>
      <div class="icon" v-else>目录</div>
      <div class="label-area">
        <div class="label">{{ folder.name }}</div>
      </div>
    </button>
    <button
      v-for="archive in archives"
      :key="archive.path"
      type="button"
      class="card folder-card"
      @click="handleArchiveClick(archive.path)"
    >
      <div :class="['thumb', { 'thumb--private': privacyEnabled && !isRevealed(`archive:${archive.path}`) }]" v-if="archiveThumb">
        <img
          :src="archiveThumb(archive.path)"
          :alt="archive.name"
          loading="lazy"
          @error="onThumbError"
        />
        <div class="thumb-fallback">压缩包</div>
        <div v-if="privacyEnabled && !isRevealed(`archive:${archive.path}`)" class="privacy-mask"></div>
      </div>
      <div class="icon" v-else>压缩包</div>
      <div class="label-area">
        <div class="label">{{ archive.name }}</div>
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
import type { FolderItem } from '../api/client'
import { computed } from 'vue'
import { usePrivacyReveal } from '../composables/usePrivacyReveal'

const props = defineProps<{
  folders: FolderItem[]
  archives: FolderItem[]
  folderThumb?: (path: string) => string
  archiveThumb?: (path: string) => string
  privacyEnabled?: boolean
  privacyStorageKey?: string
  cardMinWidth?: number
}>()

const emit = defineEmits<{
  (event: 'open-folder', path: string): void
  (event: 'open-archive', path: string): void
}>()

const revealStorageKey = computed(() => props.privacyStorageKey || '')
const privacyEnabled = computed(() => Boolean(props.privacyEnabled))
const { isRevealed, reveal } = usePrivacyReveal(revealStorageKey)
const gridStyle = computed(() => {
  const desktopMinWidth = Math.max(160, props.cardMinWidth ?? 210)
  const mobileMinWidth = Math.max(148, Math.min(desktopMinWidth, 176))
  return {
    '--folder-card-min-width': `${desktopMinWidth}px`,
    '--folder-card-mobile-min-width': `${mobileMinWidth}px`
  }
})

function handleFolderClick(path: string) {
  if (privacyEnabled.value && !isRevealed(`folder:${path}`)) {
    reveal(`folder:${path}`)
    return
  }
  emit('open-folder', path)
}

function handleArchiveClick(path: string) {
  if (privacyEnabled.value && !isRevealed(`archive:${path}`)) {
    reveal(`archive:${path}`)
    return
  }
  emit('open-archive', path)
}

function onThumbError(event: Event) {
  const target = event.target as HTMLImageElement | null
  if (!target) return
  target.classList.add('hidden')
}
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(var(--folder-card-min-width, 210px), 1fr));
  gap: 14px;
}

.card {
  appearance: none;
  width: 100%;
  padding: 0;
  cursor: pointer;
  border-radius: 16px;
  border: 1px solid var(--stroke);
  background: var(--panel);
  box-shadow: var(--shadow-tiny);
  backdrop-filter: blur(14px);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  text-align: left;
  content-visibility: auto;
  contain-intrinsic-size: 240px 210px;
}

.folder-card {
  overflow: hidden;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-soft);
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

.thumb--private img {
  filter: blur(22px) saturate(0.7);
  transform: scale(1.04);
}

.privacy-mask {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background: rgba(20, 25, 35, 0.26);
  backdrop-filter: blur(10px);
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

@media (max-width: 960px) {
  .grid {
    grid-template-columns: repeat(auto-fill, minmax(var(--folder-card-mobile-min-width, 160px), 1fr));
    gap: 10px;
  }

  .card {
    border-radius: 14px;
  }

  .label-area {
    padding: 10px 12px 12px;
  }
}

@media (max-width: 420px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
