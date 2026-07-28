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
const pointers = new Map<number, { clientX: number; clientY: number }>()
let pinchStartDist = 0
let pinchStartScale = 1
let pinchStartOffsetX = 0
let pinchStartOffsetY = 0
let pinchStartMidX = 0
let pinchStartMidY = 0

function ptrDist(a: { clientX: number; clientY: number }, b: { clientX: number; clientY: number }) {
  const dx = a.clientX - b.clientX
  const dy = a.clientY - b.clientY
  return Math.sqrt(dx * dx + dy * dy)
}

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
  pointers.set(event.pointerId, { clientX: event.clientX, clientY: event.clientY })

  if (pointers.size === 1) {
    dragging.value = true
    startX = event.clientX
    startY = event.clientY
    startOffsetX = offsetX.value
    startOffsetY = offsetY.value
  } else if (pointers.size === 2) {
    dragging.value = false
    const pts = [...pointers.values()]
    pinchStartDist = ptrDist(pts[0], pts[1])
    pinchStartScale = scale.value
    pinchStartOffsetX = offsetX.value
    pinchStartOffsetY = offsetY.value
    pinchStartMidX = (pts[0].clientX + pts[1].clientX) / 2
    pinchStartMidY = (pts[0].clientY + pts[1].clientY) / 2
  }

  const target = event.currentTarget as HTMLElement
  target.setPointerCapture(event.pointerId)
}

function onPointerMove(event: PointerEvent) {
  if (!pointers.has(event.pointerId)) return
  pointers.set(event.pointerId, { clientX: event.clientX, clientY: event.clientY })

  if (pointers.size === 1 && dragging.value) {
    offsetX.value = startOffsetX + (event.clientX - startX)
    offsetY.value = startOffsetY + (event.clientY - startY)
  } else if (pointers.size === 2) {
    const pts = [...pointers.values()]
    const dist = ptrDist(pts[0], pts[1])
    scale.value = clamp(Number((pinchStartScale * (dist / pinchStartDist)).toFixed(2)), 0.5, 4)
    const mx = (pts[0].clientX + pts[1].clientX) / 2
    const my = (pts[0].clientY + pts[1].clientY) / 2
    offsetX.value = pinchStartOffsetX + (mx - pinchStartMidX)
    offsetY.value = pinchStartOffsetY + (my - pinchStartMidY)
  }
}

function onPointerUp(event: PointerEvent) {
  pointers.delete(event.pointerId)

  if (pointers.size === 0) {
    dragging.value = false
  } else if (pointers.size === 1) {
    const pts = [...pointers.values()]
    dragging.value = true
    startX = pts[0].clientX
    startY = pts[0].clientY
    startOffsetX = offsetX.value
    startOffsetY = offsetY.value
  }

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
  gap: 8px;
  width: 100%;
  height: 100%;
}

 .stage {
   background: transparent;
   padding: 0;
   border-radius: 0;
   box-shadow: none;
   max-width: 100%;
   display: flex;
   align-items: center;
   justify-content: center;
   overflow: hidden;
   width: 100%;
   flex: 1;
   min-height: 0;
   touch-action: none;
   cursor: grab;
 }

.stage:fullscreen {
  width: 100vw;
  height: 100vh;
  padding: 24px;
  background: rgba(12, 14, 20, 0.96);
}

.stage.dragging {
  cursor: grabbing;
}

 .stage img {
   max-width: min(100%, 1100px);
   max-height: 100%;
   border-radius: 0;
   display: block;
   transition: transform 0.05s linear;
 }

.caption {
  font-size: 13px;
  color: rgba(92, 102, 114, 0.88);
  max-width: min(100%, 78vw);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hints {
  font-size: 11px;
  color: rgba(92, 102, 114, 0.68);
}

 @media (max-width: 960px) {
   .viewer { gap: 6px; }
   .stage img { max-height: 100%; }
   .caption { max-width: 100%; padding: 0 4px; font-size: 12px; }
   .hints { display: none; }
 }
</style>
