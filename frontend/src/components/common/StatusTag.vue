<template>
  <el-tag :type="color" size="small">{{ text }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ProductStatus, ProductStatusColor, QualStatus, QualStatusColor } from '@/utils/enums'

const props = defineProps<{ status: string; type?: 'product' | 'qual' }>()

const text = computed(() =>
  props.type === 'qual' ? (QualStatus[props.status] || props.status) : (ProductStatus[props.status] || props.status)
)
const color = computed(() =>
  props.type === 'qual' ? (QualStatusColor[props.status] || 'info') : (ProductStatusColor[props.status] || 'info')
)
</script>
