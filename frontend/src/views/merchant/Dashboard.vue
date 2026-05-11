<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="6"><el-statistic title="全部商品" :value="stats.total_products" /></el-col>
      <el-col :span="6"><el-statistic title="待审核" :value="stats.pending_products" /></el-col>
      <el-col :span="6"><el-statistic title="已通过" :value="stats.approved_products" /></el-col>
      <el-col :span="6"><el-statistic title="已驳回" :value="stats.rejected_products" /></el-col>
    </el-row>
    <el-divider />
    <h3>资质到期提醒</h3>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-statistic title="即将到期" :value="stats.expiring_quals">
          <template #suffix><el-tag type="warning" size="small">需关注</el-tag></template>
        </el-statistic>
      </el-col>
      <el-col :span="8">
        <el-statistic title="已过期" :value="stats.expired_quals">
          <template #suffix><el-tag type="danger" size="small">立即更新</el-tag></template>
        </el-statistic>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getDashboard } from '@/api/product'

const stats = ref({ total_products: 0, pending_products: 0, approved_products: 0, rejected_products: 0, expiring_quals: 0, expired_quals: 0 })

onMounted(async () => { const res = await getDashboard(); stats.value = res.data })
</script>
