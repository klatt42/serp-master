from langchain_core.tools import tool
import httpx
import os
import base64
from typing import Dict, Any, List

def get_dataforseo_client():
    """Create an authenticated HTTP client for DataForSEO API."""
    login = os.getenv("DATAFORSEO_LOGIN", "")
    password = os.getenv("DATAFORSEO_PASSWORD", "")

    if not login or not password:
        return None

    credentials = f"{login}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    return httpx.AsyncClient(
        base_url="https://api.dataforseo.com/v3",
        headers={
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
    )

@tool
async def get_keyword_data(keyword: str, location: str = "United States") -> Dict[str, Any]:
    """
    Get keyword data including search volume, competition, and trends.

    Args:
        keyword: The keyword to research
        location: Geographic location for the search (default: United States)

    Returns:
        Dictionary containing keyword metrics and related keywords
    """
    client = get_dataforseo_client()

    if not client:
        # Return mock data if credentials not configured
        return {
            "keyword": keyword,
            "search_volume": 5000,
            "competition": 65,
            "cpc": 2.5,
            "difficulty": 45,
            "related_keywords": [
                f"{keyword} guide",
                f"best {keyword}",
                f"{keyword} tips",
            ],
            "note": "This is mock data. Configure DATAFORSEO credentials for real data."
        }

    try:
        # Example API call structure - adjust based on DataForSEO documentation
        response = await client.post(
            "/keywords_data/google_ads/search_volume/live",
            json=[{
                "keywords": [keyword],
                "location_name": location,
                "language_name": "English"
            }]
        )

        data = response.json()
        # Process and return the data
        return {
            "keyword": keyword,
            "data": data,
            "status": "success"
        }
    except Exception as e:
        return {
            "keyword": keyword,
            "error": str(e),
            "status": "error"
        }
    finally:
        await client.aclose()

@tool
async def get_serp_data(query: str, location: str = "United States", device: str = "desktop") -> Dict[str, Any]:
    """
    Analyze Search Engine Results Pages for a specific query.

    Args:
        query: The search query to analyze
        location: Geographic location for the search (default: United States)
        device: Device type - desktop or mobile (default: desktop)

    Returns:
        Dictionary containing SERP data including top results, features, and rankings
    """
    client = get_dataforseo_client()

    if not client:
        # Return mock data if credentials not configured
        return {
            "query": query,
            "results": [
                {"position": 1, "url": "example.com/page1", "title": f"Best {query} Guide"},
                {"position": 2, "url": "example.com/page2", "title": f"{query} Tips & Tricks"},
                {"position": 3, "url": "example.com/page3", "title": f"Complete {query} Tutorial"},
            ],
            "serp_features": ["featured_snippet", "people_also_ask", "related_searches"],
            "note": "This is mock data. Configure DATAFORSEO credentials for real data."
        }

    try:
        response = await client.post(
            "/serp/google/organic/live/advanced",
            json=[{
                "keyword": query,
                "location_name": location,
                "language_name": "English",
                "device": device
            }]
        )

        data = response.json()
        return {
            "query": query,
            "data": data,
            "status": "success"
        }
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "status": "error"
        }
    finally:
        await client.aclose()

@tool
async def get_competitor_data(domain: str) -> Dict[str, Any]:
    """
    Analyze competitor domain for SEO insights.

    Args:
        domain: The competitor domain to analyze (e.g., "example.com")

    Returns:
        Dictionary containing competitor metrics, top keywords, and backlink data
    """
    client = get_dataforseo_client()

    if not client:
        # Return mock data if credentials not configured
        return {
            "domain": domain,
            "organic_keywords": 15000,
            "organic_traffic": 50000,
            "domain_rank": 75,
            "top_keywords": [
                {"keyword": "seo tools", "position": 3, "volume": 10000},
                {"keyword": "keyword research", "position": 5, "volume": 8000},
                {"keyword": "serp analysis", "position": 7, "volume": 6000},
            ],
            "backlinks": 25000,
            "note": "This is mock data. Configure DATAFORSEO credentials for real data."
        }

    try:
        response = await client.post(
            "/dataforseo_labs/google/domain_overview/live",
            json=[{
                "target": domain,
                "location_name": "United States",
                "language_name": "English"
            }]
        )

        data = response.json()
        return {
            "domain": domain,
            "data": data,
            "status": "success"
        }
    except Exception as e:
        return {
            "domain": domain,
            "error": str(e),
            "status": "error"
        }
    finally:
        await client.aclose()
