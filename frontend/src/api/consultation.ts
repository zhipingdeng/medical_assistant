import api from './index'
import type { ConsultationCreate, ConsultationReply, ConsultationResponse, ConsultationListResponse } from '@/types'

export const consultationApi = {
  // 创建问诊单
  async create(data: ConsultationCreate): Promise<ConsultationResponse> {
    const response = await api.post<ConsultationResponse>('/api/v1/consultations', data)
    return response.data
  },

  // 获取问诊单列表
  async list(params?: { status?: string; page?: number; page_size?: number }): Promise<ConsultationListResponse> {
    const response = await api.get<ConsultationListResponse>('/api/v1/consultations', { params })
    return response.data
  },

  // 获取问诊单详情
  async getDetail(id: number): Promise<ConsultationResponse> {
    const response = await api.get<ConsultationResponse>(`/api/v1/consultations/${id}`)
    return response.data
  },

  // 医生回执
  async reply(id: number, data: ConsultationReply): Promise<ConsultationResponse> {
    const response = await api.post<ConsultationResponse>(`/api/v1/consultations/${id}/reply`, data)
    return response.data
  },

  // 取消问诊单
  async cancel(id: number): Promise<ConsultationResponse> {
    const response = await api.post<ConsultationResponse>(`/api/v1/consultations/${id}/cancel`)
    return response.data
  }
}
