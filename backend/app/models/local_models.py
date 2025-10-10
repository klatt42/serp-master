"""
Local SEO Models
Pydantic models for local SEO and GEO optimization features
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== Citation Models ====================

class CitationSource(BaseModel):
    """Single citation source"""
    name: str
    url: Optional[str] = None
    category: str  # "major", "industry", "local", "government"
    importance: int = Field(ge=1, le=10)  # 1-10 importance score
    business_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    hours: Optional[str] = None


class NAPInconsistency(BaseModel):
    """Detected NAP inconsistency"""
    field: str  # "name", "address", "phone"
    source1: str
    source2: str
    value1: str
    value2: str
    similarity: float  # 0.0-1.0
    severity: str  # "low", "medium", "high", "critical"
    suggestion: str


class CitationAuditRequest(BaseModel):
    """Request for citation audit"""
    site_url: str
    business_name: str
    address: str
    phone: str
    search_radius_miles: int = 25


class CitationAuditResponse(BaseModel):
    """Response with citation audit results"""
    citations_found: List[CitationSource]
    total_citations: int
    major_platform_coverage: int  # Out of 10 major platforms
    inconsistencies: List[NAPInconsistency]
    consistency_score: int = Field(ge=0, le=100)
    citation_score: int = Field(ge=0, le=8)  # Part of 25-point GEO score
    missing_major_platforms: List[str]
    recommendations: List[str]
    analyzed_at: datetime


# ==================== Google Business Profile Models ====================

class GBPPhoto(BaseModel):
    """GBP photo metadata"""
    category: str  # "cover", "logo", "interior", "exterior", "team", "product"
    url: str
    uploaded_date: Optional[datetime] = None
    view_count: Optional[int] = None


class GBPPost(BaseModel):
    """GBP post"""
    post_type: str  # "update", "offer", "event", "product"
    content: str
    created_date: datetime
    expires_date: Optional[datetime] = None
    cta_type: Optional[str] = None  # "call", "book", "order", "learn_more"
    engagement: Optional[int] = None


class GBPReview(BaseModel):
    """GBP review"""
    reviewer_name: str
    rating: int = Field(ge=1, le=5)
    text: Optional[str] = None
    created_date: datetime
    owner_response: Optional[str] = None
    response_date: Optional[datetime] = None


class GBPQandA(BaseModel):
    """GBP Q&A"""
    question: str
    answer: Optional[str] = None
    asked_date: datetime
    answered_date: Optional[datetime] = None


class GBPProfileData(BaseModel):
    """Google Business Profile data"""
    business_name: str
    address: str
    phone: str
    website: Optional[str] = None
    category: str
    additional_categories: List[str] = []
    description: Optional[str] = None

    # Status
    is_verified: bool = False
    is_claimed: bool = False
    is_published: bool = False

    # Hours
    hours: Optional[Dict[str, str]] = None
    special_hours: Optional[Dict[str, str]] = None

    # Media
    photos: List[GBPPhoto] = []
    videos: List[str] = []

    # Engagement
    posts: List[GBPPost] = []
    reviews: List[GBPReview] = []
    qanda: List[GBPQandA] = []

    # Attributes
    attributes: List[str] = []  # wheelchair_accessible, free_wifi, etc.
    payment_methods: List[str] = []

    # Metrics
    average_rating: Optional[float] = None
    review_count: int = 0
    photo_count: int = 0
    post_count_last_30_days: int = 0


class GBPOptimizationRequest(BaseModel):
    """Request for GBP optimization"""
    site_url: str
    location_id: Optional[str] = None  # Google Place ID
    business_data: Optional[Dict] = None


class GBPOptimizationResponse(BaseModel):
    """Response with GBP optimization analysis"""
    profile_data: GBPProfileData
    completeness_score: int = Field(ge=0, le=100)
    gbp_score: int = Field(ge=0, le=12)  # Part of 25-point GEO score

    # Completeness breakdown
    profile_complete: bool = False
    profile_complete_score: int = Field(ge=0, le=5)

    is_verified: bool = False
    verification_score: int = Field(ge=0, le=3)

    has_regular_posts: bool = False
    posting_score: int = Field(ge=0, le=2)

    has_updated_photos: bool = False
    photo_score: int = Field(ge=0, le=2)

    # Recommendations
    missing_sections: List[str]
    photo_recommendations: List[str]
    posting_recommendations: List[str]
    review_recommendations: List[str]
    qanda_recommendations: List[str]

    optimization_plan: List[Dict[str, Any]]
    analyzed_at: datetime


# ==================== Local Schema Models ====================

class LocalSchemaType(str, Enum):
    """Supported local schema types"""
    LOCAL_BUSINESS = "LocalBusiness"
    RESTAURANT = "Restaurant"
    STORE = "Store"
    PROFESSIONAL_SERVICE = "ProfessionalService"
    AUTO_DEALER = "AutoDealer"
    DENTIST = "Dentist"
    PHYSICIAN = "Physician"
    ATTORNEY = "Attorney"
    REAL_ESTATE_AGENT = "RealEstateAgent"


class LocalSchemaRequest(BaseModel):
    """Request for local schema generation"""
    site_url: str
    business_type: Optional[str] = None
    include_service_area: bool = True
    include_hours: bool = True


class LocalSchemaResponse(BaseModel):
    """Response with local schema markup"""
    detected_type: LocalSchemaType
    json_ld: Dict[str, Any]
    html_snippet: str
    validation_status: str  # "valid", "warning", "error"
    validation_messages: List[str]
    implementation_guide: str
    rich_features_eligible: List[str]  # ["rich_snippets", "knowledge_panel", etc.]
    generated_at: datetime


# ==================== Review Management Models ====================

class ReviewPlatform(str, Enum):
    """Supported review platforms"""
    GOOGLE = "Google"
    YELP = "Yelp"
    FACEBOOK = "Facebook"
    TRIPADVISOR = "TripAdvisor"
    BBB = "Better Business Bureau"
    ANGIES_LIST = "Angie's List"
    HOMEADVISOR = "HomeAdvisor"
    TRUSTPILOT = "Trustpilot"


class Review(BaseModel):
    """Single review from any platform"""
    platform: ReviewPlatform
    reviewer_name: str
    rating: int = Field(ge=1, le=5)
    text: Optional[str] = None
    date: datetime
    has_response: bool = False
    response_text: Optional[str] = None
    response_date: Optional[datetime] = None
    sentiment: Optional[str] = None  # "positive", "neutral", "negative"
    keywords: List[str] = []


class ReviewAnalysis(BaseModel):
    """Review analysis results"""
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[int, int]  # {5: 100, 4: 50, ...}
    reviews_last_30_days: int
    reviews_last_90_days: int
    response_rate: float
    average_response_time_hours: Optional[float] = None

    sentiment_breakdown: Dict[str, int]  # {"positive": 80, "neutral": 15, "negative": 5}
    common_keywords: List[tuple]  # [(keyword, count), ...]
    trending_topics: List[str]

    platform_breakdown: Dict[str, Dict[str, Any]]  # Per-platform stats


class ReviewManagementRequest(BaseModel):
    """Request for review management"""
    site_url: str
    business_name: str
    platforms: List[ReviewPlatform] = [ReviewPlatform.GOOGLE, ReviewPlatform.YELP]


class ReviewManagementResponse(BaseModel):
    """Response with review management data"""
    reviews: List[Review]
    analysis: ReviewAnalysis
    review_score: int = Field(ge=0, le=5)  # Part of 25-point GEO score

    # Recommendations
    response_suggestions: List[Dict[str, str]]  # {"review_id": "...", "suggestion": "..."}
    reputation_recommendations: List[str]
    solicitation_strategy: List[str]

    analyzed_at: datetime


# ==================== Local Competitor Analysis Models ====================

class LocalCompetitor(BaseModel):
    """Single local competitor"""
    name: str
    address: str
    phone: Optional[str] = None
    website: Optional[str] = None
    distance_miles: float

    # GBP metrics
    google_rating: Optional[float] = None
    google_review_count: Optional[int] = None
    gbp_optimization_score: Optional[int] = None

    # Citations
    citation_count: Optional[int] = None
    major_platform_coverage: Optional[int] = None

    # Rankings
    local_pack_position: Optional[int] = None
    organic_position: Optional[int] = None


class CompetitorComparison(BaseModel):
    """Comparison metrics"""
    metric: str
    your_value: Any
    competitor_average: Any
    top_competitor_value: Any
    your_rank: int
    gap_analysis: str


class LocalCompetitorRequest(BaseModel):
    """Request for local competitor analysis"""
    site_url: str
    business_name: str
    address: str
    radius_miles: int = 10
    target_keywords: List[str]


class LocalCompetitorResponse(BaseModel):
    """Response with local competitor analysis"""
    competitors: List[LocalCompetitor]
    comparisons: List[CompetitorComparison]

    # Strategic insights
    citation_gaps: List[str]
    gbp_optimization_gaps: List[str]
    keyword_opportunities: List[str]
    service_expansion_opportunities: List[str]

    recommendations: List[Dict[str, Any]]
    analyzed_at: datetime


# ==================== GEO Scoring Models ====================

class GEOScoreBreakdown(BaseModel):
    """Complete 25-point GEO score breakdown"""
    # Google Business Profile (12 points)
    gbp_total: int = Field(ge=0, le=12)
    gbp_profile_complete: int = Field(ge=0, le=5)
    gbp_verified: int = Field(ge=0, le=3)
    gbp_regular_posts: int = Field(ge=0, le=2)
    gbp_photos_updated: int = Field(ge=0, le=2)

    # Local Citations (8 points)
    citations_total: int = Field(ge=0, le=8)
    citations_nap_consistency: int = Field(ge=0, le=4)
    citations_count: int = Field(ge=0, le=4)

    # Local Content (5 points)
    local_content_total: int = Field(ge=0, le=5)
    local_content_location_pages: int = Field(ge=0, le=3)
    local_content_schema: int = Field(ge=0, le=2)

    # Overall
    total_score: int = Field(ge=0, le=25)
    percentage: int = Field(ge=0, le=100)


class GEOAuditRequest(BaseModel):
    """Request for complete GEO audit"""
    site_url: str
    business_name: str
    address: str
    phone: str
    include_citations: bool = True
    include_gbp: bool = True
    include_competitors: bool = False


class GEOAuditResponse(BaseModel):
    """Complete GEO audit response"""
    score: GEOScoreBreakdown

    # Component results
    citation_audit: Optional[CitationAuditResponse] = None
    gbp_optimization: Optional[GBPOptimizationResponse] = None
    local_schema: Optional[LocalSchemaResponse] = None
    review_analysis: Optional[ReviewManagementResponse] = None
    competitor_analysis: Optional[LocalCompetitorResponse] = None

    # Priority actions
    quick_wins: List[Dict[str, Any]]
    priority_actions: List[Dict[str, Any]]

    # Overall recommendations
    recommendations: List[str]
    analyzed_at: datetime


# ==================== Helper Models ====================

class LocationData(BaseModel):
    """Geographic location data"""
    street_address: str
    city: str
    state: str
    zip_code: str
    country: str = "US"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Service area
    service_radius_miles: Optional[int] = None
    service_cities: List[str] = []
    service_counties: List[str] = []


class BusinessHours(BaseModel):
    """Business operating hours"""
    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None

    # Special hours
    holidays: Optional[Dict[str, str]] = None
    special_events: Optional[Dict[str, str]] = None
