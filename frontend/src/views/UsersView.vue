<template>
  <div class="users">
    <div class="panel">
      <div class="panel-header">
        <div>
          <div class="panel-title">用户管理</div>
          <div class="panel-sub">创建用户并设置访问目录</div>
        </div>
        <button class="ghost" @click="load">刷新</button>
      </div>

      <div class="form">
        <input v-model="newUser.username" placeholder="用户名" />
        <input v-model="newUser.password" type="password" placeholder="密码" />
        <label class="check"><input type="checkbox" v-model="newUser.is_admin" /> 管理员</label>
        <textarea v-model="newUser.allowedPaths" placeholder="允许访问路径（用逗号分隔，例如：set1, set2/sub）"></textarea>
        <button class="primary" @click="create">创建用户</button>
      </div>

      <div class="list">
        <div v-for="user in users" :key="user.id" class="row">
          <div>
            <div class="name">{{ user.username }}</div>
            <div class="meta">编号：{{ user.id }} | 管理员：{{ user.is_admin ? '是' : '否' }}</div>
            <div class="meta">允许路径：{{ (user.allowed_paths || []).join(', ') || '全部' }}</div>
          </div>
          <div class="actions">
            <button class="ghost" @click="openEdit(user)">编辑</button>
            <button class="danger" @click="remove(user.id)">删除</button>
          </div>
        </div>
      </div>

      <div v-if="error" class="error">{{ error }}</div>
    </div>

    <div v-if="editing" class="panel">
      <div class="panel-title">编辑用户：{{ editing.username }}</div>
      <div class="form">
        <label class="check"><input type="checkbox" v-model="editForm.is_admin" /> 管理员</label>
        <input v-model="editForm.password" type="password" placeholder="新密码（可选）" />
        <textarea v-model="editForm.allowedPaths" placeholder="允许访问路径（用逗号分隔）"></textarea>
        <div class="actions">
          <button class="primary" @click="save">保存</button>
          <button class="ghost" @click="cancel">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { listUsers, createUser, updateUser, deleteUser, type UserInfo } from '../api/client'

const users = ref<UserInfo[]>([])
const error = ref('')

const newUser = ref({
  username: '',
  password: '',
  is_admin: false,
  allowedPaths: ''
})

const editing = ref<UserInfo | null>(null)
const editForm = ref({
  is_admin: false,
  password: '',
  allowedPaths: ''
})

onMounted(() => {
  load()
})

function parsePaths(input: string) {
  return input
    .split(',')
    .map((p) => p.trim())
    .filter(Boolean)
}

async function load() {
  error.value = ''
  try {
    users.value = await listUsers()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
  }
}

async function create() {
  error.value = ''
  try {
    await createUser({
      username: newUser.value.username,
      password: newUser.value.password,
      is_admin: newUser.value.is_admin,
      allowed_paths: parsePaths(newUser.value.allowedPaths)
    })
    newUser.value = { username: '', password: '', is_admin: false, allowedPaths: '' }
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '创建失败'
  }
}

function openEdit(user: UserInfo) {
  editing.value = user
  editForm.value = {
    is_admin: user.is_admin,
    password: '',
    allowedPaths: (user.allowed_paths || []).join(', ')
  }
}

function cancel() {
  editing.value = null
}

async function save() {
  if (!editing.value) return
  error.value = ''
  try {
    await updateUser(editing.value.id, {
      is_admin: editForm.value.is_admin,
      password: editForm.value.password || undefined,
      allowed_paths: parsePaths(editForm.value.allowedPaths)
    })
    editing.value = null
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '更新失败'
  }
}

async function remove(userId: number) {
  error.value = ''
  try {
    await deleteUser(userId)
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除失败'
  }
}
</script>

<style scoped>
.users {
  display: grid;
  gap: 20px;
}

.panel {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--stroke);
  border-radius: 20px;
  padding: 18px;
  box-shadow: 0 12px 24px rgba(20, 25, 35, 0.08);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  gap: 12px;
}

.panel-title {
  font-size: 18px;
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-weight: 700;
}

.panel-sub {
  font-size: 12px;
  color: var(--muted);
}

.form {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

input,
textarea {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--stroke);
  font-size: 14px;
}

textarea {
  min-height: 70px;
  resize: vertical;
}

.check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--muted);
}

.primary {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 10px 18px;
  cursor: pointer;
  font-weight: 600;
}

.ghost {
  background: transparent;
  border: 1px solid var(--stroke);
  border-radius: 999px;
  padding: 6px 14px;
  cursor: pointer;
}

.danger {
  background: #ff4d4f;
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 6px 14px;
  cursor: pointer;
}

.list {
  display: grid;
  gap: 12px;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--stroke);
  background: #fff;
}

.name {
  font-weight: 700;
}

.meta {
  font-size: 12px;
  color: var(--muted);
}

.actions {
  display: flex;
  gap: 8px;
}

.error {
  color: #b00020;
  font-size: 12px;
}
</style>
