export interface QualificationInfo {
  id: number
  qual_type_id: number
  qual_type_name: string
  file_url: string
  file_name: string
  expire_date: string | null
  status: string
  remark: string
  created_at: string
}

export interface QualificationTypeInfo {
  id: number
  name: string
  code: string
  description: string
  is_required: boolean
  scope: string
  sort_order: number
}

export interface QualificationCreate {
  qual_type_id: number
  file_url: string
  file_name: string
  expire_date?: string | null
}
