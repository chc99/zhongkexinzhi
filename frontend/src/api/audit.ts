import api from './index'

export const getReviewProducts = (params: Record<string, any>) => api.get('/reviewer/products', { params })
export const getReviewProduct = (id: number) => api.get(`/reviewer/products/${id}`)
export const approveProduct = (id: number) => api.post(`/reviewer/products/${id}/approve`)
export const rejectProduct = (id: number, reason: string) => api.post(`/reviewer/products/${id}/reject`, { reason })
export const batchApprove = (ids: number[]) => api.post('/reviewer/products/batch-approve', { ids })
export const batchReject = (ids: number[], reason: string) => api.post(`/reviewer/products/batch-reject?reason=${encodeURIComponent(reason)}`, { ids })
export const getReviewerDashboard = () => api.get('/reviewer/dashboard')
