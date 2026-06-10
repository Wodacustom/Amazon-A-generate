<template>
  <el-dropdown v-if="user.isLoggedIn">
    <button class="user-menu" type="button">
      <span>{{ initials }}</span>
    </button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item>{{ displayName }}</el-dropdown-item>
        <el-dropdown-item>{{ user.profile.plan }} 计划</el-dropdown-item>
        <el-dropdown-item v-if="user.isAdmin">管理员</el-dropdown-item>
        <el-dropdown-item divided @click="user.logout()">退出登录</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
  <el-button v-else type="primary" @click="visible = true">登录</el-button>

  <el-dialog
    v-model="visible"
    align-center
    append-to-body
    class="login-dialog"
    modal-class="login-modal"
    width="560px"
    :show-close="false"
  >
    <div class="login-panel">
      <div class="login-panel__header">
        <div class="login-panel__mark">A+</div>
        <div>
          <h2>登录账号</h2>
          <p>登录后会同步真实积分额度，并开启管理员功能。</p>
        </div>
      </div>

      <el-form label-position="top" size="large" @keyup.enter="submit">
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="admin@local.test" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" placeholder="admin123456" show-password />
        </el-form-item>
      </el-form>

      <div class="login-panel__actions">
        <el-button size="large" @click="visible = false">取消</el-button>
        <el-button type="primary" size="large" :loading="user.loading" @click="submit">登录</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, reactive, ref } from 'vue'

import { useUserStore } from '@/stores/user'

const user = useUserStore()
const visible = ref(false)
const form = reactive({
  email: 'admin@local.test',
  password: 'admin123456',
})
const displayName = computed(() => user.profile.displayName || user.profile.name || user.profile.email)
const initials = computed(() => displayName.value.slice(0, 1).toUpperCase())

async function submit() {
  try {
    await user.login(form.email, form.password)
    visible.value = false
    ElMessage.success('登录成功')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '登录失败')
  }
}
</script>

<style scoped lang="scss">
.user-menu {
  display: grid;
  width: 36px;
  height: 36px;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: #111827;
  color: #fff;
  cursor: pointer;
  font-weight: 700;
}

:global(.login-modal) {
  background: rgb(15 23 42 / 52%);
  backdrop-filter: blur(6px);
}

:global(.login-dialog) {
  max-width: calc(100vw - 32px);
  border-radius: 12px;
  overflow: hidden;
}

:global(.login-dialog .el-dialog__header) {
  display: none;
}

:global(.login-dialog .el-dialog__body) {
  padding: 0;
}

.login-panel {
  display: grid;
  gap: 22px;
  padding: 32px;
  background: #fff;
}

.login-panel__header {
  display: flex;
  align-items: center;
  gap: 16px;

  h2 {
    margin: 0 0 6px;
    font-size: 24px;
  }

  p {
    margin: 0;
    color: var(--text-secondary);
    line-height: 1.5;
  }
}

.login-panel__mark {
  display: grid;
  width: 52px;
  height: 52px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 12px;
  background: var(--brand);
  color: #fff;
  font-size: 20px;
  font-weight: 800;
}

.login-panel__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 600px) {
  .login-panel {
    padding: 24px;
  }

  .login-panel__header {
    align-items: flex-start;
  }
}
</style>
