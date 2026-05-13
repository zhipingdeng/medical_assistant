"""智能体状态定义"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import MessagesState
import operator


class MedicalAgentState(TypedDict):
    """医疗智能体状态"""
    
    # 用户输入
    user_message: str
    
    # 会话信息
    session_id: str
    chat_history: List[Dict[str, str]]
    
    # 检索结果
    retrieved_diseases: List[Dict[str, Any]]
    knowledge_context: str
    
    # 智能体输出
    diagnosis_result: Optional[str]
    symptom_analysis: Optional[str]
    knowledge_response: Optional[str]
    
    # 最终响应
    final_response: str
    
    # 元数据
    metadata: Dict[str, Any]
