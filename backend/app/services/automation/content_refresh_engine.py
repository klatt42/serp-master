"""
Content Refresh Intelligence Engine
Identifies content needing updates and generates refresh recommendations
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RefreshPriority(str, Enum):
    """Content refresh priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ContentRefreshEngine:
    """Detect and prioritize content needing refreshes"""

    def __init__(self):
        """Initialize content refresh engine"""
        self.staleness_threshold_days = 180
        self.ranking_decline_threshold = 10

    async def analyze_content_staleness(
        self,
        content_id: str,
        content_data: Dict,
        performance_history: List[Dict]
    ) -> Dict:
        """
        Analyze content for staleness indicators

        Args:
            content_id: Content identifier
            content_data: Content metadata
            performance_history: Historical performance data

        Returns:
            Staleness analysis
        """
        try:
            staleness_factors = []
            staleness_score = 0

            # Check publish date
            publish_date_str = content_data.get("published_at")
            if publish_date_str:
                publish_date = datetime.fromisoformat(publish_date_str.replace('Z', '+00:00'))
                days_old = (datetime.now() - publish_date).days

                if days_old > self.staleness_threshold_days:
                    staleness_score += 30
                    staleness_factors.append(f"Published {days_old} days ago")

            # Check ranking decline
            ranking_decline = self._detect_ranking_decline(performance_history)
            if ranking_decline:
                staleness_score += 25
                staleness_factors.append(f"Rankings declined by {ranking_decline} positions")

            # Check traffic decline
            traffic_decline = self._detect_traffic_decline(performance_history)
            if traffic_decline:
                staleness_score += 20
                staleness_factors.append(f"Traffic down {traffic_decline}%")

            # Check for outdated content patterns
            outdated_patterns = self._detect_outdated_patterns(content_data)
            if outdated_patterns:
                staleness_score += 15
                staleness_factors.extend(outdated_patterns)

            # Check engagement decline
            engagement_decline = self._detect_engagement_decline(performance_history)
            if engagement_decline:
                staleness_score += 10
                staleness_factors.append("Engagement metrics declining")

            return {
                "content_id": content_id,
                "staleness_score": min(100, staleness_score),
                "priority": self._calculate_priority(staleness_score),
                "staleness_factors": staleness_factors,
                "needs_refresh": staleness_score >= 50,
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing staleness: {str(e)}")
            raise

    def _detect_ranking_decline(
        self,
        performance_history: List[Dict]
    ) -> Optional[int]:
        """Detect ranking position decline"""
        try:
            if len(performance_history) < 2:
                return None

            sorted_history = sorted(
                performance_history,
                key=lambda x: x.get("tracked_date", "")
            )

            recent = sorted_history[-7:]  # Last 7 days
            older = sorted_history[-30:-7]  # Previous 23 days

            if not recent or not older:
                return None

            recent_avg = sum(p.get("avg_position", 0) for p in recent) / len(recent)
            older_avg = sum(p.get("avg_position", 0) for p in older) / len(older)

            decline = recent_avg - older_avg

            return int(decline) if decline > self.ranking_decline_threshold else None

        except Exception as e:
            logger.error(f"Error detecting ranking decline: {str(e)}")
            return None

    def _detect_traffic_decline(
        self,
        performance_history: List[Dict]
    ) -> Optional[int]:
        """Detect traffic decline percentage"""
        try:
            if len(performance_history) < 2:
                return None

            sorted_history = sorted(
                performance_history,
                key=lambda x: x.get("tracked_date", "")
            )

            recent = sorted_history[-7:]
            older = sorted_history[-30:-7]

            if not recent or not older:
                return None

            recent_clicks = sum(p.get("clicks", 0) for p in recent)
            older_clicks = sum(p.get("clicks", 0) for p in older)

            if older_clicks == 0:
                return None

            decline_pct = ((older_clicks - recent_clicks) / older_clicks) * 100

            return int(decline_pct) if decline_pct > 20 else None

        except Exception as e:
            logger.error(f"Error detecting traffic decline: {str(e)}")
            return None

    def _detect_outdated_patterns(
        self,
        content_data: Dict
    ) -> List[str]:
        """Detect outdated language patterns or references"""
        try:
            patterns = []
            content_text = content_data.get("content", "").lower()
            title = content_data.get("title", "").lower()

            # Check for old year references
            current_year = datetime.now().year
            for year in range(current_year - 3, current_year):
                if str(year) in title or str(year) in content_text:
                    patterns.append(f"References to {year} detected")

            # Check for outdated terminology (examples)
            outdated_terms = [
                "coronavirus", "covid-19", "pandemic",  # Time-sensitive
                "latest", "new", "recent"  # Relative terms
            ]

            for term in outdated_terms:
                if term in title:
                    patterns.append(f"Time-sensitive term '{term}' in title")

            return patterns

        except Exception as e:
            logger.error(f"Error detecting outdated patterns: {str(e)}")
            return []

    def _detect_engagement_decline(
        self,
        performance_history: List[Dict]
    ) -> bool:
        """Detect declining engagement metrics"""
        try:
            if len(performance_history) < 10:
                return False

            sorted_history = sorted(
                performance_history,
                key=lambda x: x.get("tracked_date", "")
            )

            recent = sorted_history[-5:]
            older = sorted_history[-10:-5]

            recent_engagement = sum(p.get("engagement_score", 0) for p in recent) / len(recent)
            older_engagement = sum(p.get("engagement_score", 0) for p in older) / len(older)

            return recent_engagement < older_engagement * 0.8

        except Exception as e:
            logger.error(f"Error detecting engagement decline: {str(e)}")
            return False

    def _calculate_priority(self, staleness_score: int) -> str:
        """Calculate refresh priority based on staleness score"""
        try:
            if staleness_score >= 75:
                return RefreshPriority.HIGH.value
            elif staleness_score >= 50:
                return RefreshPriority.MEDIUM.value
            else:
                return RefreshPriority.LOW.value

        except Exception as e:
            logger.error(f"Error calculating priority: {str(e)}")
            return RefreshPriority.MEDIUM.value

    async def generate_refresh_recommendations(
        self,
        content_id: str,
        staleness_analysis: Dict,
        competitive_data: Optional[Dict] = None
    ) -> Dict:
        """
        Generate specific refresh recommendations

        Args:
            content_id: Content identifier
            staleness_analysis: Staleness analysis results
            competitive_data: Competitor comparison data

        Returns:
            Refresh recommendations
        """
        try:
            recommendations = []

            # Recommendations based on staleness factors
            factors = staleness_analysis.get("staleness_factors", [])

            for factor in factors:
                if "published" in factor.lower():
                    recommendations.append({
                        "type": "update_date",
                        "action": "Update publish date and add 'Updated [Year]' to title",
                        "impact": "high",
                        "effort": "low"
                    })

                if "rankings declined" in factor.lower():
                    recommendations.append({
                        "type": "improve_content",
                        "action": "Expand content depth, add new sections, update statistics",
                        "impact": "high",
                        "effort": "medium"
                    })

                if "traffic down" in factor.lower():
                    recommendations.append({
                        "type": "optimize_meta",
                        "action": "Rewrite meta title and description with current keywords",
                        "impact": "medium",
                        "effort": "low"
                    })

                if "year" in factor.lower() or "time-sensitive" in factor.lower():
                    recommendations.append({
                        "type": "update_references",
                        "action": "Replace outdated statistics, examples, and year references",
                        "impact": "medium",
                        "effort": "medium"
                    })

            # Competitive recommendations
            if competitive_data:
                recommendations.append({
                    "type": "competitive_analysis",
                    "action": "Analyze top-ranking competitors and add missing content gaps",
                    "impact": "high",
                    "effort": "high"
                })

            # Default general recommendations
            if not recommendations:
                recommendations.append({
                    "type": "general_refresh",
                    "action": "Review and update content for accuracy and relevance",
                    "impact": "medium",
                    "effort": "medium"
                })

            return {
                "content_id": content_id,
                "priority": staleness_analysis.get("priority"),
                "staleness_score": staleness_analysis.get("staleness_score"),
                "recommendations": recommendations,
                "estimated_effort_hours": self._estimate_refresh_effort(recommendations),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise

    def _estimate_refresh_effort(
        self,
        recommendations: List[Dict]
    ) -> float:
        """Estimate effort required for refresh"""
        try:
            effort_map = {
                "low": 0.5,
                "medium": 2.0,
                "high": 4.0
            }

            total_hours = sum(
                effort_map.get(rec.get("effort", "medium"), 2.0)
                for rec in recommendations
            )

            return round(total_hours, 1)

        except Exception as e:
            logger.error(f"Error estimating effort: {str(e)}")
            return 2.0

    async def create_refresh_queue(
        self,
        all_content: List[Dict],
        performance_data: Dict
    ) -> List[Dict]:
        """
        Create prioritized refresh queue

        Args:
            all_content: All published content
            performance_data: Performance history for all content

        Returns:
            Prioritized refresh queue
        """
        try:
            refresh_queue = []

            for content in all_content:
                content_id = content.get("id")
                perf_history = performance_data.get(content_id, [])

                staleness = await self.analyze_content_staleness(
                    content_id,
                    content,
                    perf_history
                )

                if staleness.get("needs_refresh"):
                    recommendations = await self.generate_refresh_recommendations(
                        content_id,
                        staleness
                    )

                    refresh_queue.append({
                        **staleness,
                        "content_title": content.get("title"),
                        "recommendations": recommendations.get("recommendations"),
                        "estimated_effort": recommendations.get("estimated_effort_hours")
                    })

            # Sort by priority and staleness score
            priority_order = {"high": 0, "medium": 1, "low": 2}
            sorted_queue = sorted(
                refresh_queue,
                key=lambda x: (
                    priority_order.get(x.get("priority", "medium"), 1),
                    -x.get("staleness_score", 0)
                )
            )

            logger.info(f"Created refresh queue with {len(sorted_queue)} items")
            return sorted_queue

        except Exception as e:
            logger.error(f"Error creating refresh queue: {str(e)}")
            raise
