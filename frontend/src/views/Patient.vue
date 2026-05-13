<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <!-- 欢迎区域 -->
      <div class="bg-gradient-to-r from-medical-blue to-medical-purple rounded-2xl p-6 mb-8 text-white">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold mb-1">您好，{{ user?.full_name }}</h1>
            <p class="text-white/80">在这里提交您的症状，医生会尽快为您回复</p>
          </div>
          <div class="flex items-center gap-3">
            <button @click="showCreateForm = true" class="bg-white text-primary-600 px-6 py-3 rounded-xl font-semibold hover:bg-white/90 transition-colors flex items-center shadow-lg">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              新建问诊
            </button>
            <button @click="handleLogout" class="bg-white/20 hover:bg-white/30 text-white px-4 py-3 rounded-xl transition-colors flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              退出
            </button>
          </div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-3 gap-4 mb-8">
        <div class="bg-white rounded-xl p-4 text-center shadow-sm">
          <div class="text-2xl font-bold text-yellow-600">{{ stats.pending }}</div>
          <div class="text-sm text-gray-500">待处理</div>
        </div>
        <div class="bg-white rounded-xl p-4 text-center shadow-sm">
          <div class="text-2xl font-bold text-green-600">{{ stats.completed }}</div>
          <div class="text-sm text-gray-500">已完成</div>
        </div>
        <div class="bg-white rounded-xl p-4 text-center shadow-sm">
          <div class="text-2xl font-bold text-gray-600">{{ stats.total }}</div>
          <div class="text-sm text-gray-500">总问诊</div>
        </div>
      </div>

      <!-- 问诊单列表 -->
      <div class="space-y-4">
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-lg font-semibold text-gray-900">我的问诊记录</h2>
          <div class="flex gap-2">
            <button v-for="filter in filters" :key="filter.value"
                    @click="currentFilter = filter.value; loadConsultations()"
                    :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-all', currentFilter === filter.value ? 'bg-primary-500 text-white' : 'bg-white text-gray-600 hover:bg-gray-100']">
              {{ filter.label }}
            </button>
          </div>
        </div>

        <div v-if="loading" class="text-center py-12">
          <div class="loading-spinner w-12 h-12 mx-auto"></div>
        </div>

        <div v-else-if="consultations.length === 0" class="text-center py-16 bg-white rounded-xl">
          <svg class="w-20 h-20 text-gray-200 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-gray-400 text-lg mb-2">暂无问诊记录</p>
          <p class="text-gray-400 text-sm mb-6">点击上方按钮开始您的第一次问诊</p>
          <button @click="showCreateForm = true" class="btn-primary">立即问诊</button>
        </div>

        <div v-else v-for="c in consultations" :key="c.id"
             class="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow cursor-pointer border border-gray-100"
             @click="selectedConsultation = c">
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-3">
              <span :class="['px-3 py-1 rounded-full text-xs font-medium', statusClass(c.status)]">
                {{ statusText(c.status) }}
              </span>
              <span class="text-sm text-gray-400">#{{ c.id }}</span>
            </div>
            <span class="text-sm text-gray-400">{{ formatDate(c.created_at) }}</span>
          </div>

          <p class="text-gray-900 mb-3 font-medium">{{ c.symptoms }}</p>

          <div v-if="c.ai_diagnosis" class="p-3 bg-blue-50 rounded-lg mb-2">
            <p class="text-sm text-blue-800">
              <span class="font-medium">🤖 AI 分析：</span>
              {{ c.ai_diagnosis.substring(0, 120) }}{{ c.ai_diagnosis.length > 120 ? '...' : '' }}
            </p>
          </div>

          <div v-if="c.status === 'completed' && c.doctor_reply" class="p-3 bg-green-50 rounded-lg">
            <p class="text-sm text-green-800">
              <span class="font-medium">👨‍⚕️ {{ c.doctor_name }} 医生：</span>
              {{ c.doctor_reply.substring(0, 120) }}{{ c.doctor_reply.length > 120 ? '...' : '' }}
            </p>
          </div>

          <div v-if="c.status === 'pending'" class="mt-3 flex items-center text-sm text-amber-600">
            <svg class="w-4 h-4 mr-1 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            等待医生回复中...
          </div>
        </div>
      </div>

      <!-- 创建问诊单弹窗 -->
      <div v-if="showCreateForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-bold">新建问诊单</h3>
            <button @click="showCreateForm = false" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleCreate" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">症状描述 *</label>
              <textarea v-model="createForm.symptoms" class="input min-h-[120px]" placeholder="请详细描述您的症状，例如：&#10;- 最近3天持续头疼&#10;- 伴有恶心、乏力&#10;- 体温37.5°C" required minlength="10"></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">症状持续时间</label>
              <input v-model="createForm.symptom_duration" type="text" class="input" placeholder="如：3天、一周、一个月" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">既往病史</label>
              <textarea v-model="createForm.medical_history" class="input min-h-[80px]" placeholder="如有重大病史请填写，如：高血压5年、糖尿病3年"></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">过敏史</label>
              <input v-model="createForm.allergies" type="text" class="input" placeholder="如有药物或食物过敏史请填写" />
            </div>

            <div class="p-3 bg-amber-50 rounded-lg text-sm text-amber-700">
              <p>⚠️ 提交后系统将自动生成 AI 初步分析，医生会根据您的情况给出专业回执。</p>
            </div>

            <div class="flex gap-3 pt-2">
              <button type="button" @click="showCreateForm = false" class="flex-1 px-4 py-2.5 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50">取消</button>
              <button type="submit" class="flex-1 btn-primary py-2.5" :disabled="creating">
                <span v-if="!creating">提交问诊</span>
                <div v-else class="loading-spinner mx-auto"></div>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- 问诊单详情弹窗 -->
      <div v-if="selectedConsultation" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-bold">问诊单详情</h3>
            <button @click="selectedConsultation = null" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="space-y-4">
            <div class="flex items-center gap-3">
              <span :class="['px-3 py-1 rounded-full text-xs font-medium', statusClass(selectedConsultation.status)]">
                {{ statusText(selectedConsultation.status) }}
              </span>
              <span class="text-sm text-gray-400">#{{ selectedConsultation.id }} · {{ formatDate(selectedConsultation.created_at) }}</span>
            </div>

            <!-- 症状 -->
            <div class="p-4 bg-gray-50 rounded-xl">
              <h4 class="font-medium text-gray-700 mb-2">📋 症状描述</h4>
              <p class="text-gray-900 whitespace-pre-wrap">{{ selectedConsultation.symptoms }}</p>
              <div class="mt-3 text-sm text-gray-500 space-y-1">
                <p v-if="selectedConsultation.symptom_duration">⏱ 持续时间：{{ selectedConsultation.symptom_duration }}</p>
                <p v-if="selectedConsultation.medical_history">📖 既往病史：{{ selectedConsultation.medical_history }}</p>
                <p v-if="selectedConsultation.allergies">⚠️ 过敏史：{{ selectedConsultation.allergies }}</p>
              </div>
            </div>

            <!-- AI 诊断 -->
            <div v-if="selectedConsultation.ai_diagnosis" class="p-4 bg-blue-50 rounded-xl">
              <h4 class="font-medium text-blue-800 mb-2">🤖 AI 初步分析</h4>
              <p class="text-blue-900 whitespace-pre-wrap text-sm">{{ selectedConsultation.ai_diagnosis }}</p>
            </div>

            <!-- 医生回执 -->
            <div v-if="selectedConsultation.status === 'completed'" class="p-4 bg-green-50 rounded-xl">
              <h4 class="font-medium text-green-800 mb-2">👨‍⚕️ {{ selectedConsultation.doctor_name }} 医生的回执</h4>
              <p class="text-green-900 whitespace-pre-wrap">{{ selectedConsultation.doctor_reply }}</p>
              <div v-if="selectedConsultation.doctor_diagnosis" class="mt-3 pt-3 border-t border-green-200">
                <p class="font-medium text-green-800">诊断：{{ selectedConsultation.doctor_diagnosis }}</p>
              </div>
              <div v-if="selectedConsultation.prescription" class="mt-2 pt-3 border-t border-green-200">
                <p class="font-medium text-green-800">💊 处方建议：</p>
                <p class="text-green-900 whitespace-pre-wrap mt-1">{{ selectedConsultation.prescription }}</p>
              </div>
            </div>

            <!-- 等待中 -->
            <div v-if="selectedConsultation.status === 'pending'" class="p-4 bg-amber-50 rounded-xl text-center">
              <svg class="w-10 h-10 text-amber-400 mx-auto mb-2 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-amber-700 font-medium">等待医生回复中...</p>
              <p class="text-amber-600 text-sm mt-1">医生正在查看您的问诊单，请耐心等待</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { consultationApi } from '@/api/consultation'
