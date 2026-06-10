import { describe, expect, it } from 'vitest'

import type { PromptOptionGroup } from '@/types/generation'
import { promptConfigToText } from '@/utils/prompt'

const groups: PromptOptionGroup[] = [
  {
    key: 'visualStyle',
    label: '视觉风格',
    selection: 'multiple',
    options: [{ key: 'minimal', label: '简洁专业', prompt: '', negative: false }],
  },
]

describe('promptConfigToText', () => {
  it('turns selected prompt options into a readable summary', () => {
    const summary = promptConfigToText(
      {
        visualStyle: ['minimal'],
        color: [],
        composition: [],
        copyTone: [],
        content: [],
        platform: [],
        negative: ['no_exaggerated_claims'],
      },
      groups,
    )

    expect(summary).toContain('视觉风格：简洁专业')
    expect(summary).toContain('禁用元素：no_exaggerated_claims')
  })
})
