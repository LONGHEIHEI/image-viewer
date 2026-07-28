
<template>
  <div ref="gridRef" class="masonry">
    <div v-for="(col, ci) in columns" :key="ci" class="masonry-col">
      <div
        v-for="image in col"
        :key="getImageKey(image)"
        class="tile"
        @click="handleTileClick(image)"
        @contextmenu.prevent="openMenu($event, image)"
      >
        <div
          :class="[
            'thumb',
            {
              'thumb--private': privacyEnabled && !isRevealed(getPrivacyKey(image)),
              'thumb--sized': hasImageSize(image),
              'thumb--ready': getImageState(getImageKey(image)) === 'ready',
              'thumb--failed': getImageState(getImageKey(image)) === 'failed'
            }
          ]"
          :style="getThumbStyle(image)"
          :data-title="image.name"
        >
          <div
            v-if="getImageState(getImageKey(image)) !== 'ready'"
            class="thumb-placeholder"
            aria-hidden="true"
          ></div>
          <img
            :src="thumb(image.path)"
            :alt="image.name"
            loading="lazy"
            decoding="async"
            @load="handleImageLoad(getImageKey(image))"
            @error="handleImageError(getImageKey(image))"
          />
          <button
            v-if="favoriteEnabled"
            type="button"
            :class="['favorite-toggle', { 'favorite-toggle--active': isFavorite?.(getImageActionPath(image)) }]"
            :aria-label="isFavorite?.(getImageActionPath(image)) ? '取消收藏' : '加入收藏'"
            @click.stop="handleFavoriteToggle(image)"
          >
            <svg
              viewBox="0 0 24 24"
              class="favorite-toggle__icon"
              aria-hidden="true"
            >
              <path
                d="M12 20.4l-1.1-.98C6.05 15.1 3 12.36 3 9.02C3 6.3 5.14 4.2 7.84 4.2c1.53 0 3 .72 3.96 1.85A5.07 5.07 0 0 1 15.76 4.2C18.46 4.2 20.6 6.3 20.6 9.02c0 3.34-3.05 6.08-7.9 10.4L12 20.4z"
              />
            </svg>
          </button>
          <div class="thumb-fallback">加载失败</div>
          <div v-if="privacyEnabled && !isRevealed(getPrivacyKey(image))" class="privacy-mask"></div>
        </div>
      </div>
    </div>
  </div>
  <n-dropdown
    trigger="manual"
    :show="menuVisible"
    :x="menuX"
    :y="menuY"
    :options="menuOptions"
    @clickoutside="menuVisible = false"
    @select="handleMenuSelect"
  />
  <n-modal v-model:show="propsVisible" preset="card" title="图片属性" style="width: 380px">
    <div class="props">
      <div class="props-item">
        <span class="props-label">标题</span>
        <span class="props-value">{{ selected?.name || '-' }}</span>
      </div>
      <div class="props-item">
        <span class="props-label">路径</span>
        <span class="props-value">{{ selected ? getDisplayPath(selected) : '-' }}</span>
      </div>
      <div class="props-item">
        <span class="props-label">格式</span>
        <span class="props-value">{{ fileExt(selected?.name) }}</span>
      </div>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { NDropdown, NModal } from 'naive-ui'
import type { FolderItem } from '../api/client'
import { usePrivacyReveal } from '../composables/usePrivacyReveal'

type SizedFolderItem = FolderItem & {
  width?: number
  height?: number
}

const props = defineProps<{
  images: FolderItem[]
  thumb: (path: string) => string
  privacyEnabled?: boolean
  privacyStorageKey?: string
  favoriteEnabled?: boolean
  isFavorite?: (path: string) => boolean
  toggleFavorite?: (path: string) => void | Promise<void>
}>()

const emit = defineEmits<{
  (event: 'open-image', path: string): void
}>()

const GAP = 8

