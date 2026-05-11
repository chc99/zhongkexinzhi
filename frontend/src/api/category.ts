import api from './index'

export const getCategories = () => api.get('/categories')
export const getQualificationTypes = (scope?: string) => api.get('/qualification-types', { params: { scope } })
