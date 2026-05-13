"""问诊单模型"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.mysql import Base


class ConsultationStatus(str, enum.Enum):
    """问诊单状态"""
    PENDING = "pending"          # 待处理
    IN_PROGRESS = "in_progress"  # 处理中
    COMPLETED = "completed"      # 已完成
    CANCELLED = "cancelled"      # 已取消


class Consultation(Base):
    """问诊单表"""
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 患者信息
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="患者ID")
    
    # 问诊信息
    symptoms = Column(Text, nullable=False, comment="症状描述")
    symptom_duration = Column(String(100), nullable=True, comment="症状持续时间")
    medical_history = Column(Text, nullable=True, comment="既往病史")
    allergies = Column(Text, nullable=True, comment="过敏史")
    
    # AI 诊断结果
    ai_diagnosis = Column(Text, nullable=True, comment="AI诊断结果")
    ai_suggestions = Column(Text, nullable=True, comment="AI建议")
    
    # 医生回执
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="处理医生ID")
    doctor_reply = Column(Text, nullable=True, comment="医生回执")
    doctor_diagnosis = Column(String(500), nullable=True, comment="医生诊断")
    prescription = Column(Text, nullable=True, comment="处方建议")
    
    # 状态和时间
    status = Column(Enum(ConsultationStatus), default=ConsultationStatus.PENDING, comment="状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    
    # 关系
    patient = relationship("User", foreign_keys=[patient_id], backref="patient_consultations")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="doctor_consultations")
    
    def __repr__(self):
        return f"<Consultation(id={self.id}, patient_id={self.patient_id}, status={self.status})>"
