import { createRouter, createWebHistory } from 'vue-router'
import LibraryView from '../views/LibraryView.vue'
import FolderView from '../views/FolderView.vue'
import ImageView from '../views/ImageView.vue'
import LoginView from '../views/LoginView.vue'
import CollectionView from '../views/CollectionView.vue'
import CollectionsView from '../views/CollectionsView.vue'
import FavoritesView from '../views/FavoritesView.vue'
import SettingsView from '../views/SettingsView.vue'
import { useAuthStore } from '../store/auth'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/', redirect: '/collections' },
    { path: '/library', component: LibraryView, meta: { requiresAuth: true, topLevel: true } },
    { path: '/folder', component: FolderView, meta: { requiresAuth: true, topLevel: false } },
    { path: '/image', component: ImageView, meta: { requiresAuth: true, topLevel: false } },
    { path: '/collections', component: CollectionsView, meta: { requiresAuth: true, topLevel: true } },
    { path: '/favorites', component: FavoritesView, meta: { requiresAuth: true, topLevel: true } },
    { path: '/collection/:id', component: CollectionView, meta: { requiresAuth: true, topLevel: false } },
    { path: '/settings', component: SettingsView, meta: { requiresAuth: true, requiresAdmin: true, topLevel: true } }
  ]
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (auth.token && !auth.user) {
    await auth.fetchMe()
  }

  if (to.meta.requiresAuth && !auth.token) {
    return { path: '/login' }
  }

  if (to.meta.requiresAdmin && !auth.user?.is_admin) {
    return { path: '/collections' }
  }

  return true
})
