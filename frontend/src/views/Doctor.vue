<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部欢迎栏 -->
    <div class="bg-white border-b border-gray-100">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">医生工作台</h1>
            <p class="text-gray-500 mt-1">{{ user?.full_name }} {{ user?.title }} · {{ user?.department }}</p>
          </div>
          <button @click="handleLogout" class="flex items-center gap-2 px-4 py-2 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            退出登录
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 py-6">
      <!-- 功能入口卡片 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <router-link to="/chat" class="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-all border border-gray-100 group">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-3 group-hover:bg-blue-200 transition-colors">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h3 class="font-semibold text-gray-900">智能问诊</h3>
          <p class="text-xs text-gray-500 mt-1">AI 辅助症状分析</p>
        </router-link>

        <router-link to="/diseases" class="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-all border border-gray-100 group">
          <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-3 group-hover:bg-green-200 transition-colors">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 class="font-semibold text-gray-900">疾病百科</h3>
          <p class="text-xs text-gray-500 mt-1">8800+ 疾病数据库</p>
        </router-link>

        <router-link to="/knowledge" class="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-all border border-gray-100 group">
          <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-3 group-hover:bg-purple-200 transition-colors">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <h3 class="font-semibold text-gray-900">知识图谱</h3>
          <p class="text-xs text-gray-500 mt-1">疾病关系可视化</p>
        </router-link>

        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-3">
            <svg class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <h3 class="font-semibold text-gray-900">待处理</h3>
          <p class="text-xs text-amber-600 font-medium mt-1">{{ pendingCount }} 个问诊单</p>
        </div>
      </div>

      <!-- 问诊单管理区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <!-- 左侧：问诊单列表 (2/5) -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100">
            <div class="p-4 border-b border-gray-100">
              <div class="flex items-center justify-between mb-3">
                <h2 class="font-semibold text-gray-900">问诊单列表</h2>
                <button @click="loadConsultations" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
              <div class="flex gap-2">
                <button v-for="tab in tabs" :key="tab.value"
                        @click="activeTab = tab.value; loadConsultations()"
                        :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition-all', activeTab === tab.value ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']">
                  {{ tab.label }}
                </button>
              </div>
            </div>

            <div class="max-h-[calc(100vh-380px)] overflow-y-auto">
              <div v-if="loading" class="text-center py-12">
                <div class="loading-spinner w-10 h-10 mx-auto"></div>
              </div>

              <div v-else-if="consultations.length === 0" class="text-center py-12">
                <svg class="w-12 h-12 text-gray-200 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="text-gray-400 text-sm">{{ activeTab === 'pending' ? '暂无待处理问诊单' : '暂无记录' }}</p>
              </div>

              <div v-else>
                <div v-for="c in consultations" :key="c.id"
                     :class="['p-4 border-b border-gray-50 cursor-pointer transition-all hover:bg-gray-50', selectedId === c.id ? 'bg-primary-50 border-l-4 border-l-primary-500' : '']"
                     @click="selectConsultation(c)">
                  <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center gap-2">
                      <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', statusClass(c.status)]">
                        {{ statusText(c.status) }}
                      </span>
                      <span class="text-xs text-gray-400">#{{ c.id }}</span>
                    </div>
                    <span class="text-xs text-gray-400">{{ formatDateShort(c.created_at) }}</span>
                  </div>
                  <div class="flex items-center gap-2 mb-1.5">
                    <div class="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center">
                      <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <span class="text-sm font-medium text-gray-700">{{ c.patient_name }}</span>
                  </div>
                  <p class="text-sm text-gray-600 line-clamp-2">{{ c.symptoms }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：详情和回执 (3/5) -->
        <div class="lg:col-span-3">
          <div v-if="selectedConsultation" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 sticky top-24">
            <!-- 头部 -->
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-3">
                <h3 class="text-lg font-bold text-gray-900">问诊单 #{{ selectedConsultation.id }}</h3>
                <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', statusClass(selectedConsultation.status)]">
                  {{ statusText(selectedConsultation.status) }}
                </span>
              </div>
              <span class="text-sm text-gray-400">{{ formatDate(selectedConsultation.created_at) }}</span>
            </div>

            <!-- 患者信息 -->
            <div class="flex items-center gap-3 mb-4 p-3 bg-gray-50 rounded-xl">
              <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-gray-900">{{ selectedConsultation.patient_name }}</p>
                <p class="text-sm text-gray-500">
                  <span v-if="selectedConsultation.symptom_duration">持续 {{ selectedConsultation.symptom_duration }}</span>
                  <span v-if="selectedConsultation.medical_history"> · 病史：{{ selectedConsultation.medical_history }}</span>
                </p>
              </div>
            </div>

            <!-- 症状描述 -->
            <div class="mb-4">
              <h4 class="font-medium text-gray-700 mb-2 flex items-center">
                <span class="w-1.5 h-5 bg-red-400 rounded-full mr-2"></span>
                症状描述
              </h4>
              <p class="text-gray-900 bg-gray-50 p-4 rounded-xl whitespace-pre-wrap">{{ selectedConsultation.symptoms }}</p>
            </div>

            <!-- AI 诊断 -->
            <div v-if="selectedConsultation.ai_diagnosis" class="mb-4">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-medium text-gray-700 flex items-center">
                  <span class="w-1.5 h-5 bg-blue-400 rounded-full mr-2"></span>
                  AI 诊断参考
                </h4>
                <button @click="askAI" class="text-xs text-primary-600 hover:text-primary-700 px-3 py-1 bg-primary-50 rounded-lg">
                  🤖 用 AI 追问
                </button>
              </div>
              <div class="text-sm text-blue-900 bg-blue-50 p-4 rounded-xl whitespace-pre-wrap max-h-[200px] overflow-y-auto">
                {{ selectedConsultation.ai_diagnosis }}
              </div>
            </div>

            <!-- 医生回执表单 -->
            <div v-if="selectedConsultation.status === 'pending'" class="border-t border-gray-100 pt-4 mt-4">
              <h4 class="font-medium text-gray-700 mb-4 flex items-center">
                <span class="w-1.5 h-5 bg-green-400 rounded-full mr-2"></span>
                填写回执
              </h4>
              <form @submit.prevent="handleReply" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">诊断 *</label>
                  <input v-model="replyForm.doctor_diagnosis" type="text" class="input" placeholder="请输入诊断结果" />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">回执内容 *</label>
                  <textarea v-model="replyForm.doctor_reply" class="input min-h-[120px]" placeholder="请输入详细的回执内容，包括：&#10;- 病情分析&#10;- 治疗建议&#10;- 注意事项" required minlength="10"></textarea>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">处方建议</label>
                  <textarea v-model="replyForm.prescription" class="input min-h-[80px]" placeholder="请输入处方建议，包括药物名称、用量、用法等"></textarea>
                </div>

                <button type="submit" class="btn-primary w-full py-3" :disabled="submitting">
                  <span v-if="!submitting">提交回执</span>
                  <div v-else class="loading-spinner mx-auto"></div>
                </button>
              </form>
            </div>

            <!-- 已完成的回执 -->
            <div v-if="selectedConsultation.status === 'completed'" class="border-t border-gray-100 pt-4 mt-4">
              <div class="p-4 bg-green-50 rounded-xl">
                <h4 class="font-medium text-green-800 mb-2">✅ 回执内容</h4>
                <p class="text-green-900 whitespace-pre-wrap">{{ selectedConsultation.doctor_reply }}</p>
                <div v-if="selectedConsultation.doctor_diagnosis" class="mt-3 pt-3 border-t border-green-200">
                  <p class="font-medium text-green-800">诊断：{{ selectedConsultation.doctor_diagnosis }}</p>
                </div>
                <div v-if="selectedConsultation.prescription" class="mt-2 pt-3 border-t border-green-200">
                  <p class="font-medium text-green-800">💊 处方：</p>
                  <p class="text-green-900 whitespace-pre-wrap mt-1">{{ selectedConsultation.prescription }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 未选择状态 -->
          <div v-else class="bg-white rounded-xl shadow-sm border border-gray-100 p-12 flex items-center justify-center" style="min-height: 400px">
            <div class="text-center text-gray-400">
              <svg class="w-20 h-20 mx-auto mb-4 text-gray-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p class="text-lg">选择左侧问诊单查看详情</p>
              <p class="text-sm mt-2">或使用上方功能卡片访问 AI 问诊、疾病百科、知识图谱</p>
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
import type { ConsultationResponse, ConsultationReply, ConsultationStatus } from '@/types'

const router = useRouter()
const user = ref<any>(null)
const consultations = ref<ConsultationResponse[]>([])
const loading = ref(true)
const activeTab = ref<'pending' | 'completed' | 'all'>('pending')
const selectedId = ref<number | null>(null)
const selectedConsultation = ref<ConsultationResponse | null>(null)
const submitting = ref(false)

const tabs = [
  { label: '待处理', value: 'pending' as const },
  { label: '已完成', value: 'completed' as const },
  { label: '全部', value: 'all' as const }
]

const replyForm = ref<ConsultationReply>({
  doctor_reply: '',
  doctor_diagnosis: '',
  prescription: ''
})

const pendingCount = computed(() => {
  return consultations.value.filter(c => c.status === 'pending').length
})

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (!userStr) {
    router.push('/login')
    return
  }
  user.value = JSON.parse(userStr)
  if (user.value.role !== 'doctor') {
    router.push('/patient')
    return
  }
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
    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }
    const result = await consultationApi.list(params)
    consultations.value = result.items
  } catch (e) {
    console.error('Failed to load consultations:', e)
  } finally {
    loading.value = false
  }
}

const selectConsultation = async (c: ConsultationResponse) => {
  selectedId.value = c.id
  try {
    selectedConsultation.value = await consultationApi.getDetail(c.id)
  } catch (e) {
    console.error('Failed to get consultation detail:', e)
  }
}

const askAI = () => {
  if (selectedConsultation.value) {
    const msg = `患者症状：${selectedConsultation.value.symptoms}`
    router.push({ path: '/chat', query: { message: msg } })
  }
}

const handleReply = async () => {
  if (!selectedConsultation.value) return
  submitting.value = true
  try {
    const result = await consultationApi.reply(selectedConsultation.value.id, replyForm.value)
    selectedConsultation.value = result
    replyForm.value = { doctor_reply: '', doctor_diagnosis: '', prescription: '' }
    await loadConsultations()
  } catch (e: any) {
    alert(e.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
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

const formatDateShort = (dateStr: string) => {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
