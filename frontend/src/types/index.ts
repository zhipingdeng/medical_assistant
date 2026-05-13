// Types for Medical Assistant

// ==================== 对话相关 ====================

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: number
}

export interface ChatRequest {
  message: string
  session_id?: string
  stream?: boolean
}

export interface ChatResponse {
  message: string
  session_id: string
  sources?: DiseaseInfo[]
}

// ==================== 疾病相关 ====================

export interface DiseaseInfo {
  name: string
  description?: string
  category?: string
  symptoms?: string[]
  departments?: string[]
  prevention?: string
  treatment?: string
  drugs?: string[]
  checks?: string[]
  cured_prob?: string
  cost_money?: string
  accompanies?: string[]
}

export interface DiseaseSearchResult {
  results: DiseaseInfo[]
  total: number
}

// ==================== 知识图谱相关 ====================

export interface KnowledgeGraphNode {
  id: string
  label: string
  name: string
  properties: Record<string, any>
}

export interface KnowledgeGraphEdge {
  source: string
  target: string
  type: string
}

export interface KnowledgeGraphData {
  nodes: KnowledgeGraphNode[]
  edges: KnowledgeGraphEdge[]
}

// ==================== 用户相关 ====================

export type UserRole = 'doctor' | 'patient'

export interface UserRegister {
  username: string
  email: string
  password: string
  full_name: string
  role: UserRole
  department?: string
  title?: string
  specialization?: string
  age?: number
  gender?: string
  phone?: string
}

export interface UserLogin {
  username: string
  password: string
}

export interface UserResponse {
  id: number
  username: string
  email: string
  full_name: string
  role: UserRole
  department?: string
  title?: string
  specialization?: string
  age?: number
  gender?: string
  phone?: string
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserResponse
}

// ==================== 问诊单相关 ====================

export type ConsultationStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled'

export interface ConsultationCreate {
  symptoms: string
  symptom_duration?: string
  medical_history?: string
  allergies?: string
}

export interface ConsultationReply {
  doctor_reply: string
  doctor_diagnosis?: string
  prescription?: string
}

export interface ConsultationResponse {
  id: number
  patient_id: number
  patient_name?: string
  symptoms: string
  symptom_duration?: string
  medical_history?: string
  allergies?: string
  ai_diagnosis?: string
  ai_suggestions?: string
  doctor_id?: number
  doctor_name?: string
  doctor_reply?: string
  doctor_diagnosis?: string
  prescription?: string
  status: ConsultationStatus
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface ConsultationListResponse {
  total: number
  items: ConsultationResponse[]
}

// ==================== API 响应 ====================

export interface ApiResponse<T> {
  data?: T
  error?: string
  detail?: string
}
