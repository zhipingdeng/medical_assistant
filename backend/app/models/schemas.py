"""Pydantic 数据模型"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== 通用 ====================

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


# ==================== 对话相关 ====================

class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")
    stream: bool = Field(True, description="是否流式响应")


class ChatResponse(BaseModel):
    """对话响应"""
    message: str = Field(..., description="助手回复")
    session_id: str = Field(..., description="会话ID")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="参考来源")


# ==================== 疾病相关 ====================

class DiseaseInfo(BaseModel):
    """疾病信息"""
    name: str = Field(..., description="疾病名称")
    description: Optional[str] = Field(None, description="疾病描述")
    category: Optional[str] = Field(None, description="分类")
    symptoms: Optional[List[str]] = Field(None, description="症状")
    departments: Optional[List[str]] = Field(None, description="就诊科室")
    prevention: Optional[str] = Field(None, description="预防措施")
    treatment: Optional[str] = Field(None, description="治疗方式")
    drugs: Optional[List[str]] = Field(None, description="推荐药物")
    checks: Optional[List[str]] = Field(None, description="检查项目")
    cured_prob: Optional[str] = Field(None, description="治愈概率")
    cost_money: Optional[str] = Field(None, description="费用")
    accompanies: Optional[List[str]] = Field(None, description="并发症")


class DiseaseSearchRequest(BaseModel):
    """疾病搜索请求"""
    query: str = Field(..., min_length=1, max_length=500, description="搜索关键词")
    top_k: int = Field(10, ge=1, le=50, description="返回数量")


class DiseaseSearchResponse(BaseModel):
    """疾病搜索响应"""
    results: List[DiseaseInfo]
    total: int


# ==================== 知识图谱相关 ====================

class KnowledgeGraphNode(BaseModel):
    """知识图谱节点"""
    id: str
    label: str
    name: str
    properties: Dict[str, Any] = {}


class KnowledgeGraphEdge(BaseModel):
    """知识图谱边"""
    source: str
    target: str
    type: str


class KnowledgeGraphResponse(BaseModel):
    """知识图谱响应"""
    nodes: List[KnowledgeGraphNode]
    edges: List[KnowledgeGraphEdge]


class KnowledgeGraphRequest(BaseModel):
    """知识图谱请求"""
    center_node: str = Field(..., description="中心节点名称")
    depth: int = Field(2, ge=1, le=3, description="图谱深度")


# ==================== 健康检查 ====================

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    version: str = "1.0.0"
    services: Dict[str, str] = {}


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None


# ==================== 用户相关 ====================

class UserRole(str, Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    full_name: str = Field(..., min_length=2, max_length=50, description="姓名")
    role: UserRole = Field(..., description="角色: doctor/patient")
    
    # 医生专属
    department: Optional[str] = Field(None, description="科室（医生专用）")
    title: Optional[str] = Field(None, description="职称（医生专用）")
    specialization: Optional[str] = Field(None, description="专长（医生专用）")
    
    # 患者专属
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄（患者专用）")
    gender: Optional[str] = Field(None, description="性别（患者专用）")
    phone: Optional[str] = Field(None, description="电话（患者专用）")


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    department: Optional[str] = None
    title: Optional[str] = None
    specialization: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """登录 token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== 问诊单相关 ====================

class ConsultationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ConsultationCreate(BaseModel):
    """创建问诊单请求"""
    symptoms: str = Field(..., min_length=10, max_length=2000, description="症状描述")
    symptom_duration: Optional[str] = Field(None, max_length=100, description="症状持续时间")
    medical_history: Optional[str] = Field(None, max_length=2000, description="既往病史")
    allergies: Optional[str] = Field(None, max_length=1000, description="过敏史")


class ConsultationReply(BaseModel):
    """医生回执请求"""
    doctor_reply: str = Field(..., min_length=10, max_length=5000, description="医生回执")
    doctor_diagnosis: Optional[str] = Field(None, max_length=500, description="医生诊断")
    prescription: Optional[str] = Field(None, max_length=2000, description="处方建议")


class ConsultationResponse(BaseModel):
    """问诊单响应"""
    id: int
    patient_id: int
    patient_name: Optional[str] = None
    symptoms: str
    symptom_duration: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    ai_diagnosis: Optional[str] = None
    ai_suggestions: Optional[str] = None
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = None
    doctor_reply: Optional[str] = None
    doctor_diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    status: ConsultationStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConsultationListResponse(BaseModel):
    """问诊单列表响应"""
    total: int
    items: List[ConsultationResponse]
