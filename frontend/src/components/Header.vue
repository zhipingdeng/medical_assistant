<template>
  <header class="fixed top-0 left-0 right-0 z-50 bg-white shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <div class="flex items-center">
          <router-link :to="user?.role === 'doctor' ? '/doctor' : '/patient'" class="flex items-center space-x-2">
            <div class="w-10 h-10 bg-gradient-to-br from-medical-blue to-medical-purple rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <span class="text-xl font-bold text-gray-900">医疗智能助手</span>
          </router-link>
        </div>

        <!-- 导航菜单 - 仅医生可见 -->
        <nav v-if="user?.role === 'doctor'" class="hidden md:flex items-center space-x-1">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
            :class="isActive(item.path) ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-100'"
          >
            <div class="flex items-center space-x-2">
              <span v-html="item.icon"></span>
              <span>{{ item.name }}</span>
            </div>
          </router-link>
        </nav>

        <!-- 用户区域 -->
        <div class="flex items-center space-x-4">
          <template v-if="user">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div class="hidden sm:block">
                <span class="text-sm font-medium text-gray-700">{{ user.full_name }}</span>
                <span class="ml-1 text-xs px-2 py-0.5 rounded-full" 
                      :class="user.role === 'doctor' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'">
                  {{ user.role === 'doctor' ? '医生' : '患者' }}
                </span>
              </div>
              <button @click="handleLogout" class="px-3 py-1.5 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                退出
              </button>
            </div>
          </template>

          <!-- 移动端菜单按钮 -->
          <button v-if="user?.role === 'doctor'" @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2 rounded-lg hover:bg-gray-100">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 移动端菜单 -->
      <div v-if="mobileMenuOpen && user?.role === 'doctor'" class="md:hidden py-4 border-t border-gray-100">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="block px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200"
          :class="isActive(item.path) ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-100'"
          @click="mobileMenuOpen = false"
        >
          <div class="flex items-center space-x-3">
            <span v-html="item.icon"></span>
            <span>{{ item.name }}</span>
          </div>
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const mobileMenuOpen = ref(false)
const user = ref<any>(null)

const loadUser = () => {
  const userStr = localStorage.getItem('user')
  user.value = userStr ? JSON.parse(userStr) : null
}

onMounted(loadUser)
watch(() => route.path, loadUser)

const navItems = [
  {
    name: '智能问诊',
    path: '/chat',
    icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>'
  },
  {
    name: '疾病百科',
    path: '/diseases',
    icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>'
  },
  {
    name: '知识图谱',
    path: '/knowledge',
    icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>'
  }
]

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>
