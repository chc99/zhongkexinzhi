export interface ProductCompliance {
  approval_number: string
  main_ingredients: string
  efficacy_ingredients: string
  suitable_population: string
  unsuitable_population: string
  health_function: string
  usage_dosage: string
  shelf_life: string
  storage_method: string
  precautions: string
}

export interface ProductImage {
  id?: number
  image_type: 'main' | 'detail'
  file_url: string
  sort_order: number
}

export interface ProductCreate {
  category_id: number
  name: string
  brand: string
  spec: string
  price: number
  stock: number
  main_image: string
}

export interface ProductUpdate {
  category_id?: number
  name?: string
  brand?: string
  spec?: string
  price?: number
  stock?: number
  main_image?: string
  compliance?: ProductCompliance
}

export interface ProductListItem {
  id: number
  name: string
  brand: string
  category_name: string
  price: number
  stock: number
  main_image: string
  status: string
  submit_at: string | null
  created_at: string
}

export interface ProductDetail {
  id: number
  merchant_id: number
  category_id: number
  name: string
  brand: string
  spec: string
  price: number
  stock: number
  main_image: string
  status: string
  reject_reason: string | null
  submit_at: string | null
  audit_at: string | null
  audit_by: number | null
  version: number
  created_at: string
  updated_at: string
  compliance: ProductCompliance | null
  images: ProductImage[]
  detail: string | null
}

export interface DashboardStats {
  total_products: number
  pending_products: number
  approved_products: number
  rejected_products: number
  expiring_quals: number
  expired_quals: number
}
