<template>
  <div>
    <h3>编辑商品</h3>
    <el-tabs v-model="tab">
      <el-tab-pane label="基本信息" name="basic"><ProductBasicForm v-model="form" /></el-tab-pane>
      <el-tab-pane label="合规信息" name="compliance"><ProductComplianceForm v-model="compliance" /></el-tab-pane>
      <el-tab-pane label="图片详情" name="media"><ProductMediaForm v-model="media" /></el-tab-pane>
      <el-tab-pane label="商品资质" name="quals"><ProductQualificationForm v-model="qualifications" /></el-tab-pane>
      <el-tab-pane label="版本历史" name="versions">
        <VersionHistory v-if="versions.length" :versions="versions" />
        <el-empty v-else description="暂无版本记录" />
      </el-tab-pane>
    </el-tabs>
    <div style="text-align:center;margin-top:16px">
      <el-button type="primary" @click="save">保存草稿</el-button>
      <el-button type="success" @click="submit">提交审核</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ProductBasicForm from '@/components/product/ProductBasicForm.vue'
import ProductComplianceForm from '@/components/product/ProductComplianceForm.vue'
import ProductMediaForm from '@/components/product/ProductMediaForm.vue'
import ProductQualificationForm from '@/components/product/ProductQualificationForm.vue'
import VersionHistory from '@/components/audit/VersionHistory.vue'
import { getProduct, updateProduct, submitProduct, getProductVersions } from '@/api/product'
import { useCategoryStore } from '@/stores/category'

const route = useRoute()
const router = useRouter()
const tab = ref('basic')
const id = Number(route.params.id)
const form = ref({ name: '', brand: '', spec: '', category_id: 0, price: 0, stock: 0, main_image: '' })
const compliance = ref({})
const media = ref({ main_images: [] as string[], detail_images: [] as string[], detail: '' })
const qualifications = ref<Record<number, any>>({})
const versions = ref<any[]>([])

const store = useCategoryStore()

onMounted(async () => {
  await store.fetchCategories()
  await store.fetchQualTypes('product')
  const res = await getProduct(id)
  const p = res.data
  form.value = { name: p.name, brand: p.brand, spec: p.spec, category_id: p.category_id, price: p.price, stock: p.stock, main_image: p.main_image }
  compliance.value = p.compliance || {}
  media.value = {
    main_images: p.images?.filter((i: any) => i.image_type === 'main').map((i: any) => i.file_url) || [],
    detail_images: p.images?.filter((i: any) => i.image_type === 'detail').map((i: any) => i.file_url) || [],
    detail: p.detail || ''
  }
  try { const v = await getProductVersions(id); versions.value = v.data } catch {}
})

async function save() {
  await updateProduct(id, { ...form.value, compliance: compliance.value })
  ElMessage.success('保存成功')
}

async function submit() {
  await save()
  await submitProduct(id)
  ElMessage.success('提交审核成功')
  router.push('/merchant/products')
}
</script>
