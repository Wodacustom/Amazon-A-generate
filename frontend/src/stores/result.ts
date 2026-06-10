import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import {
  createResultVersion,
  listResultVersions,
  restoreResultVersion,
  updateGenerationResult,
} from '@/api/generation'
import type { GeneratedModule, GenerationResult, ResultVersion } from '@/types/result'

export const useResultStore = defineStore('result', () => {
  const currentResult = ref<GenerationResult>()
  const activeModuleId = ref<string>()
  const versions = ref<ResultVersion[]>([])
  const versionLoading = ref(false)

  const activeModule = computed<GeneratedModule | undefined>(() =>
    currentResult.value?.modules.find((module) => module.id === activeModuleId.value) || currentResult.value?.modules[0],
  )

  function setResult(result: GenerationResult) {
    currentResult.value = result
    activeModuleId.value = result.modules[0]?.id
    versions.value = []
  }

  function selectModule(moduleId: string) {
    activeModuleId.value = moduleId
  }

  function updateActiveModule(patch: Partial<GeneratedModule>) {
    if (!currentResult.value || !activeModule.value) return
    currentResult.value.modules = currentResult.value.modules.map((module) =>
      module.id === activeModule.value?.id ? { ...module, ...patch } : module,
    )
  }

  async function loadVersions(resultId = currentResult.value?.id) {
    if (!resultId) {
      versions.value = []
      return versions.value
    }
    versionLoading.value = true
    try {
      versions.value = await listResultVersions(resultId)
      return versions.value
    } finally {
      versionLoading.value = false
    }
  }

  async function saveCurrentVersion(label = '手动保存') {
    if (!currentResult.value) return undefined
    versionLoading.value = true
    try {
      const selectedModuleId = activeModuleId.value
      const saved = await updateGenerationResult(currentResult.value.id, {
        ...currentResult.value,
        versionLabel: label,
      })
      currentResult.value = saved
      activeModuleId.value = selectedModuleId || saved.modules[0]?.id
      await loadVersions(saved.id)
      return saved
    } finally {
      versionLoading.value = false
    }
  }

  async function createManualVersion(label = '手动保存') {
    if (!currentResult.value) return undefined
    versionLoading.value = true
    try {
      const version = await createResultVersion(currentResult.value.id, label)
      await loadVersions(currentResult.value.id)
      return version
    } finally {
      versionLoading.value = false
    }
  }

  async function restoreVersion(versionId: string) {
    if (!currentResult.value) return undefined
    versionLoading.value = true
    try {
      const restored = await restoreResultVersion(currentResult.value.id, versionId)
      currentResult.value = restored
      activeModuleId.value = restored.modules[0]?.id
      await loadVersions(restored.id)
      return restored
    } finally {
      versionLoading.value = false
    }
  }

  return {
    currentResult,
    activeModuleId,
    activeModule,
    versions,
    versionLoading,
    setResult,
    selectModule,
    updateActiveModule,
    loadVersions,
    saveCurrentVersion,
    createManualVersion,
    restoreVersion,
  }
})
