"""
News Search API Router
API endpoints for news search
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from .news_search_service import NewsSearchService
from .news_sources import NewsSource, QueryComplexity
from ..config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/news", tags=["news"])


class NewsSearchRequest(BaseModel):
    """Request model for news search"""
    query: str = Field(..., description="Search query")
    sources: Optional[List[str]] = Field(None, description="Desired news sources (optional)")
    complexity: Optional[str] = Field(None, description="Complexity level (optional)")


class NewsSearchResponse(BaseModel):
    """Response model for search results"""
    query: str
    complexity: str
    decision: Dict[str, Any]
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    total_articles: int
    total_search_time: float
    timestamp: str


@router.post("/search", response_model=NewsSearchResponse)
async def search_news(request: NewsSearchRequest):
    """
    Intelligent news search - AI agent automatically decides how many sources to search
    
    - **query**: Search query (required)
    - **sources**: Desired news sources (optional) - if not specified, AI will choose
    - **complexity**: Complexity level (optional) - if not specified, AI will analyze
    
    Example:
    ```json
    {
        "query": "latest news about AI technology"
    }
    ```
    """
    try:
        settings = get_settings()
        
        async with NewsSearchService(serpapi_key=settings.SERP_API_KEY) as service:
            # Use intelligent search
            result = await service.intelligent_search(request.query)
            
            return NewsSearchResponse(**result)
            
    except Exception as e:
        logger.error(f"Error in news search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/custom")
async def search_news_custom(request: NewsSearchRequest):
    """
    Custom news search - specify sources and complexity yourself
    
    - **query**: Search query (required)
    - **sources**: Desired news sources (required) - reuters, bbc, nyt, washingtonpost, wsj
    - **complexity**: Complexity level (optional) - breaking, complex, general
    """
    try:
        settings = get_settings()
        
        # Validate sources
        if request.sources:
            try:
                sources = [NewsSource(s) for s in request.sources]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid source. Valid sources: {[s.value for s in NewsSource]}"
                )
        else:
            raise HTTPException(status_code=400, detail="sources is required for custom search")
        
        async with NewsSearchService(serpapi_key=settings.SERP_API_KEY) as service:
            # Search from specified sources
            results = await service.search_multiple_sources(
                query=request.query,
                sources=sources,
                timeout=15
            )
            
            return {
                "query": request.query,
                "sources_requested": request.sources,
                "results": results,
                "summary": service._create_summary(results),
                "total_articles": sum(r.get("count", 0) for r in results)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in custom news search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources")
async def get_available_sources():
    """
    Get all supported news sources
    """
    from .news_sources import NewsSourceConfig
    
    sources = []
    for source in NewsSource:
        config = NewsSourceConfig.SOURCES[source]
        sources.append({
            "id": source.value,
            "name": config["name"],
            "priority": config["priority"],
            "reliability": config["reliability"]
        })
    
    return {
        "sources": sorted(sources, key=lambda x: x["priority"]),
        "total": len(sources)
    }


@router.get("/complexity-info")
async def get_complexity_info():
    """
    Get information about complexity levels and search rules
    """
    from .news_sources import SearchRouter
    
    info = {}
    for complexity in QueryComplexity:
        rule = SearchRouter.SEARCH_RULES[complexity]
        info[complexity.value] = {
            "description": rule["description"],
            "sources_count": rule["sources_count"],
            "max_sources": rule["max_sources"],
            "timeout": rule["timeout"]
        }
    
    return {
        "complexity_levels": info,
        "examples": {
            "breaking": "latest breaking news, urgent, just now",
            "complex": "compare, analysis, why, how, examine",
            "general": "general questions, what's happening"
        }
    }


@router.post("/agent/search")
async def news_agent_search(request: NewsSearchRequest):
    """
    🤖 AI News Agent - Intelligent news search and summarization
    
    The agent will:
    1. Analyze query to determine complexity
    2. Automatically decide how many sources to search
    3. Search news from appropriate sources
    4. Provide concise summary (no raw data dump)
    
    Example:
    ```json
    {
        "query": "latest AI technology news"
    }
    ```
    """
    try:
        from ..agent.news_agent import NewsAgent
        
        # Create news agent
        agent = NewsAgent()
        
        # Search and summarize
        result = await agent.search_and_summarize(
            query=request.query,
            language="en"  # or detect from query
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        
        # Add decision explanation
        decision_explanation = agent.explain_decision(
            result["decision"]["reason"].split("-")[0].strip(),
            result["decision"]["sources_searched"]
        )
        
        return {
            **result,
            "decision_explanation": decision_explanation,
            "agent_info": {
                "name": "News Agent",
                "version": "1.0",
                "capabilities": [
                    "Intelligent source selection",
                    "Automatic complexity detection",
                    "Concise summarization",
                    "Multi-source cross-checking"
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in news agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
