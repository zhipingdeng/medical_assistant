<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto px-4 py-8">
      <!-- 聊天容器 -->
      <div class="bg-white rounded-2xl shadow-lg overflow-hidden" style="height: calc(100vh - 180px)">
        <!-- 聊天头部 -->
        <div class="bg-gradient-to-r from-medical-blue to-medical-purple px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h2 class="text-white font-semibold">医疗智能助手</h2>
                <p class="text-white/70 text-sm">在线 · AI 辅助诊断</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <router-link to="/doctor" class="text-white/70 hover:text-white text-sm px-3 py-1 rounded-lg hover:bg-white/10 transition-colors">
                ← 返回工作台
              </router-link>
              <button @click="clearChat" class="text-white/70 hover:text-white transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 聊天消息区 -->
        <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-4" style="height: calc(100% - 160px)">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center">
            <div class="w-20 h-20 bg-primary-50 rounded-full flex items-center justify-center mb-4">
              <svg class="w-10 h-10 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">您好！我是医疗智能助手</h3>
            <p class="text-gray-500 mb-6">请输入症状描述或健康问题，我将为您进行 AI 分析</p>
            <div class="flex flex-wrap gap-2 justify-center">
              <button v-for="suggestion in suggestions" :key="suggestion"
                      @click="sendMessage(suggestion)"
                      class="px-4 py-2 bg-gray-100 rounded-full text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-all">
                {{ suggestion }}
              </button>
            </div>
          </div>

          <!-- 消息列表 -->
          <div v-for="(msg, index) in messages" :key="index"
               :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'">
            <div :class="[
              'max-w-[80%] rounded-2xl px-4 py-3',
              msg.role === 'user' 
                ? 'bg-primary-500 text-white rounded-br-md'
                : 'bg-gray-100 text-gray-900 rounded-bl-md'
            ]">
              <div class="whitespace-pre-wrap">{{ msg.content }}</div>
              <div :class="['text-xs mt-1', msg.role === 'user' ? 'text-white/70' : 'text-gray-400']">
                {{ formatTime(msg.timestamp) }}
              </div>
            </div>
          </div>

          <!-- 加载中 -->
          <div v-if="loading && !streamingContent" class="flex justify-start">
            <div class="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
            </div>
          </div>

          <!-- 流式输出 -->
          <div v-if="streamingContent" class="flex justify-start">
            <div class="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
              <div class="whitespace-pre-wrap">{{ streamingContent }}</div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="border-t border-gray-200 px-6 py-4 bg-white">
          <form @submit.prevent="handleSubmit" class="flex space-x-4">
            <input
              v-model="inputMessage"
              type="text"
              placeholder="描述症状或健康问题..."
              class="input flex-1"
              :disabled="loading"
            />
            <button
              type="submit"
              class="btn-primary px-6"
              :disabled="!inputMessage.trim() || loading"
            >
              <svg v-if="!loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              <div v-else class="loading-spinner"></div>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { chatApi } from '@/api/chat'
import type { ChatMessage } from '@/types'

const route = useRoute()

const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const loading = ref(false)
const streamingContent = ref('')
const chatContainer = ref<HTMLElement | null>(null)
const sessionId = ref<string | null>(null)

const suggestions = [
  '最近总是头疼，可能是什么原因？',
  '发烧38度，需要去医院吗？',
  '咳嗽一周了还没好，怎么办？',
  '高血压患者饮食注意事项'
]

onMounted(() => {
  const presetMessage = route.query.message as string
  if (presetMessage) {
    sendMessage(presetMessage)
  }
})

watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const formatTime = (timestamp?: number) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const addMessage = (role: 'user' | 'assistant', content: string) => {
  messages.value.push({
    role,
    content,
    timestamp: Date.now()
  })
}

const sendMessage = async (message: string) => {
  if (!message.trim() || loading.value) return

  addMessage('user', message)
  inputMessage.value = ''
  loading.value = true
  streamingContent.value = ''

  try {
    await chatApi.sendMessageStream(
      {
        message,
        session_id: sessionId.value || undefined,
        stream: true
      },
      (content) => {
        streamingContent.value += content
      },
      (_sources) => {
        if (streamingContent.value) {
          addMessage('assistant', streamingContent.value)
          streamingContent.value = ''
        }
        loading.value = false
      },
      (error) => {
        console.error('Chat error:', error)
        addMessage('assistant', '抱歉，出现了一些错误，请稍后重试。')
        streamingContent.value = ''
        loading.value = false
      }
    )
  } catch (error) {
    console.error('Chat error:', error)
    addMessage('assistant', '抱歉，出现了一些错误，请稍后重试。')
    loading.value = false
  }
}

const handleSubmit = () => {
  sendMessage(inputMessage.value)
}

const clearChat = () => {
  messages.value = []
  sessionId.value = null
}
</script>
