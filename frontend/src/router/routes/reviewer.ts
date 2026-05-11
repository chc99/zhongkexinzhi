import type { RouteRecordRaw } from 'vue-router'

export const reviewerRoutes: RouteRecordRaw[] = [
  {
    path: '/reviewer',
    component: () => import('@/components/common/AppLayout.vue'),
    meta: { role: 'reviewer' },
    children: [
      { path: 'dashboard', name: 'ReviewerDashboard', component: () => import('@/views/reviewer/Dashboard.vue'), meta: { title: '审核工作台' } },
      { path: 'products', name: 'ReviewerProducts', component: () => import('@/views/reviewer/ProductList.vue'), meta: { title: '审核列表' } },
      { path: 'products/:id', name: 'ReviewerProductAudit', component: () => import('@/views/reviewer/ProductAudit.vue'), meta: { title: '审核详情' } },
    ]
  }
]
