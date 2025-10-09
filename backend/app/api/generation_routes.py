"""
API routes for AI Content Generation & Publishing
Week 12: Content generation, brand voice, SEO, publishing, attribution, predictions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.ai_generation.content_generator import ContentGenerator, GenerationMode
from app.services.ai_generation.brand_voice_engine import BrandVoiceEngine
from app.services.ai_generation.seo_auto_optimizer import SEOAutoOptimizer, OptimizationLevel, SchemaType
from app.services.ai_generation.multi_platform_publisher import MultiPlatformPublisher, PublishingPlatform
from app.services.ai_generation.revenue_attribution import RevenueAttributionTracker, AttributionModel
from app.services.ai_generation.predictive_analytics import PredictiveAnalytics

router = APIRouter(prefix="/api/generation", tags=["generation"])

# Initialize services
content_generator = ContentGenerator()
voice_engine = BrandVoiceEngine()
seo_optimizer = SEOAutoOptimizer()
publisher = MultiPlatformPublisher()
attribution_tracker = RevenueAttributionTracker()
predictive_engine = PredictiveAnalytics()


# ==================== Request/Response Models ====================

# Content Generation Models
class GenerateOutlineRequest(BaseModel):
    topic: str
    keywords: List[str]
    target_length: int = Field(default=2000, ge=500, le=10000)


class GenerateArticleRequest(BaseModel):
    outline: Dict
    tone: str = "professional"
    voice_profile: Optional[Dict] = None


class GenerateFromBriefRequest(BaseModel):
    brief: str
    keywords: List[str]
    length: int = Field(default=1000, ge=300, le=10000)
    tone: str = "professional"


# Brand Voice Models
class CreateVoiceProfileRequest(BaseModel):
    profile_name: str
    example_content: List[str] = Field(min_items=3)
    metadata: Optional[Dict] = None


class AnalyzeVoiceRequest(BaseModel):
    profile_name: str
    content: str


# SEO Optimization Models
class OptimizeContentRequest(BaseModel):
    content: str
    target_keywords: List[str]
    title: Optional[str] = None
    optimization_level: str = OptimizationLevel.BALANCED.value


class GenerateSchemaRequest(BaseModel):
    title: str
    description: str
    content: str
    schema_type: str = SchemaType.ARTICLE.value


# Publishing Models
class ConfigurePlatformRequest(BaseModel):
    platform: str
    credentials: Dict[str, str]


class PublishContentRequest(BaseModel):
    content: Dict
    platforms: List[str]
    schedule_time: Optional[datetime] = None
    tags: Optional[List[str]] = None


# Revenue Attribution Models
class TrackTouchpointRequest(BaseModel):
    user_id: str
    content_id: str
    session_id: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict] = None


class TrackConversionRequest(BaseModel):
    user_id: str
    conversion_type: str
    revenue: float
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict] = None


class GetAttributionRequest(BaseModel):
    content_id: str
    attribution_model: str = AttributionModel.LINEAR.value
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# Predictive Analytics Models
class PredictPerformanceRequest(BaseModel):
    content: Dict
    target_keywords: List[str]
    historical_context: Optional[Dict] = None


class CompareVersionsRequest(BaseModel):
    version_a: Dict
    version_b: Dict
    keywords: List[str]


# ==================== Content Generation Endpoints ====================

@router.post("/outline")
async def generate_outline(request: GenerateOutlineRequest):
    """Generate content outline from topic and keywords"""
    try:
        outline = await content_generator.generate_outline(
            request.topic,
            request.keywords,
            request.target_length
        )
        return {"success": True, "data": outline}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/article")
async def generate_article(request: GenerateArticleRequest):
    """Generate complete article from outline"""
    try:
        article = await content_generator.generate_article(
            request.outline,
            request.tone,
            request.voice_profile
        )
        return {"success": True, "data": article}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/from-brief")
async def generate_from_brief(request: GenerateFromBriefRequest):
    """Generate article directly from brief"""
    try:
        article = await content_generator.generate_from_brief(
            request.brief,
            request.keywords,
            request.length,
            request.tone
        )
        return {"success": True, "data": article}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/regenerate-section")
async def regenerate_section(
    section_heading: str,
    section_purpose: str,
    target_length: int = 300,
    tone: str = "professional"
):
    """Regenerate a specific section"""
    try:
        section = await content_generator.regenerate_section(
            section_heading,
            section_purpose,
            target_length,
            tone
        )
        return {"success": True, "data": section}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Brand Voice Endpoints ====================

@router.post("/voice/create")
async def create_voice_profile(request: CreateVoiceProfileRequest):
    """Create brand voice profile from examples"""
    try:
        profile = await voice_engine.create_voice_profile(
            request.profile_name,
            request.example_content,
            request.metadata
        )
        return {"success": True, "data": profile}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/analyze")
async def analyze_voice_consistency(request: AnalyzeVoiceRequest):
    """Analyze content against voice profile"""
    try:
        analysis = await voice_engine.analyze_voice_consistency(
            request.profile_name,
            request.content
        )
        return {"success": True, "data": analysis}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/suggest-improvements")
async def suggest_voice_improvements(request: AnalyzeVoiceRequest):
    """Get voice improvement suggestions"""
    try:
        suggestions = await voice_engine.suggest_voice_improvements(
            request.profile_name,
            request.content
        )
        return {"success": True, "data": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice/profiles")
async def list_voice_profiles():
    """List all voice profiles"""
    try:
        profiles = voice_engine.list_profiles()
        return {"success": True, "data": profiles}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice/profiles/{profile_name}")
async def get_voice_profile(profile_name: str):
    """Get specific voice profile"""
    try:
        profile = voice_engine.get_profile(profile_name)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return {"success": True, "data": profile}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SEO Optimization Endpoints ====================

@router.post("/seo/optimize")
async def optimize_content(request: OptimizeContentRequest):
    """Perform comprehensive SEO optimization"""
    try:
        result = await seo_optimizer.optimize_content(
            request.content,
            request.target_keywords,
            request.title,
            request.optimization_level
        )
        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seo/schema")
async def generate_schema_markup(request: GenerateSchemaRequest):
    """Generate Schema.org markup"""
    try:
        schema = seo_optimizer._generate_schema_markup(
            request.title,
            request.description,
            request.content,
            SchemaType(request.schema_type)
        )
        return {"success": True, "data": schema}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seo/featured-snippet")
async def optimize_for_featured_snippet(question: str, content: str):
    """Optimize content for featured snippets"""
    try:
        result = await seo_optimizer.optimize_for_featured_snippet(
            content,
            question
        )
        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Publishing Endpoints ====================

@router.post("/publish/configure")
async def configure_platform(request: ConfigurePlatformRequest):
    """Configure publishing platform credentials"""
    try:
        result = await publisher.configure_platform(
            request.platform,
            request.credentials
        )
        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish")
async def publish_content(request: PublishContentRequest):
    """Publish content to multiple platforms"""
    try:
        result = await publisher.publish_content(
            request.content,
            request.platforms,
            request.schedule_time,
            request.tags
        )
        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/publish/status/{publish_id}")
async def get_publish_status(publish_id: str):
    """Get status of publish job"""
    try:
        status = publisher.get_publish_status(publish_id)
        return {"success": True, "data": status}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish/process-queue")
async def process_publish_queue():
    """Process scheduled publishing queue"""
    try:
        result = await publisher.process_queue()
        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish/retry/{publish_id}/{platform}")
async def retry_failed_publish(publish_id: str, platform: str):
    """Retry a failed publish"""
    try:
        result = await publisher.retry_failed_publish(publish_id, platform)
        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/publish/stats")
async def get_platform_stats():
    """Get publishing statistics by platform"""
    try:
        stats = publisher.get_platform_stats()
        return {"success": True, "data": stats}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/publish/platforms")
async def list_configured_platforms():
    """List all configured platforms"""
    try:
        platforms = publisher.list_configured_platforms()
        return {"success": True, "data": platforms}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Revenue Attribution Endpoints ====================

@router.post("/attribution/touchpoint")
async def track_touchpoint(request: TrackTouchpointRequest):
    """Track content touchpoint in user journey"""
    try:
        touchpoint = await attribution_tracker.track_touchpoint(
            request.user_id,
            request.content_id,
            request.session_id,
            request.timestamp,
            request.metadata
        )
        return {"success": True, "data": touchpoint}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/attribution/conversion")
async def track_conversion(request: TrackConversionRequest):
    """Track conversion and attribute to content"""
    try:
        conversion = await attribution_tracker.track_conversion(
            request.user_id,
            request.conversion_type,
            request.revenue,
            request.timestamp,
            request.metadata
        )
        return {"success": True, "data": conversion}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/attribution/content")
async def get_content_attribution(request: GetAttributionRequest):
    """Get attribution data for specific content"""
    try:
        attribution = await attribution_tracker.get_content_attribution(
            request.content_id,
            request.attribution_model,
            request.start_date,
            request.end_date
        )
        return {"success": True, "data": attribution}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attribution/top-content")
async def get_top_revenue_content(
    limit: int = 10,
    attribution_model: str = AttributionModel.LINEAR.value
):
    """Get top revenue-generating content"""
    try:
        top_content = await attribution_tracker.get_top_revenue_content(
            limit,
            attribution_model
        )
        return {"success": True, "data": top_content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attribution/roi/{content_id}")
async def calculate_roi(
    content_id: str,
    production_cost: float,
    attribution_model: str = AttributionModel.LINEAR.value
):
    """Calculate ROI for content"""
    try:
        roi = await attribution_tracker.calculate_roi(
            content_id,
            production_cost,
            attribution_model
        )
        return {"success": True, "data": roi}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attribution/paths")
async def analyze_conversion_paths(min_touchpoints: int = 2, limit: int = 20):
    """Analyze common conversion paths"""
    try:
        paths = await attribution_tracker.analyze_conversion_paths(
            min_touchpoints,
            limit
        )
        return {"success": True, "data": paths}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attribution/clv/{user_id}")
async def get_customer_lifetime_value(user_id: str):
    """Calculate customer lifetime value"""
    try:
        clv = await attribution_tracker.get_customer_lifetime_value(user_id)
        return {"success": True, "data": clv}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attribution/summary")
async def get_attribution_summary():
    """Get overall attribution statistics"""
    try:
        summary = attribution_tracker.get_attribution_summary()
        return {"success": True, "data": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Predictive Analytics Endpoints ====================

@router.post("/predict/performance")
async def predict_performance(request: PredictPerformanceRequest):
    """Predict content performance before publishing"""
    try:
        predictions = await predictive_engine.predict_performance(
            request.content,
            request.target_keywords,
            request.historical_context
        )
        return {"success": True, "data": predictions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/compare")
async def compare_content_versions(request: CompareVersionsRequest):
    """Compare predictions for two content versions"""
    try:
        comparison = await predictive_engine.compare_content_versions(
            request.version_a,
            request.version_b,
            request.keywords
        )
        return {"success": True, "data": comparison}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/train")
async def train_prediction_model(historical_data: List[Dict]):
    """Train predictive model on historical data"""
    try:
        result = predictive_engine.train_model(historical_data)
        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Combined Workflow Endpoints ====================

@router.post("/workflow/full-generation")
async def full_content_generation_workflow(
    topic: str,
    keywords: List[str],
    target_length: int = 2000,
    tone: str = "professional",
    voice_profile_name: Optional[str] = None,
    optimize_seo: bool = True,
    predict_performance: bool = True
):
    """
    Complete content generation workflow:
    1. Generate outline
    2. Generate article
    3. Check brand voice (if profile provided)
    4. Optimize for SEO
    5. Predict performance
    """
    try:
        workflow_result = {
            "topic": topic,
            "started_at": datetime.now().isoformat()
        }

        # Step 1: Generate outline
        outline = await content_generator.generate_outline(
            topic,
            keywords,
            target_length
        )
        workflow_result["outline"] = outline

        # Step 2: Generate article
        article = await content_generator.generate_article(
            outline,
            tone
        )
        workflow_result["article"] = article

        # Step 3: Check brand voice
        if voice_profile_name:
            voice_analysis = await voice_engine.analyze_voice_consistency(
                voice_profile_name,
                article["sections"][0]["content"]  # Check first section
            )
            workflow_result["voice_analysis"] = voice_analysis

        # Step 4: Optimize for SEO
        if optimize_seo:
            # Combine all section content
            full_content = "\n\n".join([
                f"# {section['heading']}\n\n{section['content']}"
                for section in article["sections"]
            ])

            seo_result = await seo_optimizer.optimize_content(
                full_content,
                keywords,
                article["title"]
            )
            workflow_result["seo_optimization"] = seo_result

        # Step 5: Predict performance
        if predict_performance:
            content_for_prediction = {
                "title": article["title"],
                "body": full_content if optimize_seo else ""
            }

            predictions = await predictive_engine.predict_performance(
                content_for_prediction,
                keywords
            )
            workflow_result["performance_predictions"] = predictions

        workflow_result["completed_at"] = datetime.now().isoformat()

        return {"success": True, "data": workflow_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "content_generator": "active",
            "brand_voice_engine": "active",
            "seo_optimizer": "active",
            "publisher": "active",
            "attribution_tracker": "active",
            "predictive_analytics": "active"
        },
        "timestamp": datetime.now().isoformat()
    }
