import api from './index'
import type { UserRegister, UserLogin, TokenResponse, UserResponse } from '@/types'

export const authApi = {
  // 注册
  async register(data: UserRegister): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/api/v1/auth/register', data)
    return response.data
  },

  // 登录
  async login(data: UserLogin): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/api/v1/auth/login', data)
    return response.data
  },

  // 获取当前用户信息
  async getMe(): Promise<UserResponse> {
    const response = await api.get<UserResponse>('/api/v1/auth/me')
    return response.data
  },

  // 获取医生列表
  async listDoctors(): Promise<UserResponse[]> {
    const response = await api.get<UserResponse[]>('/api/v1/auth/doctors')
    return response.data
  }
}
