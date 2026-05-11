import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getCategories, getQualificationTypes } from '@/api/category'
import type { CategoryInfo } from '@/types/category'
import type { QualificationTypeInfo } from '@/types/qualification'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<CategoryInfo[]>([])
  const qualTypes = ref<QualificationTypeInfo[]>([])

  async function fetchCategories() { const res = await getCategories(); categories.value = res.data }
  async function fetchQualTypes(scope?: string) { const res = await getQualificationTypes(scope); qualTypes.value = res.data }

  return { categories, qualTypes, fetchCategories, fetchQualTypes }
})
