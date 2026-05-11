import type { RouteRecordRaw } from 'vue-router'

export const merchantRoutes: RouteRecordRaw[] = [
  {
    path: '/merchant',
    component: () => import('@/components/common/AppLayout.vue'),
    meta: { role: 'merchant' },
    children: [
      { path: 'dashboard', name: 'MerchantDashboard', component: () => import('@/views/merchant/Dashboard.vue'), meta: { title: '工作台' } },
      { path: 'products', name: 'MerchantProducts', component: () => import('@/views/merchant/ProductList.vue'), meta: { title: '商品管理' } },
      { path: 'products/create', name: 'ProductCreate', component: () => import('@/views/merchant/ProductCreate.vue'), meta: { title: '发布商品' } },
      { path: 'products/:id/edit', name: 'ProductEdit', component: () => import('@/views/merchant/ProductEdit.vue'), meta: { title: '编辑商品' } },
      { path: 'qualifications', name: 'MerchantQualifications', component: () => import('@/views/merchant/QualificationManage.vue'), meta: { title: '资质管理' } },
      { path: 'settings', name: 'MerchantSettings', component: () => import('@/views/merchant/Settings.vue'), meta: { title: '账号设置' } },
    ]
  }
]
