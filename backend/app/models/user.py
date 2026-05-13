"""用户模型"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum

from app.database.mysql import Base


class UserRole(str, enum.Enum):
    """用户角色"""
    DOCTOR = "doctor"
    PATIENT = "patient"


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    full_name = Column(String(50), nullable=False, comment="姓名")
    role = Column(Enum(UserRole), nullable=False, comment="角色: doctor/patient")
    
    # 医生专属字段
    department = Column(String(50), nullable=True, comment="科室（医生专用）")
    title = Column(String(50), nullable=True, comment="职称（医生专用）")
    specialization = Column(String(200), nullable=True, comment="专长（医生专用）")
    
    # 患者专属字段
    age = Column(Integer, nullable=True, comment="年龄（患者专用）")
    gender = Column(String(10), nullable=True, comment="性别（患者专用）")
    phone = Column(String(20), nullable=True, comment="电话（患者专用）")
    
    # 通用字段
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
