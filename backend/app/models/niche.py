"""
Niche Analysis Models
Pydantic models for market and niche analysis
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class MarketSize(str, Enum):
    """Market size classification"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"


class CompetitionLevel(str, Enum):
    """Competition level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ContentGap(BaseModel):
    """Identified content opportunity gap"""
    gap_type: str = Field(..., description="Type of content gap")
    description: str = Field(..., description="Gap description")
    keywords: List[str] = Field(..., description="Related keywords")
    estimated_impact: str = Field(..., description="Potential impact (low/medium/high)")
    priority: str = Field(..., description="Priority level")


class MarketOpportunity(BaseModel):
    """Specific market opportunity"""
    cluster_name: str
    cluster_theme: str
    opportunity_score: float
    opportunity_level: str
    total_search_volume: int
    avg_difficulty: float
    recommended_action: str


class NicheAnalysis(BaseModel):
    """Complete niche market analysis"""
    seed_keyword: str
    total_keywords: int
    total_search_volume: int
    market_size: MarketSize
    competition_level: CompetitionLevel
    avg_keyword_difficulty: float
    monetization_potential: float
    top_serp_features: List[str]
    content_gaps: List[ContentGap]
    recommended_strategy: str
    confidence_score: float
    opportunities: List[MarketOpportunity]
    cluster_count: int

    class Config:
        use_enum_values = True
