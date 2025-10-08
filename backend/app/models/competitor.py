"""
Competitor Analysis Data Models
Pydantic models for competitive intelligence
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Competitor(BaseModel):
    """Competitor domain with analysis"""
    domain: str = Field(..., description="Competitor domain name")
    appearances: int = Field(..., description="Number of SERP appearances")
    avg_position: float = Field(..., description="Average ranking position")
    keywords_ranked: List[str] = Field(..., description="Keywords they rank for")
    estimated_traffic: int = Field(..., description="Estimated monthly organic traffic")
    domain_authority: int = Field(default=0, description="Domain authority score")
    content_types: List[str] = Field(default_factory=list, description="Content types used")
    strengths: List[str] = Field(default_factory=list, description="Competitive strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Potential weaknesses")
    top_pages: Optional[List[Dict[str, Any]]] = Field(None, description="Top performing pages")


class CompetitorInsight(BaseModel):
    """Strategic insight about competitor"""
    competitor_domain: str = Field(..., description="Competitor domain")
    insight_type: str = Field(..., description="Type of insight")
    description: str = Field(..., description="Insight description")
    actionable_tip: str = Field(..., description="What you can do about it")
    priority: str = Field(..., description="Priority level (high/medium/low)")


class CompetitiveAnalysisRequest(BaseModel):
    """Request to analyze competitors"""
    keywords: List[str] = Field(..., description="Keywords to analyze")
    location: str = Field(default="United States", description="Geographic location")
    max_competitors: int = Field(default=10, description="Max competitors to analyze")
