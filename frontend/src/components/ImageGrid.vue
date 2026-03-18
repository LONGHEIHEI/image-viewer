<template>
  <div class="masonry-grid" :style="{ '--masonry-columns': String(columnCount) }">
    <div
      v-for="(column, columnIndex) in masonryColumns"
      :key="`column-${columnIndex}`"
      :ref="(el) => setColumnRef(el, columnIndex)"
      class="masonry-column"
    >
      <div
        v-for="image in column"
        :key="image.path"
        class="tile"
        @click="handleTileClick(image.path)"
        @contextmenu.prevent="openMenu($event, image)"
      >
        <div
          :class="[
            'thumb',
            {
              'thumb--private': privacyEnabled && !isRevealed(`image:${image.path}`),
              'thumb--sized': hasImageSize(image),
              'thumb--ready': getImageState(image.path) === 'ready',
              'thumb--failed': getImageState(image.path) === 'failed'
            }
          ]"
          :style="getThumbStyle(image)"
          :data-title="image.name"
        >
          <div v-if="getImageState(image.path) !== 'ready'" class="thumb-placeholder" aria-hidden="true"></div>
          <img
            :src="thumb(image.path)"
            :alt="image.name"
            loading="lazy"
            decoding="async"
            @load="handleImageLoad($event, image.path)"
            @error="handleImageError(image.path)"
          />
          <div class="thumb-fallback">加载失败</div>
          <div v-if="privacyEnabled && !isRevealed(`image:${image.path}`)" class="privacy-mask"></div>
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
        <span class="props-value">{{ selected?.path || '-' }}</span>
      </div>
      <div class="props-item">
        <span class="props-label">格式</span>
        <span class="props-value">{{ fileExt(selected?.name) }}</span>
      </div>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
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
}>()

const emit = defineEmits<{
  (event: 'open-image', path: string): void
}>()

const menuVisible = ref(false)
const menuX = ref(0)
const menuY = ref(0)
const selected = ref<FolderItem | null>(null)
const propsVisible = ref(false)
const columnCount = ref(2)
const masonryColumns = ref<FolderItem[][]>([])
const columnRefs = ref<HTMLElement[]>([])
// Height sampling is only used for future distribution estimates; it doesn't need to be reactive.
const imageHeights = new Map<string, number>()
const imageStates = ref<Record<string, 'loading' | 'ready' | 'failed'>>({})
let heightSum = 0
let heightCount = 0
const revealStorageKey = computed(() => props.privacyStorageKey || '')
const privacyEnabled = computed(() => Boolean(props.privacyEnabled))
const { isRevealed, reveal } = usePrivacyReveal(revealStorageKey)

const menuOptions = [{ label: '属性', key: 'props' }]
let renderedFirstPath = ''
let renderedLastPath = ''
let renderedCount = 0

function getColumnCount() {
  if (typeof window === 'undefined') return 2
  if (window.innerWidth >= 1280) return 4
  if (window.innerWidth >= 860) return 3
  if (window.innerWidth < 360) return 1
  return 2
}

function getAverageImageHeight() {
  if (!heightCount) return 220
  return heightSum / heightCount
}

function estimateImageHeight(image: FolderItem) {
  const sampledHeight = imageHeights.get(image.path)
  if (sampledHeight !== undefined) return sampledHeight
  if (hasImageSize(image)) {
    return 220 * (image.height / image.width)
  }
  return getAverageImageHeight()
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

function readColumnHeights() {
  return Array.from({ length: columnCount.value }, (_, index) => columnRefs.value[index]?.offsetHeight ?? 0)
}

function findShortestColumn(heights: number[]) {
  let target = 0
  for (let index = 1; index < heights.length; index += 1) {
    if (heights[index] < heights[target]) {
      target = index
    }
  }
  return target
}

function distributeImages(images: FolderItem[], initialHeights?: number[]) {
  const columns = Array.from({ length: columnCount.value }, () => [] as FolderItem[])
  const heights = initialHeights ? [...initialHeights] : Array.from({ length: columnCount.value }, () => 0)

  for (const image of images) {
    const target = findShortestColumn(heights)
    columns[target].push(image)
    heights[target] += estimateImageHeight(image) + 10
  }

  return columns
}

function setColumnRef(element: Element | null, index: number) {
  if (element instanceof HTMLElement) {
    columnRefs.value[index] = element
    return
  }
  columnRefs.value.splice(index, 1)
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
    nextStates[image.path] = imageStates.value[image.path] ?? 'loading'
  }
  imageStates.value = nextStates
}

function syncColumnCount() {
  const nextCount = getColumnCount()
  if (nextCount === columnCount.value) return
  columnCount.value = nextCount
}

function handleImageLoad(event: Event, path: string) {
  const image = event.target as HTMLImageElement | null
  if (!image) return
  updateImageState(path, 'ready')
  const renderedWidth = image.clientWidth || image.naturalWidth || 1
  const renderedHeight =
    image.clientHeight ||
    (image.naturalWidth ? renderedWidth * (image.naturalHeight / image.naturalWidth) : renderedWidth)
  const previous = imageHeights.get(path)
  if (previous !== undefined) {
    heightSum -= previous
  } else {
    heightCount += 1
  }
  imageHeights.set(path, renderedHeight)
  heightSum += renderedHeight
}

function handleImageError(path: string) {
  updateImageState(path, 'failed')
}

function handleTileClick(path: string) {
  if (privacyEnabled.value && !isRevealed(`image:${path}`)) {
    reveal(`image:${path}`)
    return
  }
  emit('open-image', path)
}

watch(
  () => props.images,
  async (images) => {
    syncImageStates(images)
    const isAppend =
      renderedCount > 0 &&
      images.length > renderedCount &&
      images[0]?.path === renderedFirstPath &&
      images[renderedCount - 1]?.path === renderedLastPath

    if (isAppend) {
      const appended = images.slice(renderedCount)
      if (appended.length) {
        await nextTick()
        const initialHeights = readColumnHeights()
        const appendedColumns = distributeImages(appended, initialHeights)
        masonryColumns.value = masonryColumns.value.map((column, index) => [...column, ...appendedColumns[index]])
      }
      renderedCount = images.length
      renderedLastPath = images[images.length - 1]?.path ?? renderedLastPath
      return
    }

    masonryColumns.value = images.length ? distributeImages(images) : []
    renderedCount = images.length
    renderedFirstPath = images[0]?.path ?? ''
    renderedLastPath = images[images.length - 1]?.path ?? ''
  },
  { immediate: true }
)

watch(
  columnCount,
  () => {
    masonryColumns.value = props.images.length ? distributeImages(props.images) : []
    renderedCount = props.images.length
    renderedFirstPath = props.images[0]?.path ?? ''
    renderedLastPath = props.images[props.images.length - 1]?.path ?? ''
  }
)

onMounted(() => {
  syncColumnCount()
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', syncColumnCount)
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', syncColumnCount)
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
.masonry-grid {
  --masonry-columns: 2;
  display: grid;
  grid-template-columns: repeat(var(--masonry-columns), minmax(0, 1fr));
  gap: 10px;
  align-items: start;
}

.masonry-column {
  display: grid;
  gap: 10px;
  align-content: start;
  min-width: 0;
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
  transition: opacity 0.2s ease;
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
  transform: scale(1.05);
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
  .masonry-grid,
  .masonry-column {
    gap: 8px;
  }

  .tile {
    border-radius: 10px;
  }
}
</style>
