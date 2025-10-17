"""
LangChain-based AI Service with LangSmith Tracing

This service provides AI chat functionality using LangChain wrappers
to ensure proper LangSmith tracing for all AI interactions.
"""

import os
import asyncio
from typing import List, AsyncGenerator, Dict, Any, Optional
import logging
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.callbacks import AsyncCallbackHandler
from app.config import settings

logger = logging.getLogger(__name__)


class StreamingCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming responses"""
    
    def __init__(self):
        self.tokens = []
    
    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is generated"""
        self.tokens.append(token)


class LangChainAIService:
    """AI service using LangChain wrappers for proper LangSmith tracing"""
    
    def __init__(self):
        self.groq_client = None
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize clients based on available API keys
        self._initialize_clients()
        
        logger.info("LangChain AI Service initialized with LangSmith tracing")
    
    def _initialize_clients(self):
        """Initialize LangChain clients with available API keys"""
        
        # Initialize Groq client
        if settings.GROQ_API_KEY:
            try:
                self.groq_client = ChatGroq(
                    groq_api_key=settings.GROQ_API_KEY,
                    model_name="llama3-8b-8192",  # Default model
                    temperature=0.7,
                    max_tokens=2000,
                    streaming=True
                )
                logger.info("✅ Groq client initialized with LangSmith tracing")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        
        # Initialize OpenAI client
        if settings.OPENAI_API_KEY:
            try:
                self.openai_client = ChatOpenAI(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model_name="gpt-3.5-turbo",  # Default model
                    temperature=0.7,
                    max_tokens=2000,
                    streaming=True
                )
                logger.info("✅ OpenAI client initialized with LangSmith tracing")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Initialize Anthropic client
        if settings.ANTHROPIC_API_KEY:
            try:
                self.anthropic_client = ChatAnthropic(
                    anthropic_api_key=settings.ANTHROPIC_API_KEY,
                    model="claude-3-sonnet-20240229",  # Default model
                    temperature=0.7,
                    max_tokens=2000,
                    streaming=True
                )
                logger.info("✅ Anthropic client initialized with LangSmith tracing")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
    
    def _get_client_for_model(self, model_id: str):
        """Get the appropriate client for a model ID"""
        
        # Groq models
        if any(groq_model in model_id.lower() for groq_model in [
            "groq", "llama", "mixtral", "gemma"
        ]):
            if self.groq_client:
                # Update model name if needed
                if "llama3-70b" in model_id.lower():
                    self.groq_client.model_name = "llama3-70b-8192"
                elif "llama3-8b" in model_id.lower():
                    self.groq_client.model_name = "llama3-8b-8192"
                elif "mixtral" in model_id.lower():
                    self.groq_client.model_name = "mixtral-8x7b-32768"
                elif "gemma" in model_id.lower():
                    self.groq_client.model_name = "gemma-7b-it"
                
                return self.groq_client
        
        # OpenAI models
        elif any(openai_model in model_id.lower() for openai_model in [
            "gpt", "openai"
        ]):
            if self.openai_client:
                # Update model name if needed
                if "gpt-4" in model_id.lower():
                    self.openai_client.model_name = "gpt-4"
                elif "gpt-3.5" in model_id.lower():
                    self.openai_client.model_name = "gpt-3.5-turbo"
                
                return self.openai_client
        
        # Anthropic models
        elif any(anthropic_model in model_id.lower() for anthropic_model in [
            "claude", "anthropic"
        ]):
            if self.anthropic_client:
                # Update model name if needed
                if "claude-3-opus" in model_id.lower():
                    self.anthropic_client.model = "claude-3-opus-20240229"
                elif "claude-3-sonnet" in model_id.lower():
                    self.anthropic_client.model = "claude-3-sonnet-20240229"
                elif "claude-3-haiku" in model_id.lower():
                    self.anthropic_client.model = "claude-3-haiku-20240307"
                
                return self.anthropic_client
        
        # Default to Groq if available
        if self.groq_client:
            logger.warning(f"Unknown model {model_id}, defaulting to Groq")
            return self.groq_client
        
        # Fallback to any available client
        for client in [self.openai_client, self.anthropic_client]:
            if client:
                logger.warning(f"Unknown model {model_id}, using fallback client")
                return client
        
        raise ValueError(f"No suitable client found for model {model_id}")
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> List:
        """Convert message format to LangChain format"""
        langchain_messages = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                # Default to human message
                langchain_messages.append(HumanMessage(content=content))
        
        return langchain_messages
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        stream: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate chat response using LangChain with LangSmith tracing
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model_id: Model identifier
            stream: Whether to stream the response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Yields:
            Response chunks as strings
        """
        
        try:
            # Get appropriate client
            client = self._get_client_for_model(model_id)
            
            # Update client parameters
            client.temperature = temperature
            client.max_tokens = max_tokens
            
            # Convert messages to LangChain format
            langchain_messages = self._convert_messages(messages)
            
            logger.info(f"🤖 Generating response with {model_id} via LangChain (LangSmith tracing enabled)")
            logger.info(f"📝 Processing {len(langchain_messages)} messages")
            
            if stream:
                # Stream response
                response_content = ""
                async for chunk in client.astream(langchain_messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        response_content += chunk.content
                        yield chunk.content
                
                logger.info(f"✅ Streamed response completed ({len(response_content)} chars)")
            else:
                # Non-streaming response
                response = await client.ainvoke(langchain_messages)
                content = response.content if hasattr(response, 'content') else str(response)
                logger.info(f"✅ Response completed ({len(content)} chars)")
                yield content
                
        except Exception as e:
            logger.error(f"❌ LangChain AI service error: {e}")
            error_message = f"AI service error: {str(e)}"
            yield error_message
    
    async def simple_chat(self, message: str, model_id: str = None) -> str:
        """Simple chat method for testing"""
        
        if not model_id:
            model_id = "groq/llama3-8b-8192"
        
        messages = [{"role": "user", "content": message}]
        
        response_content = ""
        async for chunk in self.chat(messages, model_id, stream=True):
            response_content += chunk
        
        return response_content
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        models = []
        
        if self.groq_client:
            models.extend([
                "groq/llama3-8b-8192",
                "groq/llama3-70b-8192",
                "groq/mixtral-8x7b-32768",
                "groq/gemma-7b-it"
            ])
        
        if self.openai_client:
            models.extend([
                "openai/gpt-3.5-turbo",
                "openai/gpt-4",
                "openai/gpt-4-turbo"
            ])
        
        if self.anthropic_client:
            models.extend([
                "anthropic/claude-3-haiku",
                "anthropic/claude-3-sonnet",
                "anthropic/claude-3-opus"
            ])
        
        return models
    
    def is_available(self) -> bool:
        """Check if any AI client is available"""
        return any([self.groq_client, self.openai_client, self.anthropic_client])


# Global instance
langchain_ai_service = LangChainAIService()