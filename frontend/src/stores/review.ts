import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { getReviewProducts, getReviewerDashboard } from '@/api/audit'
import type { ProductListItem } from '@/types/product'

export const useReviewStore = defineStore('review', () => {
  const list = ref<ProductListItem[]>([])
  const total = ref(0)
  const filter = reactive({ status: '', keyword: '', category_id: '', date_from: '', date_to: '', page: 1, page_size: 20 })
  const dashboard = ref({ pending_count: 0, approved_today: 0, rejected_today: 0 })

  async function fetchList() {
    const res = await getReviewProducts({ ...filter })
    list.value = res.data.list; total.value = res.data.total
  }

  async function fetchDashboard() { const res = await getReviewerDashboard(); dashboard.value = res.data }

  return { list, total, filter, dashboard, fetchList, fetchDashboard }
})
