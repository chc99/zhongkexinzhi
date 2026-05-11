import { createRouter, createWebHistory } from 'vue-router'
import { merchantRoutes } from './routes/merchant'
import { reviewerRoutes } from './routes/reviewer'
import { adminRoutes } from './routes/admin'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'Login', component: () => import('@/views/login/Login.vue'), meta: { title: '登录' } },
    ...merchantRoutes,
    ...reviewerRoutes,
    ...adminRoutes,
  ]
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  if (to.path !== '/login' && !token) {
    return next('/login')
  }
  if (to.meta.role && to.meta.role !== role) {
    return next('/login')
  }
  document.title = (to.meta.title as string) || '保健品商家后台'
  next()
})

export default router
