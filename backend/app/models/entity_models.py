"""
Entity Optimization Models
Pydantic models for entity optimization features
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ==================== Business Description Models ====================

class BusinessDescriptionVariation(BaseModel):
    """Single business description variation"""
    description: str
    character_count: int
    seo_score: int = Field(ge=0, le=100)
    local_relevance_score: int = Field(ge=0, le=100)
    entity_clarity_score: int = Field(ge=0, le=100)
    readability_score: int = Field(ge=0, le=100)
    overall_score: int = Field(ge=0, le=100)
    keywords_included: List[str]
    location_mentioned: bool


class BusinessDescriptionRequest(BaseModel):
    """Request for business description generation"""
    site_url: str
    business_name: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    target_keywords: Optional[List[str]] = None
    existing_description: Optional[str] = None


class BusinessDescriptionResponse(BaseModel):
    """Response with generated business descriptions"""
    variations: List[BusinessDescriptionVariation]
    analysis: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime


# ==================== Schema Markup Models ====================

class SchemaMarkup(BaseModel):
    """Generated schema markup"""
    schema_type: str  # Organization, LocalBusiness, Service, etc.
    json_ld: Dict[str, Any]
    html_snippet: str
    validation_status: str  # valid, warning, error
    validation_messages: List[str]
    rich_snippet_eligible: bool
    implementation_instructions: str


class SchemaGenerationRequest(BaseModel):
    """Request for schema markup generation"""
    site_url: str
    business_type: Optional[str] = None
    generate_types: List[str] = Field(default_factory=lambda: ["Organization", "LocalBusiness"])


class SchemaGenerationResponse(BaseModel):
    """Response with generated schema markups"""
    schemas: List[SchemaMarkup]
    detected_business_type: str
    recommendations: List[str]
    generated_at: datetime


# ==================== Entity Relationship Models ====================

class EntityRelationship(BaseModel):
    """Single entity relationship"""
    relationship_type: str  # certification, partnership, association, etc.
    entity_name: str
    description: str
    authority_score: int = Field(ge=0, le=10)
    relevance_score: int = Field(ge=0, le=10)
    trust_signal_strength: str  # low, medium, high
    schema_opportunity: bool
    detected_from: str  # where we found this relationship


class RelationshipAnalysisRequest(BaseModel):
    """Request for relationship analysis"""
    site_url: str
    focus_areas: Optional[List[str]] = None  # certifications, partnerships, etc.


class RelationshipAnalysisResponse(BaseModel):
    """Response with relationship analysis"""
    relationships: List[EntityRelationship]
    missing_opportunities: List[str]
    recommendations: List[Dict[str, Any]]
    authority_summary: Dict[str, int]
    analyzed_at: datetime


# ==================== About Page Models ====================

class AboutPageMetrics(BaseModel):
    """About page quality metrics"""
    word_count: int
    entity_mentions: int
    trust_signals_count: int
    team_members_mentioned: int
    achievements_mentioned: int
    contact_info_complete: bool
    visual_content_count: int
    overall_quality_score: int = Field(ge=0, le=100)


class AboutPageOptimizationRequest(BaseModel):
    """Request for About page optimization"""
    site_url: str
    about_page_url: Optional[str] = None


class AboutPageOptimizationResponse(BaseModel):
    """Response with About page optimization"""
    current_metrics: AboutPageMetrics
    missing_elements: List[str]
    content_suggestions: List[Dict[str, str]]
    schema_opportunities: List[str]
    recommendations: List[Dict[str, Any]]
    analyzed_at: datetime


# ==================== NAP Validation Models ====================

class NAPData(BaseModel):
    """Name, Address, Phone data"""
    business_name: str
    address: str
    phone: str
    hours: Optional[str] = None
    source: str  # website, schema, etc.


class NAPInconsistency(BaseModel):
    """Detected NAP inconsistency"""
    field: str  # name, address, phone
    issue_type: str  # format, spelling, outdated
    sources: List[str]
    severity: str  # low, medium, high
    suggestion: str


class NAPValidationRequest(BaseModel):
    """Request for NAP validation"""
    site_url: str
    expected_nap: Optional[NAPData] = None


class NAPValidationResponse(BaseModel):
    """Response with NAP validation"""
    nap_data_found: List[NAPData]
    inconsistencies: List[NAPInconsistency]
    consistency_score: int = Field(ge=0, le=100)
    standardized_nap: NAPData
    recommendations: List[str]
    citation_opportunities: List[str]
    validated_at: datetime


# ==================== Entity Optimization Models ====================

class EntityOptimizationRequest(BaseModel):
    """Request for full entity optimization analysis"""
    site_url: str
    business_name: Optional[str] = None
    include_description: bool = True
    include_schema: bool = True
    include_relationships: bool = True
    include_about_page: bool = True
    include_nap: bool = True


class EntityOptimizationScore(BaseModel):
    """Entity optimization scoring"""
    overall_score: int = Field(ge=0, le=100)
    description_score: int = Field(ge=0, le=100)
    schema_score: int = Field(ge=0, le=100)
    relationship_score: int = Field(ge=0, le=100)
    about_page_score: int = Field(ge=0, le=100)
    nap_consistency_score: int = Field(ge=0, le=100)


class EntityOptimizationResponse(BaseModel):
    """Complete entity optimization response"""
    scores: EntityOptimizationScore
    business_descriptions: Optional[BusinessDescriptionResponse] = None
    schema_markups: Optional[SchemaGenerationResponse] = None
    relationships: Optional[RelationshipAnalysisResponse] = None
    about_page_analysis: Optional[AboutPageOptimizationResponse] = None
    nap_validation: Optional[NAPValidationResponse] = None
    quick_wins: List[Dict[str, Any]]
    priority_actions: List[Dict[str, Any]]
    analyzed_at: datetime


# ==================== Helper Models ====================

class EntityAnalysis(BaseModel):
    """General entity analysis data"""
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    industry: Optional[str] = None
    primary_location: Optional[str] = None
    service_areas: List[str] = Field(default_factory=list)
    primary_services: List[str] = Field(default_factory=list)
    unique_value_props: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    partnerships: List[str] = Field(default_factory=list)


class OptimizationRecommendation(BaseModel):
    """Single optimization recommendation"""
    category: str  # description, schema, relationships, about, nap
    priority: str  # high, medium, low
    title: str
    description: str
    implementation: str
    impact: str  # Expected impact on entity recognition
    effort: str  # low, medium, high
    estimated_time: str  # e.g., "5 minutes", "1 hour"
