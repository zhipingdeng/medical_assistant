import api from './index'
import type { DiseaseInfo, DiseaseSearchResult } from '@/types'

export const diseaseApi = {
  // 搜索疾病
  async search(query: string, topK: number = 10): Promise<DiseaseSearchResult> {
    const response = await api.get<DiseaseSearchResult>('/api/v1/diseases', {
      params: { q: query, top_k: topK }
    })
    return response.data
  },

  // 获取疾病详情
  async getDetail(diseaseName: string): Promise<DiseaseInfo> {
    const response = await api.get<DiseaseInfo>(`/api/v1/diseases/${encodeURIComponent(diseaseName)}`)
    return response.data
  },

  // 获取相关疾病
  async getRelated(diseaseName: string): Promise<any> {
    const response = await api.get(`/api/v1/diseases/${encodeURIComponent(diseaseName)}/related`)
    return response.data
  },

  // 获取疾病统计
  async getStats(): Promise<any> {
    const response = await api.get('/api/v1/diseases/stats/overview')
    return response.data
  }
}
