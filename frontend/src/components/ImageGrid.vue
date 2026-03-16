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
        @click="$emit('open-image', image.path)"
        @contextmenu.prevent="openMenu($event, image)"
      >
        <div class="thumb" :data-title="image.name">
          <img :src="thumb(image.path)" :alt="image.name" loading="lazy" @load="handleImageLoad($event, image.path)" />
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
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { NDropdown, NModal } from 'naive-ui'
import type { FolderItem } from '../api/client'

const props = defineProps<{ images: FolderItem[]; thumb: (path: string) => string }>()

const menuVisible = ref(false)
const menuX = ref(0)
const menuY = ref(0)
const selected = ref<FolderItem | null>(null)
const propsVisible = ref(false)
const columnCount = ref(2)
const masonryColumns = ref<FolderItem[][]>([])
const columnRefs = ref<HTMLElement[]>([])
const imageHeights = ref<Record<string, number>>({})

const menuOptions = [{ label: '属性', key: 'props' }]

function getColumnCount() {
  if (typeof window === 'undefined') return 2
  if (window.innerWidth >= 1100) return 4
  if (window.innerWidth >= 700) return 3
  return 2
}

function getAverageImageHeight() {
  const heights = Object.values(imageHeights.value)
  if (!heights.length) return 220
  return heights.reduce((sum, value) => sum + value, 0) / heights.length
}

function estimateImageHeight(image: FolderItem) {
  return imageHeights.value[image.path] ?? getAverageImageHeight()
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

function syncColumnCount() {
  const nextCount = getColumnCount()
  if (nextCount === columnCount.value) return
  columnCount.value = nextCount
}

function handleImageLoad(event: Event, path: string) {
  const image = event.target as HTMLImageElement | null
  if (!image) return
  const renderedWidth = image.clientWidth || image.naturalWidth || 1
  const renderedHeight =
    image.clientHeight ||
    (image.naturalWidth ? renderedWidth * (image.naturalHeight / image.naturalWidth) : renderedWidth)
  imageHeights.value = {
    ...imageHeights.value,
    [path]: renderedHeight
  }
}

watch(
  () => props.images,
  async (images) => {
    const previous = masonryColumns.value.flat()
    const isAppend =
      previous.length > 0 &&
      images.length > previous.length &&
      previous.every((item, index) => item.path === images[index]?.path)

    if (isAppend) {
      const appended = images.slice(previous.length)
      if (appended.length) {
        await nextTick()
        const initialHeights = readColumnHeights()
        const appendedColumns = distributeImages(appended, initialHeights)
        masonryColumns.value = masonryColumns.value.map((column, index) => [...column, ...appendedColumns[index]])
      }
      return
    }

    masonryColumns.value = images.length ? distributeImages(images) : []
  },
  { immediate: true }
)

watch(
  columnCount,
  () => {
    masonryColumns.value = props.images.length ? distributeImages(props.images) : []
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
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 6px 16px rgba(20, 25, 35, 0.04);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.tile:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 22px rgba(20, 25, 35, 0.08);
}

.thumb {
  position: relative;
  overflow: hidden;
}

.thumb img {
  width: 100%;
  display: block;
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

.tile:hover .thumb::after {
  opacity: 1;
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
</style>
