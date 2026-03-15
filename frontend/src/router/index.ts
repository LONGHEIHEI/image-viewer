import { createRouter, createWebHistory } from 'vue-router'
import LibraryView from '../views/LibraryView.vue'
import FolderView from '../views/FolderView.vue'
import ImageView from '../views/ImageView.vue'
import LoginView from '../views/LoginView.vue'
import UsersView from '../views/UsersView.vue'
import CollectionView from '../views/CollectionView.vue'
import CollectionsManageView from '../views/CollectionsManageView.vue'
import { useAuthStore } from '../store/auth'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/', component: LibraryView, meta: { requiresAuth: true } },
    { path: '/folder', component: FolderView, meta: { requiresAuth: true } },
    { path: '/image', component: ImageView, meta: { requiresAuth: true } },
    { path: '/collection/:id', component: CollectionView, meta: { requiresAuth: true } },
    { path: '/users', component: UsersView, meta: { requiresAuth: true, requiresAdmin: true } },
    { path: '/collections', component: CollectionsManageView, meta: { requiresAuth: true, requiresAdmin: true } }
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
    return { path: '/' }
  }

  return true
})
