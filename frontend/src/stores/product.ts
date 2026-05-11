import { defineStore } from 'pinia'
import { ref } from 'vue'
import { updateProduct } from '@/api/product'
import type { ProductDetail, ProductCompliance } from '@/types/product'

export const useProductStore = defineStore('product', () => {
  const current = ref<Partial<ProductDetail>>({})
  const compliance = ref<ProductCompliance>({
    approval_number: '', main_ingredients: '', efficacy_ingredients: '',
    suitable_population: '', unsuitable_population: '', health_function: '',
    usage_dosage: '', shelf_life: '', storage_method: '', precautions: ''
  })

  let saveTimer: ReturnType<typeof setTimeout> | null = null

  function setCurrent(p: ProductDetail) {
    current.value = p
    if (p.compliance) compliance.value = p.compliance
  }

  function autoSave() {
    if (!current.value.id) return
    if (saveTimer) clearTimeout(saveTimer)
    saveTimer = setTimeout(async () => {
      try {
        await updateProduct(current.value.id!, {
          name: current.value.name,
          brand: current.value.brand,
          spec: current.value.spec,
          price: current.value.price,
          stock: current.value.stock,
          main_image: current.value.main_image,
          category_id: current.value.category_id,
          compliance: compliance.value,
        })
      } catch { /* silent save */ }
    }, 3000)
  }

  return { current, compliance, setCurrent, autoSave }
})
