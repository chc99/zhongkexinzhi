<template>
  <el-form :model="form" label-width="140px">
    <el-form-item label="批准文号（蓝帽）"><el-input v-model="form.approval_number" placeholder="国食健字Gxxxxxx" /></el-form-item>
    <el-form-item label="主要原料"><el-input v-model="form.main_ingredients" type="textarea" :rows="2" /></el-form-item>
    <el-form-item label="功效成分及含量"><el-input v-model="form.efficacy_ingredients" type="textarea" :rows="2" /></el-form-item>
    <el-row>
      <el-col :span="12"><el-form-item label="适宜人群"><el-input v-model="form.suitable_population" /></el-form-item></el-col>
      <el-col :span="12"><el-form-item label="不适宜人群"><el-input v-model="form.unsuitable_population" /></el-form-item></el-col>
    </el-row>
    <el-form-item label="保健功能"><el-input v-model="form.health_function" /></el-form-item>
    <el-form-item label="食用方法及用量"><el-input v-model="form.usage_dosage" /></el-form-item>
    <el-row>
      <el-col :span="12"><el-form-item label="保质期"><el-input v-model="form.shelf_life" placeholder="如 24个月" /></el-form-item></el-col>
      <el-col :span="12"><el-form-item label="贮藏方法"><el-input v-model="form.storage_method" /></el-form-item></el-col>
    </el-row>
    <el-form-item label="注意事项"><el-input v-model="form.precautions" type="textarea" :rows="2" /></el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
const props = defineProps<{ modelValue: any }>()
const emit = defineEmits(['update:modelValue'])
const form = ref({ ...props.modelValue })
watch(form, (v) => emit('update:modelValue', { ...v }), { deep: true })
</script>
