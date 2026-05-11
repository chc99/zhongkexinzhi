<template>
  <div>
    <h3>商家资质管理</h3>
    <el-row :gutter="16">
      <el-col v-for="qt in merchantQualTypes" :key="qt.id" :span="8" style="margin-bottom:16px">
        <el-card>
          <template #header>
            <span>{{ qt.name }}</span>
            <el-tag v-if="qt.is_required" type="danger" size="small" style="margin-left:8px">必传</el-tag>
          </template>
          <template v-if="getQual(qt.id)">
            <div><a :href="getQual(qt.id).file_url" target="_blank">{{ getQual(qt.id).file_name }}</a></div>
            <div v-if="getQual(qt.id).expire_date">到期: {{ getQual(qt.id).expire_date }}</div>
            <StatusTag :status="getQual(qt.id).status" type="qual" />
            <el-button size="small" type="danger" @click="deleteQual(getQual(qt.id).id)">删除</el-button>
          </template>
          <el-upload v-else :http-request="(opts:any) => doUpload(qt.id, opts)" drag :limit="1">
            <el-icon><UploadFilled /></el-icon>
            <div>点击或拖拽上传</div>
          </el-upload>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { getMerchantQualifications, createMerchantQualification, deleteMerchantQualification } from '@/api/qualification'
import { getQualificationTypes } from '@/api/category'
import { uploadFile } from '@/api/product'
import StatusTag from '@/components/common/StatusTag.vue'

const merchantQualTypes = ref<any[]>([])
const quals = ref<any[]>([])

onMounted(async () => {
  const [typesRes, qualsRes] = await Promise.all([getQualificationTypes('merchant'), getMerchantQualifications()])
  merchantQualTypes.value = typesRes.data; quals.value = qualsRes.data
})

function getQual(typeId: number) { return quals.value.find((q: any) => q.qual_type_id === typeId) }

async function doUpload(typeId: number, opts: any) {
  const fileRes = await uploadFile(opts.file)
  await createMerchantQualification({ qual_type_id: typeId, file_url: fileRes.data.url, file_name: fileRes.data.name })
  const res = await getMerchantQualifications(); quals.value = res.data
  ElMessage.success('上传成功')
}

async function deleteQual(qualId: number) {
  await deleteMerchantQualification(qualId)
  const res = await getMerchantQualifications(); quals.value = res.data
  ElMessage.success('删除成功')
}
</script>
