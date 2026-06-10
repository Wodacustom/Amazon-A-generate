import type { PromptConfig, PromptOptionGroup } from '@/types/generation'

const promptLabels: Record<keyof PromptConfig, string> = {
  visualStyle: '视觉风格',
  color: '色彩倾向',
  composition: '构图方式',
  copyTone: '文案语气',
  content: '内容重点',
  platform: '平台规则',
  negative: '禁用元素',
}

export function promptConfigToText(config: PromptConfig, groups: PromptOptionGroup[] = []) {
  return (Object.entries(config) as [keyof PromptConfig, string[]][])
    .filter(([, values]) => values.length > 0)
    .map(([key, values]) => {
      const group = groups.find((item) => item.key === key)
      const labels = values.map((value) => group?.options.find((option) => option.key === value)?.label || value)
      return `${promptLabels[key]}：${labels.join('、')}`
    })
    .join('\n')
}
