#!/usr/bin/env python3
"""
Test LangSmith Integration and Search APIs
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Add app to path
sys.path.append('app')

from app.memory.langchain_memory_service import langchain_memory_service
from app.external_apis.search_service import search_service


async def test_langsmith_tracing():
    """Test LangSmith tracing"""
    print("\n" + "="*80)
    print("🔍 TESTING LANGSMITH INTEGRATION")
    print("="*80)
    
    session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Test basic memory operations
        print(f"📝 Testing memory operations for session: {session_id}")
        
        # Add user message
        await langchain_memory_service.add_message_to_history(
            session_id=session_id,
            message="Hello, testing LangSmith integration",
            is_user=True,
            metadata={"test": "langsmith_integration"}
        )
        
        # Test LLM invocation with memory (this should show in LangSmith)
        print("🚀 Testing LLM invocation with LangSmith tracing...")
        response = await langchain_memory_service.invoke_with_memory(
            session_id=session_id,
            message="Please reply in Thai and tell me if you remember the previous message.",
            system_prompt="You are an AI that replies in Thai and can remember previous conversations."
        )
        
        print(f"✅ LLM Response: {response}")
        
        # Get conversation history
        history = await langchain_memory_service.get_conversation_history(session_id)
        print(f"📚 Conversation history has {len(history)} messages")
        
        # Get memory stats
        stats = await langchain_memory_service.get_memory_stats(session_id)
        print(f"📊 Memory stats: {stats}")
        
        print("✅ LangSmith integration test completed!")
        print("🔗 Check your LangSmith dashboard at: https://smith.langchain.com/")
        
        return True
        
    except Exception as e:
        print(f"❌ LangSmith test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_search_apis():
    """Test Search APIs"""
    print("\n" + "="*80)
    print("🔍 TESTING SEARCH APIS")
    print("="*80)
    
    try:
        # Test web search
        print("🌐 Testing web search...")
        web_results = await search_service.search_web(
            query="artificial intelligence news",
            count=3
        )
        
        if web_results:
            print(f"✅ Web search successful! Found {len(web_results)} results")
            for i, result in enumerate(web_results[:2], 1):
                print(f"  {i}. {result.get('title', 'No title')[:60]}...")
                print(f"     Provider: {result.get('provider', 'unknown')}")
        else:
            print("❌ Web search returned no results")
        
        # Test news search
        print("\n📰 Testing news search...")
        news_results = await search_service.search_news(
            query="technology",
            count=3
        )
        
        if news_results:
            print(f"✅ News search successful! Found {len(news_results)} results")
            for i, result in enumerate(news_results[:2], 1):
                print(f"  {i}. {result.get('title', 'No title')[:60]}...")
                print(f"     Provider: {result.get('provider', 'unknown')}")
        else:
            print("❌ News search returned no results")
        
        # Test combined search
        print("\n🔄 Testing combined search...")
        combined_results = await search_service.search_combined(
            query="AI technology",
            web_count=2,
            news_count=2
        )
        
        total_results = combined_results.get('total_results', 0)
        print(f"✅ Combined search completed! Total results: {total_results}")
        print(f"   Web results: {len(combined_results.get('web', []))}")
        print(f"   News results: {len(combined_results.get('news', []))}")
        
        # Get service health
        print("\n🏥 Checking search service health...")
        health = await search_service.get_service_health()
        print(f"Overall status: {health.get('overall_status', 'unknown')}")
        
        for service_name, service_health in health.get('services', {}).items():
            status = service_health.get('status', 'unknown')
            print(f"  {service_name}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration():
    """Test integration between LangSmith and Search"""
    print("\n" + "="*80)
    print("🔗 TESTING INTEGRATED FUNCTIONALITY")
    print("="*80)
    
    session_id = f"integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Search for information
        print("🔍 Searching for AI news...")
        search_results = await search_service.search_web("latest AI developments", count=2)
        
        if search_results:
            # Create context from search results
            search_context = "\n".join([
                f"- {result.get('title', '')}: {result.get('description', '')}"
                for result in search_results[:2]
            ])
            
            # Use LLM with search context and memory
            prompt = f"""Based on the latest AI news found:

{search_context}

Please summarize this information in Thai."""
            
            print("🤖 Processing with LLM and memory...")
            response = await langchain_memory_service.invoke_with_memory(
                session_id=session_id,
                message=prompt,
                system_prompt="You are an AI that summarizes news in Thai."
            )
            
            print(f"✅ Integration successful!")
            print(f"📝 AI Summary: {response[:200]}...")
            
            return True
        else:
            print("❌ No search results to process")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🚀 Starting comprehensive API tests...")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    
    # Check environment variables
    print("\n📋 Environment Check:")
    print(f"  LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
    print(f"  LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
    print(f"  BRAVE_SEARCH_API_KEY: {'✅ Set' if os.getenv('BRAVE_SEARCH_API_KEY') else '❌ Missing'}")
    print(f"  SERP_API_KEY: {'✅ Set' if os.getenv('SERP_API_KEY') else '❌ Missing'}")
    print(f"  GROQ_API_KEY: {'✅ Set' if os.getenv('GROQ_API_KEY') else '❌ Missing'}")
    
    results = []
    
    # Test LangSmith
    langsmith_result = await test_langsmith_tracing()
    results.append(("LangSmith Integration", langsmith_result))
    
    # Test Search APIs
    search_result = await test_search_apis()
    results.append(("Search APIs", search_result))
    
    # Test Integration
    integration_result = await test_integration()
    results.append(("Integration Test", integration_result))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is working correctly.")
        print("🔗 Check LangSmith dashboard: https://smith.langchain.com/")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())
