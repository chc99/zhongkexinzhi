import api from './index'
import type { ProductCreate, ProductUpdate } from '@/types/product'

export const getProducts = (params: Record<string, any>) => api.get('/merchant/products', { params })
export const createProduct = (data: ProductCreate) => api.post('/merchant/products', data)
export const getProduct = (id: number) => api.get(`/merchant/products/${id}`)
export const updateProduct = (id: number, data: ProductUpdate) => api.put(`/merchant/products/${id}`, data)
export const deleteProduct = (id: number) => api.delete(`/merchant/products/${id}`)
export const submitProduct = (id: number) => api.post(`/merchant/products/${id}/submit`)
export const getProductVersions = (id: number) => api.get(`/merchant/products/${id}/versions`)
export const getProductQualifications = (id: number) => api.get(`/merchant/products/${id}/qualifications`)
export const addProductQualification = (id: number, data: any) => api.post(`/merchant/products/${id}/qualifications`, data)
export const deleteProductQualification = (productId: number, qualId: number) => api.delete(`/merchant/products/${productId}/qualifications/${qualId}`)

export const uploadImage = (file: File) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/upload/image', fd)
}

export const uploadFile = (file: File) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/upload/file', fd)
}

export const getDashboard = () => api.get('/merchant/dashboard')
