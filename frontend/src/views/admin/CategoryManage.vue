<template>
  <div>
    <el-button type="primary" @click="openDialog()" style="margin-bottom:16px">新增品类</el-button>
    <el-table :data="tree" border row-key="id">
      <el-table-column prop="name" label="品类名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column prop="status" label="状态" width="80" />
      <el-table-column label="操作" width="240">
        <template #default="{row}">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" @click="openDialog(row, true)">添加子类</el-button>
          <el-button size="small" type="danger" @click="del(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dlg.visible" :title="dlg.isEdit ? '编辑品类' : '新增品类'" @closed="dlg.form={}">
      <el-form :model="dlg.form">
        <el-form-item label="名称"><el-input v-model="dlg.form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="dlg.form.description" /></el-form-item>
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

const tree = ref<any[]>([])
const dlg = reactive({ visible: false, isEdit: false, form: {} as any, parentId: null as number | null })

onMounted(fetchData)

async function fetchData() { const res = await api.get('/categories'); tree.value = res.data }

function findInTree(items: any[], id: number): any {
  for (const item of items) { if (item.id === id) return item; if (item.children?.length) { const f = findInTree(item.children, id); if (f) return f } }
  return null
}

function openDialog(row?: any, asChild = false) {
  dlg.visible = true
  if (row && !asChild) { dlg.isEdit = true; dlg.form = { id: row.id, name: row.name, description: row.description, sort_order: row.sort_order } }
  else { dlg.isEdit = false; dlg.form = { name: '', description: '', sort_order: 0 }; dlg.parentId = asChild ? row.id : null }
}

async function save() {
  if (dlg.isEdit) {
    await api.put(`/admin/categories/${dlg.form.id}`, dlg.form)
  } else {
    await api.post('/admin/categories', { ...dlg.form, parent_id: dlg.parentId })
  }
  dlg.visible = false; fetchData(); ElMessage.success('保存成功')
}

async function del(id: number) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await api.delete(`/admin/categories/${id}`); fetchData(); ElMessage.success('删除成功')
}
</script>
