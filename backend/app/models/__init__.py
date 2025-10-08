"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class AuditRequest(BaseModel):
    """Request model for starting an audit"""
    url: str = Field(..., description="Website URL to audit")
    max_pages: int = Field(default=100, ge=1, le=500, description="Maximum pages to crawl")


class AuditStatus(str, Enum):
    """Audit status enum"""
    CRAWLING = "crawling"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class AuditStatusResponse(BaseModel):
    """Response model for audit status"""
    task_id: str
    status: AuditStatus
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    message: Optional[str] = None


class AuditStartResponse(BaseModel):
    """Response model for audit start"""
    task_id: str
    status: AuditStatus
    estimated_time_seconds: int = Field(default=180, description="Estimated completion time")


class ScoreDetail(BaseModel):
    """Score detail for a metric"""
    score: int
    max_score: int
    status: str
    details: Optional[Dict[str, Any]] = None


class SEOScoreBreakdown(BaseModel):
    """Complete SEO score breakdown"""
    total_score: int
    max_score: int
    percentage: float
    grade: str
    technical_seo: Dict[str, Any]
    onpage_seo: Dict[str, Any]
    structure_seo: Dict[str, Any]
    summary: Dict[str, Any]


class Issue(BaseModel):
    """Single SEO issue"""
    issue: str
    severity: str
    impact: int
    effort: str
    pages_affected: str
    current_value: str
    target_value: str
    recommendation: str
    quick_win: bool


class IssueAnalysis(BaseModel):
    """Complete issue analysis"""
    critical_issues: List[Issue]
    warnings: List[Issue]
    info: List[Issue]
    quick_wins: List[Issue]
    summary: Dict[str, Any]


class AuditResults(BaseModel):
    """Complete audit results"""
    task_id: str
    url: str
    timestamp: str
    score: SEOScoreBreakdown
    issues: IssueAnalysis
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    dataforseo_configured: bool


class ManualAuditRequest(BaseModel):
    """Request model for manual audit with provided HTML"""
    html_content: str = Field(..., description="HTML content to analyze")
    business_name: str = Field(..., description="Business name for entity analysis")
    url: Optional[str] = Field(None, description="Website URL (optional)")


class QuickWin(BaseModel):
    """Quick win recommendation"""
    title: str
    impact: str
    effort: str
    points: int
    description: str


class QuickWinsResponse(BaseModel):
    """Response model for quick wins endpoint"""
    task_id: str
    url: str
    quick_wins: List[QuickWin]
