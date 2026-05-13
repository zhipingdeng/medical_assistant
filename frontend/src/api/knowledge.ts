import api from './index'
import type { KnowledgeGraphData } from '@/types'

export const knowledgeApi = {
  // 获取知识图谱数据
  async getGraph(center: string, depth: number = 2): Promise<KnowledgeGraphData> {
    const response = await api.get<KnowledgeGraphData>('/api/v1/knowledge/graph', {
      params: { center, depth }
    })
    return response.data
  },

  // 搜索知识
  async search(query: string, limit: number = 10): Promise<any> {
    const response = await api.get('/api/v1/knowledge/search', {
      params: { q: query, limit }
    })
    return response.data
  },

  // 获取知识图谱统计
  async getStats(): Promise<any> {
    const response = await api.get('/api/v1/knowledge/stats')
    return response.data
  }
}
