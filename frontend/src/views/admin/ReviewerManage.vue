<template>
  <div>
    <el-button type="primary" @click="dlg.visible=true" style="margin-bottom:16px">新增审核员</el-button>
    <PaginationTable :data="list" :total="total" :page="page" :page-size="pageSize" :loading="loading"
                     @page-change="(p:number)=>{page=p;fetch()}" @size-change="(s:number)=>{pageSize=s;fetch()}">
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="phone" label="手机号" />
      <el-table-column label="状态" width="100"><template #default="{row}"><el-tag :type="row.status==='active'?'success':'danger'">{{ row.status }}</el-tag></template></el-table-column>
      <el-table-column prop="created_at" label="创建时间" />
    </PaginationTable>
    <el-dialog v-model="dlg.visible" title="新增审核员" @closed="dlg.form={}">
      <el-form :model="dlg.form">
        <el-form-item label="用户名"><el-input v-model="dlg.form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="dlg.form.password" type="password" show-password /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="dlg.form.phone" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg.visible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/index'
import PaginationTable from '@/components/common/PaginationTable.vue'

const list = ref<any[]>([]); const total = ref(0); const loading = ref(false)
const page = ref(1); const pageSize = ref(20)
const dlg = reactive({ visible: false, form: { username: '', password: '', phone: '' } })

onMounted(fetch)
async function fetch() {
  loading.value = true
  try { const res = await api.get('/admin/reviewers', { params: { page: page.value, page_size: pageSize.value } }); list.value = res.data.list; total.value = res.data.total }
  finally { loading.value = false }
}
async function save() {
  await api.post('/admin/reviewers', null, { params: dlg.form })
  dlg.visible = false; fetch(); ElMessage.success('新增成功')
}
</script>
