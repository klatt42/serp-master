"""
Opportunity Models
Pydantic models for keyword opportunity scoring and discovery
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class OpportunityLevel(str, Enum):
    """Opportunity quality classification"""
    EXCELLENT = "excellent"  # 80-100 score
    GOOD = "good"           # 60-79 score
    MODERATE = "moderate"    # 40-59 score
    LOW = "low"             # <40 score


class KeywordOpportunity(BaseModel):
    """Scored keyword opportunity"""
    keyword: str
    search_volume: int
    keyword_difficulty: int
    cpc: float
    competition: float

    # Opportunity scoring components
    volume_score: float = Field(..., description="0-100 based on search volume")
    difficulty_score: float = Field(..., description="0-100 inverse of difficulty")
    cpc_score: float = Field(..., description="0-100 based on monetization potential")
    competition_score: float = Field(..., description="0-100 inverse of competition")

    # Composite scores
    opportunity_score: float = Field(..., description="Weighted average 0-100")
    roi_potential: float = Field(..., description="Volume * CPC / Difficulty")

    opportunity_level: OpportunityLevel

    # Action recommendations
    recommended_content_type: str = Field(..., description="Blog, video, landing page, etc.")
    estimated_traffic: int = Field(..., description="Potential monthly visitors")
    effort_level: str = Field(..., description="Low, Medium, High")

    class Config:
        use_enum_values = True


class OpportunityFilters(BaseModel):
    """Filters for opportunity discovery"""
    min_volume: int = Field(100, description="Minimum monthly searches")
    max_difficulty: int = Field(60, description="Maximum keyword difficulty")
    min_cpc: Optional[float] = Field(None, description="Minimum cost per click")
    max_cpc: Optional[float] = Field(None, description="Maximum cost per click")
    intents: List[str] = Field(default_factory=list, description="Filter by search intent")


class NicheDiscoveryRequest(BaseModel):
    """Request for niche discovery"""
    seed_keyword: str = Field(..., description="Starting keyword for discovery")
    filters: Optional[OpportunityFilters] = None
    limit: int = Field(50, description="Max opportunities to return")
    include_trends: bool = Field(False, description="Include monthly trend data")


class NicheDiscoveryResponse(BaseModel):
    """Response with discovered opportunities"""
    seed_keyword: str
    total_keywords_analyzed: int
    opportunities_found: int
    opportunities: List[KeywordOpportunity]
    avg_opportunity_score: float
    best_opportunity: Optional[KeywordOpportunity]
    summary_stats: dict
