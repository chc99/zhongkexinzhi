<template>
  <PaginationTable :data="list" :total="total" :page="page" :page-size="pageSize" :loading="loading"
                   @page-change="(p:number)=>{page=p;fetch()}" @size-change="(s:number)=>{pageSize=s;fetch()}">
    <el-table-column prop="username" label="用户名" />
    <el-table-column prop="phone" label="手机号" />
    <el-table-column label="状态" width="100">
      <template #default="{row}"><el-tag :type="row.status==='active'?'success':'danger'">{{ row.status==='active'?'启用':'停用' }}</el-tag></template>
    </el-table-column>
    <el-table-column prop="created_at" label="注册时间" />
    <el-table-column label="操作" width="120">
      <template #default="{row}">
        <el-button size="small" :type="row.status==='active'?'danger':''" @click="toggle(row)">{{ row.status==='active'?'停用':'启用' }}</el-button>
      </template>
    </el-table-column>
  </PaginationTable>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/index'
import PaginationTable from '@/components/common/PaginationTable.vue'

const list = ref<any[]>([]); const total = ref(0); const loading = ref(false)
const page = ref(1); const pageSize = ref(20)

onMounted(fetch)
async function fetch() {
  loading.value = true
  try { const res = await api.get('/admin/merchants', { params: { page: page.value, page_size: pageSize.value } }); list.value = res.data.list; total.value = res.data.total }
  finally { loading.value = false }
}
async function toggle(row: any) {
  const newStatus = row.status === 'active' ? 'disabled' : 'active'
  await api.put(`/admin/merchants/${row.id}/status?status=${newStatus}`)
  ElMessage.success('更新成功'); fetch()
}
</script>
