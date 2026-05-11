<template>
  <el-row :gutter="16">
    <el-col :span="8"><el-statistic title="待审核商品" :value="dashboard.pending_count" /></el-col>
    <el-col :span="8"><el-statistic title="今日通过" :value="dashboard.approved_today" /></el-col>
    <el-col :span="8"><el-statistic title="今日驳回" :value="dashboard.rejected_today" /></el-col>
  </el-row>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useReviewStore } from '@/stores/review'
const store = useReviewStore()
const { dashboard } = store
onMounted(() => store.fetchDashboard())
</script>
