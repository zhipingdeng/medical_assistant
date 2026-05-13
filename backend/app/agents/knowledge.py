"""知识检索智能体"""

from typing import Dict, Any, List
import logging

from app.agents.state import MedicalAgentState
from app.rag.hybrid_search import hybrid_retriever

logger = logging.getLogger(__name__)


KNOWLEDGE_PROMPT = """你是一个医学知识专家。根据用户的问题，结合检索到的医学知识，给出准确、专业的回答。

用户问题：{user_message}

检索到的知识：
{context}

聊天历史：
{chat_history}

请给出详细、准确的回答。如果涉及药物或治疗，请提醒用户遵医嘱。
"""


class KnowledgeAgent:
    """知识检索智能体"""
    
    def __init__(self, llm):
        self.llm = llm
    
    async def search_and_answer(self, state: MedicalAgentState) -> MedicalAgentState:
        """检索知识并回答"""
        user_message = state.get("user_message", "")
        chat_history = state.get("chat_history", [])
        
        # 检索相关知识
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
                prevention = result.get("prevention", "")
                treatment = result.get("treatment", "")
                drugs = result.get("drugs", [])
                
                part = f"名称：{name}\n描述：{desc}"
                if prevention:
                    part += f"\n预防：{prevention}"
                if treatment:
                    part += f"\n治疗：{treatment}"
                if drugs:
                    part += f"\n药物：{', '.join(drugs) if isinstance(drugs, list) else drugs}"
                
                context_parts.append(part)
            
            context = "\n\n".join(context_parts) if context_parts else "未找到相关知识"
            
            # 保存检索结果
            state["retrieved_diseases"] = search_results.get("combined_results", [])
            state["knowledge_context"] = context
            
        except Exception as e:
            logger.error(f"Knowledge retrieval failed: {e}")
            context = "检索失败，请基于通用医学知识回答"
        
        # 格式化聊天历史
        history_str = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in chat_history[-5:]
        ]) if chat_history else "无历史记录"
        
        # 调用 LLM 生成回答
        try:
            prompt = KNOWLEDGE_PROMPT.format(
                user_message=user_message,
                context=context,
                chat_history=history_str
            )
            
            response = await self.llm.ainvoke(prompt)
            state["knowledge_response"] = response.content
            
        except Exception as e:
            logger.error(f"Knowledge LLM call failed: {e}")
            state["knowledge_response"] = "抱歉，知识检索过程中出现错误，请稍后重试。"
        
        return state


# 全局实例
knowledge_agent = None


def init_knowledge(llm):
    """初始化知识智能体"""
    global knowledge_agent
    knowledge_agent = KnowledgeAgent(llm)
    return knowledge_agent
