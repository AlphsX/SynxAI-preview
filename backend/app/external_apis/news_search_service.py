"""
News Search Service
Search and aggregate data from multiple news sources
"""
from typing import List, Dict, Any, Optional
import aiohttp
import asyncio
from datetime import datetime
import logging
from .news_sources import NewsSource, NewsSourceConfig, SearchRouter, QueryComplexity

logger = logging.getLogger(__name__)


class NewsSearchService:
    """
    Service for searching news from multiple sources
    """
    
    def __init__(self, serpapi_key: Optional[str] = None):
        self.serpapi_key = serpapi_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_single_source(
        self,
        source: NewsSource,
        query: str,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Search from a single news source
        """
        source_config = NewsSourceConfig.SOURCES[source]
        
        try:
            # Use SerpAPI for search (if API key is available)
            if self.serpapi_key:
                result = await self._search_via_serpapi(source, query, timeout)
            else:
                # Fallback: Use limited Google Search
                result = await self._search_via_google(source, query, timeout)
            
            return {
                "source": source_config["name"],
                "source_id": source.value,
                "success": True,
                "articles": result.get("articles", []),
                "count": len(result.get("articles", [])),
                "search_time": result.get("search_time", 0),
                "reliability": source_config["reliability"]
            }
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout searching {source_config['name']}")
            return self._error_result(source, "Timeout")
        except Exception as e:
            logger.error(f"Error searching {source_config['name']}: {str(e)}")
            return self._error_result(source, str(e))
    
    async def _search_via_serpapi(
        self,
        source: NewsSource,
        query: str,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Search via SerpAPI
        """
        start_time = datetime.now()
        
        # Create site-specific query
        source_config = NewsSourceConfig.SOURCES[source]
        site_query = f"{query} site:{self._get_domain(source)}"
        
        params = {
            "q": site_query,
            "api_key": self.serpapi_key,
            "engine": "google",
            "num": 5,  # Limit results
            "tbm": "nws"  # news search
        }
        
        async with self.session.get(
            "https://serpapi.com/search",
            params=params,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            data = await response.json()
            
            articles = []
            for item in data.get("news_results", [])[:5]:
                articles.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", ""),
                    "date": item.get("date", ""),
                    "source": source_config["name"]
                })
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "articles": articles,
                "search_time": search_time
            }
    
    async def _search_via_google(
        self,
        source: NewsSource,
        query: str,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Fallback: Search via Google (limited)
        """
        start_time = datetime.now()
        source_config = NewsSourceConfig.SOURCES[source]
        
        # Create mock results for demo
        # In production, should use appropriate API
        articles = [{
            "title": f"Sample article from {source_config['name']}",
            "snippet": f"Search results for: {query}",
            "link": f"{self._get_domain(source)}/article/sample",
            "date": datetime.now().isoformat(),
            "source": source_config["name"]
        }]
        
        search_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "articles": articles,
            "search_time": search_time
        }
    
    def _get_domain(self, source: NewsSource) -> str:
        """
        Get domain of news source
        """
        domains = {
            NewsSource.REUTERS: "reuters.com",
            NewsSource.BBC: "bbc.com",
            NewsSource.NYT: "nytimes.com",
            NewsSource.WASHINGTON_POST: "washingtonpost.com",
            NewsSource.WSJ: "wsj.com"
        }
        return domains.get(source, "")
    
    def _error_result(self, source: NewsSource, error: str) -> Dict[str, Any]:
        """
        Create error result
        """
        source_config = NewsSourceConfig.SOURCES[source]
        return {
            "source": source_config["name"],
            "source_id": source.value,
            "success": False,
            "error": error,
            "articles": [],
            "count": 0,
            "search_time": 0,
            "reliability": source_config["reliability"]
        }
    
    async def search_multiple_sources(
        self,
        query: str,
        sources: List[NewsSource],
        timeout: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search from multiple sources simultaneously (parallel)
        """
        tasks = [
            self.search_single_source(source, query, timeout)
            for source in sources
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            else:
                logger.error(f"Search task failed: {result}")
        
        return valid_results
    
    async def intelligent_search(
        self,
        query: str
    ) -> Dict[str, Any]:
        """
        Intelligent search - automatically decides how many sources to search
        """
        # 1. Analyze query
        complexity = SearchRouter.analyze_query(query)
        
        # 2. Select news sources
        sources = SearchRouter.get_sources_to_search(complexity)
        
        # 3. Get configuration
        config = SearchRouter.get_search_config(complexity)
        
        logger.info(
            f"Search decision: complexity={complexity.value}, "
            f"sources={len(sources)}, timeout={config['timeout']}s"
        )
        
        # 4. Search
        start_time = datetime.now()
        results = await self.search_multiple_sources(
            query,
            sources,
            timeout=config["timeout"]
        )
        total_time = (datetime.now() - start_time).total_seconds()
        
        # 5. Aggregate results
        return {
            "query": query,
            "complexity": complexity.value,
            "decision": {
                "sources_searched": len(sources),
                "source_names": [NewsSourceConfig.SOURCES[s]["name"] for s in sources],
                "timeout": config["timeout"],
                "reason": config["description"]
            },
            "results": results,
            "summary": self._create_summary(results),
            "total_articles": sum(r.get("count", 0) for r in results),
            "total_search_time": round(total_time, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create concise summary of results
        """
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]
        
        all_articles = []
        for result in successful:
            all_articles.extend(result.get("articles", []))
        
        # Sort by reliability and recency
        sorted_articles = sorted(
            all_articles,
            key=lambda x: (x.get("date", ""), x.get("source", "")),
            reverse=True
        )
        
        return {
            "sources_successful": len(successful),
            "sources_failed": len(failed),
            "total_articles_found": len(all_articles),
            "top_articles": sorted_articles[:10],  # Show only top 10
            "sources_used": list(set(r["source"] for r in successful))
        }
