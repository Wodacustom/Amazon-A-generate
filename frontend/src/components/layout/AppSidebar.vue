<template>
  <aside class="sidebar">
    <RouterLink class="sidebar__brand" to="/">
      <div class="sidebar__mark">A+</div>
      <div>
        <strong>Amazon A+ AI</strong>
        <span>Generator</span>
      </div>
    </RouterLink>

    <nav class="sidebar__nav">
      <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="sidebar__item">
        <component :is="item.icon" :size="18" />
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="sidebar__upgrade">
      <strong>专业额度</strong>
      <span>在管理员页面创建账号、分配积分和生成卡密。</span>
      <el-button size="small" type="primary">查看额度</el-button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import {
  Brush,
  Clock3,
  FileStack,
  Home,
  Images,
  LayoutTemplate,
  Settings,
  ShieldCheck,
  Users,
  WandSparkles,
} from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

const navItems = [
  { to: '/', label: '首页', icon: Home },
  { to: '/aplus-detail', label: '生成', icon: WandSparkles },
  { to: '/templates', label: '模板', icon: LayoutTemplate },
  { to: '/style-memory', label: '品牌风格', icon: Brush },
  { to: '/tasks', label: '历史记录', icon: Clock3 },
  { to: '/product-images', label: '商品套图', icon: Images },
  { to: '/team', label: '团队', icon: Users },
  { to: '/settings', label: '设置', icon: Settings },
  { to: '/continuous-edit', label: '连续改图', icon: FileStack },
  { to: '/admin', label: '管理员', icon: ShieldCheck },
]
</script>

<style scoped lang="scss">
.sidebar {
  position: sticky;
  top: 0;
  display: flex;
  height: 100vh;
  flex-direction: column;
  gap: 24px;
  border-right: 1px solid var(--line);
  background: #fffdfa;
  padding: 22px 16px;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 8px;

  span {
    display: block;
    color: var(--text-secondary);
    font-size: 12px;
  }
}

.sidebar__mark {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: var(--radius);
  background: var(--brand);
  color: #fff;
  font-weight: 800;
}

.sidebar__nav {
  display: grid;
  gap: 4px;
}

.sidebar__item {
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: var(--radius);
  color: var(--text-secondary);
  padding: 10px 12px;
  font-size: 14px;

  &.router-link-active {
    position: relative;
    background: var(--brand-soft);
    color: var(--brand-dark);
    font-weight: 700;
  }

  &.router-link-active::before {
    position: absolute;
    left: 0;
    width: 3px;
    height: 20px;
    border-radius: 99px;
    background: var(--brand);
    content: '';
  }
}

.sidebar__upgrade {
  display: grid;
  gap: 10px;
  margin-top: auto;
  border: 1px solid #d8b9a4;
  border-radius: var(--radius);
  background: var(--accent-soft);
  padding: 14px;

  span {
    color: var(--text-secondary);
    font-size: 12px;
    line-height: 1.5;
  }
}

@media (max-width: 760px) {
  .sidebar {
    display: none;
  }
}
</style>
