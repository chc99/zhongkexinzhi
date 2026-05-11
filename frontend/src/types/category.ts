export interface CategoryInfo {
  id: number
  parent_id: number | null
  name: string
  description: string
  sort_order: number
  status: string
  children: CategoryInfo[]
}
