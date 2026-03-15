<template>
  <div class="viewer">
    <div
      ref="stageRef"
      class="stage"
      :class="{ dragging }"
      @wheel.prevent="onWheel"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointerleave="onPointerUp"
      @dblclick="resetView"
    >
      <img :src="src" :alt="name" :style="imgStyle" />
    </div>
    <div class="caption">{{ name }}</div>
    <div class="hints">滚轮缩放，拖拽平移，双击重置</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps<{ src: string; name: string }>()
const emit = defineEmits<{
  (e: 'scale-change', value: number): void
  (e: 'fullscreen-change', value: boolean): void
}>()

const stageRef = ref<HTMLElement | null>(null)
const scale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
const dragging = ref(false)
const isFullscreen = ref(false)

const imgStyle = computed(() => ({
  transform: `translate(${offsetX.value}px, ${offsetY.value}px) scale(${scale.value})`
}))

let startX = 0
let startY = 0
let startOffsetX = 0
let startOffsetY = 0

function clamp(val: number, min: number, max: number) {
  return Math.min(Math.max(val, min), max)
}

function resetView() {
  scale.value = 1
  offsetX.value = 0
  offsetY.value = 0
}

function onWheel(event: WheelEvent) {
  const delta = event.deltaY > 0 ? -0.08 : 0.08
  scale.value = clamp(Number((scale.value + delta).toFixed(2)), 0.5, 4)
}

function onPointerDown(event: PointerEvent) {
  dragging.value = true
  startX = event.clientX
  startY = event.clientY
  startOffsetX = offsetX.value
  startOffsetY = offsetY.value
  const target = event.currentTarget as HTMLElement
  target.setPointerCapture(event.pointerId)
}

function onPointerMove(event: PointerEvent) {
  if (!dragging.value) return
  offsetX.value = startOffsetX + (event.clientX - startX)
  offsetY.value = startOffsetY + (event.clientY - startY)
}

function onPointerUp(event: PointerEvent) {
  if (!dragging.value) return
  dragging.value = false
  const target = event.currentTarget as HTMLElement
  target.releasePointerCapture(event.pointerId)
}

async function toggleFullscreen() {
  if (!stageRef.value) return
  if (!document.fullscreenElement) {
    await stageRef.value.requestFullscreen()
  } else {
    await document.exitFullscreen()
  }
}

function handleFullscreenChange() {
  isFullscreen.value = Boolean(document.fullscreenElement)
  emit('fullscreen-change', isFullscreen.value)
}

onMounted(() => {
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})

watch(
  scale,
  (value) => {
    emit('scale-change', value)
  },
  { immediate: true }
)

watch(
  () => props.src,
  () => {
    resetView()
  }
)

defineExpose({
  toggleFullscreen,
  resetView
})
</script>

<style scoped>
.viewer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.stage {
  background: #fff;
  padding: 18px;
  border-radius: 18px;
  box-shadow: var(--shadow);
  max-width: 100%;
  overflow: hidden;
  touch-action: none;
  cursor: grab;
}

.stage.dragging {
  cursor: grabbing;
}

.stage img {
  max-width: min(100%, 1100px);
  max-height: 75vh;
  border-radius: 12px;
  display: block;
  transition: transform 0.05s linear;
}

.caption {
  font-size: 14px;
  color: var(--muted);
}

.hints {
  font-size: 12px;
  color: var(--muted);
}
</style>
