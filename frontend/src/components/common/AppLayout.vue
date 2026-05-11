<template>
  <el-container class="layout">
    <el-aside width="220px">
      <div class="logo">保健品商家后台</div>
      <el-menu :default-active="route.path" router>
        <template v-for="item in menuItems" :key="item.path">
          <el-menu-item v-if="!item.children" :index="item.path">{{ item.title }}</el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <span>{{ route.meta.title }}</span>
        <el-dropdown @command="handleCommand">
          <span class="user">{{ username }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const username = localStorage.getItem('username') || ''
const role = localStorage.getItem('role')

const menuItems = computed(() => {
  if (role === 'merchant') return [
    { path: '/merchant/dashboard', title: '工作台' },
    { path: '/merchant/products', title: '商品管理' },
    { path: '/merchant/qualifications', title: '资质管理' },
    { path: '/merchant/settings', title: '账号设置' },
  ]
  if (role === 'reviewer') return [
    { path: '/reviewer/dashboard', title: '审核工作台' },
    { path: '/reviewer/products', title: '审核列表' },
  ]
  if (role === 'admin') return [
    { path: '/admin/categories', title: '品类管理' },
    { path: '/admin/merchants', title: '商家管理' },
    { path: '/admin/reviewers', title: '审核员管理' },
    { path: '/admin/qualification-types', title: '资质类型管理' },
  ]
  return []
})

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    localStorage.clear()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout { min-height: 100vh; }
.logo { padding: 16px 20px; font-size: 16px; font-weight: bold; color: #fff; background: #001529; }
.el-aside { background: #001529; }
.el-header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #e8e8e8; padding: 0 20px; }
.user { cursor: pointer; }
</style>
