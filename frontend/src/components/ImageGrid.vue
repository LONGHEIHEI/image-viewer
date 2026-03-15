<template>
  <div class="masonry">
    <n-card
      v-for="image in images"
      :key="image.path"
      class="tile"
      :bordered="false"
      :content-style="{ padding: 0 }"
      @click="$emit('open-image', image.path)"
      @contextmenu.prevent="openMenu($event, image)"
    >
      <div class="thumb" :data-title="image.name">
        <img :src="thumb(image.path)" :alt="image.name" loading="lazy" />
      </div>
    </n-card>
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
import { ref } from 'vue'
import { NCard, NDropdown, NModal } from 'naive-ui'
import type { FolderItem } from '../api/client'

defineProps<{ images: FolderItem[]; thumb: (path: string) => string }>()

const menuVisible = ref(false)
const menuX = ref(0)
const menuY = ref(0)
const selected = ref<FolderItem | null>(null)
const propsVisible = ref(false)

const menuOptions = [{ label: '属性', key: 'props' }]

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
  column-count: 2;
  column-gap: 10px;
}

.tile {
  break-inside: avoid;
  margin-bottom: 10px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--stroke);
  box-shadow: var(--shadow-soft);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.tile:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 26px rgba(20, 25, 35, 0.12);
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

@media (min-width: 700px) {
  .masonry {
    column-count: 3;
  }
}

@media (min-width: 1100px) {
  .masonry {
    column-count: 4;
  }
}
</style>
