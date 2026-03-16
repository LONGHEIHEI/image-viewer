<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">图集</div>
    </div>

    <div class="collections-grid" v-if="collections.length">
      <div
        v-for="item in collections"
        :key="item.id"
        class="collection-card"
        @click="handleCollectionClick(item)"
      >
        <div :class="['cover', { 'cover--private': item.privacy_enabled && !isRevealed(`cover:${item.id}`) }]">
          <img
            :src="collectionCoverUrl(item.id)"
            :alt="item.name"
            loading="lazy"
            @error="onCoverError"
          />
          <div class="cover-fallback">图集封面</div>
          <div class="cover-sheen"></div>
          <div v-if="item.privacy_enabled && !isRevealed(`cover:${item.id}`)" class="privacy-mask">点击显示</div>
          <div v-if="item.requires_password" class="cover-tag">需密码</div>
          <div v-if="item.privacy_enabled" class="cover-tag cover-tag--secondary">隐私</div>
        </div>
        <div class="title">{{ item.name }}</div>
      </div>
    </div>

    <div v-else class="empty">暂无可访问的图集</div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getCollectionsAvailable, collectionCoverUrl, type CollectionSummary } from '../api/client'
import { usePrivacyReveal } from '../composables/usePrivacyReveal'

const router = useRouter()
const collections = ref<CollectionSummary[]>([])
const { isRevealed, reveal } = usePrivacyReveal('collection-cover-privacy')

onMounted(async () => {
  collections.value = await getCollectionsAvailable()
})

function openCollection(id: number) {
  router.push(`/collection/${id}`)
}

function handleCollectionClick(item: CollectionSummary) {
  if (item.privacy_enabled && !isRevealed(`cover:${item.id}`)) {
    reveal(`cover:${item.id}`)
    return
  }
  openCollection(item.id)
}

function onCoverError(event: Event) {
  const target = event.target as HTMLImageElement | null
  if (!target) return
  target.classList.add('hidden')
}
</script>

<style scoped>
.collections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.collection-card {
  display: grid;
  gap: 10px;
  padding: 0 0 10px;
  border: 1px solid rgba(27, 30, 39, 0.08);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 6px 16px rgba(20, 25, 35, 0.04);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  cursor: pointer;
  overflow: hidden;
}

.collection-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 22px rgba(20, 25, 35, 0.08);
}

.cover {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  position: relative;
  background: #f7f7f7;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover img.hidden {
  display: none;
}

.cover--private img {
  filter: blur(22px) saturate(0.72);
  transform: scale(1.05);
}

.cover-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-2);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background:
    radial-gradient(circle at 20% 20%, rgba(170, 196, 255, 0.35), transparent 42%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(240, 244, 248, 0.95));
}

.cover img:not(.hidden) ~ .cover-fallback {
  opacity: 0;
}

.cover-sheen {
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, rgba(255, 255, 255, 0.22), rgba(255, 255, 255, 0));
  pointer-events: none;
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

.cover-tag {
  position: absolute;
  left: 10px;
  bottom: 10px;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 11px;
  color: #fff;
  background: rgba(0, 0, 0, 0.55);
}

.cover-tag--secondary {
  left: auto;
  right: 10px;
}

.title {
  padding: 0 10px;
  font-weight: 700;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 960px) {
  .collections-grid {
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 12px;
  }

  .collection-card {
    padding: 0 0 10px;
  }
}

@media (max-width: 640px) {
  .collections-grid {
    grid-template-columns: 1fr;
  }
}
</style>
