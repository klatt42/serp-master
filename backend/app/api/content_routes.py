"""
Content Automation API Routes
Endpoints for templates and calendar generation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging

from app.services.content_automation.template_generator import TemplateGenerator
from app.services.content_automation.calendar_builder import CalendarBuilder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/content", tags=["Content Automation"])


# Request Models
class TemplateRequest(BaseModel):
    """Request model for template generation"""
    platform: str = Field(..., description="Content platform")
    keyword: str = Field(..., description="Main keyword/topic")
    intent: str = Field(default="research", description="User intent")
    content_type: Optional[str] = Field(None, description="Specific content type")


class BatchTemplateRequest(BaseModel):
    """Request model for batch template generation"""
    content_plan: List[dict] = Field(..., min_items=1, max_items=50)


class CalendarRequest(BaseModel):
    """Request model for calendar generation"""
    content_items: List[dict] = Field(..., min_items=1, description="Content to schedule")
    start_date: str = Field(..., description="Calendar start date (YYYY-MM-DD)")
    duration_weeks: int = Field(default=12, ge=1, le=52, description="Calendar duration")
    frequency: str = Field(default="weekly", description="Publishing frequency")


# Routes
@router.post("/template")
async def generate_template(request: TemplateRequest):
    """
    Generate platform-specific content template

    Returns complete template with structure, suggestions, and metadata
    """
    try:
        logger.info(f"Generating template for {request.platform} - {request.keyword}")

        generator = TemplateGenerator()

        template = generator.generate_content_template(
            platform=request.platform,
            keyword=request.keyword,
            intent=request.intent,
            content_type=request.content_type
        )

        return {
            "success": True,
            "data": template,
            "summary": {
                "platform": request.platform,
                "keyword": request.keyword,
                "estimated_time": template["metadata"]["estimated_creation_time"]
            }
        }

    except Exception as e:
        logger.error(f"Template generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/template/batch")
async def generate_batch_templates(request: BatchTemplateRequest):
    """Generate multiple templates at once"""
    try:
        logger.info(f"Generating {len(request.content_plan)} templates")

        generator = TemplateGenerator()
        templates = generator.batch_generate_templates(request.content_plan)

        return {
            "success": True,
            "data": templates,
            "summary": {
                "total_templates": len(templates),
                "by_platform": {}
            }
        }

    except Exception as e:
        logger.error(f"Batch template generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calendar")
async def generate_calendar(request: CalendarRequest):
    """
    Generate automated content calendar

    Returns complete publishing schedule with optimal times
    """
    try:
        logger.info(f"Generating {request.duration_weeks} week calendar")

        # Parse start date
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        builder = CalendarBuilder()

        calendar = builder.generate_calendar(
            content_items=request.content_items,
            start_date=start_date,
            duration_weeks=request.duration_weeks,
            frequency=request.frequency
        )

        return {
            "success": True,
            "data": calendar,
            "summary": {
                "total_items": calendar["summary"]["total_items"],
                "duration_weeks": request.duration_weeks,
                "platforms": list(calendar["summary"]["by_platform"].keys())
            }
        }

    except Exception as e:
        logger.error(f"Calendar generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calendar/export")
async def export_calendar(calendar: dict):
    """Export calendar to Google Calendar CSV format"""
    try:
        builder = CalendarBuilder()
        export_data = builder.export_to_google_calendar(calendar)

        return {
            "success": True,
            "data": export_data
        }

    except Exception as e:
        logger.error(f"Calendar export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platforms")
async def get_supported_platforms():
    """Get list of supported content platforms"""
    return {
        "success": True,
        "platforms": [
            {"id": "youtube", "name": "YouTube", "type": "Video", "avg_time": "4-8 hours"},
            {"id": "tiktok", "name": "TikTok", "type": "Short Video", "avg_time": "30-60 minutes"},
            {"id": "blog", "name": "Blog/Website", "type": "Article", "avg_time": "3-5 hours"},
            {"id": "instagram", "name": "Instagram", "type": "Image Post", "avg_time": "1-2 hours"},
            {"id": "reddit", "name": "Reddit", "type": "Discussion", "avg_time": "30-45 minutes"}
        ]
    }
