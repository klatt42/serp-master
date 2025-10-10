"""
Review Management Service
Aggregates and analyzes reviews from multiple platforms
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from collections import Counter

from app.models.local_models import (
    ReviewManagementRequest,
    ReviewManagementResponse,
    Review,
    ReviewAnalysis,
    ReviewPlatform
)

logger = logging.getLogger(__name__)


class ReviewManager:
    """Manage and analyze reviews from multiple platforms"""

    def __init__(self):
        """Initialize review manager"""
        # Sentiment keywords
        self.positive_keywords = [
            "excellent", "great", "amazing", "wonderful", "fantastic", "best",
            "love", "perfect", "professional", "recommend", "helpful", "friendly"
        ]

        self.negative_keywords = [
            "terrible", "awful", "horrible", "worst", "poor", "bad",
            "disappointed", "unprofessional", "rude", "slow", "overpriced"
        ]

    async def analyze_reviews(
        self,
        request: ReviewManagementRequest,
        site_data: Optional[Dict] = None
    ) -> ReviewManagementResponse:
        """
        Analyze reviews from multiple platforms

        Args:
            request: Review management request
            site_data: Optional site data

        Returns:
            Review analysis with scores and recommendations
        """
        try:
            logger.info(f"Analyzing reviews for: {request.business_name}")

            # Fetch reviews from all platforms
            all_reviews = self._fetch_reviews(request)

            # Analyze reviews
            analysis = self._analyze_review_data(all_reviews)

            # Calculate review score (0-5 points for GEO)
            review_score = self._calculate_review_score(analysis)

            # Generate response suggestions
            response_suggestions = self._generate_response_suggestions(all_reviews)

            # Generate reputation recommendations
            reputation_recommendations = self._generate_reputation_recommendations(
                analysis,
                review_score
            )

            # Generate solicitation strategy
            solicitation_strategy = self._generate_solicitation_strategy(analysis)

            return ReviewManagementResponse(
                reviews=all_reviews,
                analysis=analysis,
                review_score=review_score,
                response_suggestions=response_suggestions,
                reputation_recommendations=reputation_recommendations,
                solicitation_strategy=solicitation_strategy,
                analyzed_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error analyzing reviews: {str(e)}")
            raise

    def _fetch_reviews(
        self,
        request: ReviewManagementRequest
    ) -> List[Review]:
        """
        Fetch reviews from multiple platforms
        In production, this would use platform APIs
        """
        reviews = []

        # Simulate reviews from Google
        if ReviewPlatform.GOOGLE in request.platforms:
            reviews.extend(self._simulate_google_reviews(request.business_name))

        # Simulate reviews from Yelp
        if ReviewPlatform.YELP in request.platforms:
            reviews.extend(self._simulate_yelp_reviews(request.business_name))

        # Sort by date, newest first
        reviews.sort(key=lambda r: r.date, reverse=True)

        return reviews

    def _simulate_google_reviews(self, business_name: str) -> List[Review]:
        """Simulate Google reviews"""
        return [
            Review(
                platform=ReviewPlatform.GOOGLE,
                reviewer_name="John D.",
                rating=5,
                text="Excellent service! The team was professional and went above and beyond. Highly recommend!",
                date=datetime.now() - timedelta(days=5),
                has_response=True,
                response_text="Thank you for your kind words, John! We're thrilled you had a great experience.",
                response_date=datetime.now() - timedelta(days=4),
                sentiment="positive",
                keywords=["excellent", "professional", "recommend"]
            ),
            Review(
                platform=ReviewPlatform.GOOGLE,
                reviewer_name="Sarah M.",
                rating=4,
                text="Good experience overall. Fast service and friendly staff. Only issue was parking.",
                date=datetime.now() - timedelta(days=12),
                has_response=True,
                response_text="Thanks for the feedback, Sarah! We're working on improving our parking situation.",
                response_date=datetime.now() - timedelta(days=11),
                sentiment="positive",
                keywords=["fast", "friendly"]
            ),
            Review(
                platform=ReviewPlatform.GOOGLE,
                reviewer_name="Mike R.",
                rating=5,
                text="Best in the area! Quality work and fair pricing. Will definitely use again.",
                date=datetime.now() - timedelta(days=18),
                has_response=False,
                sentiment="positive",
                keywords=["best", "quality", "fair pricing"]
            ),
            Review(
                platform=ReviewPlatform.GOOGLE,
                reviewer_name="Lisa K.",
                rating=3,
                text="Decent service but took longer than expected. Communication could be better.",
                date=datetime.now() - timedelta(days=25),
                has_response=False,
                sentiment="neutral",
                keywords=["decent", "longer than expected", "communication"]
            ),
        ]

    def _simulate_yelp_reviews(self, business_name: str) -> List[Review]:
        """Simulate Yelp reviews"""
        return [
            Review(
                platform=ReviewPlatform.YELP,
                reviewer_name="David P.",
                rating=5,
                text="Amazing experience from start to finish. Professional team and great results!",
                date=datetime.now() - timedelta(days=8),
                has_response=True,
                response_text="We appreciate your review, David! It was a pleasure working with you.",
                response_date=datetime.now() - timedelta(days=7),
                sentiment="positive",
                keywords=["amazing", "professional", "great"]
            ),
            Review(
                platform=ReviewPlatform.YELP,
                reviewer_name="Jennifer L.",
                rating=4,
                text="Very satisfied with the service. Staff was helpful and knowledgeable.",
                date=datetime.now() - timedelta(days=15),
                has_response=False,
                sentiment="positive",
                keywords=["satisfied", "helpful", "knowledgeable"]
            ),
        ]

    def _analyze_review_data(self, reviews: List[Review]) -> ReviewAnalysis:
        """Analyze review data"""
        if not reviews:
            return ReviewAnalysis(
                total_reviews=0,
                average_rating=0.0,
                rating_distribution={5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
                reviews_last_30_days=0,
                reviews_last_90_days=0,
                response_rate=0.0,
                average_response_time_hours=None,
                sentiment_breakdown={"positive": 0, "neutral": 0, "negative": 0},
                common_keywords=[],
                trending_topics=[],
                platform_breakdown={}
            )

        # Calculate basic stats
        total_reviews = len(reviews)
        average_rating = sum(r.rating for r in reviews) / total_reviews

        # Rating distribution
        rating_dist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for review in reviews:
            rating_dist[review.rating] += 1

        # Time-based metrics
        now = datetime.now()
        reviews_30 = len([r for r in reviews if (now - r.date).days <= 30])
        reviews_90 = len([r for r in reviews if (now - r.date).days <= 90])

        # Response metrics
        responded = [r for r in reviews if r.has_response]
        response_rate = len(responded) / total_reviews if total_reviews > 0 else 0.0

        # Calculate average response time
        response_times = []
        for review in responded:
            if review.response_date:
                time_diff = (review.response_date - review.date).total_seconds() / 3600
                response_times.append(time_diff)

        avg_response_time = sum(response_times) / len(response_times) if response_times else None

        # Sentiment breakdown
        sentiments = {"positive": 0, "neutral": 0, "negative": 0}
        for review in reviews:
            sentiment = review.sentiment or self._detect_sentiment(review.text, review.rating)
            sentiments[sentiment] += 1

        # Extract keywords
        all_keywords = []
        for review in reviews:
            if review.keywords:
                all_keywords.extend(review.keywords)
            else:
                all_keywords.extend(self._extract_keywords(review.text))

        keyword_counts = Counter(all_keywords)
        common_keywords = keyword_counts.most_common(10)

        # Trending topics (keywords from recent reviews)
        recent_reviews = [r for r in reviews if (now - r.date).days <= 30]
        recent_keywords = []
        for review in recent_reviews:
            if review.keywords:
                recent_keywords.extend(review.keywords)
        trending = list(set(recent_keywords))[:5]

        # Platform breakdown
        platform_stats = {}
        for platform in set(r.platform for r in reviews):
            platform_reviews = [r for r in reviews if r.platform == platform]
            platform_stats[platform.value] = {
                "count": len(platform_reviews),
                "average_rating": sum(r.rating for r in platform_reviews) / len(platform_reviews),
                "response_rate": len([r for r in platform_reviews if r.has_response]) / len(platform_reviews)
            }

        return ReviewAnalysis(
            total_reviews=total_reviews,
            average_rating=round(average_rating, 2),
            rating_distribution=rating_dist,
            reviews_last_30_days=reviews_30,
            reviews_last_90_days=reviews_90,
            response_rate=round(response_rate, 2),
            average_response_time_hours=round(avg_response_time, 1) if avg_response_time else None,
            sentiment_breakdown=sentiments,
            common_keywords=common_keywords,
            trending_topics=trending,
            platform_breakdown=platform_stats
        )

    def _detect_sentiment(self, text: str, rating: int) -> str:
        """Detect sentiment from review text and rating"""
        if not text:
            return "positive" if rating >= 4 else "negative" if rating <= 2 else "neutral"

        text_lower = text.lower()

        # Count positive and negative keywords
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)

        # Combine with rating
        if rating >= 4 and (positive_count > negative_count or positive_count > 0):
            return "positive"
        elif rating <= 2 or negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from review text"""
        if not text:
            return []

        text_lower = text.lower()
        found_keywords = []

        # Find positive keywords
        for keyword in self.positive_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)

        # Find negative keywords
        for keyword in self.negative_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)

        return found_keywords[:5]  # Limit to 5 keywords per review

    def _calculate_review_score(self, analysis: ReviewAnalysis) -> int:
        """
        Calculate review score (0-5 points for GEO)

        Scoring:
        - Average rating (0-2 points)
        - Review count (0-2 points)
        - Response rate (0-1 point)
        """
        score = 0

        # Average rating score (0-2 points)
        if analysis.average_rating >= 4.5:
            score += 2
        elif analysis.average_rating >= 4.0:
            score += 1.5
        elif analysis.average_rating >= 3.5:
            score += 1
        elif analysis.average_rating >= 3.0:
            score += 0.5

        # Review count score (0-2 points)
        if analysis.total_reviews >= 50:
            score += 2
        elif analysis.total_reviews >= 25:
            score += 1.5
        elif analysis.total_reviews >= 10:
            score += 1
        elif analysis.total_reviews >= 5:
            score += 0.5

        # Response rate score (0-1 point)
        if analysis.response_rate >= 0.8:
            score += 1
        elif analysis.response_rate >= 0.5:
            score += 0.5

        return int(score)

    def _generate_response_suggestions(
        self,
        reviews: List[Review]
    ) -> List[Dict[str, str]]:
        """Generate AI-powered response suggestions for unanswered reviews"""
        suggestions = []

        # Find recent unanswered reviews
        unanswered = [r for r in reviews if not r.has_response][:3]

        for review in unanswered:
            template = self._get_response_template(review.rating, review.sentiment)
            suggestions.append({
                "reviewer": review.reviewer_name,
                "rating": str(review.rating),
                "review_text": review.text[:100] + "..." if len(review.text) > 100 else review.text,
                "suggested_response": template,
                "platform": review.platform.value
            })

        return suggestions

    def _get_response_template(self, rating: int, sentiment: str) -> str:
        """Get response template based on rating and sentiment"""
        if rating >= 4:
            return "Thank you so much for your wonderful review! We're thrilled to hear you had a great experience. We look forward to serving you again soon!"
        elif rating == 3:
            return "Thank you for your feedback. We're glad you chose us and appreciate your input. We're always working to improve. Please feel free to reach out if there's anything we can do better."
        else:
            return "Thank you for sharing your concerns. We sincerely apologize for not meeting your expectations. We'd love the opportunity to make this right. Please contact us directly so we can address your issues."

    def _generate_reputation_recommendations(
        self,
        analysis: ReviewAnalysis,
        score: int
    ) -> List[str]:
        """Generate reputation management recommendations"""
        recommendations = []

        # Review count recommendations
        if analysis.total_reviews < 10:
            recommendations.append(
                f"⚠️ Build review count to 10+ (currently {analysis.total_reviews}). Reviews are critical for local SEO."
            )
            recommendations.append(
                "Implement automated review request system after service completion"
            )

        # Average rating recommendations
        if analysis.average_rating < 4.0:
            recommendations.append(
                f"⚠️ Improve average rating to 4.0+ (currently {analysis.average_rating}). Focus on service quality improvements."
            )

        # Response rate recommendations
        if analysis.response_rate < 0.8:
            recommendations.append(
                f"Improve response rate to 80%+ (currently {analysis.response_rate:.0%}). Respond to ALL reviews within 24 hours."
            )

        # Response time recommendations
        if analysis.average_response_time_hours and analysis.average_response_time_hours > 48:
            recommendations.append(
                f"Reduce average response time (currently {analysis.average_response_time_hours:.1f} hours). Aim for <24 hours."
            )

        # Recent reviews
        if analysis.reviews_last_30_days < 2:
            recommendations.append(
                f"Increase recent review velocity (only {analysis.reviews_last_30_days} in last 30 days). Aim for 2-4 per month."
            )

        # Negative sentiment handling
        negative_pct = (analysis.sentiment_breakdown.get("negative", 0) / analysis.total_reviews * 100) if analysis.total_reviews > 0 else 0
        if negative_pct > 20:
            recommendations.append(
                f"⚠️ {negative_pct:.0f}% of reviews are negative. Address common complaints immediately."
            )

        # Platform diversification
        if len(analysis.platform_breakdown) < 2:
            recommendations.append(
                "Encourage reviews on multiple platforms (Google, Yelp, Facebook) for better visibility"
            )

        # Positive reinforcement
        if score >= 4:
            recommendations.append(
                "✅ Strong review profile! Continue current review solicitation practices."
            )

        return recommendations

    def _generate_solicitation_strategy(
        self,
        analysis: ReviewAnalysis
    ) -> List[str]:
        """Generate review solicitation strategy"""
        strategy = []

        strategy.append("📋 Review Solicitation Best Practices:")

        strategy.append(
            "1. Timing: Ask for reviews 2-3 days after service completion"
        )

        strategy.append(
            "2. Method: Send personalized email with direct review links"
        )

        strategy.append(
            "3. Make it easy: Provide platform-specific links (Google, Yelp, Facebook)"
        )

        if analysis.average_rating >= 4.0:
            strategy.append(
                "4. Target happy customers: Focus on 5-star experiences for public reviews"
            )

        strategy.append(
            "5. Follow up: Send gentle reminder if no response in 7 days"
        )

        strategy.append(
            "6. Incentivize ethically: Thank reviewers, but never offer quid pro quo"
        )

        if analysis.total_reviews < 25:
            strategy.append(
                "7. Prioritize Google: Focus on Google Business Profile for local SEO impact"
            )

        strategy.append(
            "8. Staff training: Ensure all team members know how to request reviews"
        )

        strategy.append(
            "9. Monitor & respond: Check for new reviews daily and respond within 24h"
        )

        return strategy
