"""
Local SEO API Routes
Handles citation audits, GBP optimization, local schema, and GEO scoring
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional

from app.models.local_models import (
    CitationAuditRequest,
    CitationAuditResponse,
    GBPOptimizationRequest,
    GBPOptimizationResponse,
    LocalSchemaRequest,
    LocalSchemaResponse,
    ReviewManagementRequest,
    ReviewManagementResponse,
    LocalCompetitorRequest,
    LocalCompetitorResponse,
    GEOAuditRequest,
    GEOAuditResponse
)

from app.services.local.citations.nap_auditor import NAPAuditor
from app.services.local.gbp.gbp_optimizer import GBPOptimizer
from app.services.local.schema.schema_generator import LocalSchemaGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/local", tags=["local-seo"])

# Initialize services
nap_auditor = NAPAuditor()
gbp_optimizer = GBPOptimizer()
schema_generator = LocalSchemaGenerator()


# ==================== Citation Audit Routes ====================

@router.post("/citations/audit", response_model=CitationAuditResponse)
async def audit_citations(request: CitationAuditRequest):
    """
    Perform comprehensive NAP consistency audit

    Analyzes business citations across 60+ directories and platforms.
    Returns:
    - Citations found
    - NAP inconsistencies
    - Consistency score (0-100)
    - Citation score (0-8 points for GEO scoring)
    - Actionable recommendations
    """
    try:
        logger.info(f"Starting citation audit for: {request.business_name}")

        # Perform citation audit
        audit_result = await nap_auditor.audit_citations(request)

        logger.info(
            f"Citation audit complete. Found {audit_result.total_citations} citations, "
            f"consistency score: {audit_result.consistency_score}/100, "
            f"citation score: {audit_result.citation_score}/8"
        )

        return audit_result

    except Exception as e:
        logger.error(f"Error in citation audit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Citation audit failed: {str(e)}")


@router.get("/citations/sources")
async def get_citation_sources(category: Optional[str] = None):
    """
    Get available citation sources

    Query parameters:
    - category: Filter by category (major, industry, local, government, aggregator, reviews)
    """
    try:
        # Return citation sources from the auditor
        if hasattr(nap_auditor, 'citation_data'):
            data = nap_auditor.citation_data

            if category:
                # Filter by category
                filtered = {}
                for key, sources in data.items():
                    if key == "metadata":
                        continue
                    if isinstance(sources, list):
                        category_sources = [s for s in sources if s.get('category') == category]
                        if category_sources:
                            filtered[key] = category_sources
                return filtered

            return data

        return {"message": "Citation sources not loaded"}

    except Exception as e:
        logger.error(f"Error retrieving citation sources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Google Business Profile Routes ====================

@router.post("/gbp/optimize", response_model=GBPOptimizationResponse)
async def optimize_gbp(request: GBPOptimizationRequest):
    """
    Analyze and optimize Google Business Profile

    Returns:
    - Profile completeness score
    - GBP score (0-12 points for GEO scoring)
    - Missing sections
    - Photo/post/review recommendations
    - Optimization action plan
    """
    try:
        logger.info(f"Starting GBP optimization for: {request.site_url}")

        # Perform GBP optimization
        optimization_result = await gbp_optimizer.optimize_profile(request)

        logger.info(
            f"GBP optimization complete. Completeness: {optimization_result.completeness_score}/100, "
            f"GBP score: {optimization_result.gbp_score}/12"
        )

        return optimization_result

    except Exception as e:
        logger.error(f"Error in GBP optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GBP optimization failed: {str(e)}")


# ==================== Local Schema Routes ====================

@router.post("/schema/generate", response_model=LocalSchemaResponse)
async def generate_local_schema(request: LocalSchemaRequest):
    """
    Generate local business schema markup

    Returns:
    - Detected business type
    - JSON-LD schema markup
    - HTML implementation snippet
    - Validation status
    - Rich feature eligibility
    """
    try:
        logger.info(f"Generating local schema for: {request.site_url}")

        # Generate schema markup
        schema_result = await schema_generator.generate_schema(request)

        logger.info(
            f"Schema generation complete. Type: {schema_result.detected_type.value}, "
            f"Status: {schema_result.validation_status}, "
            f"Rich features: {len(schema_result.rich_features_eligible)}"
        )

        return schema_result

    except Exception as e:
        logger.error(f"Error generating local schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Schema generation failed: {str(e)}")


# ==================== Review Management Routes ====================

@router.post("/reviews/analyze", response_model=ReviewManagementResponse)
async def analyze_reviews(request: ReviewManagementRequest):
    """
    Analyze reviews across multiple platforms

    Returns:
    - Aggregated reviews from Google, Yelp, Facebook, etc.
    - Review analysis (sentiment, keywords, trends)
    - Review score (0-5 points for GEO scoring)
    - Response suggestions
    - Reputation recommendations
    """
    try:
        logger.info(f"Starting review analysis for: {request.business_name}")

        # TODO: Implement review manager in Phase 5
        raise HTTPException(
            status_code=501,
            detail="Review management not yet implemented. Complete Phase 5 to enable."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Local Competitor Routes ====================

@router.post("/competitors/analyze", response_model=LocalCompetitorResponse)
async def analyze_competitors(request: LocalCompetitorRequest):
    """
    Analyze local competitors

    Returns:
    - Nearby competitors
    - GBP comparison metrics
    - Citation gap analysis
    - Keyword opportunities
    - Strategic recommendations
    """
    try:
        logger.info(f"Starting competitor analysis for: {request.business_name}")

        # TODO: Implement competitor analyzer in Phase 6
        raise HTTPException(
            status_code=501,
            detail="Competitor analysis not yet implemented. Complete Phase 6 to enable."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing competitors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Complete GEO Audit Routes ====================

@router.post("/geo/audit", response_model=GEOAuditResponse)
async def complete_geo_audit(request: GEOAuditRequest):
    """
    Perform complete 25-point GEO audit

    Combines all local SEO components:
    - Citation audit (8 points)
    - GBP optimization (12 points)
    - Local schema (2 points)
    - Review analysis (5 points)
    - Competitor analysis (optional)

    Returns complete GEO score breakdown and prioritized action plan
    """
    try:
        logger.info(f"Starting complete GEO audit for: {request.business_name}")

        # TODO: Implement complete GEO audit in Phase 8
        raise HTTPException(
            status_code=501,
            detail="Complete GEO audit not yet implemented. Complete Phase 8 to enable."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in GEO audit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Health Check ====================

@router.get("/health")
async def local_seo_health():
    """Check local SEO services health"""
    return {
        "status": "operational",
        "services": {
            "nap_auditor": "ready",
            "gbp_optimizer": "ready",
            "schema_generator": "ready",
            "review_manager": "pending_phase_5",
            "competitor_analyzer": "pending_phase_6",
            "geo_scorer": "pending_phase_8"
        },
        "phase": "4_complete",
        "next_phase": "phase_5_review_management"
    }
