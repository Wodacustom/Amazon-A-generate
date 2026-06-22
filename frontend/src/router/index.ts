import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/aplus-detail', name: 'aplus-detail', component: () => import('@/views/APlusDetail.vue') },
    { path: '/templates', name: 'templates', component: () => import('@/views/TemplateGallery.vue') },
    { path: '/style-memory', name: 'style-memory', component: () => import('@/views/StyleMemory.vue') },
    { path: '/tasks', name: 'tasks', component: () => import('@/views/TaskCenter.vue') },
    { path: '/results', name: 'results', component: () => import('@/views/ResultDetail.vue') },
    { path: '/results/:id', name: 'result-detail', component: () => import('@/views/ResultDetail.vue') },
    { path: '/product-images', name: 'product-images', component: () => import('@/views/ProductImages.vue') },
    { path: '/image-generation', name: 'image-generation', component: () => import('@/views/ImageGeneration.vue') },
    { path: '/tryon', name: 'tryon', component: () => import('@/views/TryonAutomation.vue') },
    { path: '/continuous-edit', name: 'continuous-edit', component: () => import('@/views/ContinuousEdit.vue') },
    { path: '/admin', name: 'admin', component: () => import('@/views/AdminPanel.vue') },
    { path: '/model-config', name: 'model-config', component: () => import('@/views/ModelConfig.vue') },
    {
      path: '/team',
      name: 'team',
      component: () => import('@/views/PlaceholderView.vue'),
      props: { title: '团队', description: '团队成员、角色权限、团队风格库和团队额度将在这里管理。' },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/PlaceholderView.vue'),
      props: { title: '设置', description: '默认平台、国家、语言、图片比例、质量等级和数据偏好设置。' },
    },
  ],
})

export default router
