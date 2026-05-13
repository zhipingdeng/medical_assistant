import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', guest: true }
  },
  {
    path: '/patient',
    name: 'Patient',
    component: () => import('@/views/Patient.vue'),
    meta: { title: '患者中心', requiresAuth: true, role: 'patient' }
  },
  {
    path: '/doctor',
    name: 'Doctor',
    component: () => import('@/views/Doctor.vue'),
    meta: { title: '医生工作台', requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue'),
    meta: { title: '智能问诊', requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/diseases',
    name: 'DiseaseList',
    component: () => import('@/views/DiseaseList.vue'),
    meta: { title: '疾病百科', requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/diseases/:name',
    name: 'DiseaseDetail',
    component: () => import('@/views/DiseaseDetail.vue'),
    meta: { title: '疾病详情', requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('@/views/Knowledge.vue'),
    meta: { title: '知识图谱', requiresAuth: true, role: 'doctor' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || '医疗智能助手'} - 医疗智能助手`
  
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  
  // Guest-only pages (login/register) - redirect if already logged in
  if (to.meta.guest) {
    if (token && user) {
      next(user.role === 'doctor' ? '/doctor' : '/patient')
      return
    }
    next()
    return
  }
  
  // Protected pages - redirect to login if not authenticated
  if (to.meta.requiresAuth) {
    if (!token || !user) {
      next('/login')
      return
    }
    
    // Check role access
    if (to.meta.role && user.role !== to.meta.role) {
      next(user.role === 'doctor' ? '/doctor' : '/patient')
      return
    }
  }
  
  next()
})

export default router
