"""主管智能体 - 路由和协调"""

from typing import Dict, Any, List, Optional
import logging

from app.agents.state import MedicalAgentState

logger = logging.getLogger(__name__)


# 路由提示词
ROUTER_PROMPT = """你是一个医疗智能助手的路由器。根据用户的问题，判断应该使用哪个智能体来回答。

可用的智能体：
1. diagnosis - 用于疾病诊断、症状分析、疾病咨询
2. knowledge - 用于医学知识查询、药物信息、检查项目
3. general - 用于一般性对话、问候、系统问题

用户问题：{user_message}

请只返回智能体名称（diagnosis/knowledge/general），不要返回其他内容。"""


class SupervisorAgent:
    """主管智能体"""
    
    def __init__(self, llm):
        self.llm = llm
    
    async def route(self, state: MedicalAgentState) -> str:
        """路由到合适的智能体"""
        user_message = state.get("user_message", "")
        
        # 简单的关键词路由
        diagnosis_keywords = ["症状", "生病", "不舒服", "疼痛", "发烧", "咳嗽", "头疼", "肚子疼", 
                            "诊断", "得了什么病", "怎么回事", "什么原因"]
        knowledge_keywords = ["什么是", "药物", "药品", "检查", "治疗", "预防", "注意事项"]
        
        for keyword in diagnosis_keywords:
            if keyword in user_message:
                return "diagnosis"
        
        for keyword in knowledge_keywords:
            if keyword in user_message:
                return "knowledge"
        
        # 使用 LLM 进行更精确的路由
        try:
            prompt = ROUTER_PROMPT.format(user_message=user_message)
            response = await self.llm.ainvoke(prompt)
            agent_name = response.content.strip().lower()
            
            if agent_name in ["diagnosis", "knowledge", "general"]:
                return agent_name
        except Exception as e:
            logger.error(f"Router LLM call failed: {e}")
        
        return "general"


# 全局实例（需要在应用启动时初始化）
supervisor_agent: Optional[SupervisorAgent] = None


def init_supervisor(llm):
    """初始化主管智能体"""
    global supervisor_agent
    supervisor_agent = SupervisorAgent(llm)
    return supervisor_agent
