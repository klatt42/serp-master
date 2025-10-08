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


# Week 4: Competitor Comparison Models

class CompetitorComparisonRequest(BaseModel):
    """Request model for competitor comparison analysis"""
    user_url: str = Field(..., description="Your website URL")
    competitor_urls: List[str] = Field(..., min_items=1, max_items=3, description="Competitor URLs (1-3)")
    max_pages: int = Field(default=50, ge=1, le=100, description="Max pages to crawl per site")


class CompetitorComparisonStatus(str, Enum):
    """Comparison analysis status"""
    CRAWLING = "crawling"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


class CompetitorComparisonStartResponse(BaseModel):
    """Response when starting competitor comparison"""
    comparison_id: str = Field(..., description="Unique comparison task ID")
    status: CompetitorComparisonStatus
    sites_to_analyze: int = Field(..., description="Total number of sites")
    estimated_time_seconds: int = Field(..., description="Estimated completion time")


class CompetitorComparisonStatusResponse(BaseModel):
    """Status of a running comparison"""
    comparison_id: str
    status: CompetitorComparisonStatus
    progress: int = Field(ge=0, le=100)
    sites_completed: int
    sites_total: int
    message: Optional[str] = None


class SiteComparisonData(BaseModel):
    """Individual site data in comparison"""
    url: str
    total_score: int
    rank: int
    scores: Dict[str, Any]


class CompetitiveGap(BaseModel):
    """A gap where competitor is stronger"""
    dimension: str
    issue: str
    user_score: float
    competitor_score: float
    competitor_url: str
    gap: float
    category: str
    priority: str


class CompetitiveAction(BaseModel):
    """Strategic action recommendation"""
    action: str
    description: str
    dimension: str
    impact: float
    effort: str
    beats: List[str]
    current_rank: int
    potential_rank: int
    priority: str
    related_competitor: str


class CompetitorQuickWin(BaseModel):
    """Quick win against competitors"""
    fix: str
    description: str
    beats: List[str]
    impact: float
    effort: str
    dimension: str
    rank_improvement: int


class CompetitorComparisonResults(BaseModel):
    """Complete competitor comparison results"""
    comparison_id: str
    user_site: SiteComparisonData
    competitors: List[SiteComparisonData]
    comparison: Dict[str, Any]
    gaps: List[CompetitiveGap]
    competitive_strategy: List[CompetitiveAction]
    quick_wins: List[CompetitorQuickWin]
    analysis_date: str
    sites_analyzed: int
