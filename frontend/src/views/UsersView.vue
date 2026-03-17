<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">用户</div>
      <div class="page-actions">
        <n-input v-model:value="keyword" placeholder="搜索用户名/允许路径" clearable class="user-search" />
        <n-select v-model:value="roleFilter" :options="roleOptions" size="small" class="role-filter" />
        <n-button type="primary" @click="openCreate">新增用户</n-button>
      </div>
    </div>

    <section class="admin-section">
      <n-list :bordered="false" class="user-list">
        <n-list-item v-for="user in filteredUsers" :key="user.id">
          <div class="row">
            <div>
              <div class="name">
                {{ user.username }}
                <span v-if="currentUserId === user.id" class="self-tag">当前账号</span>
              </div>
              <div class="meta">编号：{{ user.id }}</div>
              <div class="meta">权限：{{ user.is_admin ? '管理员' : '普通用户' }}</div>
              <div class="meta" v-if="user.created_at">创建时间：{{ formatTime(user.created_at) }}</div>
              <div class="meta">
                允许路径：
                <span v-if="(user.allowed_paths || []).length === 0">全部</span>
                <span v-else class="paths">
                  <n-tag v-for="p in (user.allowed_paths || [])" :key="p" size="small" type="warning" :bordered="false">
                    {{ p }}
                  </n-tag>
                </span>
              </div>
            </div>
            <n-space size="small">
              <n-button size="small" @click="openEdit(user)">编辑</n-button>
              <n-popconfirm
                v-if="currentUserId !== user.id"
                @positive-click="remove(user.id)"
                positive-text="删除"
                negative-text="取消"
              >
                <template #trigger>
                  <n-button size="small" type="error">删除</n-button>
                </template>
                确认删除该用户？
              </n-popconfirm>
              <n-button v-else size="small" type="error" disabled>删除</n-button>
            </n-space>
          </div>
        </n-list-item>
      </n-list>

      <div v-if="!filteredUsers.length && !loading" class="empty">暂无匹配用户</div>
      <div v-if="error" class="error">{{ error }}</div>
    </section>

    <n-modal v-model:show="showCreate" preset="card" title="新增用户" class="modal">
      <n-form>
        <n-form-item label="用户名">
          <n-input v-model:value="newUser.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="newUser.password" type="password" show-password-on="click" placeholder="至少 6 位" />
        </n-form-item>
        <n-form-item label="确认密码">
          <n-input v-model:value="newUser.confirmPassword" type="password" show-password-on="click" placeholder="请再次输入密码" />
        </n-form-item>
        <div v-if="createPasswordMismatch" class="form-tip form-tip--error">两次输入的密码不一致</div>
        <n-form-item>
          <n-checkbox v-model:checked="newUser.is_admin">管理员</n-checkbox>
        </n-form-item>
        <n-form-item label="允许访问路径">
          <n-input
            v-model:value="newUser.allowedPaths"
            type="textarea"
            placeholder="用逗号分隔，例如：set1, set2/sub"
          />
        </n-form-item>
        <n-space justify="end">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" :disabled="!canCreate" @click="create">创建</n-button>
        </n-space>
      </n-form>
    </n-modal>

    <n-modal v-model:show="showEdit" preset="card" title="编辑用户" class="modal">
      <n-form>
        <n-form-item>
          <n-checkbox v-model:checked="editForm.is_admin">管理员</n-checkbox>
        </n-form-item>
        <n-form-item label="新密码">
          <n-input v-model:value="editForm.password" type="password" show-password-on="click" placeholder="不修改请留空（至少 6 位）" />
        </n-form-item>
        <n-form-item label="确认新密码">
          <n-input v-model:value="editForm.confirmPassword" type="password" show-password-on="click" placeholder="请再次输入新密码" />
        </n-form-item>
        <div v-if="editPasswordMismatch" class="form-tip form-tip--error">两次输入的密码不一致</div>
        <n-form-item label="允许访问路径">
          <n-input v-model:value="editForm.allowedPaths" type="textarea" placeholder="用逗号分隔" />
        </n-form-item>
        <n-space justify="end">
          <n-button @click="showEdit = false">取消</n-button>
          <n-button type="primary" :disabled="!canSave" @click="save">保存</n-button>
        </n-space>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  NButton,
  NList,
  NListItem,
  NInput,
  NCheckbox,
  NModal,
  NForm,
  NFormItem,
  NSpace,
  NPopconfirm,
  NSelect,
  NTag,
  useNotification
} from 'naive-ui'
import { listUsers, createUser, updateUser, deleteUser, type UserInfo } from '../api/client'
import { useAuthStore } from '../store/auth'

const users = ref<UserInfo[]>([])
const error = ref('')
const loading = ref(false)
const notification = useNotification()
const auth = useAuthStore()
const currentUserId = computed(() => auth.user?.id ?? null)

const keyword = ref('')
const roleFilter = ref<'all' | 'admin' | 'user'>('all')
const roleOptions = [
  { label: '全部', value: 'all' },
  { label: '管理员', value: 'admin' },
  { label: '普通用户', value: 'user' }
]

const filteredUsers = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  return users.value.filter((u) => {
    if (roleFilter.value === 'admin' && !u.is_admin) return false
    if (roleFilter.value === 'user' && u.is_admin) return false
    if (!kw) return true
    if (u.username.toLowerCase().includes(kw)) return true
    return (u.allowed_paths || []).some((p) => p.toLowerCase().includes(kw))
  })
})

