<template>
  <el-form :model="form" :rules="rules" label-width="100px">
    <el-form-item label="商品名称" prop="name"><el-input v-model="form.name" maxlength="200" /></el-form-item>
    <el-row>
      <el-col :span="12">
        <el-form-item label="品类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="选择品类">
            <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12"><el-form-item label="品牌" prop="brand"><el-input v-model="form.brand" /></el-form-item></el-col>
    </el-row>
    <el-row>
      <el-col :span="12"><el-form-item label="规格" prop="spec"><el-input v-model="form.spec" placeholder="如 60粒/瓶" /></el-form-item></el-col>
      <el-col :span="6"><el-form-item label="价格(元)" prop="price"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item></el-col>
      <el-col :span="6"><el-form-item label="库存" prop="stock"><el-input-number v-model="form.stock" :min="0" /></el-form-item></el-col>
    </el-row>
  </el-form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCategoryStore } from '@/stores/category'
import { required } from '@/utils/validators'

const props = defineProps<{ modelValue: any }>()
const emit = defineEmits(['update:modelValue'])
const store = useCategoryStore()

const form = ref({ ...props.modelValue })

function flattenCats(cats: any[]): any[] {
  let result: any[] = []
  for (const cat of cats) { result.push(cat); if (cat.children?.length) result = result.concat(flattenCats(cat.children)) }
  return result
}
const flatCategories = computed(() => flattenCats(store.categories))

watch(form, (v) => emit('update:modelValue', { ...v }), { deep: true })

const rules = { name: [required('商品名称')], category_id: [required('品类')] }
</script>
