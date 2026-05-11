export interface AuditLogInfo {
  id: number
  reviewer_id: number
  action: string
  reason: string | null
  created_at: string
}

export interface VersionInfo {
  id: number
  version: number
  change_type: string
  changed_by: number
  remark: string
  created_at: string
}
