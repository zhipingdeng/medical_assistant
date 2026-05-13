"""问诊单 API"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import logging

from app.database.mysql import get_db
from app.models.user import User, UserRole
from app.models.consultation import Consultation, ConsultationStatus
from app.models.schemas import (
    ConsultationCreate, ConsultationReply, 
    ConsultationResponse, ConsultationListResponse
)
from app.api.v1.auth import get_current_user, get_current_doctor, get_current_patient
from app.api.v1.chat import get_diagnosis_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/consultations", tags=["consultations"])


def format_consultation(consultation: Consultation) -> ConsultationResponse:
    """格式化问诊单响应"""
    return ConsultationResponse(
        id=consultation.id,
        patient_id=consultation.patient_id,
        patient_name=consultation.patient.full_name if consultation.patient else None,
        symptoms=consultation.symptoms,
        symptom_duration=consultation.symptom_duration,
        medical_history=consultation.medical_history,
        allergies=consultation.allergies,
        ai_diagnosis=consultation.ai_diagnosis,
        ai_suggestions=consultation.ai_suggestions,
        doctor_id=consultation.doctor_id,
        doctor_name=consultation.doctor.full_name if consultation.doctor else None,
        doctor_reply=consultation.doctor_reply,
        doctor_diagnosis=consultation.doctor_diagnosis,
        prescription=consultation.prescription,
        status=consultation.status,
        created_at=consultation.created_at,
        updated_at=consultation.updated_at,
        completed_at=consultation.completed_at
    )


@router.post("", response_model=ConsultationResponse)
async def create_consultation(
    data: ConsultationCreate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """患者创建问诊单"""
    # 构建症状描述用于 AI 诊断
    full_symptoms = data.symptoms
    if data.symptom_duration:
        full_symptoms += f"，持续时间：{data.symptom_duration}"
    if data.medical_history:
        full_symptoms += f"，既往病史：{data.medical_history}"
    
    # 获取 AI 诊断
    ai_result = await get_diagnosis_response(full_symptoms, [])
    ai_diagnosis = ai_result.get("message", "")
    ai_suggestions = "建议及时就医，以上仅供参考。"
    
    # 创建问诊单
    consultation = Consultation(
        patient_id=current_user.id,
        symptoms=data.symptoms,
        symptom_duration=data.symptom_duration,
        medical_history=data.medical_history,
        allergies=data.allergies,
        ai_diagnosis=ai_diagnosis,
        ai_suggestions=ai_suggestions,
        status=ConsultationStatus.PENDING
    )
    
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    
    return format_consultation(consultation)


@router.get("", response_model=ConsultationListResponse)
async def list_consultations(
    status: Optional[ConsultationStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取问诊单列表"""
    query = db.query(Consultation)
    
    # 根据角色过滤
    if current_user.role == UserRole.PATIENT:
        query = query.filter(Consultation.patient_id == current_user.id)
    elif current_user.role == UserRole.DOCTOR:
        # 医生可以看到待处理和自己处理的
        if status == ConsultationStatus.PENDING:
            query = query.filter(Consultation.status == ConsultationStatus.PENDING)
        else:
            query = query.filter(
                (Consultation.doctor_id == current_user.id) |
                (Consultation.status == ConsultationStatus.PENDING)
            )
    
    # 状态过滤
    if status:
        query = query.filter(Consultation.status == status)
    
    # 计算总数
    total = query.count()
    
    # 分页
    items = query.order_by(desc(Consultation.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return ConsultationListResponse(
        total=total,
        items=[format_consultation(c) for c in items]
    )


@router.get("/{consultation_id}", response_model=ConsultationResponse)
async def get_consultation(
    consultation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取问诊单详情"""
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="问诊单不存在")
    
    # 权限检查
    if current_user.role == UserRole.PATIENT and consultation.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此问诊单")
    
    return format_consultation(consultation)


@router.post("/{consultation_id}/reply", response_model=ConsultationResponse)
async def reply_consultation(
    consultation_id: int,
    data: ConsultationReply,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    """医生回执问诊单"""
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="问诊单不存在")
    
    if consultation.status == ConsultationStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="问诊单已完成")
    
    if consultation.status == ConsultationStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="问诊单已取消")
    
    # 更新问诊单
    consultation.doctor_id = current_user.id
    consultation.doctor_reply = data.doctor_reply
    consultation.doctor_diagnosis = data.doctor_diagnosis
    consultation.prescription = data.prescription
    consultation.status = ConsultationStatus.COMPLETED
    
    db.commit()
    db.refresh(consultation)
    
    return format_consultation(consultation)


@router.post("/{consultation_id}/cancel", response_model=ConsultationResponse)
async def cancel_consultation(
    consultation_id: int,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """取消问诊单"""
    consultation = db.query(Consultation).filter(
        Consultation.id == consultation_id,
        Consultation.patient_id == current_user.id
    ).first()
    
    if not consultation:
        raise HTTPException(status_code=404, detail="问诊单不存在")
    
    if consultation.status != ConsultationStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能取消待处理的问诊单")
    
    consultation.status = ConsultationStatus.CANCELLED
    db.commit()
    db.refresh(consultation)
    
    return format_consultation(consultation)
