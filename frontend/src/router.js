import { createRouter, createWebHistory } from 'vue-router'
import { currentUser, isAdmin } from '@/session'

const routes = [
  { path: '/', redirect: '/leaderboard' },
  { path: '/join', name: 'Login', component: () => import('@/pages/Login.vue') },
  { path: '/me', name: 'Me', component: () => import('@/pages/Me.vue') },
  { path: '/leaderboard', name: 'Leaderboard', component: () => import('@/pages/Leaderboard.vue') },
  { path: '/u/:login', name: 'Profile', component: () => import('@/pages/Profile.vue'), props: true },
  { path: '/requests', name: 'Requests', component: () => import('@/pages/Requests.vue') },
  { path: '/requests/:id', name: 'Request', component: () => import('@/pages/Request.vue'), props: true },
  { path: '/badges', name: 'Badges', component: () => import('@/pages/Badges.vue') },
  { path: '/admin/point-rules', name: 'PointRules', component: () => import('@/pages/admin/PointRules.vue'), meta: { admin: true } },
  { path: '/admin/badges', name: 'BadgeAdmin', component: () => import('@/pages/admin/BadgeAdmin.vue'), meta: { admin: true } },
  { path: '/admin/products', name: 'Products', component: () => import('@/pages/admin/Products.vue'), meta: { admin: true } },
  { path: '/admin/ledger', name: 'Ledger', component: () => import('@/pages/admin/Ledger.vue'), meta: { admin: true } },
  { path: '/:pathMatch(.*)*', redirect: '/leaderboard' },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

export function guard(to) {
  if (to.name === 'Me' && currentUser.value) {
    return { name: 'Profile', params: { login: currentUser.value } }
  }
  if (to.meta.admin && !isAdmin.value) {
    return { name: 'Leaderboard' }
  }
}

router.beforeEach(guard)
