export const ProductStatus: Record<string, string> = {
  draft: '草稿',
  pending_review: '待审核',
  approved: '已通过',
  rejected: '已驳回',
}

export const ProductStatusColor: Record<string, string> = {
  draft: 'info',
  pending_review: 'warning',
  approved: 'success',
  rejected: 'danger',
}

export const QualStatus: Record<string, string> = {
  valid: '有效',
  expiring: '即将到期',
  expired: '已过期',
}

export const QualStatusColor: Record<string, string> = {
  valid: 'success',
  expiring: 'warning',
  expired: 'danger',
}

export const ChangeType: Record<string, string> = {
  submit: '提交审核',
  approve: '审核通过',
  reject: '审核驳回',
  resubmit: '重新提交',
}
