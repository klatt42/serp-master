"""
Content Performance Tracking Service
Monitors content effectiveness through ranking data, engagement metrics, and ROI calculation
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
import statistics

logger = logging.getLogger(__name__)


class PerformanceMetricType(str, Enum):
    """Types of performance metrics"""
    RANKINGS = "rankings"
    TRAFFIC = "traffic"
    ENGAGEMENT = "engagement"
    CONVERSIONS = "conversions"
    ROI = "roi"


class PerformanceTracker:
    """Track and analyze content performance"""

    def __init__(self):
        """Initialize performance tracker"""
        self.score_weights = {
            "rankings": 0.30,
            "traffic": 0.25,
            "engagement": 0.20,
            "conversions": 0.15,
            "roi": 0.10
        }

    async def track_content_performance(
        self,
        content_id: str,
        metrics: Dict
    ) -> Dict:
        """
        Track performance for a piece of content

        Args:
            content_id: Content identifier
            metrics: Performance metrics data

        Returns:
            Tracked performance record
        """
        try:
            performance_score = self._calculate_performance_score(metrics)

            performance_data = {
                "content_id": content_id,
                "tracked_date": datetime.now().isoformat(),
                "impressions": metrics.get("impressions", 0),
                "clicks": metrics.get("clicks", 0),
                "avg_position": metrics.get("avg_position", 0),
                "ctr": metrics.get("ctr", 0),
                "engagement_score": metrics.get("engagement_score", 0),
                "conversion_count": metrics.get("conversions", 0),
                "performance_score": performance_score,
                "time_on_page": metrics.get("time_on_page", 0),
                "bounce_rate": metrics.get("bounce_rate", 0)
            }

            logger.info(f"Tracked performance for content {content_id}: {performance_score}")
            return performance_data

        except Exception as e:
            logger.error(f"Error tracking performance: {str(e)}")
            raise

    def _calculate_performance_score(self, metrics: Dict) -> int:
        """
        Calculate overall performance score (0-100)

        Scoring components:
        - Rankings: Position improvement, keyword coverage
        - Traffic: Impressions, clicks, CTR
        - Engagement: Time on page, bounce rate, shares
        - Conversions: Goal completions, revenue
        - ROI: Results vs effort invested
        """
        try:
            # Rankings score (0-100)
            avg_position = metrics.get("avg_position", 100)
            rankings_score = max(0, 100 - avg_position) if avg_position > 0 else 0

            # Traffic score (0-100)
            impressions = metrics.get("impressions", 0)
            clicks = metrics.get("clicks", 0)
            ctr = metrics.get("ctr", 0) * 100
            traffic_score = min(100, (clicks / 100) + (impressions / 1000) + ctr)

            # Engagement score (0-100)
            time_on_page = metrics.get("time_on_page", 0)
            bounce_rate = metrics.get("bounce_rate", 100)
            shares = metrics.get("shares", 0)
            engagement_score = min(100, (time_on_page / 3) + (100 - bounce_rate) + shares)

            # Conversions score (0-100)
            conversions = metrics.get("conversions", 0)
            conversion_rate = metrics.get("conversion_rate", 0) * 100
            conversions_score = min(100, (conversions * 10) + (conversion_rate * 2))

            # ROI score (0-100)
            revenue = metrics.get("revenue", 0)
            effort_hours = metrics.get("effort_hours", 1)
            roi_score = min(100, (revenue / effort_hours) / 10) if effort_hours > 0 else 0

            # Weighted average
            total_score = (
                rankings_score * self.score_weights["rankings"] +
                traffic_score * self.score_weights["traffic"] +
                engagement_score * self.score_weights["engagement"] +
                conversions_score * self.score_weights["conversions"] +
                roi_score * self.score_weights["roi"]
            )

            return int(min(100, max(0, total_score)))

        except Exception as e:
            logger.error(f"Error calculating performance score: {str(e)}")
            return 0

    async def analyze_content_trends(
        self,
        content_id: str,
        performance_history: List[Dict],
        days: int = 30
    ) -> Dict:
        """
        Analyze performance trends over time

        Args:
            content_id: Content identifier
            performance_history: Historical performance data
            days: Number of days to analyze

        Returns:
            Trend analysis
        """
        try:
            if not performance_history:
                return {
                    "content_id": content_id,
                    "trend": "no_data",
                    "trend_direction": "neutral",
                    "avg_score": 0,
                    "score_change": 0
                }

            # Sort by date
            sorted_history = sorted(
                performance_history,
                key=lambda x: x.get("tracked_date", ""),
                reverse=True
            )

            # Get recent data
            recent_data = sorted_history[:days] if len(sorted_history) >= days else sorted_history

            scores = [item.get("performance_score", 0) for item in recent_data]
            avg_score = statistics.mean(scores) if scores else 0

            # Calculate trend
            if len(scores) >= 2:
                first_half = scores[:len(scores)//2]
                second_half = scores[len(scores)//2:]
                first_avg = statistics.mean(first_half)
                second_avg = statistics.mean(second_half)
                score_change = second_avg - first_avg

                if score_change > 5:
                    trend = "improving"
                elif score_change < -5:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
                score_change = 0

            return {
                "content_id": content_id,
                "trend": trend,
                "trend_direction": "up" if score_change > 0 else "down" if score_change < 0 else "neutral",
                "avg_score": round(avg_score, 2),
                "score_change": round(score_change, 2),
                "data_points": len(scores),
                "period_days": days
            }

        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            raise

    async def identify_top_performers(
        self,
        all_content_performance: List[Dict],
        metric: str = "performance_score",
        limit: int = 5
    ) -> List[Dict]:
        """
        Identify top performing content

        Args:
            all_content_performance: Performance data for all content
            metric: Metric to rank by
            limit: Number of top performers to return

        Returns:
            List of top performers
        """
        try:
            sorted_content = sorted(
                all_content_performance,
                key=lambda x: x.get(metric, 0),
                reverse=True
            )

            return sorted_content[:limit]

        except Exception as e:
            logger.error(f"Error identifying top performers: {str(e)}")
            raise

    async def identify_underperformers(
        self,
        all_content_performance: List[Dict],
        threshold: int = 50,
        limit: int = 10
    ) -> List[Dict]:
        """
        Identify underperforming content needing attention

        Args:
            all_content_performance: Performance data for all content
            threshold: Score below which content is underperforming
            limit: Number of underperformers to return

        Returns:
            List of underperformers
        """
        try:
            underperformers = [
                content for content in all_content_performance
                if content.get("performance_score", 0) < threshold
            ]

            sorted_underperformers = sorted(
                underperformers,
                key=lambda x: x.get("performance_score", 0)
            )

            return sorted_underperformers[:limit]

        except Exception as e:
            logger.error(f"Error identifying underperformers: {str(e)}")
            raise

    def calculate_roi(
        self,
        revenue: float,
        effort_hours: float,
        hourly_rate: float = 50.0
    ) -> Dict:
        """
        Calculate content ROI

        Args:
            revenue: Revenue generated
            effort_hours: Hours invested
            hourly_rate: Cost per hour

        Returns:
            ROI metrics
        """
        try:
            cost = effort_hours * hourly_rate
            profit = revenue - cost
            roi_percentage = (profit / cost * 100) if cost > 0 else 0

            return {
                "revenue": revenue,
                "cost": cost,
                "profit": profit,
                "roi_percentage": round(roi_percentage, 2),
                "effort_hours": effort_hours,
                "revenue_per_hour": round(revenue / effort_hours, 2) if effort_hours > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            raise
