<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">设置</div>
    </div>

    <n-tabs v-model:value="active" type="segment" size="large">
      <n-tab-pane name="collections" tab="集合配置">
        <div class="settings-section">
          <CollectionsManageView />
        </div>
      </n-tab-pane>
      <n-tab-pane name="users" tab="用户管理">
        <div class="settings-section">
          <UsersView />
        </div>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { NTabs, NTabPane } from 'naive-ui'
import CollectionsManageView from './CollectionsManageView.vue'
import UsersView from './UsersView.vue'

const active = ref('collections')
</script>

<style scoped>
.settings-section :deep(.page-header) {
  display: none;
}

.settings-section :deep(.page) {
  gap: 12px;
}

@media (max-width: 960px) {
  :deep(.n-tabs-nav-scroll-content) {
    width: 100%;
  }

  :deep(.n-tabs-tab) {
    flex: 1 1 0;
    min-width: 0;
    justify-content: center;
  }
}
</style>
