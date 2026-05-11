import api from './index'
import type { QualificationCreate } from '@/types/qualification'

export const getMerchantQualifications = () => api.get('/merchant/qualifications')
export const createMerchantQualification = (data: QualificationCreate) => api.post('/merchant/qualifications', data)
export const updateMerchantQualification = (id: number, data: any) => api.put(`/merchant/qualifications/${id}`, data)
export const deleteMerchantQualification = (id: number) => api.delete(`/merchant/qualifications/${id}`)
