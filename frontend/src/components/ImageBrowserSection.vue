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
  .browser-mobile-bar {
    display: grid;
    gap: 0;
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
