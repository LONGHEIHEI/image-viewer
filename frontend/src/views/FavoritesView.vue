<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">收藏</div>
      <div class="page-actions">
        <span v-if="store.favorites.length" class="page-meta-badge">共 {{ store.favorites.length }} 张</span>
      </div>
    </div>

    <ImageBrowserSection
      :images="favoriteImages"
      :thumb="thumb"
      search-enabled
      search-placeholder="搜索收藏图片"
      search-scope-key="favorites"
      :show-empty-state="!store.favoritesLoading"
      empty-text="暂无收藏"
      favorite-enabled
      :is-favorite="isFavorite"
      :toggle-favorite="toggleFavorite"
      @open-image="openImage"
    />

    <div v-if="store.favoritesLoading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { FavoriteItem, FolderItem } from '../api/client'
import ImageBrowserSection from '../components/ImageBrowserSection.vue'
import { useGalleryStore } from '../store/gallery'
import { buildFavoriteKey, favoriteDisplayPath, favoriteThumbUrl, openFavorite } from '../utils/favorites'

const router = useRouter()
const store = useGalleryStore()

const favoriteMap = computed(() => {
  const entries = new Map<string, FavoriteItem>()
  for (const item of store.favorites) {
    entries.set(buildFavoriteKey(item), item)
  }
  return entries
})

const favoriteImages = computed<FolderItem[]>(() =>
  store.favorites.map((item) => {
    const key = buildFavoriteKey(item)
    return {
      name: item.item_name || item.item_path.split(/[\\/]+/).filter(Boolean).pop() || item.item_path,
      path: key,
      favorite_key: key,
      display_path: favoriteDisplayPath(item)
    }
  })
)

onMounted(async () => {
  await store.loadFavorites()
})

function thumb(key: string) {
  const item = favoriteMap.value.get(key)
  return item ? favoriteThumbUrl(item) : ''
}

function openImage(key: string) {
  const item = favoriteMap.value.get(key)
  if (!item) return
  openFavorite(router, item)
}

function isFavorite(key: string) {
  return favoriteMap.value.has(key)
}

async function toggleFavorite(key: string) {
  const item = favoriteMap.value.get(key)
  if (!item) return
  await store.removeFavoriteItem(item)
}
</script>
