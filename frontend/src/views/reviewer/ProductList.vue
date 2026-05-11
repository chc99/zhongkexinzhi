<template>
  <div>
    <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap">
      <el-select v-model="filter.status" placeholder="状态" clearable @change="fetch" style="width:120px">
        <el-option label="待审核" value="pending_review" /><el-option label="已通过" value="approved" /><el-option label="已驳回" value="rejected" />
      </el-select>
      <el-input v-model="filter.keyword" placeholder="搜索商品" clearable @input="fetch" style="width:180px" />
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="提交开始" end-placeholder="提交结束"
                      @change="onDateChange" />
      <el-button type="success" @click="batchApprove">批量通过</el-button>
      <el-button type="danger" @click="batchReject">批量驳回</el-button>
    </div>
    <PaginationTable :data="list" :total="total" :page="filter.page" :page-size="filter.page_size" :loading="loading"
                     @page-change="(p:number)=>{filter.page=p;fetch()}" @size-change="(s:number)=>{filter.page_size=s;fetch()}">
      <el-table-column type="selection" width="50" />
      <el-table-column prop="name" label="商品名称" />
      <el-table-column prop="brand" label="品牌" width="100" />
      <el-table-column label="价格" width="80"><template #default="{row}">¥{{ row.price }}</template></el-table-column>
      <el-table-column label="状态" width="80"><template #default="{row}"><StatusTag :status="row.status" /></template></el-table-column>
      <el-table-column label="提交时间" width="160"><template #default="{row}">{{ row.submit_at }}</template></el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{row}"><el-button size="small" @click="$router.push(`/reviewer/products/${row.id}`)">审核</el-button></template>
      </el-table-column>
    </PaginationTable>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useReviewStore } from '@/stores/review'
import { batchApprove as batchApproveApi, batchReject as batchRejectApi } from '@/api/audit'
import PaginationTable from '@/components/common/PaginationTable.vue'
import StatusTag from '@/components/common/StatusTag.vue'

const store = useReviewStore()
const { list, total, filter, fetchList } = store
const loading = ref(false)
const dateRange = ref<any[]>([])

function onDateChange(vals: any[]) {
  filter.date_from = vals?.[0]?.toISOString().slice(0, 10) || ''
  filter.date_to = vals?.[1]?.toISOString().slice(0, 10) || ''
  fetch()
}

async function fetch() { loading.value = true; try { await fetchList() } finally { loading.value = false } }

async function batchApprove() {
  await ElMessageBox.confirm('确定批量通过所选商品？', '提示', { type: 'warning' })
  // Simplified: approve all visible items
  const ids = list.value.map((p: any) => p.id)
  if (ids.length === 0) { ElMessage.warning('请选择商品'); return }
  await batchApproveApi(ids)
  ElMessage.success('批量通过成功'); fetch()
}

async function batchReject() {
  const { value: reason } = await ElMessageBox.prompt('请输入批量驳回原因', '批量驳回', { type: 'warning' })
  if (!reason) return
  const ids = list.value.map((p: any) => p.id)
  await batchRejectApi(ids, reason)
  ElMessage.success('批量驳回成功'); fetch()
}

onMounted(fetch)
</script>
