<template>
  <el-descriptions title="商品信息预览" :column="2" border>
    <el-descriptions-item label="商品名称">{{ data.name }}</el-descriptions-item>
    <el-descriptions-item label="品牌">{{ data.brand }}</el-descriptions-item>
    <el-descriptions-item label="规格">{{ data.spec }}</el-descriptions-item>
    <el-descriptions-item label="价格">¥{{ data.price }}</el-descriptions-item>
    <el-descriptions-item label="库存">{{ data.stock }}</el-descriptions-item>
    <el-descriptions-item label="批准文号">{{ data.compliance?.approval_number }}</el-descriptions-item>
  </el-descriptions>
</template>

<script setup lang="ts">
defineProps<{ data: any }>()
</script>
