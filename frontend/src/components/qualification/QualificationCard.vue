<template>
  <el-card>
    <template #header>
      <span>{{ qual.qual_type_name || `资质 #${qual.qual_type_id}` }}</span>
      <StatusTag :status="qual.status" type="qual" style="margin-left:8px" />
    </template>
    <div><a :href="qual.file_url" target="_blank">{{ qual.file_name }}</a></div>
    <div v-if="qual.expire_date">到期日期: {{ qual.expire_date }}</div>
    <slot />
  </el-card>
</template>

<script setup lang="ts">
import StatusTag from '@/components/common/StatusTag.vue'
defineProps<{ qual: any }>()
</script>
