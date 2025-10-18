"""Memory management module"""

from .simple_memory_service import simple_memory_service, SimpleMemoryService

# Keep old names for backward compatibility
langchain_memory_service = simple_memory_service
LangChainMemoryService = SimpleMemoryService

__all__ = ["simple_memory_service", "SimpleMemoryService", "langchain_memory_service", "LangChainMemoryService"]
