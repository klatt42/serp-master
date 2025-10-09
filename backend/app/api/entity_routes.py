"""
Entity Optimization API Routes
Week 13: Entity Optimization Engine
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Optional, Dict
import logging

from app.models.entity_models import (
    # Description models
    BusinessDescriptionRequest,
    BusinessDescriptionResponse,
    # Schema models
    SchemaGenerationRequest,
    SchemaGenerationResponse,
    # Relationship models
    RelationshipAnalysisRequest,
    RelationshipAnalysisResponse,
    # About page models
    AboutPageOptimizationRequest,
    AboutPageOptimizationResponse,
    # NAP models
    NAPValidationRequest,
    NAPValidationResponse,
    # Full optimization models
    EntityOptimizationRequest,
    EntityOptimizationResponse
)

from app.services.entity.description_generator import BusinessDescriptionGenerator
from app.services.entity.schema_generator import SchemaGenerator
from app.services.entity.relationship_analyzer import RelationshipAnalyzer
from app.services.entity.about_optimizer import AboutPageOptimizer
from app.services.entity.nap_validator import NAPValidator
from app.services.entity.entity_optimizer import EntityOptimizer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/entity", tags=["Entity Optimization"])


# ==================== Business Description Endpoints ====================

@router.post("/descriptions/generate", response_model=BusinessDescriptionResponse)
async def generate_business_descriptions(
    request: BusinessDescriptionRequest
):
    """
    Generate AI-powered business descriptions optimized for entity recognition

    **Features:**
    - 5 unique variations (150-200 characters)
    - SEO score, local relevance, entity clarity
    - GPT-4 powered with template fallback
    - Keyword optimization
    - Location optimization

    **Returns:**
    - Multiple scored variations
    - Analysis and recommendations
    """
    try:
        generator = BusinessDescriptionGenerator()
        result = await generator.generate_descriptions(request)
        return result
    except Exception as e:
        logger.error(f"Error generating descriptions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Schema Markup Endpoints ====================

@router.post("/schema/generate", response_model=SchemaGenerationResponse)
async def generate_schema_markup(
    request: SchemaGenerationRequest,
    site_data: Optional[Dict] = Body(None)
):
    """
    Generate copy-paste ready Schema.org JSON-LD markup

    **Supported Schema Types:**
    - Organization
    - LocalBusiness (+ 30+ specific types)
    - Service
    - Product
    - FAQPage
    - BreadcrumbList

    **Features:**
    - Auto-detect business type
    - Validation against Schema.org specs
    - Rich snippet eligibility check
    - Implementation instructions

    **Returns:**
    - Copy-paste ready JSON-LD
    - HTML snippet
    - Validation results
    - Implementation guide
    """
    try:
        generator = SchemaGenerator()
        result = await generator.generate_schemas(request, site_data)
        return result
    except Exception as e:
        logger.error(f"Error generating schema: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/templates")
async def get_schema_templates():
    """
    Get list of available schema templates

    **Returns:**
    - Available schema types
    - Template descriptions
    - Use cases
    """
    return {
        "templates": [
            {
                "type": "Organization",
                "description": "Basic organization information",
                "use_case": "Homepage, all pages",
                "required_fields": ["name", "url"]
            },
            {
                "type": "LocalBusiness",
                "description": "Local business with address and hours",
                "use_case": "Homepage, contact page",
                "required_fields": ["name", "address", "telephone"]
            },
            {
                "type": "Service",
                "description": "Service offerings",
                "use_case": "Service pages",
                "required_fields": ["name", "provider", "serviceType"]
            },
            {
                "type": "Product",
                "description": "Product listings",
                "use_case": "Product pages",
                "required_fields": ["name", "offers"]
            },
            {
                "type": "FAQPage",
                "description": "Frequently asked questions",
                "use_case": "FAQ pages",
                "required_fields": ["mainEntity"]
            },
            {
                "type": "BreadcrumbList",
                "description": "Page breadcrumb navigation",
                "use_case": "All pages with breadcrumbs",
                "required_fields": ["itemListElement"]
            }
        ]
    }


# ==================== Entity Relationship Endpoints ====================

@router.post("/relationships/analyze", response_model=RelationshipAnalysisResponse)
async def analyze_entity_relationships(
    request: RelationshipAnalysisRequest,
    site_data: Optional[Dict] = Body(None)
):
    """
    Analyze and score entity relationships (certifications, partnerships, awards)

    **Detects:**
    - Certifications and licenses
    - Industry associations
    - Partnerships
    - Awards and recognition
    - Media mentions
    - Educational affiliations

    **Features:**
    - Authority scoring (0-10)
    - Relevance scoring (0-10)
    - Trust signal strength
    - Schema markup opportunities
    - Missing opportunity detection

    **Returns:**
    - Scored relationships
    - Recommendations
    - Authority summary
    """
    try:
        analyzer = RelationshipAnalyzer()
        result = await analyzer.analyze_relationships(request, site_data)
        return result
    except Exception as e:
        logger.error(f"Error analyzing relationships: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== About Page Endpoints ====================

@router.post("/about-page/optimize", response_model=AboutPageOptimizationResponse)
async def optimize_about_page(
    request: AboutPageOptimizationRequest,
    site_data: Optional[Dict] = Body(None)
):
    """
    Analyze and optimize About page for entity recognition

    **Analyzes:**
    - Word count and content depth
    - Entity mentions
    - Trust signals (credentials, experience, team)
    - Team member information
    - Achievements and awards
    - Contact information completeness
    - Visual content

    **Features:**
    - Quality scoring (0-100)
    - Missing element detection
    - Content suggestions with templates
    - Schema opportunities
    - Prioritized recommendations

    **Returns:**
    - Current metrics
    - Missing elements
    - Content suggestions
    - Recommendations
    """
    try:
        optimizer = AboutPageOptimizer()
        result = await optimizer.optimize_about_page(request, site_data)
        return result
    except Exception as e:
        logger.error(f"Error optimizing about page: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== NAP Validation Endpoints ====================

@router.post("/nap/validate", response_model=NAPValidationResponse)
async def validate_nap_consistency(
    request: NAPValidationRequest,
    site_data: Optional[Dict] = Body(None)
):
    """
    Validate Name, Address, Phone (NAP) consistency across web presence

    **Checks:**
    - Homepage, footer, contact page
    - Schema markup
    - Meta tags
    - Multiple page sources

    **Detects:**
    - Spelling inconsistencies
    - Format inconsistencies
    - Outdated information
    - Missing NAP data

    **Features:**
    - Consistency scoring (0-100)
    - Inconsistency detection with severity
    - Standardized NAP recommendation
    - Citation opportunities
    - Format suggestions

    **Returns:**
    - All NAP data found
    - Detected inconsistencies
    - Consistency score
    - Standardized NAP
    - Recommendations
    - Citation opportunities
    """
    try:
        validator = NAPValidator()
        result = await validator.validate_nap(request, site_data)
        return result
    except Exception as e:
        logger.error(f"Error validating NAP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Full Entity Optimization Endpoint ====================

@router.post("/optimize", response_model=EntityOptimizationResponse)
async def optimize_entity(
    request: EntityOptimizationRequest,
    site_data: Optional[Dict] = Body(None)
):
    """
    **COMPREHENSIVE ENTITY OPTIMIZATION**

    Run all entity optimization features in one request

    **Includes:**
    - ✅ Business description generation (5 variations)
    - ✅ Schema markup generation (6+ types)
    - ✅ Entity relationship analysis
    - ✅ About page optimization
    - ✅ NAP consistency validation

    **Features:**
    - Overall entity optimization score
    - Individual component scores
    - Quick wins (easy high-impact actions)
    - Priority actions (sorted by importance)
    - Comprehensive recommendations

    **Request Options:**
    - `include_description` (default: true)
    - `include_schema` (default: true)
    - `include_relationships` (default: true)
    - `include_about_page` (default: true)
    - `include_nap` (default: true)

    **Returns:**
    - Complete entity optimization analysis
    - All component results
    - Unified scoring
    - Action plan
    """
    try:
        optimizer = EntityOptimizer()
        result = await optimizer.optimize_entity(request, site_data)
        return result
    except Exception as e:
        logger.error(f"Error in entity optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Health Check ====================

@router.get("/health")
async def entity_health():
    """
    Health check for entity optimization services

    **Returns:**
    - Service status
    - Available features
    """
    return {
        "status": "healthy",
        "service": "Entity Optimization Engine",
        "version": "1.0.0",
        "features": {
            "description_generation": "active",
            "schema_generation": "active",
            "relationship_analysis": "active",
            "about_page_optimization": "active",
            "nap_validation": "active",
            "full_optimization": "active"
        }
    }


# ==================== Stats Endpoint ====================

@router.get("/stats")
async def get_entity_stats():
    """
    Get entity optimization statistics

    **Returns:**
    - Total optimizations run
    - Average scores
    - Most common issues
    """
    # In production, these would come from database
    return {
        "total_optimizations": 0,
        "average_scores": {
            "overall": 0,
            "description": 0,
            "schema": 0,
            "relationships": 0,
            "about_page": 0,
            "nap_consistency": 0
        },
        "common_issues": [
            "Missing schema markup",
            "Incomplete About page",
            "NAP inconsistencies",
            "Few authority relationships"
        ]
    }
