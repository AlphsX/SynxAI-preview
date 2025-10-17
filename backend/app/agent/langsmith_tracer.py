"""
LangSmith Tracing Integration

This module provides LangSmith tracing capabilities for AI interactions
without requiring full LangChain integration.
"""

import os
import asyncio
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from langsmith import Client
from app.config import settings

logger = logging.getLogger(__name__)


class LangSmithTracer:
    """Simple LangSmith tracer for AI interactions"""
    
    def __init__(self):
        self.client = None
        self.enabled = False
        self.project_name = settings.LANGCHAIN_PROJECT
        
        # Initialize LangSmith client if configured
        if (settings.LANGCHAIN_API_KEY and 
            settings.LANGCHAIN_TRACING_V2 == "true"):
            try:
                self.client = Client(
                    api_key=settings.LANGCHAIN_API_KEY,
                    api_url=settings.LANGCHAIN_ENDPOINT
                )
                self.enabled = True
                logger.info(f"✅ LangSmith tracer initialized for project: {self.project_name}")
            except Exception as e:
                logger.error(f"Failed to initialize LangSmith client: {e}")
                self.enabled = False
        else:
            logger.info("LangSmith tracing not configured")
    
    async def trace_ai_interaction(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
        run_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Trace an AI interaction to LangSmith
        
        Args:
            messages: The conversation messages
            model_id: The AI model used
            response: The AI response
            metadata: Additional metadata
            run_name: Custom run name
            
        Returns:
            Run ID if successful, None otherwise
        """
        
        if not self.enabled:
            return None
        
        try:
            # Generate run ID
            run_id = str(uuid.uuid4())
            
            # Prepare inputs
            inputs = {
                "messages": messages,
                "model": model_id
            }
            
            # Add metadata if provided
            if metadata:
                inputs.update(metadata)
            
            # Prepare outputs
            outputs = {
                "response": response
            }
            
            # Create run name
            if not run_name:
                run_name = f"AI_Chat_{model_id.replace('/', '_')}"
            
            # Create the run
            run = self.client.create_run(
                name=run_name,
                run_type="llm",
                inputs=inputs,
                outputs=outputs,
                project_name=self.project_name,
                run_id=run_id,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow()
            )
            
            logger.info(f"✅ LangSmith trace created: {run_id}")
            return run_id
            
        except Exception as e:
            logger.error(f"Failed to create LangSmith trace: {e}")
            return None
    
    async def trace_streaming_interaction(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        run_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Start tracing a streaming AI interaction
        
        Returns:
            Run ID for updating later
        """
        
        if not self.enabled:
            return None
        
        try:
            # Generate run ID
            run_id = str(uuid.uuid4())
            
            # Prepare inputs
            inputs = {
                "messages": messages,
                "model": model_id
            }
            
            # Add metadata if provided
            if metadata:
                inputs.update(metadata)
            
            # Create run name
            if not run_name:
                run_name = f"AI_Chat_Stream_{model_id.replace('/', '_')}"
            
            # Create the run (without outputs initially)
            run = self.client.create_run(
                name=run_name,
                run_type="llm",
                inputs=inputs,
                project_name=self.project_name,
                run_id=run_id,
                start_time=datetime.utcnow()
            )
            
            logger.info(f"✅ LangSmith streaming trace started: {run_id}")
            return run_id
            
        except Exception as e:
            logger.error(f"Failed to start LangSmith streaming trace: {e}")
            return None
    
    async def update_streaming_trace(
        self,
        run_id: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a streaming trace with the final response
        
        Args:
            run_id: The run ID from trace_streaming_interaction
            response: The complete AI response
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        
        if not self.enabled or not run_id:
            return False
        
        try:
            # Prepare outputs
            outputs = {
                "response": response
            }
            
            # Add metadata if provided
            if metadata:
                outputs.update(metadata)
            
            # Update the run
            self.client.update_run(
                run_id=run_id,
                outputs=outputs,
                end_time=datetime.utcnow()
            )
            
            logger.info(f"✅ LangSmith streaming trace completed: {run_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update LangSmith streaming trace: {e}")
            return False
    
    async def trace_enhanced_context(
        self,
        query: str,
        context_data: Dict[str, Any],
        run_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Trace enhanced context gathering
        
        Args:
            query: The user query
            context_data: The gathered context data
            run_name: Custom run name
            
        Returns:
            Run ID if successful, None otherwise
        """
        
        if not self.enabled:
            return None
        
        try:
            # Generate run ID
            run_id = str(uuid.uuid4())
            
            # Prepare inputs
            inputs = {
                "query": query
            }
            
            # Prepare outputs
            outputs = {
                "context_data": context_data,
                "context_types": list(context_data.keys()),
                "context_size": len(str(context_data))
            }
            
            # Create run name
            if not run_name:
                run_name = "Enhanced_Context_Gathering"
            
            # Create the run
            run = self.client.create_run(
                name=run_name,
                run_type="chain",
                inputs=inputs,
                outputs=outputs,
                project_name=self.project_name,
                run_id=run_id,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow()
            )
            
            logger.info(f"✅ LangSmith context trace created: {run_id}")
            return run_id
            
        except Exception as e:
            logger.error(f"Failed to create LangSmith context trace: {e}")
            return None
    
    def is_enabled(self) -> bool:
        """Check if LangSmith tracing is enabled"""
        return self.enabled


# Global tracer instance
langsmith_tracer = LangSmithTracer()