import type { ConsultationResponse, ConsultationCreate, ConsultationStatus } from '@/types'

const router = useRouter()
const user = ref<any>(null)
const consultations = ref<ConsultationResponse[]>([])
const loading = ref(true)
const showCreateForm = ref(false)
const creating = ref(false)
const selectedConsultation = ref<ConsultationResponse | null>(null)
const currentFilter = ref<string>('all')

const filters = [
  { label: '全部', value: 'all' },
  { label: '待处理', value: 'pending' },
  { label: '已完成', value: 'completed' }
]

const createForm = ref<ConsultationCreate>({
  symptoms: '',
  symptom_duration: '',
  medical_history: '',
  allergies: ''
})

const stats = computed(() => {
  const all = consultations.value
  return {
    total: all.length,
    pending: all.filter(c => c.status === 'pending').length,
    completed: all.filter(c => c.status === 'completed').length
  }
})

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (!userStr) {
    router.push('/login')
    return
  }
  user.value = JSON.parse(userStr)
  loadConsultations()
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

const loadConsultations = async () => {
  loading.value = true
  try {
    const params: any = { page: 1, page_size: 50 }
    if (currentFilter.value !== 'all') {
      params.status = currentFilter.value
    }
    const result = await consultationApi.list(params)
    consultations.value = result.items
  } catch (e) {
    console.error('Failed to load consultations:', e)
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  creating.value = true
  try {
    await consultationApi.create(createForm.value)
    showCreateForm.value = false
    createForm.value = { symptoms: '', symptom_duration: '', medical_history: '', allergies: '' }
    await loadConsultations()
  } catch (e: any) {
    alert(e.response?.data?.detail || '创建失败，请重试')
  } finally {
    creating.value = false
  }
}

const statusText = (status: ConsultationStatus) => {
  const map: Record<string, string> = { pending: '待处理', in_progress: '处理中', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

const statusClass = (status: ConsultationStatus) => {
  const map: Record<string, string> = { pending: 'bg-yellow-100 text-yellow-800', in_progress: 'bg-blue-100 text-blue-800', completed: 'bg-green-100 text-green-800', cancelled: 'bg-gray-100 text-gray-800' }
  return map[status] || ''
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>
