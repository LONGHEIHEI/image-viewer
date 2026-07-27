<template>
  <div class="grid" :style="gridStyle">
    <button
      v-for="folder in folders"
      :key="folder.path"
      type="button"
      class="card"
      @click="handleFolderClick(folder.path)"
    >
      <div
        :class="[
          'cover',
          {
            'cover--private': privacyEnabled && !isRevealed(`folder:${folder.path}`),
            'cover--ready': getThumbState(`folder:${folder.path}`) === 'ready',
            'cover--failed': getThumbState(`folder:${folder.path}`) === 'failed'
          }
        ]"
      >
        <div
          v-if="getThumbState(`folder:${folder.path}`) !== 'ready'"
          class="cover-placeholder"
          aria-hidden="true"
        >
          <svg class="cover-placeholder-icon" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <img
          v-if="folderThumb"
          :ref="(el) => setThumbImageRef(el, `folder:${folder.path}`)"
          :src="folderThumb(folder.path)"
          :alt="folder.name"
          loading="lazy"
          decoding="async"
          @load="onThumbLoad(`folder:${folder.path}`)"
          @error="onThumbError(`folder:${folder.path}`)"
        />
        <div class="cover-gradient"></div>
        <div class="cover-label">
          <div class="cover-name">{{ folder.name }}</div>
          <div class="cover-kind">目录</div>
        </div>
        <div v-if="privacyEnabled && !isRevealed(`folder:${folder.path}`)" class="privacy-mask"></div>
      </div>
    </button>
    <button
      v-for="archive in archives"
      :key="archive.path"
      type="button"
      class="card"
      @click="handleArchiveClick(archive.path)"
    >
      <div
        :class="[
          'cover',
          {
            'cover--private': privacyEnabled && !isRevealed(`archive:${archive.path}`),
            'cover--ready': getThumbState(`archive:${archive.path}`) === 'ready',
            'cover--failed': getThumbState(`archive:${archive.path}`) === 'failed'
          }
        ]"
      >
        <div
          v-if="getThumbState(`archive:${archive.path}`) !== 'ready'"
          class="cover-placeholder"
          aria-hidden="true"
        >
          <svg class="cover-placeholder-icon" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round">
            <path d="M21 8v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2z"/>
            <path d="M8 12h8M8 16h6"/>
          </svg>
        </div>
        <img
          v-if="archiveThumb"
          :ref="(el) => setThumbImageRef(el, `archive:${archive.path}`)"
          :src="archiveThumb(archive.path)"
          :alt="archive.name"
          loading="lazy"
          decoding="async"
          @load="onThumbLoad(`archive:${archive.path}`)"
          @error="onThumbError(`archive:${archive.path}`)"
        />
        <div class="cover-gradient"></div>
        <div class="cover-label">
          <div class="cover-name">{{ archive.name }}</div>
          <div class="cover-kind">压缩包</div>
        </div>
        <div v-if="privacyEnabled && !isRevealed(`archive:${archive.path}`)" class="privacy-mask"></div>
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
import type { FolderItem } from '../api/client'
import { computed, ref, watch } from 'vue'
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
const thumbStates = ref<Record<string, 'loading' | 'ready' | 'failed'>>({})
const gridStyle = computed(() => {
  const desktopMinWidth = Math.max(180, props.cardMinWidth ?? 240)
  const mobileMinWidth = Math.max(140, Math.min(desktopMinWidth, 160))
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

function getThumbState(key: string) {
  return thumbStates.value[key] ?? 'loading'
}

function updateThumbState(key: string, state: 'loading' | 'ready' | 'failed') {
  if (thumbStates.value[key] === state) return
  thumbStates.value = {
    ...thumbStates.value,
    [key]: state
  }
}

function syncThumbStates() {
  const nextStates: Record<string, 'loading' | 'ready' | 'failed'> = {}
  for (const folder of props.folders) {
    const key = `folder:${folder.path}`
    nextStates[key] = thumbStates.value[key] ?? 'loading'
  }
  for (const archive of props.archives) {
    const key = `archive:${archive.path}`
    nextStates[key] = thumbStates.value[key] ?? 'loading'
  }
  thumbStates.value = nextStates
}

function setThumbImageRef(element: Element | null, key: string) {
  if (!(element instanceof HTMLImageElement)) {
    return
  }
  if (!element.complete) {
    return
  }
  if (element.naturalWidth > 0 && element.naturalHeight > 0) {
    onThumbLoad(key)
    return
  }
  onThumbError(key)
}

function onThumbError(key: string) {
  updateThumbState(key, 'failed')
}

function onThumbLoad(key: string) {
  updateThumbState(key, 'ready')
}

watch(
  () => [props.folders, props.archives],
  () => {
    syncThumbStates()
  },
  { immediate: true }
)
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(var(--folder-card-min-width, 240px), 1fr));
  gap: 12px;
}

.card {
  appearance: none;
  width: 100%;
  padding: 0;
  cursor: pointer;
  border: none;
  background: none;
  text-align: left;
}

.cover {
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  background: var(--placeholder-surface);
  aspect-ratio: 3 / 2;
  border: 1px solid var(--stroke);
  box-shadow: var(--shadow-tiny);
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.card:hover .cover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-soft);
}

.cover-placeholder {
  position: absolute;
  inset: 0;
  z-index: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--placeholder-surface);
  opacity: 1;
  transition: opacity 0.25s ease;
}

.cover-placeholder-icon {
  color: rgba(92, 102, 114, 0.25);
}

.cover img {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  opacity: 0;
  transition: opacity 0.25s ease, filter 0.22s ease;
  will-change: opacity, filter;
}

.cover--ready img {
  opacity: 1;
}

.cover--ready .cover-placeholder,
.cover--failed .cover-placeholder {
  opacity: 0;
}

.cover--private img {
  filter: blur(22px) saturate(0.7);
}

.cover-gradient {
  position: absolute;
  inset: 0;
  z-index: 2;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0) 45%, rgba(0, 0, 0, 0.55) 100%);
  opacity: 1;
  pointer-events: none;
  transition: opacity 0.22s ease;
}

.cover--failed .cover-gradient {
  opacity: 0.3;
}

.cover-label {
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 12px;
  z-index: 3;
  display: flex;
  flex-direction: column;
  gap: 2px;
  pointer-events: none;
}

.cover-name {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.cover-kind {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.72);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.privacy-mask {
  position: absolute;
  inset: 0;
  z-index: 4;
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

@media (max-width: 960px) {
  .grid {
    grid-template-columns: repeat(auto-fill, minmax(var(--folder-card-mobile-min-width, 160px), 1fr));
    gap: 10px;
  }

  .cover {
    border-radius: 10px;
    aspect-ratio: 3 / 2;
  }

  .cover-label {
    left: 8px;
    right: 8px;
    bottom: 8px;
  }

  .cover-name {
    font-size: 12px;
  }

  .cover-kind {
    font-size: 10px;
  }
}

@media (max-width: 420px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
