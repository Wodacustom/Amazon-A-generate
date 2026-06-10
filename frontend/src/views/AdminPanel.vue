<template>
  <div class="admin-page">
    <section class="admin-header">
      <div>
        <h1>管理员</h1>
        <p>创建账号、分配积分、生成积分卡密。</p>
      </div>
      <el-input v-model="accessToken" class="token-input" placeholder="粘贴管理员 accessToken" show-password />
      <el-button type="primary" :loading="loading" @click="loadAdminData">加载数据</el-button>
    </section>

    <div class="admin-grid">
      <section class="workbench-panel admin-card">
        <div class="section-title">
          <h3>注册用户</h3>
        </div>
        <el-form label-position="top">
          <el-form-item label="邮箱">
            <el-input v-model="userDraft.email" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="userDraft.password" show-password />
          </el-form-item>
          <el-form-item label="显示名称">
            <el-input v-model="userDraft.displayName" />
          </el-form-item>
          <div class="form-row">
            <el-form-item label="角色">
              <el-select v-model="userDraft.role">
                <el-option label="普通用户" value="user" />
                <el-option label="管理员" value="admin" />
              </el-select>
            </el-form-item>
            <el-form-item label="初始积分">
              <el-input-number v-model="userDraft.credits" :min="0" />
            </el-form-item>
          </div>
          <el-button type="primary" :loading="submittingUser" @click="createUser">创建账号</el-button>
        </el-form>
      </section>

      <section class="workbench-panel admin-card">
        <div class="section-title">
          <h3>生成卡密</h3>
        </div>
        <el-form label-position="top">
          <div class="form-row">
            <el-form-item label="每张积分">
              <el-input-number v-model="codeDraft.amount" :min="1" />
            </el-form-item>
            <el-form-item label="数量">
              <el-input-number v-model="codeDraft.count" :min="1" :max="200" />
            </el-form-item>
          </div>
          <el-form-item label="备注">
            <el-input v-model="codeDraft.note" />
          </el-form-item>
          <el-button type="primary" :loading="submittingCodes" @click="createCodes">生成卡密</el-button>
        </el-form>
      </section>
    </div>

    <section class="workbench-panel admin-card">
      <div class="section-title">
        <h3>用户积分</h3>
        <el-tag>{{ users.length }} 个账号</el-tag>
      </div>
      <el-table :data="users" height="360">
        <el-table-column prop="email" label="邮箱" min-width="220" />
        <el-table-column prop="displayName" label="名称" min-width="140" />
        <el-table-column prop="role" label="角色" width="100" />
        <el-table-column prop="plan" label="计划" width="100" />
        <el-table-column prop="credits" label="积分" width="100" />
        <el-table-column label="调整积分" min-width="260">
          <template #default="{ row }">
            <div class="adjust-row">
              <el-input-number v-model="adjustments[row.id]" />
              <el-button size="small" @click="adjustCredits(row.id)">提交</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <section class="workbench-panel admin-card">
      <div class="section-title">
        <h3>积分卡密</h3>
        <el-tag>{{ codes.length }} 张</el-tag>
      </div>
      <el-table :data="codes" height="360">
        <el-table-column prop="code" label="卡密" min-width="240" />
        <el-table-column prop="amount" label="积分" width="100" />
        <el-table-column prop="status" label="状态" width="110" />
        <el-table-column prop="note" label="备注" min-width="160" />
        <el-table-column prop="redeemedByUserId" label="兑换用户" min-width="220" />
      </el-table>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'

import {
  adminAdjustCredits,
  adminCreateCreditCodes,
  adminCreateUser,
  adminListCreditCodes,
  adminListUsers,
} from '@/api/auth'
import { useUserStore } from '@/stores/user'
import type { CreditRedemptionCode, UserProfile } from '@/types/user'

const user = useUserStore()
const accessToken = ref(user.accessToken || localStorage.getItem('accessToken') || localStorage.getItem('adminAccessToken') || '')
const loading = ref(false)
const submittingUser = ref(false)
const submittingCodes = ref(false)
const users = ref<UserProfile[]>([])
const codes = ref<CreditRedemptionCode[]>([])
const adjustments = reactive<Record<string, number>>({})

const userDraft = reactive({
  email: '',
  password: '',
  displayName: '',
  plan: 'free',
  credits: 0,
  role: 'user',
})

const codeDraft = reactive({
  amount: 100,
  count: 1,
  note: '',
})

async function loadAdminData() {
  if (!accessToken.value) {
    ElMessage.warning('请先粘贴管理员 accessToken')
    return
  }
  loading.value = true
  try {
    localStorage.setItem('adminAccessToken', accessToken.value)
    localStorage.setItem('accessToken', accessToken.value)
    const [userItems, codeItems] = await Promise.all([
      adminListUsers(accessToken.value),
      adminListCreditCodes(accessToken.value),
    ])
    users.value = userItems
    codes.value = codeItems
  } finally {
    loading.value = false
  }
}

async function createUser() {
  submittingUser.value = true
  try {
    await adminCreateUser(accessToken.value, { ...userDraft })
    ElMessage.success('账号已创建')
    userDraft.email = ''
    userDraft.password = ''
    userDraft.displayName = ''
    userDraft.credits = 0
    await loadAdminData()
  } finally {
    submittingUser.value = false
  }
}

async function adjustCredits(userId: string) {
  const amount = adjustments[userId] || 0
  if (!amount) {
    ElMessage.warning('请输入需要增减的积分')
    return
  }
  await adminAdjustCredits(accessToken.value, { userId, amount, reason: 'admin_adjustment' })
  adjustments[userId] = 0
  ElMessage.success('积分已更新')
  await loadAdminData()
}

async function createCodes() {
  submittingCodes.value = true
  try {
    await adminCreateCreditCodes(accessToken.value, { ...codeDraft })
    ElMessage.success('卡密已生成')
    await loadAdminData()
  } finally {
    submittingCodes.value = false
  }
}
</script>

<style scoped lang="scss">
.admin-page {
  display: grid;
  gap: 16px;
}

.admin-header {
  display: grid;
  align-items: end;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 420px) auto;
  gap: 12px;

  h1 {
    margin: 0 0 4px;
  }

  p {
    margin: 0;
    color: var(--text-secondary);
  }
}

.token-input {
  width: 100%;
}

.admin-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.admin-card {
  padding: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.adjust-row {
  display: flex;
  gap: 8px;
}

@media (max-width: 980px) {
  .admin-header,
  .admin-grid {
    grid-template-columns: 1fr;
  }
}
</style>
