<template>
  <div class="masonry">
    <div v-for="(image, idx) in images" :key="image.path" class="tile" @click="$emit('open-image', image.path, idx)">
      <div class="thumb">
        <img :src="thumb(image.path)" :alt="image.name" loading="lazy" />
      </div>
      <div class="name">{{ image.name }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FolderItem } from '../api/client'

defineProps<{ images: FolderItem[]; thumb: (path: string) => string }>()
</script>

<style scoped>
.masonry {
  column-count: 2;
  column-gap: 14px;
}

.tile {
  break-inside: avoid;
  margin-bottom: 14px;
  background: var(--panel);
  border-radius: 16px;
  border: 1px solid var(--stroke);
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 10px 18px rgba(20, 25, 35, 0.08);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.tile:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 26px rgba(20, 25, 35, 0.16);
}

.thumb img {
  width: 100%;
  display: block;
}

.name {
  padding: 10px 12px 12px;
  font-size: 12px;
  color: var(--muted);
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
