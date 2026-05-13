"""对话 API - 优化版"""

import uuid
import json
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import logging

from app.models.schemas import ChatRequest, ChatResponse
from app.database.redis import redis_client
from app.database.neo4j import neo4j_client
from app.rag.hybrid_search import hybrid_retriever
from app.agents.state import MedicalAgentState

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# 通用回复模板
GREETING_RESPONSES = {
    "你好": "您好！我是医疗智能助手，有什么可以帮助您的吗？您可以描述症状让我帮您分析，也可以搜索疾病了解详情。",
    "hi": "您好！我是医疗智能助手，有什么可以帮助您的吗？",
    "hello": "您好！我是医疗智能助手，有什么可以帮助您的吗？",
}

# 关键词路由（不依赖 LLM）
DIAGNOSIS_KEYWORDS = ["症状", "生病", "不舒服", "疼痛", "发烧", "咳嗽", "头疼", "头痛", 
                      "肚子疼", "腹痛", "诊断", "得了什么病", "怎么回事", "什么原因",
                      "恶心", "呕吐", "腹泻", "便秘", "失眠", "乏力", "眩晕", "胸闷",
                      "心悸", "皮疹", "瘙痒", "肿胀", "出血", "感染", "发炎"]

KNOWLEDGE_KEYWORDS = ["什么是", "药物", "药品", "检查", "治疗", "预防", "注意事项",
                      "怎么治", "吃什么药", "如何预防", "病因", "发病机制"]


def route_message(message: str) -> str:
    """基于关键词的消息路由"""
    message_lower = message.lower().strip()
    
    # 检查是否是问候
    if message_lower in GREETING_RESPONSES:
        return "greeting"
    
    # 检查诊断类
    for keyword in DIAGNOSIS_KEYWORDS:
        if keyword in message:
            return "diagnosis"
    
    # 检查知识类
    for keyword in KNOWLEDGE_KEYWORDS:
        if keyword in message:
            return "knowledge"
    
    # 默认：尝试诊断
    return "diagnosis"


async def get_diagnosis_response(message: str, chat_history: list) -> dict:
    """获取诊断响应"""
    try:
        diseases = []
        
        # 1. 尝试 Milvus 向量检索
        try:
            search_results = await hybrid_retriever.search(
                query=message,
                top_k=5,
                use_vector=True,
                use_graph=True
            )
            diseases = search_results.get("combined_results", [])
            diseases = [d for d in diseases if d.get("name")]
        except Exception as e:
            logger.warning(f"Milvus search failed: {e}")
        
        # 2. 如果 Milvus 没有好结果，使用 Neo4j 文本搜索
        if not diseases:
            try:
                # 提取关键词进行搜索
                keywords = []
                for keyword in DIAGNOSIS_KEYWORDS:
                    if keyword in message:
                        keywords.append(keyword)
                
                # 如果没有匹配的关键词，使用消息中的词
                if not keywords:
                    keywords = [message[:10]]  # 取前10个字符
                
                for keyword in keywords[:3]:
                    neo4j_results = await neo4j_client.search_by_symptom(keyword, limit=5)
                    for r in neo4j_results:
                        if r.get("name") and r["name"] not in [d.get("name") for d in diseases]:
                            diseases.append({
                                "name": r.get("name", ""),
                                "description": r.get("description", ""),
                                "symptoms": r.get("symptoms", [])
                            })
            except Exception as e:
                logger.warning(f"Neo4j search failed: {e}")
        
        # 3. 如果还是没有结果，返回提示
        if not diseases:
            return {
                "message": "抱歉，我没有找到与您描述相关的疾病信息。请尝试更详细地描述您的症状，或者直接搜索疾病名称。",
                "sources": []
            }
        
        # 构建响应
        response_parts = []
        response_parts.append(f"根据您描述的症状，以下是一些可能相关的疾病信息：\n")
        
        for i, disease in enumerate(diseases[:3], 1):
            name = disease.get("name", "")
            desc = disease.get("description", "")
            symptoms = disease.get("symptoms", [])
            departments = disease.get("departments") or disease.get("department", "")
            prevention = disease.get("prevention", "")
            
            response_parts.append(f"**{i}. {name}**")
            if desc:
                response_parts.append(f"简介：{desc[:200]}{'...' if len(desc) > 200 else ''}")
            if symptoms:
                if isinstance(symptoms, list):
                    response_parts.append(f"常见症状：{', '.join(symptoms[:5])}")
                else:
                    response_parts.append(f"常见症状：{symptoms}")
            if departments:
                if isinstance(departments, list):
                    response_parts.append(f"就诊科室：{', '.join(departments)}")
                else:
                    response_parts.append(f"就诊科室：{departments}")
            response_parts.append("")
        
        response_parts.append("⚠️ 以上信息仅供参考，不能替代专业医生的诊断。如果您有不适，请及时就医。")
        
        return {
            "message": "\n".join(response_parts),
            "sources": diseases[:3]
        }
        
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        return {
            "message": "抱歉，诊断分析过程中出现错误，请稍后重试。",
            "sources": []
        }


