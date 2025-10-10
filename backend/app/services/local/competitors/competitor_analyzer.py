"""
Local Competitor Analysis Service
Discovers and analyzes local competitors for SEO opportunities
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta

from app.models.local_models import (
    LocalCompetitorRequest,
    LocalCompetitorResponse,
    CompetitorProfile,
    CompetitorComparison,
    CompetitorGap
)

logger = logging.getLogger(__name__)


class LocalCompetitorAnalyzer:
    """Analyze local competitors and identify SEO gaps"""

    def __init__(self):
        """Initialize competitor analyzer"""
        pass

    async def analyze_competitors(
        self,
        request: LocalCompetitorRequest,
        site_data: Optional[Dict] = None
    ) -> LocalCompetitorResponse:
        """
        Analyze local competitors

        Args:
            request: Competitor analysis request
            site_data: Optional site data

        Returns:
            Competitor analysis with gaps and recommendations
        """
        try:
            logger.info(f"Starting competitor analysis for: {request.business_name}")

            # Discover competitors in the area
            competitors = self._discover_competitors(request)

            # Analyze your business metrics
            your_metrics = self._analyze_your_metrics(request, site_data)

            # Compare competitors
            comparison = self._compare_competitors(your_metrics, competitors)

            # Identify gaps
            citation_gaps = self._identify_citation_gaps(your_metrics, competitors)
            keyword_gaps = self._identify_keyword_gaps(request, competitors)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                comparison,
                citation_gaps,
                keyword_gaps
            )

            return LocalCompetitorResponse(
                your_metrics=your_metrics,
                competitors=competitors,
                comparison=comparison,
                citation_gaps=citation_gaps,
                keyword_gaps=keyword_gaps,
                recommendations=recommendations,
                analyzed_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error analyzing competitors: {str(e)}")
            raise

    def _discover_competitors(
        self,
        request: LocalCompetitorRequest
    ) -> List[CompetitorProfile]:
        """
        Discover competitors in the local area
        In production, this would use Google Places API, business directories, etc.
        """
        # Simulate competitor discovery
        competitors = [
            CompetitorProfile(
                name="Premier Local Services",
                website="https://premierlocalservices.com",
                address="456 Oak Ave, Same City, ST 12345",
                phone="(555) 234-5678",
                distance_miles=2.3,
                google_rating=4.5,
                google_reviews=127,
                yelp_rating=4.0,
                yelp_reviews=43,
                citation_count=42,
                estimated_monthly_traffic=3200,
                ranks_for_keywords=["local services", "professional services"],
                gbp_optimized=True,
                has_regular_posts=True,
                photo_count=87,
                business_hours_listed=True,
                response_rate=0.85
            ),
            CompetitorProfile(
                name="City Professional Group",
                website="https://cityprofessional.com",
                address="789 Main St, Same City, ST 12345",
                phone="(555) 345-6789",
                distance_miles=1.8,
                google_rating=4.2,
                google_reviews=89,
                yelp_rating=3.8,
                yelp_reviews=27,
                citation_count=35,
                estimated_monthly_traffic=2100,
                ranks_for_keywords=["professional services", "business consulting"],
                gbp_optimized=True,
                has_regular_posts=False,
                photo_count=52,
                business_hours_listed=True,
                response_rate=0.65
            ),
            CompetitorProfile(
                name="Quality Service Pros",
                website="https://qualityservicepros.com",
                address="321 Elm St, Same City, ST 12345",
                phone="(555) 456-7890",
                distance_miles=3.1,
                google_rating=4.7,
                google_reviews=201,
                yelp_rating=4.5,
                yelp_reviews=67,
                citation_count=58,
                estimated_monthly_traffic=5400,
                ranks_for_keywords=["quality services", "local professional", "best in city"],
                gbp_optimized=True,
                has_regular_posts=True,
                photo_count=134,
                business_hours_listed=True,
                response_rate=0.92
            )
        ]

        # Filter by radius
        competitors = [c for c in competitors if c.distance_miles <= request.radius_miles]

        return competitors[:request.max_competitors] if request.max_competitors else competitors

    def _analyze_your_metrics(
        self,
        request: LocalCompetitorRequest,
        site_data: Optional[Dict] = None
    ) -> CompetitorProfile:
        """Analyze your business metrics"""
        # In production, this would fetch real data
        return CompetitorProfile(
            name=request.business_name,
            website=request.site_url,
            address=request.address,
            phone=request.phone if hasattr(request, 'phone') else None,
            distance_miles=0.0,
            google_rating=4.3,
            google_reviews=45,
            yelp_rating=4.1,
            yelp_reviews=18,
            citation_count=28,
            estimated_monthly_traffic=1800,
            ranks_for_keywords=request.target_keywords if request.target_keywords else [],
            gbp_optimized=True,
            has_regular_posts=False,
            photo_count=34,
            business_hours_listed=True,
            response_rate=0.50
        )

    def _compare_competitors(
        self,
        your_metrics: CompetitorProfile,
        competitors: List[CompetitorProfile]
    ) -> CompetitorComparison:
        """Compare your business against competitors"""

        # Calculate averages
        avg_google_rating = sum(c.google_rating for c in competitors) / len(competitors) if competitors else 0
        avg_google_reviews = sum(c.google_reviews for c in competitors) / len(competitors) if competitors else 0
        avg_citation_count = sum(c.citation_count for c in competitors) / len(competitors) if competitors else 0
        avg_response_rate = sum(c.response_rate for c in competitors) / len(competitors) if competitors else 0

        # Find top competitor
        top_competitor = max(
            competitors,
            key=lambda c: (c.google_rating * c.google_reviews + c.citation_count),
            default=None
        )

        # Calculate your ranking
        all_businesses = [your_metrics] + competitors
        sorted_businesses = sorted(
            all_businesses,
            key=lambda c: (c.google_rating * c.google_reviews + c.citation_count),
            reverse=True
        )
        your_rank = sorted_businesses.index(your_metrics) + 1

        return CompetitorComparison(
            your_rank=your_rank,
            total_competitors=len(competitors),
            your_google_rating=your_metrics.google_rating,
            avg_google_rating=round(avg_google_rating, 2),
            your_google_reviews=your_metrics.google_reviews,
            avg_google_reviews=int(avg_google_reviews),
            your_citation_count=your_metrics.citation_count,
            avg_citation_count=int(avg_citation_count),
            your_response_rate=your_metrics.response_rate,
            avg_response_rate=round(avg_response_rate, 2),
            top_competitor=top_competitor.name if top_competitor else None,
            strengths=self._identify_strengths(your_metrics, avg_google_rating, avg_google_reviews, avg_citation_count),
            weaknesses=self._identify_weaknesses(your_metrics, avg_google_rating, avg_google_reviews, avg_citation_count)
        )

    def _identify_strengths(
        self,
        your_metrics: CompetitorProfile,
        avg_rating: float,
        avg_reviews: float,
        avg_citations: float
    ) -> List[str]:
        """Identify competitive strengths"""
        strengths = []

        if your_metrics.google_rating > avg_rating:
            strengths.append(f"Above-average Google rating ({your_metrics.google_rating} vs {avg_rating:.1f})")

        if your_metrics.google_reviews > avg_reviews:
            strengths.append(f"More Google reviews than average ({your_metrics.google_reviews} vs {int(avg_reviews)})")

        if your_metrics.citation_count > avg_citations:
            strengths.append(f"More citations than average ({your_metrics.citation_count} vs {int(avg_citations)})")

        if your_metrics.gbp_optimized:
            strengths.append("Google Business Profile is optimized")

        if your_metrics.response_rate > 0.7:
            strengths.append(f"High review response rate ({your_metrics.response_rate:.0%})")

        if not strengths:
            strengths.append("Opportunity to establish competitive advantages")

        return strengths

    def _identify_weaknesses(
        self,
        your_metrics: CompetitorProfile,
        avg_rating: float,
        avg_reviews: float,
        avg_citations: float
    ) -> List[str]:
        """Identify competitive weaknesses"""
        weaknesses = []

        if your_metrics.google_rating < avg_rating:
            weaknesses.append(f"Below-average Google rating ({your_metrics.google_rating} vs {avg_rating:.1f})")

        if your_metrics.google_reviews < avg_reviews:
            weaknesses.append(f"Fewer Google reviews than average ({your_metrics.google_reviews} vs {int(avg_reviews)})")

        if your_metrics.citation_count < avg_citations:
            weaknesses.append(f"Fewer citations than competitors ({your_metrics.citation_count} vs {int(avg_citations)})")

        if not your_metrics.has_regular_posts:
            weaknesses.append("Not posting regularly to Google Business Profile")

        if your_metrics.response_rate < 0.7:
            weaknesses.append(f"Low review response rate ({your_metrics.response_rate:.0%})")

        if your_metrics.photo_count < 50:
            weaknesses.append(f"Limited photos on GBP ({your_metrics.photo_count})")

        return weaknesses

    def _identify_citation_gaps(
        self,
        your_metrics: CompetitorProfile,
        competitors: List[CompetitorProfile]
    ) -> List[CompetitorGap]:
        """Identify citation gaps where competitors are listed but you aren't"""
        gaps = []

        # Simulate gap discovery
        # In production, this would cross-reference actual citation sources
        gap_sources = [
            ("Yelp Business", "review_platform", 9, "Competitors have strong presence"),
            ("Better Business Bureau", "major_directory", 8, "3 competitors listed"),
            ("Angie's List", "review_platform", 7, "2 competitors with high ratings"),
            ("Thumbtack", "industry_directory", 6, "Lead generation opportunity"),
            ("Houzz", "industry_directory", 5, "Industry-specific directory")
        ]

        for source_name, source_type, importance, note in gap_sources:
            gaps.append(CompetitorGap(
                gap_type="citation",
                source=source_name,
                importance=importance,
                competitors_using=[c.name for c in competitors[:2]],  # First 2 competitors
                opportunity=note
            ))

        return gaps[:5]  # Return top 5 gaps

    def _identify_keyword_gaps(
        self,
        request: LocalCompetitorRequest,
        competitors: List[CompetitorProfile]
    ) -> List[CompetitorGap]:
        """Identify keyword opportunities where competitors rank but you don't"""
        gaps = []

        # Aggregate all competitor keywords
        competitor_keywords = set()
        for competitor in competitors:
            competitor_keywords.update(competitor.ranks_for_keywords)

        # Your keywords
        your_keywords = set(request.target_keywords) if request.target_keywords else set()

        # Find gap keywords
        gap_keywords = competitor_keywords - your_keywords

        # Simulate keyword gap data
        # In production, this would use rank tracking and search volume data
        for keyword in list(gap_keywords)[:5]:
            gaps.append(CompetitorGap(
                gap_type="keyword",
                source=keyword,
                importance=7,  # Would be based on search volume
                competitors_using=[c.name for c in competitors if keyword in c.ranks_for_keywords],
                opportunity=f"Multiple competitors ranking for this term"
            ))

        return gaps

    def _generate_recommendations(
        self,
        comparison: CompetitorComparison,
        citation_gaps: List[CompetitorGap],
        keyword_gaps: List[CompetitorGap]
    ) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []

        # Ranking recommendations
        if comparison.your_rank > 3:
            recommendations.append(
                f"⚠️ You rank #{comparison.your_rank} out of {comparison.total_competitors + 1} local competitors. "
                "Focus on differentiation and improving key metrics."
            )
        elif comparison.your_rank == 1:
            recommendations.append(
                f"✅ You're ranked #1 in your local market! Maintain your competitive edge."
            )

        # Review recommendations
        if comparison.your_google_reviews < comparison.avg_google_reviews:
            gap = comparison.avg_google_reviews - comparison.your_google_reviews
            recommendations.append(
                f"Build {int(gap)} more Google reviews to match market average ({comparison.avg_google_reviews})"
            )

        # Citation recommendations
        if comparison.your_citation_count < comparison.avg_citation_count:
            gap = comparison.avg_citation_count - comparison.your_citation_count
            recommendations.append(
                f"Add {int(gap)} more citations to reach market average ({comparison.avg_citation_count})"
            )

        # Top citation gaps
        if citation_gaps:
            top_gap = citation_gaps[0]
            recommendations.append(
                f"Priority citation: Add your business to {top_gap.source} (importance: {top_gap.importance}/10)"
            )

        # Keyword opportunities
        if keyword_gaps:
            top_keywords = [gap.source for gap in keyword_gaps[:3]]
            recommendations.append(
                f"Target these competitor keywords: {', '.join(top_keywords)}"
            )

        # Response rate
        if comparison.your_response_rate < comparison.avg_response_rate:
            recommendations.append(
                f"Improve review response rate to {comparison.avg_response_rate:.0%} (currently {comparison.your_response_rate:.0%})"
            )

        # Top competitor learning
        if comparison.top_competitor:
            recommendations.append(
                f"Study {comparison.top_competitor}'s strategy - they're the market leader"
            )

        # Weaknesses
        for weakness in comparison.weaknesses[:2]:
            if "regular" in weakness.lower():
                recommendations.append("Start posting to Google Business Profile 2-4 times per month")
            elif "photo" in weakness.lower():
                recommendations.append("Upload more photos to GBP (aim for 50+ total)")

        return recommendations
