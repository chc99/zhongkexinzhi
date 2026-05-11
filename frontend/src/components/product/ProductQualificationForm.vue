<template>
  <div>
    <h4>商品资质</h4>
    <div v-for="qt in productQualTypes" :key="qt.id" style="margin-bottom:16px">
      <label>{{ qt.name }} <el-tag v-if="qt.is_required" type="danger" size="small">必传</el-tag></label>
      <UploadFile :model-value="getQualFile(qt.id)" :model-file-name="getQualName(qt.id)"
                  :show-expire="true" :expire-model-value="getQualExpire(qt.id)"
                  @update:model-value="(v: string) => setQualFile(qt.id, v)"
                  @update:model-file-name="(v: string) => setQualName(qt.id, v)"
                  @update:expire-model-value="(v: string) => setQualExpire(qt.id, v)" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import UploadFile from '@/components/common/UploadFile.vue'
import { getQualificationTypes } from '@/api/category'

const props = defineProps<{ modelValue: Record<number, { file_url: string; file_name: string; expire_date: string }> }>()
const emit = defineEmits(['update:modelValue'])
const productQualTypes = ref<any[]>([])
const qualData = ref<Record<number, any>>({ ...props.modelValue })

onMounted(async () => { const res = await getQualificationTypes('product'); productQualTypes.value = res.data })

function getQualFile(id: number) { return qualData.value[id]?.file_url || '' }
function getQualName(id: number) { return qualData.value[id]?.file_name || '' }
function getQualExpire(id: number) { return qualData.value[id]?.expire_date || '' }
function setQualFile(id: number, v: string) { if (!qualData.value[id]) qualData.value[id] = {}; qualData.value[id].file_url = v; emit('update:modelValue', { ...qualData.value }) }
function setQualName(id: number, v: string) { if (!qualData.value[id]) qualData.value[id] = {}; qualData.value[id].file_name = v; emit('update:modelValue', { ...qualData.value }) }
function setQualExpire(id: number, v: string) { if (!qualData.value[id]) qualData.value[id] = {}; qualData.value[id].expire_date = v; emit('update:modelValue', { ...qualData.value }) }
</script>