async def get_knowledge_response(message: str) -> dict:
    """获取知识响应"""
    try:
        diseases = []
        
        # 1. 尝试直接匹配疾病名称
        common_diseases = ["高血压", "糖尿病", "感冒", "发烧", "咳嗽", "头痛", "胃炎", "肺炎",
                           "哮喘", "冠心病", "肝炎", "肾炎", "关节炎", "失眠", "贫血", "肿瘤",
                           "甲亢", "乙肝", "肺结核", "阑尾炎", "胆囊炎", "胰腺炎", "肠炎"]
        
        for disease_name in common_diseases:
            if disease_name in message:
                try:
                    disease_info = await neo4j_client.get_disease_info(disease_name)
                    if disease_info and disease_info.get("name"):
                        diseases.append(disease_info)
                        break
                except Exception as e:
                    logger.warning(f"Failed to get disease info for {disease_name}: {e}")
        
        # 2. 如果没有直接匹配，尝试 Milvus 搜索
        if not diseases:
            try:
                search_results = await hybrid_retriever.search(
                    query=message,
                    top_k=3,
                    use_vector=True,
                    use_graph=True
                )
                diseases = search_results.get("combined_results", [])
                diseases = [d for d in diseases if d.get("name")]
            except Exception as e:
                logger.warning(f"Milvus search failed: {e}")
        
        # 3. 如果还是没有结果，使用 Neo4j 文本搜索
        if not diseases:
            try:
                keywords = []
                for keyword in KNOWLEDGE_KEYWORDS:
                    if keyword in message:
                        keywords.append(keyword)
                
                if not keywords:
                    keywords = [message[:10]]
                
                for keyword in keywords[:3]:
                    neo4j_results = await neo4j_client.search_by_symptom(keyword, limit=3)
                    for r in neo4j_results:
                        if r.get("name") and r["name"] not in [d.get("name") for d in diseases]:
                            diseases.append({
                                "name": r.get("name", ""),
                                "description": r.get("description", ""),
                                "symptoms": r.get("symptoms", [])
                            })
            except Exception as e:
                logger.warning(f"Neo4j search failed: {e}")
        
        # 4. 如果还是没有结果，返回提示
        if not diseases:
            return {
                "message": "抱歉，我没有找到相关的医学知识。请尝试换个关键词搜索。",
                "sources": []
            }
        
        response_parts = []
        response_parts.append("以下是相关的医学知识：\n")
        
        for disease in diseases[:3]:
            name = disease.get("name", "")
            desc = disease.get("description", "")
            prevention = disease.get("prevention", "")
            treatment = disease.get("treatment", "")
            drugs = disease.get("drugs", [])
            
            response_parts.append(f"📋 **{name}**")
            if desc:
                response_parts.append(f"描述：{desc[:300]}{'...' if len(desc) > 300 else ''}")
            if treatment:
                response_parts.append(f"治疗方式：{treatment}")
            if drugs:
                if isinstance(drugs, list):
                    response_parts.append(f"推荐药物：{', '.join(drugs[:5])}")
                else:
                    response_parts.append(f"推荐药物：{drugs}")
            if prevention:
                response_parts.append(f"预防措施：{prevention[:200]}{'...' if len(prevention) > 200 else ''}")
            response_parts.append("")
        
        response_parts.append("💡 以上信息仅供参考，具体用药请遵医嘱。")
        
        return {
            "message": "\n".join(response_parts),
            "sources": diseases[:3]
        }
        
    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        return {
            "message": "抱歉，知识检索过程中出现错误，请稍后重试。",
            "sources": []
        }


