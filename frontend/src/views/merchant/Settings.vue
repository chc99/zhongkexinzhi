<template>
  <el-card>
    <el-descriptions title="账号信息" :column="1" border>
      <el-descriptions-item label="用户名">{{ username }}</el-descriptions-item>
      <el-descriptions-item label="角色">商家</el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>

<script setup lang="ts">
const username = localStorage.getItem('username') || ''
</script>
