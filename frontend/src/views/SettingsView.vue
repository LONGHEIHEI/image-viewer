<template>
  <div class="page">
    <div class="page-header settings-header">
      <div class="page-title">系统设置</div>
      <div class="page-subtitle">统一管理集合展示方式、访问策略与账号权限。</div>
    </div>

    <n-tabs v-model:value="active" class="settings-tabs" type="segment" size="large">
      <n-tab-pane name="collections" tab="集合与访问">
        <div class="tab-intro">
          <div class="tab-intro-title">集合设置</div>
          <div class="tab-intro-desc">配置图片来源目录、封面、隐私模式和访问密码。</div>
        </div>
        <div class="settings-section">
          <CollectionsManageView />
        </div>
      </n-tab-pane>
      <n-tab-pane name="users" tab="账号与权限">
        <div class="tab-intro">
          <div class="tab-intro-title">用户管理</div>
          <div class="tab-intro-desc">维护系统账号并控制可访问的集合范围。</div>
        </div>
        <div class="settings-section">
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
.settings-header {
  display: grid;
  gap: 4px;
}

.page-subtitle {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.45;
}

.tab-intro {
  display: grid;
  gap: 2px;
  margin-bottom: 8px;
  padding: 10px 12px;
  border: 1px solid var(--stroke);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.68);
}

.tab-intro-title {
  font-size: 13px;
  font-weight: 700;
}

.tab-intro-desc {
  font-size: 12px;
  color: var(--muted);
}

.settings-section :deep(.page-header) {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-bottom: 0;
}

.settings-section :deep(.page-header .page-title) {
  display: none;
}

.settings-section :deep(.page) {
  gap: 8px;
}

.settings-tabs {
  padding: 2px;
  border-radius: 12px;
}

.settings-tabs :deep(.n-tabs-nav) {
  margin-bottom: 6px;
}

.settings-tabs :deep(.n-tabs-pane-wrapper) {
  padding-top: 6px;
}

@media (max-width: 960px) {
  .page-subtitle {
    font-size: 12px;
  }

  .tab-intro {
    padding: 8px 10px;
  }

  :deep(.n-tabs-nav-scroll-content) {
    width: 100%;
  }

  :deep(.n-tabs-tab) {
    flex: 1 1 0;
    min-width: 0;
    justify-content: center;
  }
}

/* Unified spacing rhythm for settings pages: 12 / 8 / 6 */
.settings-header {
  gap: 6px;
}

.settings-tabs :deep(.n-tabs-nav) {
  margin-bottom: 8px;
}

.settings-tabs :deep(.n-tabs-pane-wrapper) {
  padding-top: 8px;
}

.tab-intro {
  gap: 6px;
  margin-bottom: 8px;
  padding: 12px;
  border-radius: 12px;
}

.settings-section :deep(.page) {
  gap: 12px;
}
</style>
