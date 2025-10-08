"""
Cluster Data Models
Pydantic models for keyword clustering
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ClusterTheme(BaseModel):
    """Semantic theme of a keyword cluster"""
    theme_type: str = Field(..., description="Type of content theme")
    key_terms: List[str] = Field(default_factory=list, description="Most important terms")
    description: str = Field(..., description="Human-readable description")


class KeywordCluster(BaseModel):
    """Group of semantically related keywords"""
    cluster_id: int = Field(..., description="Cluster identifier")
    cluster_name: str = Field(..., description="Descriptive cluster name")
    theme: ClusterTheme = Field(..., description="Semantic theme")
    keywords: List[str] = Field(..., description="Keywords in this cluster")
    total_keywords: int = Field(..., description="Count of keywords")
    total_search_volume: int = Field(..., description="Combined monthly searches")
    avg_search_volume: int = Field(..., description="Average monthly searches")
    avg_difficulty: float = Field(..., description="Average keyword difficulty")
    avg_cpc: float = Field(..., description="Average cost per click")
    primary_intent: str = Field(..., description="Dominant search intent")
    common_serp_features: List[str] = Field(default_factory=list, description="Common SERP features")


class ClusterAnalysis(BaseModel):
    """Complete cluster analysis for a niche"""
    seed_keyword: str
    total_clusters: int
    clusters: List[KeywordCluster]
    unclustered_keywords: int
    analysis_summary: dict
