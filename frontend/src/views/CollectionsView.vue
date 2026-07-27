<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">图集</div>
      <div class="page-actions">
        <n-button size="small" @click="router.push('/favorites')">收藏</n-button>
      </div>
    </div>

    <div class="collections-grid collections-grid--placeholder" v-if="loading">
      <div v-for="item in loadingPlaceholders" :key="item" class="collection-card collection-card--placeholder">
        <div class="cover cover--placeholder">
          <div class="cover-placeholder"></div>
        </div>
        <div class="title title--placeholder"></div>
      </div>
    </div>

    <div class="collections-grid" v-else-if="collections.length">
      <div
        v-for="item in collections"
        :key="item.id"
        class="collection-card"
        @click="handleCollectionClick(item)"
      >
        <div :class="['cover', { 'cover--private': item.privacy_enabled && !isRevealed(`cover:${item.id}`) }]">
          <div class="cover-placeholder" aria-hidden="true"></div>
          <img
            :src="collectionCoverUrl(item.id)"
            :alt="item.name"
            loading="lazy"
            decoding="async"
            @load="onCoverLoad"
            @error="onCoverError"
          />
          <div class="cover-fallback">图集封面</div>
          <div class="cover-sheen"></div>
          <div v-if="item.privacy_enabled && !isRevealed(`cover:${item.id}`)" class="privacy-mask"></div>
          <div v-if="item.requires_password" class="cover-tag">需密码</div>
          <div v-if="item.privacy_enabled" class="cover-tag cover-tag--secondary">隐私</div>
        </div>
        <div class="title">{{ item.name }}</div>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-state-icon">
        <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <rect x="7" y="7" width="10" height="10" rx="1"/>
          <circle cx="12" cy="12" r="1.5"/>
        </svg>
      </div>
      <div class="empty-state-title">暂无图集</div>
      <div class="empty-state-desc">
        图集可以将不同目录的图片聚合展示
        <template v-if="auth.user?.is_admin">，前往设置页创建第一个图集</template>
      </div>
      <n-button v-if="auth.user?.is_admin" type="primary" size="small" @click="router.push('/settings')">去创建图集</n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
import { getCollectionsAvailable, collectionCoverUrl, type CollectionSummary } from '../api/client'
import { useAuthStore } from '../store/auth'
import { usePrivacyReveal } from '../composables/usePrivacyReveal'

const router = useRouter()
const collections = ref<CollectionSummary[]>([])
const loading = ref(true)
const loadingPlaceholders = Array.from({ length: 6 }, (_, index) => index)
const { isRevealed, reveal } = usePrivacyReveal('collection-cover-privacy')
const auth = useAuthStore()

onMounted(async () => {
  try {
    collections.value = await getCollectionsAvailable()
  } finally {
    loading.value = false
  }
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
  target.closest('.cover')?.classList.add('cover--failed')
}

function onCoverLoad(event: Event) {
  const target = event.target as HTMLImageElement | null
  target?.closest('.cover')?.classList.add('cover--ready')
}
</script>

<style scoped>
.collections-grid--placeholder {
  pointer-events: none;
}

.collections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}

.collection-card {
  display: grid;
  gap: 10px;
  padding: 0 0 10px;
  border: 1px solid var(--stroke);
  border-radius: 14px;
  background: var(--panel);
  box-shadow: var(--shadow-tiny);
  backdrop-filter: blur(14px);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  cursor: pointer;
  overflow: hidden;
  content-visibility: auto;
  contain-intrinsic-size: 260px 200px;
}

.collection-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-soft);
}

.cover {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  position: relative;
  background: var(--placeholder-surface);
}

.cover-placeholder {
  position: absolute;
  inset: 0;
  background: var(--placeholder-surface);
  opacity: 1;
  transition: opacity 0.2s ease;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.cover img.hidden {
  display: none;
}

.cover--ready img {
  opacity: 1;
}

.cover--ready .cover-placeholder,
.cover--failed .cover-placeholder {
  opacity: 0;
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
  padding: 0 12px;
  font-weight: 700;
  font-size: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.title--placeholder {
  height: 18px;
  margin: 0 12px;
  border-radius: 999px;
  background: var(--placeholder-surface);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 56px 24px;
  text-align: center;
}

.empty-state-icon {
  color: rgba(92, 102, 114, 0.3);
  margin-bottom: 4px;
}

.empty-state-title {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: var(--ink);
}

.empty-state-desc {
  font-size: 13px;
  color: var(--muted);
  max-width: 300px;
  line-height: 1.5;
}

@media (max-width: 960px) {
  .collections-grid {
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 12px;
  }

  .collection-card {
    padding: 0 0 10px;
  }

  .empty-state {
    padding: 48px 20px;
    gap: 8px;
  }
}

@media (max-width: 640px) {
  .collections-grid {
    grid-template-columns: 1fr;
  }
}
</style>
