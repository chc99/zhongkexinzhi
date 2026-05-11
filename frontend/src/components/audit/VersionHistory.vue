<template>
  <el-timeline>
    <el-timeline-item v-for="v in versions" :key="v.id" :timestamp="v.created_at" placement="top">
      <el-tag>{{ changeTypeText(v.change_type) }}</el-tag>
      <span v-if="v.remark" style="margin-left:8px;color:#999">{{ v.remark }}</span>
    </el-timeline-item>
  </el-timeline>
</template>

<script setup lang="ts">
import { ChangeType } from '@/utils/enums'
defineProps<{ versions: any[] }>()
function changeTypeText(t: string) { return (ChangeType as any)[t] || t }
</script>
