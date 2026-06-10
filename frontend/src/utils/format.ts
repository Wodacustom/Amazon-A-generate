export function formatStatus(status: string) {
  const statusMap: Record<string, string> = {
    queued: '排队中',
    running: '生成中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
    partial_success: '部分成功',
  }
  return statusMap[status] || status
}

export function formatDateTime(value?: string) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}
