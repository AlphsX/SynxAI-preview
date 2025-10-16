"""
Intelligent Search Router
Analyzes queries and routes to optimal search provider (Brave Search or SerpAPI)
"""
import re
from typing import Dict, Any, Literal
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    """Types of search queries"""
    GENERAL = "general"              # General web search
    REAL_TIME = "real_time"          # News, current events, latest updates
    STRUCTURED = "structured"        # Needs rich metadata, featured snippets
    SPECIALIZED = "specialized"      # Images, shopping, maps, knowledge graph
    DEEP_RESEARCH = "deep_research"  # Site-specific, academic, detailed


class SearchProviderChoice(str, Enum):
    """Search provider selection"""
    BRAVE = "brave"      # Primary for general and real-time
    SERPAPI = "serpapi"  # Primary for structured and specialized


class IntelligentSearchRouter:
    """
    Analyzes search queries and determines optimal search provider
    
    Strategy:
    - Brave Search: General queries, real-time info, news, clean results
    - SerpAPI: Structured data, rich metadata, specialized searches
    """
    
    # Keywords that indicate different query types
    REAL_TIME_KEYWORDS = [
        "latest", "recent", "today", "now", "current", "breaking",
        "news", "update", "2024", "2025", "this week", "this month"
    ]
    
    STRUCTURED_KEYWORDS = [
        "how to", "what is", "define", "explain", "tutorial",
        "guide", "steps", "compare", "vs", "difference between"
    ]
    
    SPECIALIZED_KEYWORDS = [
        "image", "images", "photo", "picture", "buy", "shop",
        "price", "map", "location", "directions", "weather"
    ]
    
    DEEP_RESEARCH_KEYWORDS = [
        "site:", "filetype:", "intitle:", "inurl:",
        "research", "study", "paper", "academic", "scholarly"
    ]
    
    @staticmethod
    def analyze_query(query: str) -> Dict[str, Any]:
        """
        Analyze query and determine optimal search strategy
        
        Returns:
            Dict with query_type, provider, reasoning, and confidence
        """
        query_lower = query.lower()
        
        # Check for specialized search operators or keywords
        if any(keyword in query_lower for keyword in IntelligentSearchRouter.SPECIALIZED_KEYWORDS):
            return {
                "query_type": QueryType.SPECIALIZED,
                "provider": SearchProviderChoice.SERPAPI,
                "reasoning": "Query requires specialized search (images, shopping, maps)",
                "confidence": 0.95
            }
        
        # Check for deep research indicators (site:, filetype:, etc.)
        if any(keyword in query_lower for keyword in IntelligentSearchRouter.DEEP_RESEARCH_KEYWORDS):
            return {
                "query_type": QueryType.DEEP_RESEARCH,
                "provider": SearchProviderChoice.SERPAPI,
                "reasoning": "Query uses advanced search operators or requires deep research",
                "confidence": 0.90
            }
        
        # Check for structured data needs
        if any(keyword in query_lower for keyword in IntelligentSearchRouter.STRUCTURED_KEYWORDS):
            return {
                "query_type": QueryType.STRUCTURED,
                "provider": SearchProviderChoice.SERPAPI,
                "reasoning": "Query requires structured data or rich metadata (featured snippets, knowledge graph)",
                "confidence": 0.80
            }
        
        # Check for real-time information needs
        if any(keyword in query_lower for keyword in IntelligentSearchRouter.REAL_TIME_KEYWORDS):
            return {
                "query_type": QueryType.REAL_TIME,
                "provider": SearchProviderChoice.BRAVE,
                "reasoning": "Query requires real-time information (news, current events, latest updates)",
                "confidence": 0.85
            }
        
        # Default to general search with Brave
        return {
            "query_type": QueryType.GENERAL,
            "provider": SearchProviderChoice.BRAVE,
            "reasoning": "General web search - Brave provides clean, privacy-friendly results",
            "confidence": 0.75
        }
    
    @staticmethod
    def should_use_brave(query: str) -> bool:
        """Quick check if Brave Search should be used"""
        analysis = IntelligentSearchRouter.analyze_query(query)
        return analysis["provider"] == SearchProviderChoice.BRAVE
    
    @staticmethod
    def should_use_serpapi(query: str) -> bool:
        """Quick check if SerpAPI should be used"""
        analysis = IntelligentSearchRouter.analyze_query(query)
        return analysis["provider"] == SearchProviderChoice.SERPAPI
    
    @staticmethod
    def get_search_strategy(query: str) -> Dict[str, Any]:
        """
        Get complete search strategy including fallback plan
        
        Returns:
            Dict with primary_provider, fallback_provider, and analysis
        """
        analysis = IntelligentSearchRouter.analyze_query(query)
        
        # Determine fallback provider (opposite of primary)
        if analysis["provider"] == SearchProviderChoice.BRAVE:
            fallback = SearchProviderChoice.SERPAPI
        else:
            fallback = SearchProviderChoice.BRAVE
        
        return {
            "primary_provider": analysis["provider"],
            "fallback_provider": fallback,
            "query_type": analysis["query_type"],
            "reasoning": analysis["reasoning"],
            "confidence": analysis["confidence"],
            "use_fallback_if": "insufficient results or primary provider fails"
        }


class NewsSearchRouter:
    """
    Specialized router for news searches
    
    Strategy:
    - Brave Search: Real-time news, breaking news, general news queries
    - SerpAPI: News with rich metadata, news feed, trending topics
    """
    
    NEWS_KEYWORDS = [
        "news", "breaking", "latest", "headline", "report",
        "announcement", "update", "press release"
    ]
    
    TRENDING_KEYWORDS = [
        "trending", "viral", "popular", "top stories",
        "most read", "hot topics"
    ]
    
    @staticmethod
    def analyze_news_query(query: str) -> Dict[str, Any]:
        """
        Analyze news query and determine optimal provider
        
        Returns:
            Dict with provider, reasoning, and search parameters
        """
        query_lower = query.lower()
        
        # Check for trending/popular content (needs SerpAPI for metadata)
        if any(keyword in query_lower for keyword in NewsSearchRouter.TRENDING_KEYWORDS):
            return {
                "provider": SearchProviderChoice.SERPAPI,
                "reasoning": "Trending news requires rich metadata and popularity signals",
                "search_type": "news_trending",
                "confidence": 0.85
            }
        
        # Check for breaking/real-time news (Brave is faster)
        if "breaking" in query_lower or "just now" in query_lower:
            return {
                "provider": SearchProviderChoice.BRAVE,
                "reasoning": "Breaking news requires real-time results - Brave is faster",
                "search_type": "news_breaking",
                "confidence": 0.90
            }
        
        # Default to Brave for general news (faster, cleaner results)
        return {
            "provider": SearchProviderChoice.BRAVE,
            "reasoning": "General news search - Brave provides fast, clean results",
            "search_type": "news_general",
            "confidence": 0.80
        }
    
    @staticmethod
    def get_news_strategy(query: str) -> Dict[str, Any]:
        """Get complete news search strategy"""
        analysis = NewsSearchRouter.analyze_news_query(query)
        
        # Determine fallback
        if analysis["provider"] == SearchProviderChoice.BRAVE:
            fallback = SearchProviderChoice.SERPAPI
        else:
            fallback = SearchProviderChoice.BRAVE
        
        return {
            "primary_provider": analysis["provider"],
            "fallback_provider": fallback,
            "search_type": analysis["search_type"],
            "reasoning": analysis["reasoning"],
            "confidence": analysis["confidence"]
        }