const menuVisible = ref(false)
const menuX = ref(0)
const menuY = ref(0)
const selected = ref<FolderItem | null>(null)
const propsVisible = ref(false)
const columnCount = ref(getColumnCount())
const gridWidth = ref(estimateGridWidth())
const imageStates = ref<Record<string, 'loading' | 'ready' | 'failed'>>({})
const revealStorageKey = computed(() => props.privacyStorageKey || '')
const privacyEnabled = computed(() => Boolean(props.privacyEnabled))
const favoriteEnabled = computed(() => Boolean(props.favoriteEnabled && props.toggleFavorite && props.isFavorite))
const { isRevealed, reveal } = usePrivacyReveal(revealStorageKey)

const gridRef = ref<HTMLElement | null>(null)

const menuOptions = [{ label: '属性', key: 'props' }]

function estimateGridWidth() {
  if (typeof window === 'undefined') return 800
  // Mobile: no sidebar, subtract gutters only. Desktop: subtract sidebar ~280px.
  const mobile = window.innerWidth <= 960
  return Math.max(360, window.innerWidth - (mobile ? 32 : 280))
}

function getColumnCount() {
  if (typeof window === 'undefined') return 2
  if (window.innerWidth >= 1600) return 5
  if (window.innerWidth >= 1100) return 4
  if (window.innerWidth >= 720) return 3
  if (window.innerWidth < 360) return 1
  return 2
}

function getImageKey(image: FolderItem) {
  return image.favorite_key || image.path
}

function getImageActionPath(image: FolderItem) {
  return image.favorite_key || image.path
}

function getDisplayPath(image: FolderItem) {
  return image.display_path || image.path
}

function getPrivacyKey(image: FolderItem) {
  return `image:${getImageActionPath(image)}`
}

function hasImageSize(image: FolderItem): image is SizedFolderItem {
  const sizedImage = image as SizedFolderItem
  return (
    Number.isFinite(sizedImage.width) &&
    Number.isFinite(sizedImage.height) &&
    Number(sizedImage.width) > 0 &&
    Number(sizedImage.height) > 0
  )
}

function getThumbStyle(image: FolderItem) {
  if (!hasImageSize(image)) return undefined
  return {
    aspectRatio: `${image.width} / ${image.height}`
  }
}

function getImageState(path: string) {
  return imageStates.value[path] ?? 'loading'
}

function updateImageState(path: string, state: 'loading' | 'ready' | 'failed') {
  if (imageStates.value[path] === state) return
  imageStates.value = {
    ...imageStates.value,
    [path]: state
  }
}

function syncImageStates(images: FolderItem[]) {
  const nextStates: Record<string, 'loading' | 'ready' | 'failed'> = {}
  for (const image of images) {
    nextStates[getImageKey(image)] = imageStates.value[getImageKey(image)] ?? 'loading'
  }
  imageStates.value = nextStates
}

function syncColumnCount() {
  columnCount.value = getColumnCount()
  // Re-estimate width when column count changes (might mean viewport changed)
  if (gridRef.value) {
    gridWidth.value = gridRef.value.clientWidth
  } else {
    gridWidth.value = estimateGridWidth()
  }
}

function handleImageLoad(path: string) {
  updateImageState(path, 'ready')
}

function handleImageError(path: string) {
  updateImageState(path, 'failed')
}

function handleTileClick(image: FolderItem) {
  const actionPath = getImageActionPath(image)
  if (privacyEnabled.value && !isRevealed(getPrivacyKey(image))) {
    reveal(getPrivacyKey(image))
    return
  }
  emit('open-image', actionPath)
}

async function handleFavoriteToggle(image: FolderItem) {
  if (!favoriteEnabled.value || !props.toggleFavorite) return
  await props.toggleFavorite(getImageActionPath(image))
}

const colWidth = computed(() => {
  const cols = columnCount.value
  if (cols <= 1) return gridWidth.value || 300
  return (gridWidth.value - GAP * (cols - 1)) / cols
})

function estimateHeight(image: FolderItem): number {
  if (hasImageSize(image)) {
    return colWidth.value / (image.width! / image.height!)
  }
  return colWidth.value * 0.75
}

// Round-robin distribution: image i goes to column i % cols.
// Preserves natural left→right, top→bottom reading order.
const columns = computed(() => {
  const images = props.images
  const cols = columnCount.value
  if (!images.length) return []
  if (cols <= 1) return [images]

  const result: FolderItem[][] = Array.from({ length: cols }, () => [])

  for (let i = 0; i < images.length; i++) {
    result[i % cols].push(images[i])
  }

  return result
})

