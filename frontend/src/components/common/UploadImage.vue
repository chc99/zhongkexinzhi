<template>
  <el-upload :http-request="customUpload" list-type="picture-card" :file-list="fileList"
             :on-preview="onPreview" :on-remove="onRemove" :limit="limit">
    <el-icon><Plus /></el-icon>
  </el-upload>
  <el-dialog v-model="previewVisible" title="预览">
    <img :src="previewUrl" style="width:100%" />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { uploadImage } from '@/api/product'
import { Plus } from '@element-plus/icons-vue'

const props = defineProps<{ modelValue: string[]; limit?: number }>()
const emit = defineEmits(['update:modelValue'])

const fileList = ref<any[]>([])
const previewVisible = ref(false)
const previewUrl = ref('')

watch(() => props.modelValue, (v) => {
  fileList.value = (v || []).map((url, i) => ({ uid: i, name: `image-${i}`, url, status: 'success' }))
}, { immediate: true })

async function customUpload(opts: any) {
  const res = await uploadImage(opts.file)
  const urls = [...(props.modelValue || []), res.data.url]
  emit('update:modelValue', urls)
}

function onPreview(file: any) { previewUrl.value = file.url; previewVisible.value = true }
function onRemove(_file: any, files: any[]) {
  emit('update:modelValue', files.map((f: any) => f.url))
}
</script>
