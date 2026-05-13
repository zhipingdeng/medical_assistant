import api from './index'
import type { ChatRequest, ChatResponse } from '@/types'

export const chatApi = {
  // 发送消息（非流式）
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/api/v1/chat', {
      ...request,
      stream: false
    })
    return response.data
  },

  // 发送消息（流式）
  async sendMessageStream(
    request: ChatRequest,
    onMessage: (content: string) => void,
    onDone: (sources?: any[]) => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    try {
      const token = localStorage.getItem('token')
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${api.defaults.baseURL}/api/v1/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          ...request,
          stream: true
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No reader available')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          break
        }

        buffer += decoder.decode(value, { stream: true })
        
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.done) {
                onDone(data.sources)
              } else if (data.content) {
                onMessage(data.content)
              }
            } catch (e) {
              // Ignore parse errors
            }
          }
        }
      }
    } catch (error) {
      if (onError) {
        onError(error as Error)
      }
      throw error
    }
  },
}
