"""
News Sources Configuration and Search Logic
Support for searching from Reuters, BBC, NYT, Washington Post, WSJ
"""
from typing import List, Dict, Any, Optional
from enum import Enum
import aiohttp
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NewsSource(str, Enum):
    """Supported news sources"""
    REUTERS = "reuters"
    BBC = "bbc"
    NYT = "nyt"
    WASHINGTON_POST = "washingtonpost"
    WSJ = "wsj"


class QueryComplexity(str, Enum):
    """Query complexity levels"""
    BREAKING = "breaking"  # Breaking news/urgent news
    COMPLEX = "complex"    # Requires cross-checking
    GENERAL = "general"    # General queries


class NewsSourceConfig:
    """Configuration for each news source"""
    
    SOURCES = {
        NewsSource.REUTERS: {
            "name": "Reuters",
            "priority": 1,  # Highest priority
            "search_url": "https://www.reuters.com/site-search/",
            "api_param": "query",
            "reliability": 0.95
        },
        NewsSource.BBC: {
            "name": "BBC News",
            "priority": 2,
            "search_url": "https://www.bbc.com/search",
            "api_param": "q",
            "reliability": 0.93
        },
        NewsSource.NYT: {
            "name": "The New York Times",
            "priority": 3,
            "search_url": "https://www.nytimes.com/search",
            "api_param": "query",
            "reliability": 0.92
        },
        NewsSource.WASHINGTON_POST: {
            "name": "The Washington Post",
            "priority": 4,
            "search_url": "https://www.washingtonpost.com/search",
            "api_param": "query",
            "reliability": 0.91
        },
        NewsSource.WSJ: {
            "name": "The Wall Street Journal",
            "priority": 5,
            "search_url": "https://www.wsj.com/search",
            "api_param": "query",
            "reliability": 0.90
        }
    }


class SearchRouter:
    """
    Decides how many news sources to search from
    based on query complexity
    """
    
    # Decision rules
    SEARCH_RULES = {
        QueryComplexity.BREAKING: {
            "sources_count": 2,  # Search only 2-3 sources
            "max_sources": 3,
            "timeout": 10,  # seconds
            "description": "Breaking news - fast search"
        },
        QueryComplexity.COMPLEX: {
            "sources_count": 4,  # Search 4-5 sources
            "max_sources": 5,
            "timeout": 15,
            "description": "Complex - requires cross-checking"
        },
        QueryComplexity.GENERAL: {
            "sources_count": 1,  # Start with 1-2 sources
            "max_sources": 2,
            "timeout": 8,
            "description": "General - basic search"
        }
    }
    
    @staticmethod
    def analyze_query(query: str) -> QueryComplexity:
        """
        Analyze query to determine complexity
        """
        query_lower = query.lower()
        
        # Breaking news keywords
        breaking_keywords = [
            "breaking", "urgent", "just now", "latest", "today",
            "urgent", "immediate", "now", "current"
        ]
        
        # Complex query indicators
        complex_keywords = [
            "compare", "analysis", "why", "how", "impact", "consequence",
            "analyze", "examine", "evaluate", "assess", "implications"
        ]
        
        # Check for breaking news
        if any(keyword in query_lower for keyword in breaking_keywords):
            return QueryComplexity.BREAKING
        
        # Check for complex query
        if any(keyword in query_lower for keyword in complex_keywords):
            return QueryComplexity.COMPLEX
        
        # Check query length (longer = more complex)
        if len(query.split()) > 10:
            return QueryComplexity.COMPLEX
        
        # Default to general
        return QueryComplexity.GENERAL
    
    @staticmethod
    def get_sources_to_search(complexity: QueryComplexity) -> List[NewsSource]:
        """
        Select news sources to search based on complexity
        """
        rule = SearchRouter.SEARCH_RULES[complexity]
        sources_count = rule["sources_count"]
        
        # Sort by priority
        sorted_sources = sorted(
            NewsSource,
            key=lambda s: NewsSourceConfig.SOURCES[s]["priority"]
        )
        
        return sorted_sources[:sources_count]
    
    @staticmethod
    def get_search_config(complexity: QueryComplexity) -> Dict[str, Any]:
        """
        Get search configuration based on complexity
        """
        return SearchRouter.SEARCH_RULES[complexity]
