"""
FastAPI Routes for SERP-Master API
Endpoints for website auditing and SEO analysis
"""

import os
import asyncio
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List
from datetime import datetime

from app.models import (
    AuditRequest,
    AuditStartResponse,
    AuditStatusResponse,
    AuditResults,
    AuditStatus,
    HealthResponse,
    ManualAuditRequest,
    QuickWinsResponse,
    CompetitorComparisonRequest,
    CompetitorComparisonStartResponse,
    CompetitorComparisonStatus,
    CompetitorComparisonStatusResponse,
    CompetitorComparisonResults
)
from app.services.site_crawler import SiteCrawler
from app.services.seo_scorer import SEOScorer
from app.services.issue_analyzer import IssueAnalyzer
from app.services.aeo_scorer import AEOScorer
from app.services.geo_scorer import GEOScorer
from app.services.mock_data import generate_mock_site
from app.services.competitor_analyzer import CompetitorAnalyzer
from app.services.supabase_client import SupabaseComparisonStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# In-memory storage for audit tasks (replace with database in production)
audit_tasks: Dict[str, Dict] = {}

# In-memory storage for competitor comparison tasks (Week 4)
comparison_tasks: Dict[str, Dict] = {}

# Supabase storage for comparisons (Week 4 Phase 4E)
supabase_store = SupabaseComparisonStore()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns API status and configuration
    """
    dataforseo_configured = bool(
        os.getenv("DATAFORSEO_LOGIN") and os.getenv("DATAFORSEO_PASSWORD")
    )

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        dataforseo_configured=dataforseo_configured
    )


@router.post("/api/audit/start", response_model=AuditStartResponse)
async def start_audit(request: AuditRequest, background_tasks: BackgroundTasks):
    """
    Start a new website audit

    This endpoint initiates a crawl and returns immediately with a task_id.
    The actual crawl runs in the background.

    Args:
        request: Audit request with URL and max_pages
        background_tasks: FastAPI background tasks

    Returns:
        Task ID and estimated completion time
    """
    try:
        # Generate task ID
        task_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(request)}"

        # Initialize task in storage
        audit_tasks[task_id] = {
            "task_id": task_id,
            "url": request.url,
            "max_pages": request.max_pages,
            "status": AuditStatus.CRAWLING,
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }

        # Start background task
        background_tasks.add_task(run_audit, task_id, request.url, request.max_pages)

        logger.info(f"Started audit task {task_id} for {request.url}")

        return AuditStartResponse(
            task_id=task_id,
            status=AuditStatus.CRAWLING,
            estimated_time_seconds=180
        )

    except Exception as e:
        logger.error(f"Failed to start audit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start audit: {str(e)}")


@router.get("/api/audit/status/{task_id}", response_model=AuditStatusResponse)
async def get_audit_status(task_id: str):
    """
    Get the status of an audit task

    Args:
        task_id: Task ID from start_audit

    Returns:
        Current status and progress
    """
    if task_id not in audit_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = audit_tasks[task_id]

    return AuditStatusResponse(
        task_id=task_id,
        status=task_data["status"],
        progress=task_data["progress"],
        message=task_data.get("error")
    )


@router.get("/api/audit/results/{task_id}")
async def get_audit_results(task_id: str):
    """
    Get complete audit results

    Args:
        task_id: Task ID from start_audit

    Returns:
        Complete audit results including scores and issues

    Raises:
        404: If task not found
        425: If task not complete yet
        500: If task failed
    """
    if task_id not in audit_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = audit_tasks[task_id]

    # Check status
    if task_data["status"] == AuditStatus.CRAWLING:
        raise HTTPException(
            status_code=425,
            detail="Audit still in progress. Check status endpoint for progress."
        )

    if task_data["status"] == AuditStatus.PROCESSING:
        raise HTTPException(
            status_code=425,
            detail="Audit processing results. Please wait."
        )

    if task_data["status"] == AuditStatus.FAILED:
        raise HTTPException(
            status_code=500,
            detail=f"Audit failed: {task_data.get('error', 'Unknown error')}"
        )

    # Return results
    if not task_data.get("result"):
        raise HTTPException(status_code=500, detail="No results available")

    return task_data["result"]


@router.post("/api/audit/manual")
async def manual_audit(request: ManualAuditRequest):
    """
    Run audit with manually provided HTML content (for testing/demos)

    This endpoint allows testing AEO scoring without waiting for DataForSEO.
    Useful for demos, testing, and when you have HTML but don't need a crawl.

    Args:
        request: Manual audit request with HTML and metadata

    Returns:
        Complete audit results with AEO scoring
    """
    try:
        logger.info(f"Running manual audit for {request.business_name}")

        # Create mock site data structure
        site_data = {
            "url": request.url or f"https://{request.business_name.lower().replace(' ', '')}.com",
            "html": request.html_content,
            "business_name": request.business_name,
            "pages": [
                {
                    "url": "/",
                    "title": f"{request.business_name} - Home",
                    "html": request.html_content,
                    "meta": {
                        "title": f"{request.business_name}",
                        "description": f"{request.business_name} website"
                    }
                }
            ],
            "metadata": {
                "pages_crawled": 1,
                "business_info": {
                    "name": request.business_name
                }
            }
        }

        # Calculate AEO scores
        aeo_scorer = AEOScorer()
        aeo_data = aeo_scorer.calculate_aeo_score(site_data)

        # Calculate GEO scores (stub)
        geo_scorer = GEOScorer()
        geo_data = geo_scorer.calculate_geo_score(site_data)

        # Calculate combined score (no traditional SEO for manual input)
        combined_score = aeo_scorer.calculate_combined_score(
            site_data,
            seo_score=0,  # Manual input doesn't include crawl-based SEO
            geo_score=geo_data.get("geo_score", 0)
        )

        # Get quick wins
        quick_wins = aeo_scorer.get_quick_wins(site_data)

        # Build result
        result = {
            "url": site_data["url"],
            "business_name": request.business_name,
            "timestamp": datetime.now().isoformat(),
            "score": combined_score,
            "aeo_score": aeo_data,
            "geo_score": geo_data,
            "quick_wins": quick_wins,
            "metadata": {
                "audit_type": "manual",
                "scoring_version": "2.0",
                "includes_aeo": True,
                "includes_geo": False,
                "includes_seo": False
            }
        }

        logger.info(f"Manual audit completed for {request.business_name}")
        return result

    except Exception as e:
        logger.error(f"Manual audit failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Manual audit failed: {str(e)}")


@router.get("/api/audit/quick-wins/{task_id}", response_model=QuickWinsResponse)
async def get_quick_wins(task_id: str):
    """
    Get quick win recommendations for a completed audit

    Args:
        task_id: Task ID from start_audit

    Returns:
        List of high-impact, low-effort recommendations
    """
    if task_id not in audit_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = audit_tasks[task_id]

    if task_data["status"] != AuditStatus.COMPLETE:
        raise HTTPException(status_code=425, detail="Audit not complete yet")

    result = task_data.get("result", {})
    quick_wins = result.get("quick_wins", [])

    return QuickWinsResponse(
        task_id=task_id,
        url=task_data["url"],
        quick_wins=quick_wins
    )


# ============================================================================
# Week 4: Competitor Comparison Endpoints
# ============================================================================

@router.post("/api/compare/start", response_model=CompetitorComparisonStartResponse)
async def start_competitor_comparison(
    request: CompetitorComparisonRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new competitor comparison analysis

    Compares your website against 1-3 competitors across all scoring dimensions.
    Returns immediately with a comparison_id while analysis runs in background.

    Args:
        request: Comparison request with user URL, competitor URLs, and max pages
        background_tasks: FastAPI background tasks

    Returns:
        Comparison ID and status information
    """
    try:
        # Validate request
        if len(request.competitor_urls) == 0:
            raise HTTPException(status_code=400, detail="At least 1 competitor URL required")

        if len(request.competitor_urls) > 3:
            raise HTTPException(status_code=400, detail="Maximum 3 competitor URLs allowed")

        if request.user_url in request.competitor_urls:
            raise HTTPException(status_code=400, detail="User URL cannot be in competitor list")

        # Generate comparison ID
        comparison_id = f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(request)}"

        # Calculate estimated time (50-70 seconds per site)
        sites_total = 1 + len(request.competitor_urls)
        estimated_time = sites_total * 60

        # Initialize task in storage
        comparison_tasks[comparison_id] = {
            "comparison_id": comparison_id,
            "user_url": request.user_url,
            "competitor_urls": request.competitor_urls,
            "max_pages": request.max_pages,
            "status": CompetitorComparisonStatus.CRAWLING,
            "progress": 0,
            "sites_completed": 0,
            "sites_total": sites_total,
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }

        # Start background task
        background_tasks.add_task(
            run_competitor_comparison,
            comparison_id,
            request.user_url,
            request.competitor_urls,
            request.max_pages
        )

        logger.info(f"Started comparison {comparison_id}: {request.user_url} vs {len(request.competitor_urls)} competitors")

        return CompetitorComparisonStartResponse(
            comparison_id=comparison_id,
            status=CompetitorComparisonStatus.CRAWLING,
            sites_to_analyze=sites_total,
            estimated_time_seconds=estimated_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start comparison: {str(e)}")


@router.get("/api/compare/status/{comparison_id}", response_model=CompetitorComparisonStatusResponse)
async def get_comparison_status(comparison_id: str):
    """
    Get the status of a competitor comparison

    Args:
        comparison_id: Comparison ID from start_competitor_comparison

    Returns:
        Current status, progress, and site completion info
    """
    if comparison_id not in comparison_tasks:
        raise HTTPException(status_code=404, detail="Comparison not found")

    task_data = comparison_tasks[comparison_id]

    return CompetitorComparisonStatusResponse(
        comparison_id=comparison_id,
        status=task_data["status"],
        progress=task_data["progress"],
        sites_completed=task_data["sites_completed"],
        sites_total=task_data["sites_total"],
        message=task_data.get("error")
    )


@router.get("/api/compare/results/{comparison_id}")
async def get_comparison_results(comparison_id: str):
    """
    Get complete competitor comparison results

    Args:
        comparison_id: Comparison ID from start_competitor_comparison

    Returns:
        Complete comparison results with gaps, strategy, and quick wins

    Raises:
        404: If comparison not found
        425: If comparison not complete yet
        500: If comparison failed
    """
    if comparison_id not in comparison_tasks:
        raise HTTPException(status_code=404, detail="Comparison not found")

    task_data = comparison_tasks[comparison_id]

    # Check status
    if task_data["status"] in [CompetitorComparisonStatus.CRAWLING, CompetitorComparisonStatus.ANALYZING]:
        raise HTTPException(
            status_code=425,
            detail=f"Comparison still {task_data['status']}. Check status endpoint for progress."
        )

    if task_data["status"] == CompetitorComparisonStatus.FAILED:
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {task_data.get('error', 'Unknown error')}"
        )

    # Return results
    if not task_data.get("result"):
        raise HTTPException(status_code=500, detail="No results available")

    return task_data["result"]


