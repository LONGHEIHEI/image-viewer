<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">系统设置</div>
    </div>

    <n-tabs v-model:value="active" class="settings-tabs" type="line" size="medium" animated>
      <n-tab-pane name="collections" tab="集合与访问">
        <div class="tab-content">
          <CollectionsManageView />
        </div>
      </n-tab-pane>
      <n-tab-pane name="users" tab="账号与权限">
        <div class="tab-content">
          <UsersView />
        </div>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { NTabs, NTabPane } from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'
import CollectionsManageView from './CollectionsManageView.vue'
import UsersView from './UsersView.vue'

const route = useRoute()
const router = useRouter()

const VALID_TABS = new Set(['collections', 'users'])

function normalizeTab(value: unknown) {
  const raw = Array.isArray(value) ? value[0] : value
  const tab = typeof raw === 'string' ? raw : ''
  return VALID_TABS.has(tab) ? tab : 'collections'
}

const active = ref(normalizeTab(route.query.tab))

watch(
  () => route.query.tab,
  (tab) => {
    active.value = normalizeTab(tab)
  }
)

watch(
  active,
  (tab) => {
    const normalized = normalizeTab(tab)
    const nextQuery: Record<string, any> = { ...route.query }
    if (normalized === 'collections') {
      delete nextQuery.tab
    } else {
      nextQuery.tab = normalized
    }
    router.replace({ query: nextQuery })
  },
  { flush: 'post' }
)
</script>

<style scoped>
.settings-tabs {
  margin-top: 2px;
}

.settings-tabs :deep(.n-tabs-nav) {
  margin-bottom: 16px;
}

.tab-content :deep(.page-header) {
  margin-bottom: 2px;
}

.tab-content :deep(.page-title) {
  display: none;
}

.settings-tabs :deep(.n-tabs-tab) {
  font-weight: 600;
  font-size: 14px;
}

@media (max-width: 960px) {
  .settings-tabs :deep(.n-tabs-nav) {
    margin-bottom: 12px;
  }

  .settings-tabs :deep(.n-tabs-tab) {
    font-size: 13px;
  }
}
</style>
