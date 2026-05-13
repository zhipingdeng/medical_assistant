"""症状分析智能体"""

from typing import Dict, Any, List
import logging

from app.agents.state import MedicalAgentState
from app.rag.hybrid_search import hybrid_retriever

logger = logging.getLogger(__name__)


SYMPTOM_PROMPT = """你是一个症状分析专家。根据用户描述的症状，进行专业的分析。

用户描述：{user_message}

相关症状知识：
{context}

请分析：
1. 症状特征：描述用户的主要症状
2. 可能原因：分析可能的病因
3. 严重程度：评估症状的严重程度（轻度/中度/重度）
4. 就医建议：是否需要立即就医

注意：请提醒用户，这只是初步分析，不能替代专业医生的诊断。
"""


class SymptomAgent:
    """症状分析智能体"""
    
    def __init__(self, llm):
        self.llm = llm
    
    async def analyze(self, state: MedicalAgentState) -> MedicalAgentState:
        """分析症状"""
        user_message = state.get("user_message", "")
        
        # 检索相关症状信息
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
                symptoms = result.get("symptoms", [])
                desc = result.get("description", "")
                
                part = f"疾病：{name}\n相关症状：{', '.join(symptoms) if isinstance(symptoms, list) else symptoms}"
                if desc:
                    part += f"\n描述：{desc[:200]}..."
                
                context_parts.append(part)
            
            context = "\n\n".join(context_parts) if context_parts else "未找到相关症状信息"
            
        except Exception as e:
            logger.error(f"Symptom retrieval failed: {e}")
            context = "检索失败"
        
        # 调用 LLM 分析症状
        try:
            prompt = SYMPTOM_PROMPT.format(
                user_message=user_message,
                context=context
            )
            
            response = await self.llm.ainvoke(prompt)
            state["symptom_analysis"] = response.content
            
        except Exception as e:
            logger.error(f"Symptom LLM call failed: {e}")
            state["symptom_analysis"] = "抱歉，症状分析过程中出现错误，请稍后重试。"
        
        return state


# 全局实例
symptom_agent = None


def init_symptom(llm):
    """初始化症状智能体"""
    global symptom_agent
    symptom_agent = SymptomAgent(llm)
    return symptom_agent
