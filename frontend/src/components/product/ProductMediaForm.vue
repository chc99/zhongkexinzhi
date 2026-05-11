<template>
  <div>
    <h4>商品主图</h4>
    <UploadImage v-model="mainImages" :limit="1" />
    <h4 style="margin-top:16px">详情图片</h4>
    <UploadImage v-model="detailImages" :limit="10" />
    <h4 style="margin-top:16px">商品详情描述</h4>
    <el-input v-model="detail" type="textarea" :rows="8" placeholder="商品详情描述" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import UploadImage from '@/components/common/UploadImage.vue'

const props = defineProps<{ modelValue: { main_images: string[]; detail_images: string[]; detail: string } }>()
const emit = defineEmits(['update:modelValue'])

const mainImages = ref(props.modelValue?.main_images || [])
const detailImages = ref(props.modelValue?.detail_images || [])
const detail = ref(props.modelValue?.detail || '')

watch([mainImages, detailImages, detail], () => {
  emit('update:modelValue', { main_images: mainImages.value, detail_images: detailImages.value, detail: detail.value })
}, { deep: true })
</script>