async def generate_stream_response(message: str, route_type: str) -> AsyncGenerator[str, None]:
    """生成流式响应"""
    
    if route_type == "greeting":
        response = GREETING_RESPONSES.get(message.lower().strip(), 
                                          "您好！我是医疗智能助手，有什么可以帮助您的吗？")
        for char in response:
            yield f"data: {json.dumps({'content': char}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'done': True, 'sources': []}, ensure_ascii=False)}\n\n"
        return
    
    if route_type == "diagnosis":
        result = await get_diagnosis_response(message, [])
    else:
        result = await get_knowledge_response(message)
    
    response = result["message"]
    sources = result.get("sources", [])
    
    for char in response:
        yield f"data: {json.dumps({'content': char}, ensure_ascii=False)}\n\n"
    
    yield f"data: {json.dumps({'done': True, 'sources': sources}, ensure_ascii=False)}\n\n"


@router.post("")
async def chat(request: ChatRequest, req: Request):
    """对话接口"""
    
    # 获取或生成会话 ID
    session_id = request.session_id or str(uuid.uuid4())
    
    # 获取聊天历史
    try:
        chat_history = await redis_client.get_chat_history(session_id)
    except Exception:
        chat_history = []
    
    # 路由消息
    route_type = route_message(request.message)
    logger.info(f"Message: {request.message[:50]}... -> Route: {route_type}")
    
    # 保存用户消息到历史
    try:
        await redis_client.add_chat_history(session_id, "user", request.message)
    except Exception as e:
        logger.warning(f"Failed to save chat history: {e}")
    
    if request.stream:
        # 流式响应
        return StreamingResponse(
            generate_stream_response(request.message, route_type),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Session-ID": session_id
            }
        )
    else:
        # 非流式响应
        if route_type == "greeting":
            response_text = GREETING_RESPONSES.get(request.message.lower().strip(),
                                                    "您好！我是医疗智能助手，有什么可以帮助您的吗？")
            sources = []
        elif route_type == "diagnosis":
            result = await get_diagnosis_response(request.message, chat_history)
            response_text = result["message"]
            sources = result.get("sources", [])
        else:
            result = await get_knowledge_response(request.message)
            response_text = result["message"]
            sources = result.get("sources", [])
        
        # 保存助手回复到历史
        try:
            await redis_client.add_chat_history(session_id, "assistant", response_text)
        except Exception as e:
            logger.warning(f"Failed to save chat history: {e}")
        
        return ChatResponse(
            message=response_text,
            session_id=session_id,
            sources=sources
        )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 20):
    """获取聊天历史"""
    try:
        history = await redis_client.get_chat_history(session_id, limit=limit)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        logger.error(f"Get chat history failed: {e}")
        return {"session_id": session_id, "messages": []}


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """清空聊天历史"""
    try:
        await redis_client.delete_session(f"chat_history:{session_id}")
        return {"message": "Chat history cleared", "session_id": session_id}
    except Exception as e:
        logger.error(f"Clear chat history failed: {e}")
        return {"message": "Failed to clear history", "session_id": session_id}
