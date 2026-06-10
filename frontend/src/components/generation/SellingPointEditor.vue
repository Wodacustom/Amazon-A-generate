<template>
  <section class="workbench-panel form-panel">
    <div class="section-title">
      <h3>商品信息与卖点</h3>
      <el-button :loading="recommending" @click="recommendInfo">AI 推荐</el-button>
    </div>
    <el-form label-position="top">
      <el-form-item label="商品名称">
        <el-input v-model="product.productInfo.productName" placeholder="例如 Portable Grinder" />
      </el-form-item>
      <el-form-item label="核心卖点">
        <el-input
          v-model="product.productInfo.coreSellingPoints"
          type="textarea"
          :rows="4"
          placeholder="用分号或换行拆分核心卖点，也可以点击 AI 推荐自动生成"
        />
      </el-form-item>
      <el-form-item label="目标用户">
        <el-input v-model="product.productInfo.targetAudience" placeholder="例如 Coffee lovers" />
      </el-form-item>
      <el-form-item label="使用场景">
        <el-input v-model="product.productInfo.useScenes" placeholder="旅行、办公室、家庭等" />
      </el-form-item>
      <el-form-item label="规格 / 合规">
        <el-input v-model="product.productInfo.specifications" placeholder="尺寸、材质、容量等" />
      </el-form-item>
      <el-form-item label="禁用词 / 合规备注">
        <el-input v-model="product.productInfo.forbiddenWords" placeholder="避免绝对化、医疗化或平台禁词" />
      </el-form-item>
      <el-alert
        v-if="assumptions.length"
        class="assumption-alert"
        type="info"
        :closable="false"
        show-icon
        :title="`AI 已补全 ${recommendationSource} 草稿，仍需人工确认规格和合规信息。`"
      >
        <template #default>
          <span>{{ assumptions.join('；') }}</span>
        </template>
      </el-alert>
    </el-form>
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { ref } from 'vue'

import { recommendProductInfo } from '@/api/product'
import { useGenerationStore } from '@/stores/generation'
import { useProductStore } from '@/stores/product'

const product = useProductStore()
const generation = useGenerationStore()
const recommending = ref(false)
const assumptions = ref<string[]>([])
const recommendationSource = ref('')

async function recommendInfo() {
  recommending.value = true
  ElMessage.info(product.readyImages.length ? '正在看图识别商品并生成卖点...' : '正在根据已填信息生成卖点草稿...')
  try {
    const response = await recommendProductInfo({
      productInfo: product.productInfo,
      images: product.readyImages.map((image) => image.url),
      platform: generation.settings.platform,
      country: generation.settings.country,
      language: generation.settings.language,
      designStyle: generation.settings.designStyle,
    })
    product.productInfo = response.productInfo
    assumptions.value = response.assumptions
    recommendationSource.value = response.source
    ElMessage.success(response.source === 'gemini' ? 'AI 已生成商品信息与卖点' : '已生成可编辑卖点草稿')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '商品信息推荐失败')
  } finally {
    recommending.value = false
  }
}
</script>

<style scoped lang="scss">
.form-panel {
  padding: 16px;
}

.section-title {
  align-items: center;
}

.assumption-alert {
  margin-top: 8px;
}
</style>
