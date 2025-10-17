"""
LangChain Memory Service with LangSmith Integration
Provides conversation memory management with full tracing and debugging capabilities
"""

from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_postgres import PostgresChatMessageHistory
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import logging
import json
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


class LangChainMemoryService:
    """
    Advanced memory service using LangChain with multiple memory strategies
    - ConversationBufferMemory: Stores all messages
    - ConversationSummaryMemory: Summarizes old conversations
    - PostgresChatMessageHistory: Persistent storage
    """
    
    def __init__(self):
        self.groq_llm = None
        self.memory_store = {}  # In-memory store for sessions
        self.postgres_enabled = False
        
        # Initialize Groq LLM for memory operations
        if settings.GROQ_API_KEY:
            try:
                self.groq_llm = ChatGroq(
                    groq_api_key=settings.GROQ_API_KEY,
                    model_name="llama-3.1-8b-instant",
                    temperature=0.7,
                    verbose=True  # Enable verbose logging to see invocations
                )
                logger.info("✅ LangChain Groq LLM initialized with verbose logging")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Groq LLM: {e}")
        
        # Try to enable PostgreSQL persistent memory
        try:
            if settings.DATABASE_URL and "postgresql" in settings.DATABASE_URL:
                self.postgres_enabled = True
                logger.info("✅ PostgreSQL memory persistence enabled")
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL memory disabled: {e}")
        
        logger.info("🧠 LangChain Memory Service initialized")
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """
        Get or create chat history for a session
        Uses PostgreSQL if available, otherwise in-memory
        """
        try:
            if self.postgres_enabled:
                # Use PostgreSQL for persistent storage
                return PostgresChatMessageHistory(
                    connection_string=settings.DATABASE_URL,
                    session_id=session_id,
                    table_name="langchain_chat_history"
                )
            else:
                # Use in-memory storage
                if session_id not in self.memory_store:
                    self.memory_store[session_id] = InMemoryChatMessageHistory()
                    logger.info(f"📝 Created new in-memory session: {session_id}")
                return self.memory_store[session_id]
        except Exception as e:
            logger.error(f"❌ Error getting session history: {e}")
            # Fallback to in-memory
            if session_id not in self.memory_store:
                self.memory_store[session_id] = InMemoryChatMessageHistory()
            return self.memory_store[session_id]
    
    def create_buffer_memory(self, session_id: str, return_messages: bool = True) -> ConversationBufferMemory:
        """
        Create ConversationBufferMemory for a session
        Stores all conversation messages without summarization
        """
        chat_history = self.get_session_history(session_id)
        
        memory = ConversationBufferMemory(
            chat_memory=chat_history,
            return_messages=return_messages,
            memory_key="chat_history",
            input_key="input",
            output_key="output"
        )
        
        logger.info(f"🔵 Created BufferMemory for session: {session_id}")
        return memory
    
    def create_summary_memory(self, session_id: str) -> ConversationSummaryMemory:
        """
        Create ConversationSummaryMemory for a session
        Automatically summarizes old conversations to save tokens
        """
        if not self.groq_llm:
            logger.warning("⚠️ Groq LLM not available, falling back to buffer memory")
            return self.create_buffer_memory(session_id)
        
        chat_history = self.get_session_history(session_id)
        
        memory = ConversationSummaryMemory(
            llm=self.groq_llm,
            chat_memory=chat_history,
            return_messages=True,
            memory_key="chat_history"
        )
        
        logger.info(f"🟢 Created SummaryMemory for session: {session_id}")
        return memory
    
    async def add_message_to_history(
        self, 
        session_id: str, 
        message: str, 
        is_user: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a message to conversation history with metadata
        """
        try:
            chat_history = self.get_session_history(session_id)
            
            # Create message with metadata
            msg_metadata = {
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
                **(metadata or {})
            }
            
            if is_user:
                msg = HumanMessage(content=message, additional_kwargs=msg_metadata)
                logger.info(f"👤 User message added to session {session_id}: {message[:50]}...")
            else:
                msg = AIMessage(content=message, additional_kwargs=msg_metadata)
                logger.info(f"🤖 AI message added to session {session_id}: {message[:50]}...")
            
            chat_history.add_message(msg)
            
            # Log to console for visibility
            print(f"\n{'='*80}")
            print(f"📝 MESSAGE LOGGED TO LANGCHAIN MEMORY")
            print(f"Session: {session_id}")
            print(f"Type: {'Human' if is_user else 'AI'}")
            print(f"Content: {message[:100]}...")
            print(f"Metadata: {json.dumps(msg_metadata, indent=2)}")
            print(f"{'='*80}\n")
            
        except Exception as e:
            logger.error(f"❌ Error adding message to history: {e}")
    
    async def get_conversation_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session
        Returns list of messages with metadata
        """
        try:
            chat_history = self.get_session_history(session_id)
            messages = chat_history.messages
            
            if limit:
                messages = messages[-limit:]
            
            # Convert to dict format
            history = []
            for msg in messages:
                history.append({
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content,
                    "metadata": getattr(msg, "additional_kwargs", {})
                })
            
            logger.info(f"📚 Retrieved {len(history)} messages from session {session_id}")
            
            # Log to console
            print(f"\n{'='*80}")
            print(f"📖 CONVERSATION HISTORY RETRIEVED")
            print(f"Session: {session_id}")
            print(f"Messages: {len(history)}")
            print(f"{'='*80}\n")
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Error retrieving conversation history: {e}")
            return []
    
    async def clear_session_history(self, session_id: str):
        """Clear all messages from a session"""
        try:
            chat_history = self.get_session_history(session_id)
            chat_history.clear()
            
            if session_id in self.memory_store:
                del self.memory_store[session_id]
            
            logger.info(f"🗑️ Cleared history for session: {session_id}")
            print(f"\n{'='*80}")
            print(f"🗑️ SESSION HISTORY CLEARED")
            print(f"Session: {session_id}")
            print(f"{'='*80}\n")
            
        except Exception as e:
            logger.error(f"❌ Error clearing session history: {e}")
    
    def create_conversational_chain(
        self, 
        session_id: str,
        system_prompt: Optional[str] = None
    ) -> RunnableWithMessageHistory:
        """
        Create a conversational chain with memory
        This enables full LangSmith tracing and debugging
        """
        if not self.groq_llm:
            raise ValueError("Groq LLM not initialized")
        
        # Default system prompt
        if not system_prompt:
            system_prompt = """You are Checkmate Spec Preview, an AI assistant. 
You have access to the full conversation history and can reference previous messages.
Be helpful, informative, and maintain context throughout the conversation."""
        
        # Create prompt template with message history placeholder
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # Create chain
        chain = prompt | self.groq_llm
        
        # Wrap with message history
        chain_with_history = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )
        
        logger.info(f"⛓️ Created conversational chain for session: {session_id}")
        return chain_with_history
    
    async def invoke_with_memory(
        self,
        session_id: str,
        message: str,
        system_prompt: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Invoke LLM with full conversation memory and LangSmith tracing
        This will show detailed logs in terminal
        """
        try:
            # Create chain with memory
            chain = self.create_conversational_chain(session_id, system_prompt)
            
            # Prepare config with session ID
            invoke_config = {
                "configurable": {"session_id": session_id},
                **(config or {})
            }
            
            # Log invocation details
            print(f"\n{'='*80}")
            print(f"🚀 LANGCHAIN INVOCATION STARTED")
            print(f"Session: {session_id}")
            print(f"Input: {message}")
            print(f"Timestamp: {datetime.utcnow().isoformat()}")
            print(f"{'='*80}\n")
            
            # Invoke chain with memory
            response = await chain.ainvoke(
                {"input": message},
                config=invoke_config
            )
            
            # Extract content from response
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Log response
            print(f"\n{'='*80}")
            print(f"✅ LANGCHAIN INVOCATION COMPLETED")
            print(f"Session: {session_id}")
            print(f"Response: {response_text[:200]}...")
            print(f"{'='*80}\n")
            
            logger.info(f"✅ Invoked chain for session {session_id}")
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Error invoking chain: {e}")
            print(f"\n{'='*80}")
            print(f"❌ LANGCHAIN INVOCATION FAILED")
            print(f"Session: {session_id}")
            print(f"Error: {str(e)}")
            print(f"{'='*80}\n")
            raise
    
    async def get_memory_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics about memory usage for a session"""
        try:
            history = await self.get_conversation_history(session_id)
            
            stats = {
                "session_id": session_id,
                "total_messages": len(history),
                "user_messages": sum(1 for m in history if m["role"] == "user"),
                "assistant_messages": sum(1 for m in history if m["role"] == "assistant"),
                "storage_type": "postgresql" if self.postgres_enabled else "in_memory",
                "langsmith_enabled": settings.LANGCHAIN_TRACING_V2 == "true"
            }
            
            print(f"\n{'='*80}")
            print(f"📊 MEMORY STATISTICS")
            print(json.dumps(stats, indent=2))
            print(f"{'='*80}\n")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting memory stats: {e}")
            return {}


# Global instance
langchain_memory_service = LangChainMemoryService()
