<template>
  <div>
    <h3>商品审核</h3>
    <el-descriptions :column="2" border>
      <el-descriptions-item label="商品名称">{{ product.name }}</el-descriptions-item>
      <el-descriptions-item label="品牌">{{ product.brand }}</el-descriptions-item>
      <el-descriptions-item label="规格">{{ product.spec }}</el-descriptions-item>
      <el-descriptions-item label="价格">¥{{ product.price }}</el-descriptions-item>
      <el-descriptions-item label="库存">{{ product.stock }}</el-descriptions-item>
      <el-descriptions-item label="批准文号">{{ product.compliance?.approval_number }}</el-descriptions-item>
      <el-descriptions-item label="主要原料" :span="2">{{ product.compliance?.main_ingredients }}</el-descriptions-item>
      <el-descriptions-item label="适宜人群">{{ product.compliance?.suitable_population }}</el-descriptions-item>
      <el-descriptions-item label="不适宜人群">{{ product.compliance?.unsuitable_population }}</el-descriptions-item>
      <el-descriptions-item label="保健功能" :span="2">{{ product.compliance?.health_function }}</el-descriptions-item>
      <el-descriptions-item label="详情描述" :span="2">{{ product.detail }}</el-descriptions-item>
    </el-descriptions>
    <div v-if="product.images?.length" style="margin-top:16px">
      <h4>商品图片</h4>
      <el-image v-for="img in product.images" :key="img.id" :src="img.file_url" style="width:120px;height:120px;margin-right:8px" />
    </div>
    <div style="margin-top:16px">
      <AuditActionPanel v-if="product.status==='pending_review'" @approve="doApprove" @reject="doReject" />
      <el-tag v-else :type="product.status==='approved'?'success':'danger'">{{ product.status==='approved'?'已通过':'已驳回' }}</el-tag>
      <div v-if="product.reject_reason" style="margin-top:8px;color:red">驳回原因: {{ product.reject_reason }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getReviewProduct, approveProduct, rejectProduct } from '@/api/audit'
import AuditActionPanel from '@/components/audit/AuditActionPanel.vue'

const route = useRoute()
const router = useRouter()
const product = ref<any>({})

onMounted(async () => { const res = await getReviewProduct(Number(route.params.id)); product.value = res.data })

async function doApprove() { await approveProduct(product.value.id); ElMessage.success('审核通过'); router.push('/reviewer/products') }
async function doReject(reason: string) { await rejectProduct(product.value.id, reason); ElMessage.success('已驳回'); router.push('/reviewer/products') }
</script>
