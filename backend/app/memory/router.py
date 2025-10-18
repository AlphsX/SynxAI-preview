"""
API Router for LangChain Memory Management
Provides endpoints to interact with conversation memory
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.memory.simple_memory_service import simple_memory_service as langchain_memory_service
from app.auth.middleware import get_optional_user
from app.auth.schemas import UserResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


class MessageInput(BaseModel):
    session_id: str
    message: str
    is_user: bool = True
    metadata: Optional[Dict[str, Any]] = None


class InvokeInput(BaseModel):
    session_id: str
    message: str
    system_prompt: Optional[str] = None


class SessionRequest(BaseModel):
    session_id: str


@router.post("/add-message")
async def add_message(
    data: MessageInput,
    current_user: Optional[UserResponse] = Depends(get_optional_user)
):
    """Add a message to conversation history"""
    try:
        # Add user info to metadata if authenticated
        metadata = data.metadata or {}
        if current_user:
            metadata["user_id"] = current_user.id
            metadata["username"] = current_user.username
        
        await langchain_memory_service.add_message_to_history(
            session_id=data.session_id,
            message=data.message,
            is_user=data.is_user,
            metadata=metadata
        )
        
        return {
            "success": True,
            "message": "Message added to history",
            "session_id": data.session_id
        }
    except Exception as e:
        logger.error(f"Error adding message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoke")
async def invoke_with_memory(
    data: InvokeInput,
    current_user: Optional[UserResponse] = Depends(get_optional_user)
):
    """
    Invoke LLM with full conversation memory
    Shows detailed logs in terminal with LangSmith tracing
    """
    try:
        # Add user context to config
        config = {}
        if current_user:
            config["metadata"] = {
                "user_id": current_user.id,
                "username": current_user.username
            }
        
        response = await langchain_memory_service.invoke_with_memory(
            session_id=data.session_id,
            message=data.message,
            system_prompt=data.system_prompt,
            config=config
        )
        
        return {
            "success": True,
            "response": response,
            "session_id": data.session_id
        }
    except Exception as e:
        logger.error(f"Error invoking with memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    limit: Optional[int] = None,
    current_user: Optional[UserResponse] = Depends(get_optional_user)
):
    """Get conversation history for a session"""
    try:
        history = await langchain_memory_service.get_conversation_history(
            session_id=session_id,
            limit=limit
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear/{session_id}")
async def clear_history(
    session_id: str,
    current_user: Optional[UserResponse] = Depends(get_optional_user)
):
    """Clear conversation history for a session"""
    try:
        await langchain_memory_service.clear_session_history(session_id)
        
        return {
            "success": True,
            "message": "History cleared",
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{session_id}")
async def get_stats(
    session_id: str,
    current_user: Optional[UserResponse] = Depends(get_optional_user)
):
    """Get memory statistics for a session"""
    try:
        stats = await langchain_memory_service.get_memory_stats(session_id)
        
        return {
            "success": True,
            **stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enable")
async def enable_memory(
    current_user: Optional[UserResponse] = Depends(get_optional_user)
):
    """Enable LangChain memory for enhanced chat service"""
    try:
        from app.enhanced_chat_service import enhanced_chat_service
        enhanced_chat_service.enable_langchain_memory()
        
        return {
            "success": True,
            "message": "LangChain memory enabled",
            "memory_enabled": enhanced_chat_service.is_langchain_memory_enabled()
        }
    except Exception as e:
        logger.error(f"Error enabling memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disable")
async def disable_memory(
    current_user: Optional[UserResponse] = Depends(get_optional_user)
):
    """Disable LangChain memory for enhanced chat service"""
    try:
        from app.enhanced_chat_service import enhanced_chat_service
        enhanced_chat_service.disable_langchain_memory()
        
        return {
            "success": True,
            "message": "LangChain memory disabled",
            "memory_enabled": enhanced_chat_service.is_langchain_memory_enabled()
        }
    except Exception as e:
        logger.error(f"Error disabling memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_memory_status(
    current_user: Optional[UserResponse] = Depends(get_optional_user)
):
    """Get LangChain memory status"""
    try:
        from app.enhanced_chat_service import enhanced_chat_service
        
        return {
            "success": True,
            "memory_enabled": enhanced_chat_service.is_langchain_memory_enabled(),
            "service_available": True,
            "storage_type": "postgresql" if langchain_memory_service.postgres_enabled else "in_memory"
        }
    except Exception as e:
        logger.error(f"Error getting memory status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
