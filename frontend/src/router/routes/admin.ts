import type { RouteRecordRaw } from 'vue-router'

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    component: () => import('@/components/common/AppLayout.vue'),
    meta: { role: 'admin' },
    children: [
      { path: 'categories', name: 'AdminCategories', component: () => import('@/views/admin/CategoryManage.vue'), meta: { title: '品类管理' } },
      { path: 'merchants', name: 'AdminMerchants', component: () => import('@/views/admin/MerchantManage.vue'), meta: { title: '商家管理' } },
      { path: 'reviewers', name: 'AdminReviewers', component: () => import('@/views/admin/ReviewerManage.vue'), meta: { title: '审核员管理' } },
      { path: 'qualification-types', name: 'AdminQualTypes', component: () => import('@/views/admin/QualificationTypeManage.vue'), meta: { title: '资质类型管理' } },
    ]
  }
]
