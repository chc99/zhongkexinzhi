<template>
  <div>
    <div style="display:flex;justify-content:space-between;margin-bottom:16px">
      <div>
        <el-select v-model="filter.status" placeholder="状态筛选" clearable style="width:140px" @change="fetchData">
          <el-option v-for="(label, key) in ProductStatus" :key="key" :label="label" :value="key" />
        </el-select>
        <el-input v-model="filter.keyword" placeholder="搜索商品名称" clearable style="width:200px;margin-left:8px" @input="fetchData" />
      </div>
      <el-button type="primary" @click="$router.push('/merchant/products/create')">发布商品</el-button>
    </div>
    <PaginationTable :data="list" :total="total" :page="filter.page" :page-size="filter.page_size" :loading="loading"
                     @page-change="(p:number)=>{filter.page=p;fetchData()}" @size-change="(s:number)=>{filter.page_size=s;fetchData()}">
      <el-table-column prop="name" label="商品名称" />
      <el-table-column prop="brand" label="品牌" width="120" />
      <el-table-column label="价格" width="100"><template #default="{row}">¥{{ row.price }}</template></el-table-column>
      <el-table-column prop="stock" label="库存" width="80" />
      <el-table-column label="状态" width="100"><template #default="{row}"><StatusTag :status="row.status" /></template></el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{row}">
          <el-button size="small" @click="$router.push(`/merchant/products/${row.id}/edit`)">编辑</el-button>
          <el-button v-if="row.status==='draft'" size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </PaginationTable>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getProducts, deleteProduct } from '@/api/product'
import PaginationTable from '@/components/common/PaginationTable.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import { ProductStatus } from '@/utils/enums'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const filter = reactive({ status: '', keyword: '', page: 1, page_size: 20 })

async function fetchData() {
  loading.value = true
  try { const res = await getProducts({ ...filter }); list.value = res.data.list; total.value = res.data.total }
  finally { loading.value = false }
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm('确定删除该商品？', '提示', { type: 'warning' })
  await deleteProduct(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

onMounted(fetchData)
</script>
