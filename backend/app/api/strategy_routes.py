"""
Content Strategy API Routes
Week 8: AI-powered content strategy generation
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
import logging
import os

from app.models.content_strategy import (
    StrategyGenerationRequest,
    ContentStrategy
)
from app.models.competitor import CompetitiveAnalysisRequest, Competitor
from app.models.keyword import KeywordData
from app.models.cluster import KeywordCluster
from app.services.content_strategist import ContentStrategist
from app.services.competitive_analyzer import CompetitiveAnalyzer
from app.services.calendar_generator import CalendarGenerator
from app.services.keyword_discoverer import KeywordDiscoverer
from app.services.keyword_clusterer import KeywordClusterer
from app.services.niche_analyzer import NicheAnalyzer

router = APIRouter(prefix="/api/strategy", tags=["content-strategy"])
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=ContentStrategy)
async def generate_content_strategy(request: StrategyGenerationRequest):
    """
    Generate AI-powered content strategy from niche keyword

    This endpoint:
    1. Discovers keywords for the niche
    2. Clusters keywords into themes
    3. Analyzes market dynamics
    4. Generates content strategy with AI (GPT-4)
    """
    logger.info(f"Generating content strategy for: {request.seed_keyword}")

    try:
        # Step 1: Discover keywords
        async with KeywordDiscoverer() as discoverer:
            keyword_batch = await discoverer.discover_keywords(
                seed_keyword=request.seed_keyword,
                limit=100
            )

        if not keyword_batch.keywords:
            raise HTTPException(status_code=404, detail="No keywords found for this niche")

        # Step 2: Cluster keywords
        clusterer = KeywordClusterer(min_cluster_size=3, max_clusters=10)
        clusters = clusterer.cluster_keywords(keyword_batch.keywords)

        # Step 3: Analyze niche
        analyzer = NicheAnalyzer()
        niche_analysis = analyzer.analyze_niche(
            seed_keyword=request.seed_keyword,
            keywords=keyword_batch.keywords,
            clusters=clusters
        )

        # Step 4: Generate content strategy with AI
        strategist = ContentStrategist()

        # Convert keywords to dict format for strategist
        opportunities = [
            {
                'keyword': kw.keyword,
                'search_volume': kw.search_volume,
                'keyword_difficulty': kw.keyword_difficulty or 50,
                'cpc': kw.cpc or 0,
                'opportunity_score': 75  # Simplified
            }
            for kw in keyword_batch.keywords[:20]
        ]

        # Convert niche analysis to dict
        niche_dict = {
            'market_size': niche_analysis.market_size,
            'competition_level': niche_analysis.competition_level,
            'avg_keyword_difficulty': niche_analysis.avg_keyword_difficulty,
            'content_gaps': [
                {
                    'gap_type': gap.gap_type,
                    'description': gap.description,
                    'keywords': gap.keywords,
                    'priority': gap.priority
                }
                for gap in niche_analysis.content_gaps
            ]
        }

        strategy = await strategist.generate_strategy(
            seed_keyword=request.seed_keyword,
            clusters=clusters,
            opportunities=opportunities,
            niche_analysis=niche_dict,
            options={
                'timeline_weeks': request.timeline_weeks,
                'content_types': request.content_types,
                'max_pieces_per_week': request.max_pieces_per_week
            }
        )

        logger.info(f"Strategy generated: {strategy.total_pieces} pieces, {len(strategy.pillars)} pillars")
        return strategy

    except Exception as e:
        logger.error(f"Error generating strategy: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate strategy: {str(e)}")


@router.post("/competitors/analyze", response_model=List[Competitor])
async def analyze_competitors(request: CompetitiveAnalysisRequest):
    """
    Analyze competitors for given keywords

    Returns top competitors with strengths/weaknesses
    """
    logger.info(f"Analyzing competitors for {len(request.keywords)} keywords")

    try:
        analyzer = CompetitiveAnalyzer()

        # Create keyword data with SERP info
        keywords_with_serp = [
            {'keyword': kw, 'search_volume': 1000}  # Simplified
            for kw in request.keywords
        ]

        competitors = await analyzer.analyze_competitors(
            keywords_with_serp=keywords_with_serp,
            max_competitors=request.max_competitors
        )

        logger.info(f"Identified {len(competitors)} competitors")
        return competitors

    except Exception as e:
        logger.error(f"Error analyzing competitors: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze competitors: {str(e)}")


@router.post("/calendar/export-ics")
async def export_calendar_ics(strategy_id: str):
    """
    Export content calendar in ICS format

    For now, returns sample calendar
    """
    try:
        # In real implementation, fetch strategy from database
        # For now, return sample ICS
        from datetime import datetime, timedelta
        from app.models.content_strategy import ContentItem, ContentType, Priority, Difficulty, ContentStatus

        sample_items = [
            ContentItem(
                id=f"item_{i}",
                title=f"Sample Content {i}",
                pillar_name="Sample Pillar",
                content_type=ContentType.BLOG_POST,
                target_keyword=f"keyword {i}",
                supporting_keywords=[],
                priority=Priority.HIGH,
                estimated_difficulty=Difficulty.MEDIUM,
                estimated_hours=6,
                scheduled_date=datetime.now() + timedelta(weeks=i),
                optimization_tips=["Include keyword in title"],
                status=ContentStatus.PLANNED
            )
            for i in range(1, 6)
        ]

        ics_content = CalendarGenerator.generate_ics(sample_items)

        return {"format": "ics", "content": ics_content}

    except Exception as e:
        logger.error(f"Error generating ICS: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate calendar: {str(e)}")


@router.post("/calendar/export-csv")
async def export_calendar_csv(strategy_id: str):
    """
    Export content calendar in CSV format
    """
    try:
        # Sample implementation
        from datetime import datetime, timedelta
        from app.models.content_strategy import ContentItem, ContentType, Priority, Difficulty, ContentStatus

        sample_items = [
            ContentItem(
                id=f"item_{i}",
                title=f"Sample Content {i}",
                pillar_name="Sample Pillar",
                content_type=ContentType.BLOG_POST,
                target_keyword=f"keyword {i}",
                supporting_keywords=[],
                priority=Priority.HIGH,
                estimated_difficulty=Difficulty.MEDIUM,
                estimated_hours=6,
                scheduled_date=datetime.now() + timedelta(weeks=i),
                optimization_tips=["Include keyword in title"],
                status=ContentStatus.PLANNED
            )
            for i in range(1, 6)
        ]

        csv_content = CalendarGenerator.generate_csv(sample_items)

        return {"format": "csv", "content": csv_content}

    except Exception as e:
        logger.error(f"Error generating CSV: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate calendar: {str(e)}")


@router.get("/health")
async def strategy_health():
    """Health check for strategy service"""
    return {
        "status": "healthy",
        "service": "content-strategy",
        "openai_configured": bool(os.getenv('OPENAI_API_KEY'))
    }