async def run_competitor_comparison(
    comparison_id: str,
    user_url: str,
    competitor_urls: List[str],
    max_pages: int
):
    """
    Background task to run competitor comparison analysis

    This function:
    1. Audits all sites in parallel (user + competitors)
    2. Compares scores and calculates rankings
    3. Identifies competitive gaps
    4. Generates strategic recommendations
    5. Identifies quick wins

    Args:
        comparison_id: Comparison task identifier
        user_url: User's website URL
        competitor_urls: List of competitor URLs
        max_pages: Max pages to crawl per site
    """
    try:
        logger.info(f"Running comparison {comparison_id}: {user_url} vs {len(competitor_urls)} competitors")

        # Update progress
        comparison_tasks[comparison_id]["progress"] = 5
        comparison_tasks[comparison_id]["status"] = CompetitorComparisonStatus.CRAWLING

        # Initialize analyzer
        analyzer = CompetitorAnalyzer()

        comparison_tasks[comparison_id]["progress"] = 10

        # Run full competitor analysis
        results = await analyzer.analyze_competitors(
            user_url=user_url,
            competitor_urls=competitor_urls,
            max_pages=max_pages
        )

        comparison_tasks[comparison_id]["progress"] = 90
        comparison_tasks[comparison_id]["status"] = CompetitorComparisonStatus.ANALYZING

        # Add comparison_id to results
        results["comparison_id"] = comparison_id

        # Store results in memory
        comparison_tasks[comparison_id]["result"] = results
        comparison_tasks[comparison_id]["status"] = CompetitorComparisonStatus.COMPLETE
        comparison_tasks[comparison_id]["progress"] = 100
        comparison_tasks[comparison_id]["sites_completed"] = 1 + len(competitor_urls)

        # Save to Supabase (non-blocking, best-effort)
        try:
            await supabase_store.save_comparison(
                comparison_id=comparison_id,
                user_url=user_url,
                competitor_urls=competitor_urls,
                max_pages=max_pages,
                status="complete",
                progress=100,
                results=results
            )
        except Exception as db_error:
            logger.warning(f"Failed to save comparison to Supabase: {db_error}")
            # Continue anyway - results are in memory

        logger.info(f"Comparison {comparison_id} completed successfully")

    except Exception as e:
        logger.error(f"Comparison {comparison_id} failed: {str(e)}")
        comparison_tasks[comparison_id]["status"] = CompetitorComparisonStatus.FAILED
        comparison_tasks[comparison_id]["error"] = str(e)
        comparison_tasks[comparison_id]["progress"] = 0


