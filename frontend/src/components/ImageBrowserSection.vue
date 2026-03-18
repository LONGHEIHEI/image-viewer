<template>
  <section class="browser-section">
    <div v-if="showMobileSearch" class="browser-mobile-bar">
      <n-input
        v-model:value="searchTerm"
        class="panel-search panel-search--mobile"
        :placeholder="resolvedSearchPlaceholder"
        clearable
      />
    </div>

    <div :class="['panel-header', 'browser-header', { 'browser-header--mobile-hidden': showMobileSearch }]">
      <div class="browser-main">
        <div v-if="title || subtitle" class="panel-left">
          <div v-if="title" class="panel-title">{{ title }}</div>
          <div v-if="subtitle" class="panel-subtitle mobile-topbar-title-hidden">{{ subtitle }}</div>
        </div>
        <n-input
          v-if="searchEnabled"
          v-model:value="searchTerm"
          class="panel-search"
          :placeholder="resolvedSearchPlaceholder"
          clearable
        />
      </div>
      <div v-if="metaText || showBackButton" class="browser-side">
        <div class="meta" v-if="metaText">{{ metaText }}</div>
        <n-button v-if="showBackButton" size="small" @click="emit('back')">返回</n-button>
      </div>
    </div>

    <ImageGrid
      v-if="filteredImages.length"
      :images="filteredImages"
      :thumb="thumb"
      :privacy-enabled="privacyEnabled"
      :privacy-storage-key="privacyStorageKey"
      @open-image="(path) => emit('open-image', path)"
    />
    <div v-else-if="showEmptyState" class="empty">{{ emptyText }}</div>

    <div class="load" v-if="hasMore">
      <n-button type="primary" :loading="loading" @click="emit('load-more')">加载更多</n-button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { NButton, NInput } from 'naive-ui'
import type { FolderItem } from '../api/client'
import ImageGrid from './ImageGrid.vue'

const props = withDefaults(
  defineProps<{
    images: FolderItem[]
    thumb: (path: string) => string
    title?: string
    subtitle?: string
    metaText?: string
    searchEnabled?: boolean
    searchPlaceholder?: string
    searchScopeKey?: string
    showBackButton?: boolean
    hasMore?: boolean
    loading?: boolean
    emptyText?: string
    showEmptyState?: boolean
    privacyEnabled?: boolean
    privacyStorageKey?: string
  }>(),
  {
    title: '',
    subtitle: '',
    metaText: '',
    searchEnabled: false,
    searchPlaceholder: '搜索图片',
    searchScopeKey: '',
    showBackButton: false,
    hasMore: false,
    loading: false,
    emptyText: '暂无图片',
    showEmptyState: false,
    privacyEnabled: false,
    privacyStorageKey: ''
  }
)

const emit = defineEmits<{
  (event: 'open-image', path: string): void
  (event: 'back'): void
  (event: 'load-more'): void
}>()

const searchTerm = ref('')

const resolvedSearchPlaceholder = computed(() => props.searchPlaceholder || '搜索图片')
const showMobileSearch = computed(() => props.searchEnabled)
const normalizedSearchTerm = computed(() => searchTerm.value.trim().toLowerCase())
const filteredImages = computed(() => {
  if (!normalizedSearchTerm.value) return props.images
  return props.images.filter((image) => image.name.toLowerCase().includes(normalizedSearchTerm.value))
})

watch(
  () => props.images,
  () => {
    if (!props.images.length) {
      searchTerm.value = ''
    }
  }
)

watch(
  () => props.searchScopeKey,
  () => {
    searchTerm.value = ''
  }
)
</script>

<style scoped>
.browser-section {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.browser-mobile-bar {
  display: none;
}

.browser-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.browser-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
  flex-wrap: wrap;
}

.panel-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  min-width: 0;
}

.browser-side {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.panel-subtitle {
  font-size: 12px;
  color: var(--muted);
  font-weight: 700;
  letter-spacing: 0.01em;
}

.panel-search {
  width: 320px;
  max-width: 40vw;
  --n-color: #fafafa;
  --n-color-focus: #fff;
  --n-color-hover: #fdfdfd;
  --n-border: rgba(27, 30, 39, 0.08);
  --n-border-hover: rgba(27, 30, 39, 0.12);
  --n-border-focus: rgba(27, 30, 39, 0.18);
  --n-box-shadow-focus: none;
}

@media (max-width: 960px) {
  .browser-header--mobile-hidden {
    display: none;
  }

  .browser-mobile-bar {
    display: grid;
    gap: 0;
  }

  .browser-header,
  .browser-main,
  .browser-side {
    align-items: flex-start;
  }

  .browser-side {
    width: 100%;
    justify-content: space-between;
  }

  .panel-search {
    width: 100%;
    max-width: none;
  }

  .panel-search--mobile {
    width: 100%;
  }
}
</style>
