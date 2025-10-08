import os
import asyncio
import json
import logging
import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Dict, Any
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SERP-Master API",
    description="AI-Powered SEO Tool Backend with DataForSEO Integration",
    version="1.0.0"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
# Add port 3005 if not already present
if "http://localhost:3005" not in cors_origins:
    cors_origins.append("http://localhost:3005")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DataForSEO API configuration
DATAFORSEO_LOGIN = os.getenv("DATAFORSEO_LOGIN")
DATAFORSEO_PASSWORD = os.getenv("DATAFORSEO_PASSWORD")
DATAFORSEO_API_URL = os.getenv("DATAFORSEO_API_URL", "https://api.dataforseo.com/v3")

# DataForSEO API Client
class DataForSEOClient:
    """Client for DataForSEO API integration"""

    def __init__(self):
        self.base_url = DATAFORSEO_API_URL
        self.login = DATAFORSEO_LOGIN
        self.password = DATAFORSEO_PASSWORD
        self.auth_header = self._create_auth_header()

    def _create_auth_header(self):
        """Create Basic Auth header for DataForSEO"""
        if not self.login or not self.password:
            return None
        credentials = f"{self.login}:{self.password}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {b64_credentials}"}

    async def get_keywords(self, query: str, location: str = "United States"):
        """Get keyword data from DataForSEO"""
        if not self.auth_header:
            return {"error": "DataForSEO credentials not configured"}

        endpoint = f"{self.base_url}/keywords_data/google_ads/search_volume/live"

        payload = [{
            "keywords": [query],
            "location_name": location,
            "language_name": "English"
        }]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    json=payload,
                    headers={**self.auth_header, "Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        return {"error": f"API error: {response.status} - {error_text}"}
        except Exception as e:
            logger.error(f"DataForSEO API error: {str(e)}")
            return {"error": str(e)}

# Initialize DataForSEO client
dataforseo_client = DataForSEOClient()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with DataForSEO status"""
    return {
        "status": "healthy",
        "service": "SERP-Master API",
        "version": "1.0.0",
        "dataforseo_configured": bool(DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD)
    }

# CopilotKit compatible streaming endpoint
@app.post("/api/copilotkit")
async def copilotkit_endpoint(request: dict):
    """CopilotKit compatible streaming endpoint"""

    messages = request.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    last_message = messages[-1].get("content", "")

    async def stream_response() -> AsyncGenerator[str, None]:
        """Stream SSE responses for CopilotKit"""

        # Generate SEO-specific response
        response_text = await generate_seo_response(last_message)

        # Stream response in chunks
        for chunk in response_text.split():
            yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_CONTENT', 'content': chunk + ' '})}\n\n"
            await asyncio.sleep(0.05)

        # Send completion event
        yield f"data: {json.dumps({'type': 'RUN_COMPLETED'})}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Keyword research endpoint
@app.post("/api/keywords/research")
async def keyword_research(request: dict):
    """Keyword research using DataForSEO API"""
    query = request.get("query", "")
    location = request.get("location", "United States")

    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")

    # Get data from DataForSEO
    result = await dataforseo_client.get_keywords(query, location)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return {"query": query, "location": location, "data": result}

async def generate_seo_response(user_message: str) -> str:
    """Generate SEO-specific assistant response with DataForSEO integration"""

    message_lower = user_message.lower()

    # Check if DataForSEO is configured
    config_status = "✅ Connected" if DATAFORSEO_LOGIN else "⚠️ Not configured"

    if any(word in message_lower for word in ["keyword", "keywords", "research"]):
        return f"I can help you with keyword research using live data from DataForSEO! {config_status}\n\nWhat's your business or target topic? I'll find relevant keywords with search volumes, difficulty scores, and opportunities."

    elif any(word in message_lower for word in ["audit", "technical", "speed", "seo audit"]):
        return f"I'll help you run a comprehensive technical SEO audit! {config_status}\n\nI can check: Core Web Vitals, mobile optimization, page speed, schema markup, and more. What's your website URL?"

    elif any(word in message_lower for word in ["content", "optimize", "writing"]):
        return f"Content optimization is my specialty! {config_status}\n\nI can analyze your content for SEO improvements, suggest better titles/descriptions, and optimize for target keywords. Share your page URL or content topic."

    elif "google discover" in message_lower:
        return f"Google Discover is a massive opportunity with 1B+ users! {config_status}\n\nI can help optimize your content for Discover: high-quality images (1200px width), fresh content, RSS setup, and follow button placement."

    elif any(word in message_lower for word in ["status", "health", "working"]):
        return f"SERP-Master Status:\n🚀 Backend: Running\n📊 DataForSEO API: {config_status}\n🤖 AI Assistant: Active\n\nReady to help with your SEO needs!"

    else:
        return f"Hi! I'm your AI SEO assistant. {config_status}\n\nI can help with:\n• Keyword research\n• Technical SEO audits\n• Content optimization\n• Google Discover optimization\n\nWhat would you like to work on?"

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
