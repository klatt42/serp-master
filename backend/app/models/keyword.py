"""
Keyword Data Models
Pydantic models for keyword discovery and analysis
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SearchIntent(str, Enum):
    """Search intent classification"""
    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"


class KeywordTrend(BaseModel):
    """Monthly search volume trend"""
    month: str
    volume: int


class KeywordData(BaseModel):
    """Individual keyword with all metrics"""
    keyword: str = Field(..., description="The keyword phrase")
    search_volume: int = Field(0, description="Monthly search volume")
    keyword_difficulty: Optional[int] = Field(None, description="SEO difficulty 0-100")
    cpc: Optional[float] = Field(None, description="Cost per click in USD")
    competition: Optional[float] = Field(None, description="Competition level 0-1")
    intent: Optional[SearchIntent] = Field(None, description="Search intent classification")
    serp_features: List[str] = Field(default_factory=list, description="SERP features present")
    trend: List[KeywordTrend] = Field(default_factory=list, description="12-month trend data")

    class Config:
        use_enum_values = True


class KeywordDB(KeywordData):
    """Database model with ID and timestamps"""
    id: int
    last_updated: datetime
    created_at: datetime


class KeywordBatch(BaseModel):
    """Batch of keywords from discovery"""
    seed_keyword: str
    keywords: List[KeywordData]
    total_found: int
    processed_at: datetime = Field(default_factory=datetime.now)
