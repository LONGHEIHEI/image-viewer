import { defineStore } from 'pinia'
import { login, getMe, type UserInfo } from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null as UserInfo | null,
    loading: false,
    error: ''
  }),
  actions: {
    async signIn(username: string, password: string) {
      this.loading = true
      this.error = ''
      try {
        const data = await login(username, password)
        this.token = data.access_token
        localStorage.setItem('token', data.access_token)
        this.user = data.user
      } catch (err) {
        this.error = err instanceof Error ? err.message : '登录失败'
        throw err
      } finally {
        this.loading = false
      }
    },
    async fetchMe() {
      if (!this.token) return
      this.loading = true
      try {
        this.user = await getMe()
      } catch (err) {
        this.user = null
        this.token = ''
        localStorage.removeItem('token')
      } finally {
        this.loading = false
      }
    },
    signOut() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
