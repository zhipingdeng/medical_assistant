<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 搜索区域 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">疾病百科</h1>
        <div class="max-w-2xl">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索疾病名称、症状..."
              class="input pl-12 pr-4 py-4 text-lg"
              @input="handleSearch"
            />
            <svg class="w-6 h-6 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- 热门标签 -->
      <div class="mb-8">
        <h3 class="text-sm font-medium text-gray-500 mb-3">热门搜索</h3>
        <div class="flex flex-wrap gap-2">
          <button v-for="tag in hotTags" :key="tag"
                  @click="searchByTag(tag)"
                  class="px-4 py-2 bg-white rounded-full text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-all shadow-sm">
            {{ tag }}
          </button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center py-20">
        <div class="loading-spinner w-12 h-12"></div>
      </div>

      <!-- 疾病列表 -->
      <div v-else-if="diseases.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <router-link v-for="disease in diseases" :key="disease.name"
                    :to="`/diseases/${disease.name}`"
                    class="card p-6 hover:shadow-lg transition-all">
          <div class="flex items-start justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">{{ disease.name }}</h3>
            <span class="tag text-xs">{{ disease.category?.split('>')[0] || '疾病' }}</span>
          </div>
          
          <p class="text-gray-600 text-sm mb-4 line-clamp-3">
            {{ disease.description || '暂无描述' }}
          </p>
          
          <div v-if="disease.symptoms && disease.symptoms.length > 0" class="mb-4">
            <p class="text-xs text-gray-500 mb-2">常见症状：</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="symptom in disease.symptoms.slice(0, 3)" :key="symptom"
                    class="px-2 py-1 bg-red-50 text-red-600 rounded text-xs">
                {{ symptom }}
              </span>
              <span v-if="disease.symptoms.length > 3" class="px-2 py-1 bg-gray-100 text-gray-500 rounded text-xs">
                +{{ disease.symptoms.length - 3 }}
              </span>
            </div>
          </div>
          
          <div class="flex items-center justify-between text-xs text-gray-400">
            <span v-if="disease.departments">{{ disease.departments.join(' · ') }}</span>
            <span v-if="disease.cured_prob" class="text-medical-green font-medium">
              治愈率 {{ disease.cured_prob }}
            </span>
          </div>
        </router-link>
      </div>

      <!-- 空状态 -->
      <div v-else class="text-center py-20">
        <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-gray-500 text-lg">未找到相关疾病</p>
        <p class="text-gray-400 text-sm mt-2">请尝试其他关键词</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { diseaseApi } from '@/api/disease'
import type { DiseaseInfo } from '@/types'

const searchQuery = ref('')
const diseases = ref<DiseaseInfo[]>([])
const loading = ref(false)
const searchTimeout = ref<number | null>(null)

const hotTags = ['感冒', '发烧', '咳嗽', '高血压', '糖尿病', '冠心病', '肺炎', '胃炎', '头痛', '失眠']

onMounted(() => {
  // 初始加载热门疾病
  searchDiseases('感冒')
})

const handleSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  searchTimeout.value = window.setTimeout(() => {
    if (searchQuery.value.trim()) {
      searchDiseases(searchQuery.value)
    }
  }, 300)
}

const searchByTag = (tag: string) => {
  searchQuery.value = tag
  searchDiseases(tag)
}

const searchDiseases = async (query: string) => {
  loading.value = true
  try {
    const result = await diseaseApi.search(query, 12)
    diseases.value = result.results
  } catch (error) {
    console.error('Search failed:', error)
    diseases.value = []
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
