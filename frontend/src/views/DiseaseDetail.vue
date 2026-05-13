<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 返回按钮 -->
      <router-link to="/diseases" class="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        返回疾病列表
      </router-link>

      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center py-20">
        <div class="loading-spinner w-12 h-12"></div>
      </div>

      <!-- 疾病详情 -->
      <div v-else-if="disease" class="space-y-6">
        <!-- 基本信息卡片 -->
        <div class="card p-8">
          <div class="flex items-start justify-between mb-6">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ disease.name }}</h1>
              <div class="flex items-center space-x-4">
                <span class="tag">{{ disease.category }}</span>
                <span v-if="disease.cured_prob" class="text-medical-green font-medium">
                  治愈率: {{ disease.cured_prob }}
                </span>
              </div>
            </div>
            <button @click="goToChat" class="btn-primary flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              咨询此疾病
            </button>
          </div>
          
          <p class="text-gray-700 leading-relaxed">{{ disease.description }}</p>
        </div>

        <!-- 症状 -->
        <div v-if="disease.symptoms && disease.symptoms.length > 0" class="card p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <svg class="w-6 h-6 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            常见症状
          </h2>
          <div class="flex flex-wrap gap-3">
            <span v-for="symptom in disease.symptoms" :key="symptom"
                  class="px-4 py-2 bg-red-50 text-red-700 rounded-full text-sm">
              {{ symptom }}
            </span>
          </div>
        </div>

        <!-- 治疗信息 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 就诊科室 -->
          <div v-if="disease.departments && disease.departments.length > 0" class="card p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
              <svg class="w-5 h-5 text-medical-blue mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              就诊科室
            </h3>
            <div class="flex flex-wrap gap-2">
              <span v-for="dept in disease.departments" :key="dept"
                    class="px-3 py-1 bg-blue-50 text-blue-700 rounded-lg text-sm">
                {{ dept }}
              </span>
            </div>
          </div>

          <!-- 治疗方式 -->
          <div v-if="disease.treatment" class="card p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
              <svg class="w-5 h-5 text-medical-green mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              治疗方式
            </h3>
            <p class="text-gray-700">{{ disease.treatment }}</p>
          </div>
        </div>

        <!-- 推荐药物 -->
        <div v-if="disease.drugs && disease.drugs.length > 0" class="card p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <svg class="w-5 h-5 text-medical-purple mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
            推荐药物
          </h3>
          <div class="flex flex-wrap gap-2">
            <span v-for="drug in disease.drugs" :key="drug"
                  class="px-4 py-2 bg-purple-50 text-purple-700 rounded-full text-sm">
              {{ drug }}
            </span>
          </div>
        </div>

        <!-- 检查项目 -->
        <div v-if="disease.checks && disease.checks.length > 0" class="card p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <svg class="w-5 h-5 text-medical-orange mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            检查项目
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div v-for="check in disease.checks" :key="check"
                 class="flex items-center p-3 bg-orange-50 rounded-lg">
              <svg class="w-4 h-4 text-orange-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4" />
              </svg>
              <span class="text-gray-700 text-sm">{{ check }}</span>
            </div>
          </div>
        </div>

        <!-- 预防措施 -->
        <div v-if="disease.prevention" class="card p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <svg class="w-5 h-5 text-medical-green mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            预防措施
          </h3>
          <div class="text-gray-700 leading-relaxed whitespace-pre-line">{{ disease.prevention }}</div>
        </div>

        <!-- 并发症 -->
        <div v-if="disease.accompanies && disease.accompanies.length > 0" class="card p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            可能的并发症
          </h3>
          <div class="flex flex-wrap gap-2">
            <router-link v-for="acc in disease.accompanies" :key="acc"
                        :to="`/diseases/${acc}`"
                        class="px-4 py-2 bg-red-50 text-red-700 rounded-full text-sm hover:bg-red-100 transition-colors">
              {{ acc }}
            </router-link>
          </div>
        </div>

        <!-- 费用信息 -->
        <div v-if="disease.cost_money" class="card p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <svg class="w-5 h-5 text-yellow-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            预估费用
          </h3>
          <p class="text-gray-700">{{ disease.cost_money }}</p>
        </div>
      </div>

      <!-- 未找到疾病 -->
      <div v-else class="text-center py-20">
        <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-gray-500 text-lg">未找到该疾病</p>
        <router-link to="/diseases" class="btn-primary mt-4 inline-block">
          返回疾病列表
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { diseaseApi } from '@/api/disease'
import type { DiseaseInfo } from '@/types'

const route = useRoute()
const router = useRouter()

const disease = ref<DiseaseInfo | null>(null)
const loading = ref(true)

const fetchDisease = async (name: string) => {
  loading.value = true
  try {
    disease.value = await diseaseApi.getDetail(name)
  } catch (error) {
    console.error('Failed to fetch disease:', error)
    disease.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const name = route.params.name as string
  if (name) {
    fetchDisease(name)
  }
})

watch(() => route.params.name, (newName) => {
  if (newName) {
    fetchDisease(newName as string)
  }
})

const goToChat = () => {
  router.push({
    path: '/chat',
    query: { message: `请详细介绍一下${disease.value?.name}这个疾病` }
  })
}
</script>
