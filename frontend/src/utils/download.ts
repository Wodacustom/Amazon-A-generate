export async function downloadImage(url: string, filename: string) {
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error('图片下载失败')
  }
  const blob = await response.blob()
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(objectUrl)
}

export function imageFilename(title: string, url: string) {
  const extension = url.split('?')[0]?.split('.').pop() || 'png'
  const safeTitle = title.replace(/[\\/:*?"<>|]+/g, '-').trim() || 'aplus-image'
  return `${safeTitle}.${extension}`
}
