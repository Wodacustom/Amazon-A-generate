import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { createGenerationTask, getGenerationResult } from '@/api/generation'
import { recommendMockups as requestMockupRecommendations } from '@/api/mockup'
import { defaultGenerationSettings, defaultModules, defaultPromptConfig } from '@/data/options'
import type {
  GenerationProgressStep,
  GenerationSettings,
  GenerationTask,
  PromptConfig,
  StyleMemorySelection,
} from '@/types/generation'
import type { MockupGenerationPlan, MockupRecommendationResponse } from '@/types/mockup'
import type { ProductImage, ProductInfo } from '@/types/product'
import type { GenerationResult } from '@/types/result'
import { buildGenerationPayload } from '@/utils/buildGenerationPayload'

export const useGenerationStore = defineStore('generation', () => {
  const settings = ref<GenerationSettings>({ ...defaultGenerationSettings })
  const promptConfig = ref<PromptConfig>(structuredClone(defaultPromptConfig))
  const modules = ref<string[]>([...defaultModules])
  const styleMemory = ref<StyleMemorySelection>({ mode: 'none', updateAfterGeneration: false })
  const task = ref<GenerationTask>()
  const result = ref<GenerationResult>()
  const mockupRecommendation = ref<MockupRecommendationResponse>()
  const mockupPlan = ref<MockupGenerationPlan>()
  const mockupLoading = ref(false)
  const loading = ref(false)
  const error = ref('')
  const progress = ref(0)
  const progressStep = ref<GenerationProgressStep>()
  const progressSteps = ref<GenerationProgressStep[]>([])
  let progressTimer: number | undefined

  const hasResult = computed(() => Boolean(result.value?.modules.length))
  const isFullMockupMode = computed(() => Boolean(mockupPlan.value?.template))

  function setHomeDraft(prompt: string) {
    promptConfig.value.content = prompt ? ['home_prompt'] : []
  }

  async function run(productId: string | undefined, images: ProductImage[], productInfo: ProductInfo) {
    loading.value = true
    error.value = ''
    startProgress()
    try {
      const payload = buildGenerationPayload(
        productId,
        images,
        settings.value,
        productInfo,
        modules.value,
        promptConfig.value,
        styleMemory.value,
        mockupPlan.value,
      )
      task.value = await createGenerationTask(payload)
      setProgress(96, 'result_ready')
      result.value = await getGenerationResult(task.value.id)
      setProgress(100, 'completed')
      return result.value
    } catch (event) {
      error.value = event instanceof Error ? event.message : '生成失败'
      setProgress(progress.value || 10, 'failed')
      throw event
    } finally {
      stopProgress()
      loading.value = false
    }
  }

  function startProgress() {
    stopProgress()
    const fullMockup = isFullMockupMode.value
    progressSteps.value = [
      {
        key: 'queued',
        label: '任务已提交',
        detail: '正在整理商品图、样机图和生成参数。',
        percentage: 8,
      },
      {
        key: 'analyzing',
        label: '分析商品与样机',
        detail: fullMockup ? '正在读取产品图和整页样机结构。' : '正在分析商品卖点和模块结构。',
        percentage: 22,
      },
      {
        key: 'prompting',
        label: '生成视觉提示词',
        detail: fullMockup ? '正在组织整页 A+ 样机融合提示词。' : '正在为每个 A+ 模块组织画面提示词。',
        percentage: 38,
      },
      {
        key: 'imaging',
        label: '生成图片中',
        detail: fullMockup ? '正在将产品图融合进整页样机，请等待 1-3 分钟。' : '正在生成 A+ 模块图，请等待 1-3 分钟。',
        percentage: 68,
      },
      {
        key: 'quality_check',
        label: '整理结果',
        detail: '正在保存生成图、整理预览和质量备注。',
        percentage: 90,
      },
    ]
    setProgress(6, 'queued')
    progressTimer = window.setInterval(() => {
      if (!loading.value) return
      const next = Math.min(progress.value + nextProgressIncrement(progress.value), 95)
      const nextStep = [...progressSteps.value].reverse().find((step) => next >= step.percentage)
      progress.value = next
      progressStep.value = nextStep || progressSteps.value[0]
    }, 1800)
  }

  function nextProgressIncrement(current: number) {
    if (current < 30) return 5
    if (current < 70) return 3
    if (current < 90) return 1
    return 0.5
  }

  function setProgress(next: number, stepKey: string) {
    progress.value = next
    progressStep.value =
      progressSteps.value.find((step) => step.key === stepKey) ||
      {
        key: stepKey,
        label: stepKey === 'completed' ? '生成完成' : stepKey === 'failed' ? '生成失败' : '处理中',
        detail: stepKey === 'completed' ? '图片已生成，可以查看和编辑结果。' : error.value || '请稍后重试。',
        percentage: next,
      }
  }

  function stopProgress() {
    if (progressTimer) {
      window.clearInterval(progressTimer)
      progressTimer = undefined
    }
  }

  function selectModule(moduleKey: string, selected: boolean) {
    if (isFullMockupMode.value) {
      modules.value = ['full_aplus_mockup']
      return
    }
    modules.value = selected
      ? Array.from(new Set([...modules.value, moduleKey]))
      : modules.value.filter((item) => item !== moduleKey)
  }

  function setMockupPlan(plan: MockupGenerationPlan) {
    mockupPlan.value = plan
    if (plan.template) {
      modules.value = ['full_aplus_mockup']
    }
  }

  async function recommendMockups(images: ProductImage[], productInfo: ProductInfo) {
    mockupLoading.value = true
    error.value = ''
    try {
      mockupRecommendation.value = await requestMockupRecommendations({
        productInfo,
        images: images.filter((image) => image.uploadStatus === 'success').map((image) => image.url),
        platform: settings.value.platform,
        country: settings.value.country,
        language: settings.value.language,
        imageRatio: settings.value.imageRatio,
        designStyle: settings.value.designStyle,
      })
      mockupPlan.value = mockupRecommendation.value.selectedPlan
      if (mockupPlan.value?.template) {
        modules.value = ['full_aplus_mockup']
      }
      return mockupRecommendation.value
    } catch (event) {
      error.value = event instanceof Error ? event.message : '场景样机推荐失败'
      throw event
    } finally {
      mockupLoading.value = false
    }
  }

  return {
    settings,
    promptConfig,
    modules,
    styleMemory,
    task,
    result,
    mockupRecommendation,
    mockupPlan,
    mockupLoading,
    loading,
    error,
    progress,
    progressStep,
    progressSteps,
    hasResult,
    isFullMockupMode,
    setHomeDraft,
    run,
    selectModule,
    setMockupPlan,
    recommendMockups,
  }
})
