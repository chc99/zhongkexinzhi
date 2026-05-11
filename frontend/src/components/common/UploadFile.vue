<template>
  <el-upload :http-request="customUpload" :file-list="fileList" :on-remove="onRemove" :limit="1"
             :on-change="onChange" :auto-upload="false" drag>
    <el-icon><UploadFilled /></el-icon>
    <div class="el-upload__text">拖拽文件到此处或<em>点击上传</em></div>
    <template #tip><div class="el-upload__tip">支持 JPG/PNG/PDF，不超过 10MB</div></template>
  </el-upload>
  <el-input v-if="fileList.length && showExpire" v-model="expireDate" type="date" placeholder="到期日期" style="width:200px;margin-top:8px" />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { uploadFile } from '@/api/product'
import { UploadFilled } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: string; modelFileName?: string
  showExpire?: boolean; expireModelValue?: string
}>()
const emit = defineEmits(['update:modelValue', 'update:modelFileName', 'update:expireModelValue'])

const fileList = ref<any[]>([])
const expireDate = ref(props.expireModelValue || '')

watch(() => props.modelValue, (v) => {
  fileList.value = v ? [{ uid: 0, name: props.modelFileName || 'file', url: v, status: 'success' }] : []
}, { immediate: true })

watch(expireDate, (v) => emit('update:expireModelValue', v))

async function customUpload(opts: any) {
  const res = await uploadFile(opts.file)
  emit('update:modelValue', res.data.url)
  emit('update:modelFileName', res.data.name)
}

function onChange(_file: any, files: any[]) {
  if (files.length) customUpload({ file: files[0].raw })
}
function onRemove() {
  emit('update:modelValue', '')
  emit('update:modelFileName', '')
}
</script>