async def run_audit(task_id: str, url: str, max_pages: int):
    """
    Background task to run complete audit

    This function:
    1. Crawls the website
    2. Calculates SEO scores
    3. Analyzes issues
    4. Stores results

    Args:
        task_id: Task identifier
        url: Website URL to audit
        max_pages: Maximum pages to crawl
    """
    try:
        logger.info(f"Running audit {task_id} for {url}")

        # Update progress
        audit_tasks[task_id]["progress"] = 10
        audit_tasks[task_id]["status"] = AuditStatus.CRAWLING

        # Step 1: Crawl website
        crawler = SiteCrawler()
        crawl_data = await crawler.crawl_site(url, max_pages)

        audit_tasks[task_id]["progress"] = 60
        audit_tasks[task_id]["status"] = AuditStatus.PROCESSING

        # Step 2: Calculate SEO scores
        scorer = SEOScorer()
        score_data = scorer.calculate_total_seo_score(crawl_data)

        audit_tasks[task_id]["progress"] = 70

        # Step 3: Calculate AEO scores
        aeo_scorer = AEOScorer()
        aeo_data = aeo_scorer.calculate_aeo_score(crawl_data)

        audit_tasks[task_id]["progress"] = 75

        # Step 4: Calculate GEO scores (stub)
        geo_scorer = GEOScorer()
        geo_data = geo_scorer.calculate_geo_score(crawl_data)

        audit_tasks[task_id]["progress"] = 80

        # Step 5: Calculate combined score
        combined_score = aeo_scorer.calculate_combined_score(
            crawl_data,
            seo_score=score_data.get("total_score", 0),
            geo_score=geo_data.get("geo_score", 0)
        )

        audit_tasks[task_id]["progress"] = 85

        # Step 6: Analyze issues
        analyzer = IssueAnalyzer()
        issue_data = analyzer.analyze_issues(score_data)

        audit_tasks[task_id]["progress"] = 90

        # Step 7: Get quick wins
        quick_wins = aeo_scorer.get_quick_wins(crawl_data)

        audit_tasks[task_id]["progress"] = 95

        # Step 8: Build final result
        result = {
            "task_id": task_id,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "score": combined_score,
            "seo_score": score_data,
            "aeo_score": aeo_data,
            "geo_score": geo_data,
            "issues": issue_data,
            "quick_wins": quick_wins,
            "metadata": {
                **crawl_data.get("metadata", {}),
                "max_pages_requested": max_pages,
                "scoring_version": "2.0",
                "includes_aeo": True,
                "includes_geo": False  # Phase 2
            }
        }

        # Store result
        audit_tasks[task_id]["result"] = result
        audit_tasks[task_id]["status"] = AuditStatus.COMPLETE
        audit_tasks[task_id]["progress"] = 100

        logger.info(f"Audit {task_id} completed successfully")

    except Exception as e:
        logger.error(f"Audit {task_id} failed: {str(e)}")
        audit_tasks[task_id]["status"] = AuditStatus.FAILED
        audit_tasks[task_id]["error"] = str(e)
        audit_tasks[task_id]["progress"] = 0
