export const WARNING_LEVEL = {
  NORMAL: 'normal',
  ATTENTION: 'attention',
  URGENT: 'urgent',
  OUT_OF_STOCK: 'out_of_stock'
}

export function statusText(status) {
  const map = {
    draft: '草稿',
    approved: '已审批',
    received: '已到货',
    cancelled: '已取消'
  }
  return map[status] || status
}

export function warningLevelText(level) {
  const map = {
    [WARNING_LEVEL.NORMAL]: '正常',
    [WARNING_LEVEL.ATTENTION]: '关注',
    [WARNING_LEVEL.URGENT]: '紧急',
    [WARNING_LEVEL.OUT_OF_STOCK]: '断货'
  }
  return map[level] || level
}

export function warningLevelVariant(level) {
  const map = {
    [WARNING_LEVEL.NORMAL]: 'success',
    [WARNING_LEVEL.ATTENTION]: 'warning',
    [WARNING_LEVEL.URGENT]: 'danger',
    [WARNING_LEVEL.OUT_OF_STOCK]: 'out_of_stock'
  }
  return map[level] || 'neutral'
}

export function formatDateTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}
