"""
Google Business Profile Optimizer
Analyzes and optimizes GBP listings for local SEO
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta

from app.models.local_models import (
    GBPOptimizationRequest,
    GBPOptimizationResponse,
    GBPProfileData,
    GBPPhoto,
    GBPPost,
    GBPReview,
    GBPQandA
)

logger = logging.getLogger(__name__)


class GBPOptimizer:
    """Optimize Google Business Profile listings"""

    def __init__(self):
        """Initialize GBP optimizer"""
        # Required fields for complete profile
        self.required_fields = [
            "business_name",
            "address",
            "phone",
            "website",
            "category",
            "description",
            "hours"
        ]

        # Recommended photo counts
        self.min_photos = {
            "cover": 1,
            "logo": 1,
            "interior": 3,
            "exterior": 2,
            "team": 2,
            "product": 5
        }

    async def optimize_profile(
        self,
        request: GBPOptimizationRequest,
        site_data: Optional[Dict] = None
    ) -> GBPOptimizationResponse:
        """
        Analyze and optimize Google Business Profile

        Args:
            request: GBP optimization request
            site_data: Optional site data from crawling

        Returns:
            GBP optimization response with scores and recommendations
        """
        try:
            logger.info(f"Starting GBP optimization for: {request.site_url}")

            # Simulate fetching GBP data (in production would use Google My Business API)
            profile_data = self._simulate_gbp_data(request, site_data)

            # Calculate profile completeness
            completeness_score = self._calculate_completeness(profile_data)

            # Calculate 12-point GBP score
            profile_complete_score = self._score_profile_completeness(profile_data)
            verification_score = self._score_verification(profile_data)
            posting_score = self._score_posting(profile_data)
            photo_score = self._score_photos(profile_data)

            gbp_score = (
                profile_complete_score +
                verification_score +
                posting_score +
                photo_score
            )

            # Generate recommendations
            missing_sections = self._identify_missing_sections(profile_data)
            photo_recommendations = self._generate_photo_recommendations(profile_data)
            posting_recommendations = self._generate_posting_recommendations(profile_data)
            review_recommendations = self._generate_review_recommendations(profile_data)
            qanda_recommendations = self._generate_qanda_recommendations(profile_data)

            # Create optimization plan
            optimization_plan = self._create_optimization_plan(
                profile_data,
                profile_complete_score,
                verification_score,
                posting_score,
                photo_score
            )

            return GBPOptimizationResponse(
                profile_data=profile_data,
                completeness_score=completeness_score,
                gbp_score=gbp_score,
                profile_complete=completeness_score >= 80,
                profile_complete_score=profile_complete_score,
                is_verified=profile_data.is_verified,
                verification_score=verification_score,
                has_regular_posts=profile_data.post_count_last_30_days >= 4,
                posting_score=posting_score,
                has_updated_photos=len(profile_data.photos) >= 10,
                photo_score=photo_score,
                missing_sections=missing_sections,
                photo_recommendations=photo_recommendations,
                posting_recommendations=posting_recommendations,
                review_recommendations=review_recommendations,
                qanda_recommendations=qanda_recommendations,
                optimization_plan=optimization_plan,
                analyzed_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error optimizing GBP: {str(e)}")
            raise

    def _simulate_gbp_data(
        self,
        request: GBPOptimizationRequest,
        site_data: Optional[Dict] = None
    ) -> GBPProfileData:
        """
        Simulate GBP data retrieval
        In production, this would query Google My Business API
        """
        # Simulate varying levels of profile completeness
        business_name = site_data.get("business_name", "Example Business") if site_data else "Example Business"

        # Simulate profile with some data filled, some missing
        return GBPProfileData(
            business_name=business_name,
            address="123 Main Street, Anytown, CA 90210",
            phone="(555) 123-4567",
            website=request.site_url,
            category="Professional Services",
            additional_categories=["Consultant", "Business Service"],
            description="A professional business providing excellent services to the local community.",
            is_verified=True,
            is_claimed=True,
            is_published=True,
            hours={
                "monday": "9:00 AM - 5:00 PM",
                "tuesday": "9:00 AM - 5:00 PM",
                "wednesday": "9:00 AM - 5:00 PM",
                "thursday": "9:00 AM - 5:00 PM",
                "friday": "9:00 AM - 5:00 PM",
                "saturday": "Closed",
                "sunday": "Closed"
            },
            photos=[
                GBPPhoto(category="cover", url="https://example.com/cover.jpg", uploaded_date=datetime.now() - timedelta(days=30)),
                GBPPhoto(category="logo", url="https://example.com/logo.jpg", uploaded_date=datetime.now() - timedelta(days=60)),
                GBPPhoto(category="interior", url="https://example.com/interior1.jpg", uploaded_date=datetime.now() - timedelta(days=90)),
                GBPPhoto(category="exterior", url="https://example.com/exterior1.jpg", uploaded_date=datetime.now() - timedelta(days=120)),
            ],
            posts=[
                GBPPost(
                    post_type="update",
                    content="We're excited to announce our new services!",
                    created_date=datetime.now() - timedelta(days=15),
                    cta_type="learn_more"
                ),
                GBPPost(
                    post_type="offer",
                    content="Special discount for new customers!",
                    created_date=datetime.now() - timedelta(days=45),
                    expires_date=datetime.now() + timedelta(days=15),
                    cta_type="call"
                )
            ],
            reviews=[
                GBPReview(
                    reviewer_name="John D.",
                    rating=5,
                    text="Excellent service! Highly recommend.",
                    created_date=datetime.now() - timedelta(days=10),
                    owner_response="Thank you for your kind words!",
                    response_date=datetime.now() - timedelta(days=9)
                ),
                GBPReview(
                    reviewer_name="Sarah M.",
                    rating=4,
                    text="Good experience overall.",
                    created_date=datetime.now() - timedelta(days=20)
                )
            ],
            qanda=[
                GBPQandA(
                    question="What are your business hours?",
                    answer="We're open Monday-Friday 9am-5pm",
                    asked_date=datetime.now() - timedelta(days=30),
                    answered_date=datetime.now() - timedelta(days=29)
                )
            ],
            attributes=["wheelchair_accessible", "free_wifi"],
            payment_methods=["cash", "credit_card", "debit_card"],
            average_rating=4.5,
            review_count=2,
            photo_count=4,
            post_count_last_30_days=1
        )

    def _calculate_completeness(self, profile: GBPProfileData) -> int:
        """Calculate profile completeness percentage (0-100)"""
        completed = 0
        total = len(self.required_fields) + 4  # +4 for photos, reviews, posts, attributes

        # Check required fields
        if profile.business_name:
            completed += 1
        if profile.address:
            completed += 1
        if profile.phone:
            completed += 1
        if profile.website:
            completed += 1
        if profile.category:
            completed += 1
        if profile.description:
            completed += 1
        if profile.hours:
            completed += 1

        # Check additional sections
        if profile.photo_count >= 5:
            completed += 1
        if profile.review_count > 0:
            completed += 1
        if profile.post_count_last_30_days > 0:
            completed += 1
        if len(profile.attributes) > 0:
            completed += 1

        return int((completed / total) * 100)

    def _score_profile_completeness(self, profile: GBPProfileData) -> int:
        """
        Score profile completeness (0-5 points)

        5 points: All required fields + photos + description + hours
        4 points: All required fields + most sections
        3 points: All required fields
        2 points: Missing 1-2 required fields
        1 point: Missing 3-4 required fields
        0 points: Missing 5+ required fields
        """
        missing = 0

        if not profile.business_name:
            missing += 1
        if not profile.address:
            missing += 1
        if not profile.phone:
            missing += 1
        if not profile.category:
            missing += 1
        if not profile.description:
            missing += 1
        if not profile.hours:
            missing += 1
        if not profile.website:
            missing += 1

        # Award points based on completeness
        if missing == 0:
            # All required fields present
            if profile.photo_count >= 10 and len(profile.description) >= 200:
                return 5  # Perfect profile
            elif profile.photo_count >= 5:
                return 4  # Good profile
            else:
                return 3  # Basic complete
        elif missing <= 2:
            return 2
        elif missing <= 4:
            return 1
        else:
            return 0

    def _score_verification(self, profile: GBPProfileData) -> int:
        """
        Score verification status (0-3 points)

        3 points: Verified and claimed
        1 point: Claimed but not verified
        0 points: Not claimed
        """
        if profile.is_verified and profile.is_claimed:
            return 3
        elif profile.is_claimed:
            return 1
        else:
            return 0

    def _score_posting(self, profile: GBPProfileData) -> int:
        """
        Score posting frequency (0-2 points)

        2 points: 4+ posts in last 30 days
        1 point: 1-3 posts in last 30 days
        0 points: No posts in last 30 days
        """
        if profile.post_count_last_30_days >= 4:
            return 2
        elif profile.post_count_last_30_days >= 1:
            return 1
        else:
            return 0

    def _score_photos(self, profile: GBPProfileData) -> int:
        """
        Score photo quantity and recency (0-2 points)

        2 points: 15+ photos with recent uploads
        1 point: 5-14 photos
        0 points: <5 photos
        """
        if profile.photo_count >= 15:
            # Check for recent photos (within 60 days)
            recent_photos = [p for p in profile.photos if p.uploaded_date and
                           (datetime.now() - p.uploaded_date).days <= 60]
            if len(recent_photos) >= 2:
                return 2
            else:
                return 1
        elif profile.photo_count >= 5:
            return 1
        else:
            return 0

    def _identify_missing_sections(self, profile: GBPProfileData) -> List[str]:
        """Identify missing or incomplete profile sections"""
        missing = []

        if not profile.business_name:
            missing.append("Business Name")
        if not profile.address:
            missing.append("Address")
        if not profile.phone:
            missing.append("Phone Number")
        if not profile.website:
            missing.append("Website URL")
        if not profile.category:
            missing.append("Primary Category")
        if not profile.description or len(profile.description) < 200:
            missing.append("Complete Business Description (200+ characters)")
        if not profile.hours:
            missing.append("Business Hours")
        if profile.photo_count < 10:
            missing.append(f"Photos ({profile.photo_count}/10 minimum)")
        if not profile.attributes:
            missing.append("Business Attributes")
        if not profile.payment_methods:
            missing.append("Payment Methods")

        return missing

    def _generate_photo_recommendations(self, profile: GBPProfileData) -> List[str]:
        """Generate photo recommendations"""
        recommendations = []

        # Count photos by category
        photo_categories = {}
        for photo in profile.photos:
            photo_categories[photo.category] = photo_categories.get(photo.category, 0) + 1

        # Check minimum requirements
        for category, min_count in self.min_photos.items():
            current = photo_categories.get(category, 0)
            if current < min_count:
                recommendations.append(
                    f"Add {min_count - current} more {category} photo(s) (have {current}, need {min_count})"
                )

        # Check photo recency
        if profile.photos:
            most_recent = max(profile.photos, key=lambda p: p.uploaded_date or datetime.min)
            days_old = (datetime.now() - (most_recent.uploaded_date or datetime.now())).days
            if days_old > 30:
                recommendations.append(
                    f"Upload new photos - most recent is {days_old} days old"
                )

        if not recommendations:
            recommendations.append("✅ Photo library looks good! Continue uploading monthly.")

        return recommendations

    def _generate_posting_recommendations(self, profile: GBPProfileData) -> List[str]:
        """Generate posting recommendations"""
        recommendations = []

        posts_needed = max(0, 4 - profile.post_count_last_30_days)

        if posts_needed > 0:
            recommendations.append(
                f"Create {posts_needed} more post(s) this month for optimal engagement (currently {profile.post_count_last_30_days}/4)"
            )
            recommendations.append(
                "Post types to consider: Updates, Offers, Events, Products"
            )
            recommendations.append(
                "Include call-to-action buttons: Call, Book, Order, Learn More"
            )
        else:
            recommendations.append(
                "✅ Great posting frequency! Maintain 4+ posts per month."
            )

        return recommendations

    def _generate_review_recommendations(self, profile: GBPProfileData) -> List[str]:
        """Generate review management recommendations"""
        recommendations = []

        if profile.review_count < 10:
            recommendations.append(
                f"Build review count to 10+ (currently {profile.review_count})"
            )
            recommendations.append(
                "Ask satisfied customers for reviews after service completion"
            )

        # Check response rate
        reviews_with_responses = len([r for r in profile.reviews if r.owner_response])
        if profile.review_count > 0:
            response_rate = (reviews_with_responses / profile.review_count) * 100
            if response_rate < 80:
                recommendations.append(
                    f"Improve review response rate ({response_rate:.0f}% currently, aim for 80%+)"
                )

        if profile.average_rating and profile.average_rating < 4.5:
            recommendations.append(
                f"Work on improving average rating (currently {profile.average_rating:.1f}/5.0)"
            )

        if not recommendations:
            recommendations.append(
                "✅ Review management looking good! Continue responding promptly."
            )

        return recommendations

    def _generate_qanda_recommendations(self, profile: GBPProfileData) -> List[str]:
        """Generate Q&A recommendations"""
        recommendations = []

        answered_count = len([q for q in profile.qanda if q.answer])
        unanswered_count = len(profile.qanda) - answered_count

        if unanswered_count > 0:
            recommendations.append(
                f"Answer {unanswered_count} pending question(s)"
            )

        if len(profile.qanda) < 5:
            recommendations.append(
                "Add frequently asked questions preemptively"
            )
            recommendations.append(
                "Common topics: Hours, Services, Pricing, Location, Parking"
            )

        if not recommendations:
            recommendations.append(
                "✅ Q&A section maintained well!"
            )

        return recommendations

    def _create_optimization_plan(
        self,
        profile: GBPProfileData,
        profile_score: int,
        verification_score: int,
        posting_score: int,
        photo_score: int
    ) -> List[Dict[str, Any]]:
        """Create prioritized optimization action plan"""
        plan = []

        # Priority 1: Verification
        if verification_score < 3:
            plan.append({
                "priority": "high",
                "category": "verification",
                "action": "Verify your Google Business Profile",
                "impact": f"+{3 - verification_score} GBP points",
                "effort": "low",
                "timeframe": "1-2 days"
            })

        # Priority 2: Profile Completeness
        if profile_score < 5:
            plan.append({
                "priority": "high",
                "category": "profile",
                "action": "Complete all required profile sections",
                "impact": f"+{5 - profile_score} GBP points",
                "effort": "medium",
                "timeframe": "1-2 hours"
            })

        # Priority 3: Photos
        if photo_score < 2:
            plan.append({
                "priority": "medium",
                "category": "photos",
                "action": "Upload high-quality photos (aim for 15+ total)",
                "impact": f"+{2 - photo_score} GBP points",
                "effort": "medium",
                "timeframe": "2-3 hours"
            })

        # Priority 4: Posts
        if posting_score < 2:
            plan.append({
                "priority": "medium",
                "category": "posts",
                "action": "Create regular posts (4+ per month)",
                "impact": f"+{2 - posting_score} GBP points",
                "effort": "low",
                "timeframe": "ongoing"
            })

        # Add ongoing maintenance
        plan.append({
            "priority": "ongoing",
            "category": "maintenance",
            "action": "Monitor and respond to reviews within 24 hours",
            "impact": "Improves reputation and engagement",
            "effort": "low",
            "timeframe": "daily"
        })

        plan.append({
            "priority": "ongoing",
            "category": "maintenance",
            "action": "Post updates weekly, offers monthly",
            "impact": "Maintains visibility and engagement",
            "effort": "low",
            "timeframe": "weekly/monthly"
        })

        return plan
