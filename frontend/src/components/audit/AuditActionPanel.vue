<template>
  <div>
    <el-button type="success" size="large" @click="$emit('approve')">审核通过</el-button>
    <el-popconfirm title="确定驳回该商品？" @confirm="confirmReject">
      <template #reference><el-button type="danger" size="large" style="margin-left:16px">驳回</el-button></template>
      <div style="margin-top:8px">
        <el-input v-model="reason" placeholder="请输入驳回原因（必填）" style="width:300px" />
      </div>
    </el-popconfirm>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const emit = defineEmits(['approve', 'reject'])
const reason = ref('')
function confirmReject() {
  if (!reason.value.trim()) return
  emit('reject', reason.value)
}
</script>
