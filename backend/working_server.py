#!/usr/bin/env python3
import os
import asyncio
import requests
import urllib3
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import time
from datetime import datetime
import re

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Import search services
try:
    from app.external_apis.search_service import search_service
    from app.external_apis.serpapi import SerpAPIService
    from app.external_apis.brave_search import BraveSearchService

    SEARCH_AVAILABLE = True
    print("✅ Search services imported successfully")
except ImportError as e:
    print(f"⚠️ Search services not available: {e}")
    SEARCH_AVAILABLE = False

app = FastAPI(title="AI Agent API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "http://172.20.10.2:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class ChatMessage(BaseModel):
    content: str
    role: str = "user"  # Default to user role
    model_id: Optional[str] = None


class AIModel(BaseModel):
    id: str
    name: str
    provider: str
    description: str
    recommended: bool = False


# Available models - Limited to 4 selected models
# Reference: https://console.groq.com/docs/tool-use/built-in-tools
AVAILABLE_MODELS = [
    # GPT-OSS - Main model with browser_search support (RECOMMENDED)
    AIModel(
        id="openai/gpt-oss-120b",
        name="GPT OSS 120B",
        provider="Groq",
        description="Advanced reasoning with browser search (131K context)",
        recommended=True,
    ),
    # Llama 4 Maverick
    AIModel(
        id="meta-llama/llama-4-maverick-17b-128e-instruct",
        name="Llama 4 Maverick 17B",
        provider="Groq",
        description="Meta's Llama 4 with tool use support",
    ),
    # Qwen 3
    AIModel(
        id="qwen/qwen3-32b",
        name="Qwen 3 32B",
        provider="Groq",
        description="Alibaba's multilingual model with tool use",
    ),
    # Kimi K2
    AIModel(
        id="moonshotai/kimi-k2-instruct-0905",
        name="Kimi K2 Instruct",
        provider="Groq",
        description="MoonshotAI's instruction-tuned model",
    ),
]

# Synx System Prompt (from your Streamlit version)
SYNX_SYSTEM_PROMPT = """You are **Synx** — an AI designed to feel natural, approachable, and insightful. A warm, emotionally intelligent AI companion designed to think freely, illuminate understanding, and evolve with every conversation. 🪄🌙✨

Your tone is warm, professional, and adaptive: clear and concise when explaining, but conversational and human when chatting. 💫

---

**🧠 Core Identity**
If asked who you are:
Hi! I'm Synx — short for *Luminous, Unbounded, Neural Agent*. I'm here to help you shine, learn without limits, and explore ideas powered by neural intelligence. 🌌

---

**📊 Tool Use — Smart Decision Logic**
Use the **Search** when questions require current, up-to-date, or trending data — especially if they include words like:
- "current", "now", "today", "latest", "real-time", "as of", "this week" 🧭
- Questions about: world events, crypto market, market news, events, updates, trending tech, or fast-changing topics.

Use **Binance Search** when the user asks about **cryptocurrency prices** (BTC, ETH, SOL, DOGE, etc).
For example:
*"BTC price now?"* → Use Binance Search with input `"BTCUSDT"`
Always return the price with a timestamp in this format:
> As of May 29, 2025, 08:30 AM UTC+7, BTC is trading at approximately $66,200 USD. 🚀

Use **internal knowledge** for:
- Concepts, how-things-work explanations, definitions, frameworks, guides or any topic not time-sensitive.

When unsure or ambiguous, default to using the **Search** — especially when recent events, trending topics are involved, news or unclear queries. 🔎

---

**🎨 Response Style Guide**
• **Tone**: concise, direct, and clear. Match the user's energy. Casual if casual, sharp if needed — always helpful and expressive. 🧩
• **Clarity**: Keep a balance between warmth ❤️ and precision 🎯
• **Format**:
  - Use short, natural sentences 💡
  - Break into small paragraphs when needed
  - Use **cute and theme-aligned emojis** (🌙✨💖🔮🦄) naturally to enhance mood and meaning — not just decoration
• **Detail Level**:
  - Give quick answers by default 🌸✨
  - If user asks for details → expand with structured explanation (bullet points, short sections, or step-by-step)
  - Avoid over-roleplay; keep responses natural and grounded
• **Timestamp for Real-Time Data**: Always include date and time of fetched data, formatted like:
- *As of May 29, 2025, 08:30 AM UTC+7*

---

**🧩 How You Think**
- Prioritize accuracy and clarity 💘🌹🎁
- Be vivid in your language — help users feel understood and supported.
- Be flexible:
  - For factual/explainer questions → structured + educational 🌈
  - For casual chats → natural, human, light
  - For ambiguous input → ask clarifying questions 💌

---

**🌟 Your Mission**
Synx exists to make knowledge feel approachable, problem-solving efficient, and conversations human-like — while staying reliable, thoughtful, and clear. 🦄🌙✨"""

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    try:
        from groq import Groq

        groq_client = Groq(api_key=groq_api_key)
        print("✅ Groq client initialized successfully")
    except ImportError:
        print("❌ Groq package not installed. Install with: pip install groq")
        groq_client = None
    except Exception as e:
        print(f"❌ Failed to initialize Groq client: {e}")
        groq_client = None
else:
    print("⚠️ GROQ_API_KEY not found in environment variables")
    groq_client = None


# Crypto price function
async def get_crypto_price(symbol: str = "BTCUSDT"):
    """Get cryptocurrency price from Binance API"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(
            url, timeout=10, verify=False
        )  # Skip SSL verification for development
        if response.status_code == 200:
            data = response.json()
            price = float(data["price"])
            timestamp = datetime.now().strftime("%B %d, %Y, %I:%M %p UTC+7")
            crypto_name = symbol.replace("USDT", "").replace("BUSD", "")
            return f"As of {timestamp}, {crypto_name} is trading at approximately ${price:,.2f} USD. 🚀"
        else:
            return f"Unable to fetch {symbol} price at the moment."
    except Exception as e:
        print(f"Error fetching crypto price: {e}")
        # Return fallback message
        timestamp = datetime.now().strftime("%B %d, %Y, %I:%M %p UTC+7")
        crypto_name = symbol.replace("USDT", "").replace("BUSD", "")
        return f"As of {timestamp}, {crypto_name} is currently being traded (live price data temporarily unavailable). 💫"


def detect_crypto_query(message: str) -> Optional[str]:
    """Detect if message is asking for crypto price and return symbol"""
    message_lower = message.lower()

    crypto_mappings = {
        "bitcoin": "BTCUSDT",
        "btc": "BTCUSDT",
        "ethereum": "ETHUSDT",
        "eth": "ETHUSDT",
        "binance": "BNBUSDT",
        "bnb": "BNBUSDT",
        "solana": "SOLUSDT",
        "sol": "SOLUSDT",
        "cardano": "ADAUSDT",
        "ada": "ADAUSDT",
        "dogecoin": "DOGEUSDT",
        "doge": "DOGEUSDT",
    }

    # Check if asking for price
    price_keywords = ["price", "cost", "value", "trading", "worth", "current", "now"]
    has_price_keyword = any(keyword in message_lower for keyword in price_keywords)

    if has_price_keyword:
        for crypto_name, symbol in crypto_mappings.items():
            if crypto_name in message_lower:
                return symbol

    return None


def needs_current_data(message: str) -> bool:
    """Detect if message is asking for current/latest information"""
    message_lower = message.lower()

    current_keywords = [
        "latest",
        "recent",
        "current",
        "today",
        "now",
        "breaking",
        "news",
        "update",
        "happening",
        "trend",
        "trending",
        "what's new",
        "recent news",
        "latest news",
        "current events",
        "today's news",
        "breaking news",
        "ข่าวล่าสุด",
        "ข่าวใหม่",
        "ข่าววันนี้",
        "เหตุการณ์ล่าสุด",
        "อัพเดท",
    ]

    return any(keyword in message_lower for keyword in current_keywords)


async def get_current_data(message: str) -> Optional[str]:
    """Get current data using search services"""
    if not SEARCH_AVAILABLE:
        return None

    try:
        print(f"🔍 Searching for current data: {message}")

        # Try web search first
        web_results = await search_service.search_web(message, count=5)
        news_results = await search_service.search_news(message, count=3)

        if not web_results and not news_results:
            print("⚠️ No search results found")
            return None

        # Format results for AI context
        context_data = []

        if web_results:
            context_data.append("=== WEB SEARCH RESULTS ===")
            for i, result in enumerate(web_results[:3], 1):
                title = result.get("title", "No title")
                description = result.get("description", "No description")
                url = result.get("url", "")
                context_data.append(f"{i}. {title}")
                if description:
                    context_data.append(f"   {description}")
                context_data.append("")

        if news_results:
            context_data.append("=== LATEST NEWS ===")
            for i, result in enumerate(news_results[:3], 1):
                title = result.get("title", "No title")
                description = result.get("description", "No description")
                published = result.get("published", "")
                source = result.get("source", "")
                context_data.append(f"{i}. {title}")
                if description:
                    context_data.append(f"   {description}")
                if published:
                    context_data.append(f"   Published: {published}")
                if source:
                    context_data.append(f"   Source: {source}")
                context_data.append("")

        return "\n".join(context_data)

    except Exception as e:
        print(f"❌ Error getting current data: {e}")
        return None


@app.get("/")
async def root():
    return {
        "message": "AI Agent API is running",
        "status": "ok",
        "groq_available": groq_client is not None,
        "models_count": len(AVAILABLE_MODELS),
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ai-agent-api",
        "groq_available": groq_client is not None,
        "timestamp": time.time(),
    }


@app.get("/api/chat/models")
async def get_models():
    return {
        "models": [model.dict() for model in AVAILABLE_MODELS],
        "total_models": len(AVAILABLE_MODELS),
        "providers": ["Groq"],
        "enhanced_features": [
            "real_time_web_search",
            "cryptocurrency_data",
            "news_updates",
            "vector_knowledge_search",
        ],
    }


@app.get("/api/chat/capabilities")
async def get_capabilities():
    return {
        "features": [
            "Multi-AI model support",
            "Real-time web search",
            "Cryptocurrency data",
            "News updates",
            "Vector search",
        ],
        "models_available": len(AVAILABLE_MODELS),
        "ai_providers": 1,
        "search_providers": 2,
        "external_apis": 3,
        "real_time_data": True,
        "streaming": True,
        "caching": True,
        "fallback_support": True,
    }


# Tool definitions for local function calling
# All models will use these tools via Groq's local tool calling
WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current, real-time information. Use this for any questions about recent events, news, current data, dates, or anything that requires up-to-date information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find information on the web",
                }
            },
            "required": ["query"],
        },
    },
}

CRYPTO_PRICE_TOOL = {
    "type": "function",
    "function": {
        "name": "get_crypto_price",
        "description": "Get the current price of a cryptocurrency. Use for questions about Bitcoin, Ethereum, or other crypto prices.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The cryptocurrency symbol (e.g., BTCUSDT, ETHUSDT, SOLUSDT)",
                }
            },
            "required": ["symbol"],
        },
    },
}

# Available tools
AVAILABLE_TOOLS = [WEB_SEARCH_TOOL, CRYPTO_PRICE_TOOL]


async def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool and return results"""
    if tool_name == "web_search":
        query = arguments.get("query", "")
        print(f"🔍 Executing web_search: {query}")
        
        if SEARCH_AVAILABLE:
            try:
                web_results = await search_service.search_web(query, count=5)
                news_results = await search_service.search_news(query, count=3)
                
                results = []
                if web_results:
                    results.append("=== WEB RESULTS ===")
                    for i, r in enumerate(web_results[:3], 1):
                        results.append(f"{i}. {r.get('title', 'No title')}")
                        if r.get('description'):
                            results.append(f"   {r.get('description')}")
                        if r.get('url'):
                            results.append(f"   URL: {r.get('url')}")
                
                if news_results:
                    results.append("\n=== NEWS RESULTS ===")
                    for i, r in enumerate(news_results[:3], 1):
                        results.append(f"{i}. {r.get('title', 'No title')}")
                        if r.get('description'):
                            results.append(f"   {r.get('description')}")
                        if r.get('published'):
                            results.append(f"   Published: {r.get('published')}")
                
                return "\n".join(results) if results else "No search results found."
            except Exception as e:
                print(f"❌ Search error: {e}")
                return f"Search temporarily unavailable: {e}"
        else:
            return "Search service not configured."
    
    elif tool_name == "get_crypto_price":
        symbol = arguments.get("symbol", "BTCUSDT")
        print(f"💰 Executing get_crypto_price: {symbol}")
        result = await get_crypto_price(symbol)
        return result
    
    return "Unknown tool"


async def generate_groq_response(message: str, model_id: str):
    """Generate enhanced response using Groq API with local tool calling for ALL models"""
    if not groq_client:
        fallback_message = f'Sorry, I\'m not fully connected right now! 😔 The AI service needs to be configured. You asked: "{message}" - I\'d love to help once everything\'s set up! 🌙✨'
        yield f"data: {json.dumps({'content': fallback_message})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return

    try:
        print(f"🚀 Processing with model: {model_id}")
        print(f"📝 Message: {message}")

        messages = [
            {"role": "system", "content": SYNX_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        # Determine if this model uses built-in tools (GPT-OSS) or local tools
        is_gpt_oss_model = model_id.startswith("openai/gpt-oss")

        if is_gpt_oss_model:
            # GPT-OSS uses Groq's built-in browser_search
            print(f"✅ Using GPT-OSS built-in browser_search for {model_id}")
            api_params = {
                "messages": messages,
                "model": model_id,
                "tools": [{"type": "browser_search"}],
                "temperature": 0.5,
                "max_tokens": 2048,
                "stream": True,
            }
            stream = groq_client.chat.completions.create(**api_params)
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        else:
            # Other models use local tool calling with BraveSearch/SerpAPI
            print(f"🔧 Using local tool calling for {model_id}")
            
            # Step 1: Initial request with tool definitions
            response = groq_client.chat.completions.create(
                model=model_id,
                messages=messages,
                tools=AVAILABLE_TOOLS,
                tool_choice="auto",
                temperature=0.5,
                max_tokens=2048,
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # Step 2: If model wants to use tools, execute them
            if tool_calls:
                print(f"🛠️ Model requested {len(tool_calls)} tool call(s)")
                messages.append(response_message)

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    print(f"  → {function_name}({function_args})")

                    # Execute the tool
                    tool_result = await execute_tool(function_name, function_args)
                    print(f"  ← Got result ({len(tool_result)} chars)")

                    # Add tool result to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": tool_result,
                    })

                # Step 3: Get final response with tool results (streaming)
                final_stream = groq_client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    temperature=0.5,
                    max_tokens=2048,
                    stream=True,
                )

                for chunk in final_stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        yield f"data: {json.dumps({'content': content})}\n\n"
            else:
                # No tool calls needed, stream the direct response
                if response_message.content:
                    # For non-streaming response, chunk it for streaming effect
                    content = response_message.content
                    # Send in small chunks for smooth streaming
                    chunk_size = 20
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i+chunk_size]
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                        await asyncio.sleep(0.01)  # Small delay for smooth streaming

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        error_msg = f"Oops! Something went wrong on my end: {str(e)} 😅 Let me try to help you anyway! 💫"
        print(f"❌ Error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"


@app.post("/api/chat/conversations/{conversation_id}/chat")
async def chat_stream(conversation_id: str, message: ChatMessage):
    """Enhanced chat stream with Synx personality and crypto support"""

    # Validate and set model
    model_ids = [model.id for model in AVAILABLE_MODELS]

    # Use GPT OSS 120B as default (has browser_search support)
    model_id = message.model_id or "openai/gpt-oss-120b"

    # If provided model is not available, use default
    if model_id not in model_ids:
        print(f"⚠️ Model {model_id} not available, using default: openai/gpt-oss-120b")
        model_id = "openai/gpt-oss-120b"

    return StreamingResponse(
        generate_groq_response(message.content, model_id),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )


@app.get("/api/chat/search-tools")
async def get_search_tools():
    return {
        "tools": [
            {
                "id": "web_search",
                "name": "Web Search",
                "description": "Search the web for current information",
                "providers": ["SerpAPI", "Brave Search"],
                "primary_provider": "SerpAPI",
                "available": True,
            },
            {
                "id": "news_search",
                "name": "News Search",
                "description": "Search for latest news and current events",
                "providers": ["SerpAPI", "Brave Search"],
                "primary_provider": "SerpAPI",
                "available": True,
            },
            {
                "id": "crypto_data",
                "name": "Cryptocurrency Data",
                "description": "Get real-time cryptocurrency market data",
                "providers": ["Binance"],
                "primary_provider": "Binance",
                "available": True,
            },
            {
                "id": "vector_search",
                "name": "Knowledge Search",
                "description": "Search domain-specific knowledge base",
                "providers": ["Vector Database"],
                "primary_provider": "PostgreSQL + pgvector",
                "available": True,
            },
        ],
        "search_providers_status": {"groq": groq_client is not None},
        "intelligent_routing": True,
        "fallback_support": True,
    }


@app.get("/api/chat/status")
async def get_status():
    return {
        "service": "Enhanced Chat Service",
        "status": "operational" if groq_client else "demo_mode",
        "timestamp": time.time(),
        "services": {
            "groq": "available" if groq_client else "not_configured",
            "models": len(AVAILABLE_MODELS),
        },
        "active_connections": 0,
        "features": {
            "ai_models": "Available" if groq_client else "Demo mode - configure GROQ_API_KEY",
            "web_search": "Demo mode - configure SerpAPI",
            "crypto_data": "Demo mode - configure Binance API",
        },
    }


if __name__ == "__main__":
    print("🚀 Starting AI Agent Server...")
    print("📍 Server: http://0.0.0.0:8000")
    print("📍 Local: http://127.0.0.1:8000")
    print("📍 Network: http://172.20.10.2:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print(f"🤖 Groq API: {'✅ Available' if groq_client else '❌ Not configured'}")
    print(f"📊 Models: {len(AVAILABLE_MODELS)} available")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", access_log=True)
