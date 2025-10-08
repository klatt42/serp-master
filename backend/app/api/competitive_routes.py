"""
Competitive Intelligence API Routes
Endpoints for competitor tracking and analysis
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
import logging

from app.services.competitive_intelligence.competitor_tracker import CompetitorTracker
from app.services.dataforseo_client import DataForSEOClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/competitive", tags=["Competitive Intelligence"])


# Request Models
class CompetitorAnalysisRequest(BaseModel):
    """Request model for competitor analysis"""
    your_brand: str = Field(..., description="Your business/brand name")
    competitor_brands: List[str] = Field(..., min_items=1, max_items=10, description="Competitor names")
    platforms: List[str] = Field(
        default=["youtube", "tiktok", "amazon", "google", "reddit"],
        description="Platforms to analyze"
    )
    keywords: List[str] = Field(..., min_items=1, max_items=50, description="Keywords to track")
    location: str = Field(default="United States", description="Geographic location")


# Routes
@router.post("/analyze")
async def analyze_competitors(request: CompetitorAnalysisRequest):
    """
    Comprehensive competitor analysis across all platforms

    Returns competitive insights, positioning, gaps, and opportunities
    """
    try:
        logger.info(f"Analyzing competitors for {request.your_brand}")

        client = DataForSEOClient()
        tracker = CompetitorTracker(client)

        results = await tracker.analyze_competitors(
            your_brand=request.your_brand,
            competitor_brands=request.competitor_brands,
            platforms=request.platforms,
            keywords=request.keywords,
            location=request.location
        )

        return {
            "success": True,
            "data": results,
            "summary": {
                "your_brand": request.your_brand,
                "competitors_analyzed": len(request.competitor_brands),
                "platforms_analyzed": len(request.platforms),
                "keywords_tracked": len(request.keywords),
                "overall_score": results["overall_positioning"].get("your_score", 0),
                "opportunities_found": len(results.get("opportunities", [])),
                "gaps_identified": len(results.get("competitive_gaps", []))
            }
        }

    except Exception as e:
        logger.error(f"Competitor analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platforms")
async def get_supported_platforms():
    """Get list of supported platforms for competitive analysis"""
    return {
        "success": True,
        "platforms": [
            {
                "id": "youtube",
                "name": "YouTube",
                "metrics": ["Video count", "Subscriber count", "Keyword coverage"]
            },
            {
                "id": "tiktok",
                "name": "TikTok",
                "metrics": ["Follower count", "Video count", "Trending content"]
            },
            {
                "id": "amazon",
                "name": "Amazon",
                "metrics": ["Product count", "Rating", "Review count"]
            },
            {
                "id": "google",
                "name": "Google Search",
                "metrics": ["Rankings", "SERP features", "Content gaps"]
            },
            {
                "id": "reddit",
                "name": "Reddit",
                "metrics": ["Mentions", "Sentiment", "Community engagement"]
            }
        ]
    }