const showCreate = ref(false)
const showEdit = ref(false)

const newUser = ref({
  username: '',
  password: '',
  confirmPassword: '',
  is_admin: false,
  allowedPaths: ''
})

const editing = ref<UserInfo | null>(null)
const editForm = ref({
  is_admin: false,
  password: '',
  confirmPassword: '',
  allowedPaths: ''
})

onMounted(() => {
  load()
})

function formatTime(iso: string) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function parsePaths(input: string) {
  return input
    .split(',')
    .map((p) => p.trim())
    .filter(Boolean)
}

async function load() {
  error.value = ''
  try {
    loading.value = true
    users.value = await listUsers()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
    notification.error({ title: '加载失败', content: error.value })
  } finally {
    loading.value = false
  }
}

function openCreate() {
  newUser.value = { username: '', password: '', confirmPassword: '', is_admin: false, allowedPaths: '' }
  showCreate.value = true
}

const createPasswordMismatch = computed(() => {
  const hasInput = Boolean(newUser.value.password) || Boolean(newUser.value.confirmPassword)
  if (!hasInput) return false
  return newUser.value.password !== newUser.value.confirmPassword
})

const canCreate = computed(() => {
  if (!newUser.value.username.trim()) return false
  if (newUser.value.password.length < 6) return false
  return !createPasswordMismatch.value
})

async function create() {
  if (createPasswordMismatch.value) {
    notification.error({ title: '创建失败', content: '两次输入的密码不一致' })
    return
  }
  error.value = ''
  try {
    await createUser({
      username: newUser.value.username,
      password: newUser.value.password,
      is_admin: newUser.value.is_admin,
      allowed_paths: parsePaths(newUser.value.allowedPaths)
    })
    showCreate.value = false
    notification.success({ title: '创建成功', content: `用户 ${newUser.value.username} 已创建` })
    newUser.value = { username: '', password: '', confirmPassword: '', is_admin: false, allowedPaths: '' }
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '创建失败'
    notification.error({ title: '创建失败', content: error.value })
  }
}

function openEdit(user: UserInfo) {
  editing.value = user
  editForm.value = {
    is_admin: user.is_admin,
    password: '',
    confirmPassword: '',
    allowedPaths: (user.allowed_paths || []).join(', ')
  }
  showEdit.value = true
}

const editPasswordMismatch = computed(() => {
  const hasInput = Boolean(editForm.value.password) || Boolean(editForm.value.confirmPassword)
  if (!hasInput) return false
  return editForm.value.password !== editForm.value.confirmPassword
})

const canSave = computed(() => {
  if (!editing.value) return false
  if (editForm.value.password && editForm.value.password.length < 6) return false
  if (editPasswordMismatch.value) return false
  if (currentUserId.value === editing.value.id && editing.value.is_admin && !editForm.value.is_admin) return false
  return true
})

async function save() {
  if (!editing.value) return
  if (editPasswordMismatch.value) {
    notification.error({ title: '更新失败', content: '两次输入的密码不一致' })
    return
  }
  error.value = ''
  try {
    await updateUser(editing.value.id, {
      is_admin: editForm.value.is_admin,
      password: editForm.value.password || undefined,
      allowed_paths: parsePaths(editForm.value.allowedPaths)
    })
    showEdit.value = false
    notification.success({ title: '更新成功', content: `已更新用户 ${editing.value.username}` })
    editing.value = null
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '更新失败'
    notification.error({ title: '更新失败', content: error.value })
  }
}

async function remove(userId: number) {
  error.value = ''
  try {
    await deleteUser(userId)
    notification.success({ title: '删除成功', content: '用户已删除' })
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除失败'
    notification.error({ title: '删除失败', content: error.value })
  }
}
</script>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
}

.admin-section {
  display: grid;
  gap: 12px;
}

.user-list {
  border-top: none;
}

.user-list :deep(.n-list-item) {
  padding: 10px 12px;
  margin-bottom: 10px;
  border: 1px solid var(--stroke);
  border-radius: 12px;
  background: var(--panel);
  box-shadow: var(--shadow-tiny);
}

.user-list :deep(.n-list-item:last-child) {
  margin-bottom: 0;
}

.user-list :deep(.n-list-item__main) {
  width: 100%;
  padding: 0;
}

.meta {
  margin-top: 2px;
}

.name {
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.self-tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid var(--stroke);
  background: rgba(255, 255, 255, 0.6);
  color: var(--muted);
}

.paths {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-left: 4px;
}

.user-search {
  width: min(280px, 52vw);
}

.role-filter {
  width: 110px;
}

.form-tip {
  font-size: 12px;
  margin-top: -6px;
}

.form-tip--error {
  color: #b00020;
}

.modal {
  width: min(520px, 92vw);
}

@media (max-width: 960px) {
  .row {
    flex-direction: column;
    align-items: flex-start;
  }

  .row :deep(.n-space) {
    width: 100%;
    flex-wrap: wrap;
  }

  .user-search {
    width: 100%;
  }

  .role-filter {
    width: 100%;
  }
}

/* Unified spacing rhythm for settings pages: 12 / 8 / 6 */
.admin-section {
  gap: 12px;
}

.page-actions {
  gap: 8px;
}

.row {
  gap: 8px;
}

.user-list :deep(.n-list-item) {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 12px;
}

.name {
  margin-bottom: 2px;
}

.meta {
  line-height: 1.45;
}

.paths {
  gap: 6px;
}

.form-tip {
  margin-top: -4px;
}
</style>
