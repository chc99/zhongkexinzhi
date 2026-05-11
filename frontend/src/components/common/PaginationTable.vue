<template>
  <div>
    <el-table :data="data" border stripe v-loading="loading" style="width:100%">
      <slot />
    </el-table>
    <el-pagination
      v-if="showPagination"
      :current-page="page" :page-size="pageSize" :total="total"
      :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next, jumper"
      @size-change="$emit('sizeChange', $event)"
      @current-change="$emit('pageChange', $event)"
      style="margin-top:16px;justify-content:flex-end"
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  data: any[]; loading?: boolean; total?: number
  page?: number; pageSize?: number; showPagination?: boolean
}>()
defineEmits(['sizeChange', 'pageChange'])
</script>
