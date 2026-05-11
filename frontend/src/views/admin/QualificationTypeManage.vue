<template>
  <div>
    <el-button type="primary" @click="openDialog()" style="margin-bottom:16px">新增资质类型</el-button>
    <el-table :data="list" border>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="code" label="编码" />
      <el-table-column prop="scope" label="适用维度" />
      <el-table-column label="必传" width="80"><template #default="{row}"><el-tag :type="row.is_required?'danger':'info'">{{ row.is_required?'是':'否' }}</el-tag></template></el-table-column>
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column label="操作" width="160">
        <template #default="{row}"><el-button size="small" @click="openDialog(row)">编辑</el-button><el-button size="small" type="danger" @click="del(row.id)">删除</el-button></template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dlg.visible" :title="dlg.isEdit ? '编辑' : '新增'" @closed="dlg.form={}">
      <el-form :model="dlg.form">
        <el-form-item label="名称"><el-input v-model="dlg.form.name" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="dlg.form.code" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="dlg.form.description" /></el-form-item>
        <el-form-item label="适用维度"><el-select v-model="dlg.form.scope"><el-option label="商家" value="merchant" /><el-option label="商品" value="product" /></el-select></el-form-item>
        <el-form-item label="是否必传"><el-switch v-model="dlg.form.is_required" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="dlg.form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg.visible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api/index'

const list = ref<any[]>([])
const dlg = reactive({ visible: false, isEdit: false, form: {} as any })

onMounted(fetchData)
async function fetchData() { const res = await api.get('/admin/qualification-types'); list.value = res.data }

function openDialog(row?: any) {
  dlg.visible = true
  if (row) { dlg.isEdit = true; dlg.form = { ...row } }
  else { dlg.isEdit = false; dlg.form = { name: '', code: '', description: '', scope: 'merchant', is_required: true, sort_order: 0 } }
}

async function save() {
  if (dlg.isEdit) {
    await api.put(`/admin/qualification-types/${dlg.form.id}`, dlg.form)
  } else {
    await api.post('/admin/qualification-types', dlg.form)
  }
  dlg.visible = false; fetchData(); ElMessage.success('保存成功')
}

async function del(id: number) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await api.delete(`/admin/qualification-types/${id}`); fetchData(); ElMessage.success('删除成功')
}
</script>
