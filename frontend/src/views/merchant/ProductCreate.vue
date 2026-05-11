<template>
  <div>
    <el-steps :active="step" align-center style="margin-bottom:24px">
      <el-step title="基本信息" /><el-step title="合规信息" /><el-step title="图片详情" /><el-step title="商品资质" /><el-step title="预览提交" />
    </el-steps>
    <ProductBasicForm v-if="step===0" v-model="basic" />
    <ProductComplianceForm v-if="step===1" v-model="compliance" />
    <ProductMediaForm v-if="step===2" v-model="media" />
    <ProductQualificationForm v-if="step===3" v-model="qualifications" />
    <ProductPreview v-if="step===4" :data="previewData" />
    <div style="text-align:center;margin-top:24px">
      <el-button v-if="step>0" @click="step--">上一步</el-button>
      <el-button v-if="step<4" type="primary" @click="nextStep">下一步</el-button>
      <el-button v-if="step===4" type="success" @click="submit">确认提交</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ProductBasicForm from '@/components/product/ProductBasicForm.vue'
import ProductComplianceForm from '@/components/product/ProductComplianceForm.vue'
import ProductMediaForm from '@/components/product/ProductMediaForm.vue'
import ProductQualificationForm from '@/components/product/ProductQualificationForm.vue'
import ProductPreview from '@/components/product/ProductPreview.vue'
import { createProduct, updateProduct, submitProduct, addProductQualification } from '@/api/product'
import { useCategoryStore } from '@/stores/category'

const router = useRouter()
const step = ref(0)
const productId = ref(0)
const basic = ref({ name: '', brand: '', spec: '', category_id: 0, price: 0, stock: 0, main_image: '' })
const compliance = ref({})
const media = ref({ main_images: [] as string[], detail_images: [] as string[], detail: '' })
const qualifications = ref<Record<number, any>>({})

const store = useCategoryStore()

onMounted(async () => { await store.fetchCategories(); await store.fetchQualTypes('product') })

const previewData = computed(() => ({ ...basic.value, compliance: compliance.value }))

async function nextStep() {
  if (step.value === 0 && !productId.value) {
    const res = await createProduct(basic.value)
    productId.value = res.data.id
  }
  step.value++
}

async function submit() {
  try {
    await updateProduct(productId.value, { compliance: compliance.value, main_image: basic.value.main_image })
    for (const [typeId, data] of Object.entries(qualifications.value)) {
      if (data.file_url) {
        await addProductQualification(productId.value, {
          qual_type_id: Number(typeId), file_url: data.file_url, file_name: data.file_name, expire_date: data.expire_date || null
        })
      }
    }
    await submitProduct(productId.value)
    ElMessage.success('提交审核成功')
    router.push('/merchant/products')
  } catch (e: any) { ElMessage.error(e.message || '提交失败') }
}
</script>
