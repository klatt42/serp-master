"""
Platform Intelligence API Routes
Endpoints for multi-platform keyword discovery and intent matching
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from app.services.platform_intelligence.platform_orchestrator import PlatformOrchestrator
from app.services.intent_matcher import IntentMatcher
from app.services.dataforseo_client import DataForSEOClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/platform", tags=["Platform Intelligence"])


# Request Models
class PlatformAnalysisRequest(BaseModel):
    """Request model for platform analysis"""
    keywords: List[str] = Field(..., min_items=1, max_items=20)
    platforms: List[str] = Field(
        default=["youtube", "tiktok", "amazon", "reddit"],
        description="Platforms to analyze"
    )
    location: str = Field(default="United States", description="Geographic location")


class IntentAnalysisRequest(BaseModel):
    """Request model for intent analysis"""
    keywords: List[str] = Field(..., min_items=1, max_items=50)


class MultiPlatformStrategyRequest(BaseModel):
    """Request model for comprehensive multi-platform strategy"""
    niche_keywords: List[str] = Field(..., min_items=1, max_items=10)
    target_platforms: List[str] = Field(
        default=["youtube", "tiktok", "amazon", "reddit", "google", "blog"]
    )
    location: str = Field(default="United States")


# Routes
@router.post("/analyze")
async def analyze_platforms(request: PlatformAnalysisRequest):
    """
    Analyze keywords across multiple platforms

    Returns platform-specific opportunities, trending topics,
    and cross-platform content ideas
    """
    try:
        logger.info(f"Platform analysis requested for {len(request.keywords)} keywords")

        client = DataForSEOClient()
        orchestrator = PlatformOrchestrator(client)

        results = await orchestrator.analyze_all_platforms(
            seed_keywords=request.keywords,
            platforms=request.platforms,
            location=request.location
        )

        return {
            "success": True,
            "data": results,
            "summary": {
                "platforms_analyzed": len(request.platforms),
                "keywords_analyzed": len(request.keywords),
                "cross_platform_opportunities": len(
                    results.get("cross_platform_opportunities", [])
                )
            }
        }

    except Exception as e:
        logger.error(f"Platform analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intent")
async def analyze_intent(request: IntentAnalysisRequest):
    """
    Classify keywords by user intent

    Returns intent classifications, platform recommendations,
    and content strategy suggestions
    """
    try:
        logger.info(f"Intent analysis requested for {len(request.keywords)} keywords")

        matcher = IntentMatcher()
        results = matcher.batch_classify(request.keywords)

        return {
            "success": True,
            "data": results,
            "summary": {
                "total_keywords": results["insights"]["total_keywords"],
                "intent_distribution": results["insights"]["intent_distribution"],
                "top_platform": results["insights"]["top_platforms"][0][0]
                if results["insights"]["top_platforms"] else None
            }
        }

    except Exception as e:
        logger.error(f"Intent analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategy")
async def generate_multi_platform_strategy(request: MultiPlatformStrategyRequest):
    """
    Generate comprehensive multi-platform content strategy

    Combines platform analysis + intent matching to create
    a unified content strategy across all platforms
    """
    try:
        logger.info(f"Multi-platform strategy requested for: {request.niche_keywords}")

        client = DataForSEOClient()
        orchestrator = PlatformOrchestrator(client)
        matcher = IntentMatcher()

        # Step 1: Platform analysis
        platform_results = await orchestrator.analyze_all_platforms(
            seed_keywords=request.niche_keywords,
            platforms=request.target_platforms,
            location=request.location
        )

        # Step 2: Extract all discovered keywords
        all_keywords = []
        for platform, data in platform_results.get("platforms", {}).items():
            if platform == "youtube":
                all_keywords.extend([kw["keyword"] for kw in data.get("keywords", [])])
            elif platform == "tiktok":
                all_keywords.extend([idea["keyword"] for idea in data.get("content_ideas", [])])
            elif platform == "amazon":
                all_keywords.extend([kw["keyword"] for kw in data.get("product_keywords", [])])
            elif platform == "reddit":
                all_keywords.extend([topic["keyword"] for topic in data.get("discussion_topics", [])])

        # Remove duplicates
        all_keywords = list(set(all_keywords))[:100]  # Limit to top 100

        # Step 3: Intent analysis
        intent_results = matcher.batch_classify(all_keywords) if all_keywords else {
            "insights": {"intent_distribution": {}, "total_keywords": 0}
        }

        # Step 4: Generate unified strategy
        strategy = _create_unified_strategy(
            platform_results,
            intent_results,
            request.target_platforms
        )

        return {
            "success": True,
            "data": {
                "platform_analysis": platform_results,
                "intent_analysis": intent_results,
                "unified_strategy": strategy
            },
            "summary": {
                "platforms_covered": len(request.target_platforms),
                "content_opportunities": len(all_keywords),
                "cross_platform_ideas": len(
                    platform_results.get("cross_platform_opportunities", [])
                ),
                "recommended_focus": strategy.get("priority_platform")
            }
        }

    except Exception as e:
        logger.error(f"Strategy generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _create_unified_strategy(
    platform_results: dict,
    intent_results: dict,
    target_platforms: List[str]
) -> dict:
    """Create unified content strategy from platform and intent analysis"""

    # Analyze platform priorities
    platform_scores = {}
    for platform in target_platforms:
        platform_data = platform_results.get("platforms", {}).get(platform, {})

        # Count opportunities per platform
        if platform == "youtube":
            opportunity_count = len(platform_data.get("keywords", []))
        elif platform == "tiktok":
            opportunity_count = len(platform_data.get("content_ideas", []))
        elif platform == "amazon":
            opportunity_count = len(platform_data.get("product_keywords", []))
        elif platform == "reddit":
            opportunity_count = len(platform_data.get("discussion_topics", []))
        else:
            opportunity_count = 0

        platform_scores[platform] = opportunity_count

    # Determine priority platform
    priority_platform = max(platform_scores, key=platform_scores.get) if platform_scores else None

    # Get intent distribution
    intent_dist = intent_results.get("insights", {}).get("intent_distribution", {})
    dominant_intent = max(intent_dist, key=intent_dist.get) if intent_dist else None

    # Create strategy
    strategy = {
        "priority_platform": priority_platform,
        "platform_breakdown": platform_scores,
        "dominant_intent": dominant_intent,
        "intent_distribution": intent_dist,
        "content_calendar_recommendations": {
            "discovery_content": f"{intent_dist.get('discovery', 0)}% of content",
            "research_content": f"{intent_dist.get('research', 0)}% of content",
            "decision_content": f"{intent_dist.get('decision', 0)}% of content",
            "validation_content": f"{intent_dist.get('validation', 0)}% of content"
        },
        "immediate_actions": [
            f"Start with {priority_platform} - highest opportunity platform",
            f"Focus on {dominant_intent} intent keywords first",
            "Create platform-specific variations of top cross-platform keywords",
            "Build content funnel: Discovery → Research → Decision"
        ],
        "cross_platform_workflow": [
            {
                "step": 1,
                "action": "Create discovery content for TikTok/Instagram",
                "goal": "Awareness and initial engagement"
            },
            {
                "step": 2,
                "action": "Develop research content for YouTube/Blog",
                "goal": "Education and trust-building"
            },
            {
                "step": 3,
                "action": "Build decision content for Amazon/Google",
                "goal": "Conversion and sales"
            },
            {
                "step": 4,
                "action": "Foster validation content on Reddit/Reviews",
                "goal": "Social proof and community"
            }
        ]
    }

    return strategy


@router.get("/platforms")
async def get_supported_platforms():
    """Get list of supported platforms"""
    return {
        "success": True,
        "platforms": [
            {
                "id": "youtube",
                "name": "YouTube",
                "intent": "Research",
                "content_type": "Long-form video"
            },
            {
                "id": "tiktok",
                "name": "TikTok",
                "intent": "Discovery",
                "content_type": "Short-form video"
            },
            {
                "id": "amazon",
                "name": "Amazon",
                "intent": "Decision",
                "content_type": "Product listings"
            },
            {
                "id": "reddit",
                "name": "Reddit",
                "intent": "Validation",
                "content_type": "Discussions"
            },
            {
                "id": "google",
                "name": "Google Search",
                "intent": "Research/Decision",
                "content_type": "SEO content"
            },
            {
                "id": "blog",
                "name": "Blog/Website",
                "intent": "Research",
                "content_type": "Articles"
            }
        ]
    }
