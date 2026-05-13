"""诊断智能体"""

from typing import Dict, Any, List
import logging

from app.agents.state import MedicalAgentState
from app.rag.hybrid_search import hybrid_retriever

logger = logging.getLogger(__name__)


DIAGNOSIS_PROMPT = """你是一个专业的医疗诊断助手。根据用户的症状描述，结合检索到的医学知识，给出专业的分析和建议。

用户描述：{user_message}

相关医学知识：
{context}

聊天历史：
{chat_history}

请按照以下格式回答：
1. 症状分析：分析用户描述的症状
2. 可能的疾病：列出可能相关的疾病（按可能性排序）
3. 建议：给出就诊建议和注意事项

注意：
- 不要给出确定的诊断，只提供参考意见
- 建议用户及时就医
- 回答要专业但易懂
"""


class DiagnosisAgent:
    """诊断智能体"""
    
    def __init__(self, llm):
        self.llm = llm
    
    async def analyze(self, state: MedicalAgentState) -> MedicalAgentState:
        """分析症状并给出诊断建议"""
        user_message = state.get("user_message", "")
        chat_history = state.get("chat_history", [])
        
        # 检索相关疾病信息
        try:
            search_results = await hybrid_retriever.search(
                query=user_message,
                top_k=5,
                use_vector=True,
                use_graph=True
            )
            
            # 构建上下文
            context_parts = []
            for result in search_results.get("combined_results", [])[:3]:
                name = result.get("name", "")
                desc = result.get("description", "")
                symptoms = result.get("symptoms", [])
                context_parts.append(f"疾病：{name}\n描述：{desc}\n症状：{', '.join(symptoms) if isinstance(symptoms, list) else symptoms}")
            
            context = "\n\n".join(context_parts) if context_parts else "未找到相关疾病信息"
            
            # 保存检索结果
            state["retrieved_diseases"] = search_results.get("combined_results", [])
            state["knowledge_context"] = context
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            context = "检索失败，请基于通用医学知识回答"
        
        # 格式化聊天历史
        history_str = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in chat_history[-5:]  # 最近5条
        ]) if chat_history else "无历史记录"
        
        # 调用 LLM 生成诊断分析
        try:
            prompt = DIAGNOSIS_PROMPT.format(
                user_message=user_message,
                context=context,
                chat_history=history_str
            )
            
            response = await self.llm.ainvoke(prompt)
            state["diagnosis_result"] = response.content
            
        except Exception as e:
            logger.error(f"Diagnosis LLM call failed: {e}")
            state["diagnosis_result"] = "抱歉，诊断分析过程中出现错误，请稍后重试。"
        
        return state


# 全局实例
diagnosis_agent = None


def init_diagnosis(llm):
    """初始化诊断智能体"""
    global diagnosis_agent
    diagnosis_agent = DiagnosisAgent(llm)
    return diagnosis_agent