watch(
  () => props.images,
  (images) => {
    syncImageStates(images)
  },
  { immediate: true }
)

let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  syncColumnCount()
  if (gridRef.value) {
    gridWidth.value = gridRef.value.clientWidth
    resizeObserver = new ResizeObserver(() => {
      if (gridRef.value) gridWidth.value = gridRef.value.clientWidth
    })
    resizeObserver.observe(gridRef.value)
  }
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', syncColumnCount)
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', syncColumnCount)
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
})

function openMenu(event: MouseEvent, image: FolderItem) {
  selected.value = image
  menuVisible.value = false
  menuX.value = event.clientX
  menuY.value = event.clientY
  window.setTimeout(() => {
    menuVisible.value = true
  }, 0)
}

function handleMenuSelect(key: string | number) {
  menuVisible.value = false
  if (key === 'props') {
    propsVisible.value = true
  }
}

function fileExt(name?: string) {
  if (!name) return '-'
  const parts = name.split('.')
  if (parts.length < 2) return '-'
  return parts[parts.length - 1].toUpperCase()
}
</script>

<style scoped>
.masonry {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  width: 100%;
  overflow: hidden;
}

.masonry-col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tile {
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--stroke);
  background: var(--panel);
  box-shadow: var(--shadow-tiny);
  backdrop-filter: blur(14px);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  content-visibility: auto;
  contain-intrinsic-size: 220px 160px;
}

.tile:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-soft);
}

.thumb {
  position: relative;
  overflow: hidden;
  min-height: 160px;
  background: var(--placeholder-surface);
}

.thumb--sized {
  min-height: 0;
}

.thumb-placeholder {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: var(--placeholder-surface);
  opacity: 1;
  transition: opacity 0.2s ease;
}

.thumb img {
  position: relative;
  z-index: 1;
  width: 100%;
  display: block;
  opacity: 0;
  transition: opacity 0.2s ease, filter 0.18s ease;
  will-change: opacity, filter;
}

.thumb--ready img {
  opacity: 1;
}

.thumb--ready .thumb-placeholder,
.thumb--failed .thumb-placeholder {
  opacity: 0;
}

.thumb--private img {
  filter: blur(22px) saturate(0.72);
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
  background: rgba(20, 25, 35, 0.28);
  backdrop-filter: blur(10px);
}

.favorite-toggle {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 3;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: none;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.22);
  color: rgba(255, 255, 255, 0.92);
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease;
}

.favorite-toggle:hover {
  background: rgba(0, 0, 0, 0.36);
}

.favorite-toggle__icon {
  position: relative;
  z-index: 1;
  width: 14px;
  height: 14px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.favorite-toggle--active {
  background: rgba(194, 101, 75, 0.9);
  color: #fff;
}

.favorite-toggle--active .favorite-toggle__icon {
  fill: currentColor;
  stroke: none;
}

.thumb::after {
  content: attr(data-title);
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 8px 10px;
  font-size: 12px;
  color: #fff;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.65) 100%);
  opacity: 0;
  transition: opacity 0.18s ease;
  pointer-events: none;
}

.tile:hover .thumb--ready::after {
  opacity: 1;
}

.thumb-fallback {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: grid;
  place-items: center;
  padding: 12px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  opacity: 0;
}

.thumb--failed .thumb-fallback {
  opacity: 1;
}

.thumb--failed img {
  opacity: 0;
}

.props {
  display: grid;
  gap: 10px;
}

.props-item {
  display: grid;
  gap: 4px;
}

.props-label {
  font-size: 12px;
  color: var(--muted);
}

.props-value {
  font-size: 13px;
  color: var(--ink);
  word-break: break-all;
}

@media (max-width: 960px) {
  .masonry {
    gap: 8px;
  }

  .masonry-col {
    gap: 8px;
  }

  .tile {
    border-radius: 10px;
  }

  .favorite-toggle {
    top: 6px;
    right: 6px;
    width: 26px;
    height: 26px;
  }

  .favorite-toggle__icon {
    width: 13px;
    height: 13px;
  }
}
</style>
