"""
News Agent - AI Agent that intelligently searches and summarizes news
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from ..external_apis.news_search_service import NewsSearchService
from ..external_apis.news_sources import SearchRouter, QueryComplexity
from ..config import settings

logger = logging.getLogger(__name__)


class NewsAgent:
    """
    AI Agent for searching and summarizing news
    - Automatically decides how many sources to search
    - Provides concise news summaries
    - Does not dump raw results
    """
    
    def __init__(self, ai_provider=None):
        """
        Args:
            ai_provider: AI provider สำหรับสรุปข่าว (Groq, OpenAI, etc.)
        """
        self.ai_provider = ai_provider
        self.settings = get_settings()
    
    async def search_and_summarize(
        self,
        query: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Intelligently search and summarize news
        
        Args:
            query: Search query
            language: Language for summary (en/th)
        
        Returns:
            Dict containing search results and summary
        """
        try:
            # 1. Search news (intelligent search)
            async with NewsSearchService(
                serpapi_key=self.settings.SERP_API_KEY
            ) as news_service:
                search_result = await news_service.intelligent_search(query)
            
            # 2. Summarize news
            summary = await self._create_intelligent_summary(
                search_result,
                language
            )
            
            # 3. Create response
            return {
                "success": True,
                "query": query,
                "decision": search_result["decision"],
                "summary": summary,
                "sources_used": search_result["summary"]["sources_used"],
                "total_articles": search_result["total_articles"],
                "search_time": search_result["total_search_time"],
                "timestamp": search_result["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error in news agent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def _create_intelligent_summary(
        self,
        search_result: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """
        Create concise and intelligent news summary
        """
        summary_data = search_result["summary"]
        top_articles = summary_data["top_articles"]
        
        if not top_articles:
            return {
                "text": "No relevant news found" if language == "en" else "ไม่พบข่าวที่เกี่ยวข้อง",
                "key_points": [],
                "sources": []
            }
        
        # If AI provider is available, use AI summarization
        if self.ai_provider:
            ai_summary = await self._ai_summarize(
                top_articles,
                search_result["query"],
                language
            )
            return ai_summary
        
        # If no AI provider, use rule-based summary
        return self._rule_based_summary(top_articles, language)
    
    async def _ai_summarize(
        self,
        articles: List[Dict[str, Any]],
        query: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Use AI to summarize news
        """
        try:
            # Create prompt
            articles_text = "\n\n".join([
                f"**{article['title']}**\n{article['snippet']}\nSource: {article['source']}"
                for article in articles[:5]  # Use only first 5 articles
            ])
            
            prompt = f"""You are an AI News Analyst specialized in news summarization.

Search Query: {query}

Found Articles:
{articles_text}

Please summarize these articles concisely in {'English' if language == 'en' else 'Thai'}:
1. Main summary in 2-3 sentences
2. Key points (3-5 items)
3. Reliable sources

Respond in JSON format:
{{
    "summary": "Main summary...",
    "key_points": ["Point 1", "Point 2", ...],
    "sources": ["Source 1", "Source 2", ...]
}}"""
            
            # Call AI provider
            response = await self.ai_provider.generate(
                prompt=prompt,
                temperature=0.3,  # Low for accuracy
                max_tokens=500
            )
            
            # Parse JSON response
            import json
            result = json.loads(response)
            
            return {
                "text": result.get("summary", ""),
                "key_points": result.get("key_points", []),
                "sources": result.get("sources", [])
            }
            
        except Exception as e:
            logger.error(f"Error in AI summarization: {str(e)}")
            # Fallback to rule-based
            return self._rule_based_summary(articles, language)
    
    def _rule_based_summary(
        self,
        articles: List[Dict[str, Any]],
        language: str
    ) -> Dict[str, Any]:
        """
        Rule-based news summary (without AI)
        """
        # Count news sources
        sources = list(set(article["source"] for article in articles))
        
        # Create summary
        if language == "en":
            summary_text = f"Found {len(articles)} relevant articles from {len(sources)} sources"
        else:
            summary_text = f"พบข่าวที่เกี่ยวข้อง {len(articles)} ข่าว จาก {len(sources)} แหล่ง"
        
        # Key points (use titles of first few articles)
        key_points = [
            article["title"]
            for article in articles[:5]
        ]
        
        return {
            "text": summary_text,
            "key_points": key_points,
            "sources": sources,
            "articles": articles[:5]  # Show only first 5 articles
        }
    
    def explain_decision(
        self,
        complexity: str,
        sources_count: int
    ) -> str:
        """
        Explain agent's decision
        """
        explanations = {
            "breaking": f"🔴 Breaking news - fast search from {sources_count} sources for speed",
            "complex": f"🔍 Complex query - search {sources_count} sources for cross-checking",
            "general": f"📰 General query - search {sources_count} sources for efficiency"
        }
        return explanations.get(complexity, f"Search {sources_count} sources")
