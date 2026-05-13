<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-gradient-to-br from-medical-blue to-medical-purple rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
          <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </div>
        <h2 class="text-3xl font-bold text-gray-900">医疗智能助手</h2>
        <p class="text-gray-500 mt-2">{{ isLogin ? '欢迎回来，请登录您的账号' : '创建新账号，开始使用智能医疗服务' }}</p>
      </div>

      <!-- 表单卡片 -->
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <!-- 切换标签 -->
        <div class="flex mb-6 bg-gray-100 rounded-lg p-1">
          <button @click="isLogin = true" :class="['flex-1 py-2.5 rounded-md text-sm font-medium transition-all', isLogin ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500']">
            登录
          </button>
          <button @click="isLogin = false" :class="['flex-1 py-2.5 rounded-md text-sm font-medium transition-all', !isLogin ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500']">
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <form v-if="isLogin" @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">用户名</label>
            <input v-model="loginForm.username" type="text" class="input" placeholder="请输入用户名" required />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">密码</label>
            <input v-model="loginForm.password" type="password" class="input" placeholder="请输入密码" required />
          </div>
          <button type="submit" class="btn-primary w-full py-3 text-base" :disabled="loading">
            <span v-if="!loading">登 录</span>
            <div v-else class="loading-spinner mx-auto"></div>
          </button>
        </form>

        <!-- 注册表单 -->
        <form v-else @submit.prevent="handleRegister" class="space-y-4">
          <!-- 角色选择 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">选择身份</label>
            <div class="flex gap-4">
              <label :class="['flex-1 flex items-center justify-center p-4 rounded-xl border-2 cursor-pointer transition-all', registerForm.role === 'patient' ? 'border-primary-500 bg-primary-50 shadow-sm' : 'border-gray-200 hover:border-gray-300']">
                <input v-model="registerForm.role" type="radio" value="patient" class="sr-only" />
                <div class="text-center">
                  <div class="w-12 h-12 mx-auto mb-2 rounded-full flex items-center justify-center" :class="registerForm.role === 'patient' ? 'bg-primary-100' : 'bg-gray-100'">
                    <svg class="w-7 h-7" :class="registerForm.role === 'patient' ? 'text-primary-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <span class="text-sm font-semibold" :class="registerForm.role === 'patient' ? 'text-primary-700' : 'text-gray-500'">患者</span>
                  <p class="text-xs text-gray-400 mt-1">提交问诊，获取回执</p>
                </div>
              </label>
              <label :class="['flex-1 flex items-center justify-center p-4 rounded-xl border-2 cursor-pointer transition-all', registerForm.role === 'doctor' ? 'border-primary-500 bg-primary-50 shadow-sm' : 'border-gray-200 hover:border-gray-300']">
                <input v-model="registerForm.role" type="radio" value="doctor" class="sr-only" />
                <div class="text-center">
                  <div class="w-12 h-12 mx-auto mb-2 rounded-full flex items-center justify-center" :class="registerForm.role === 'doctor' ? 'bg-primary-100' : 'bg-gray-100'">
                    <svg class="w-7 h-7" :class="registerForm.role === 'doctor' ? 'text-primary-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <span class="text-sm font-semibold" :class="registerForm.role === 'doctor' ? 'text-primary-700' : 'text-gray-500'">医生</span>
                  <p class="text-xs text-gray-400 mt-1">AI辅助，管理问诊</p>
                </div>
              </label>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">姓名</label>
            <input v-model="registerForm.full_name" type="text" class="input" placeholder="请输入真实姓名" required />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">用户名</label>
            <input v-model="registerForm.username" type="text" class="input" placeholder="请输入用户名" required />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">邮箱</label>
            <input v-model="registerForm.email" type="email" class="input" placeholder="请输入邮箱" required />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">密码</label>
            <input v-model="registerForm.password" type="password" class="input" placeholder="请输入密码（至少6位）" required minlength="6" />
          </div>

          <!-- 医生专属字段 -->
          <template v-if="registerForm.role === 'doctor'">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">科室</label>
                <input v-model="registerForm.department" type="text" class="input" placeholder="如：内科" required />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">职称</label>
                <input v-model="registerForm.title" type="text" class="input" placeholder="如：主任医师" required />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">专长</label>
              <input v-model="registerForm.specialization" type="text" class="input" placeholder="如：心血管疾病" />
            </div>
          </template>

          <!-- 患者专属字段 -->
          <template v-if="registerForm.role === 'patient'">
            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">年龄</label>
                <input v-model.number="registerForm.age" type="number" class="input" placeholder="年龄" min="0" max="150" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">性别</label>
                <select v-model="registerForm.gender" class="input">
                  <option value="">请选择</option>
                  <option value="男">男</option>
                  <option value="女">女</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">电话</label>
                <input v-model="registerForm.phone" type="tel" class="input" placeholder="手机号" />
              </div>
            </div>
          </template>

          <button type="submit" class="btn-primary w-full py-3 text-base" :disabled="loading">
            <span v-if="!loading">注 册</span>
            <div v-else class="loading-spinner mx-auto"></div>
          </button>
        </form>

        <!-- 错误提示 -->
        <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm flex items-center">
          <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ error }}
        </div>

        <!-- 成功提示 -->
        <div v-if="success" class="mt-4 p-3 bg-green-50 text-green-600 rounded-lg text-sm flex items-center">
          <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ success }}
        </div>
      </div>

      <!-- 底部信息 -->
      <p class="text-center text-xs text-gray-400 mt-8">
        本系统仅供医疗参考，不构成诊断建议
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { authApi } from '@/api/auth'
import type { UserRegister, UserLogin } from '@/types'

const isLogin = ref(true)
const loading = ref(false)
const error = ref('')
const success = ref('')

const loginForm = reactive<UserLogin>({
  username: '',
  password: ''
})

const registerForm = reactive<UserRegister>({
  username: '',
  email: '',
  password: '',
  full_name: '',
  role: 'patient',
  department: '',
  title: '',
  specialization: '',
  age: undefined,
  gender: '',
  phone: ''
})

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const result = await authApi.login(loginForm)
    localStorage.setItem('token', result.access_token)
    localStorage.setItem('user', JSON.stringify(result.user))
    // Force reload to update header state
    if (result.user.role === 'doctor') {
      window.location.href = '/doctor'
    } else {
      window.location.href = '/patient'
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const result = await authApi.register(registerForm)
    localStorage.setItem('token', result.access_token)
    localStorage.setItem('user', JSON.stringify(result.user))
    success.value = '注册成功！正在跳转...'
    setTimeout(() => {
      if (result.user.role === 'doctor') {
        window.location.href = '/doctor'
      } else {
        window.location.href = '/patient'
      }
    }, 1000)
  } catch (e: any) {
    error.value = e.response?.data?.detail || '注册失败，请检查信息'
  } finally {
    loading.value = false
  }
}
</script>
