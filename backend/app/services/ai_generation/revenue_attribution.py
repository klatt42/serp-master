"""
Revenue Attribution Tracker
Connect content performance to business revenue with attribution modeling
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class AttributionModel(str, Enum):
    """Attribution model types"""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"


class ConversionType(str, Enum):
    """Types of conversions to track"""
    PURCHASE = "purchase"
    SIGNUP = "signup"
    LEAD = "lead"
    TRIAL = "trial"
    DOWNLOAD = "download"
    CONTACT = "contact"


class RevenueAttributionTracker:
    """Track and attribute revenue to content"""

    def __init__(self):
        """Initialize revenue attribution tracker"""
        self.touchpoints = []
        self.conversions = []
        self.content_revenue = defaultdict(lambda: {
            "total_revenue": 0,
            "conversions": 0,
            "assisted_conversions": 0,
            "first_touch_conversions": 0,
            "last_touch_conversions": 0
        })

    async def track_touchpoint(
        self,
        user_id: str,
        content_id: str,
        session_id: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Track content touchpoint in user journey

        Args:
            user_id: User identifier
            content_id: Content identifier
            session_id: Session identifier
            timestamp: Touchpoint timestamp
            metadata: Additional metadata (source, campaign, etc.)

        Returns:
            Touchpoint record
        """
        try:
            touchpoint = {
                "touchpoint_id": f"tp_{len(self.touchpoints)}",
                "user_id": user_id,
                "content_id": content_id,
                "session_id": session_id,
                "timestamp": (timestamp or datetime.now()).isoformat(),
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat()
            }

            self.touchpoints.append(touchpoint)

            logger.info(f"Tracked touchpoint for user {user_id} on content {content_id}")
            return touchpoint

        except Exception as e:
            logger.error(f"Error tracking touchpoint: {str(e)}")
            raise

    async def track_conversion(
        self,
        user_id: str,
        conversion_type: str,
        revenue: float,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Track conversion and attribute to content

        Args:
            user_id: User identifier
            conversion_type: Type of conversion
            revenue: Revenue amount
            timestamp: Conversion timestamp
            metadata: Additional conversion data

        Returns:
            Conversion record with attribution
        """
        try:
            conversion_time = timestamp or datetime.now()

            # Get user's touchpoint journey
            user_journey = self._get_user_journey(user_id, conversion_time)

            if not user_journey:
                logger.warning(f"No touchpoints found for user {user_id}")
                user_journey = []

            # Calculate attribution using multiple models
            attribution = self._calculate_attribution(user_journey, revenue)

            conversion = {
                "conversion_id": f"conv_{len(self.conversions)}",
                "user_id": user_id,
                "conversion_type": conversion_type,
                "revenue": revenue,
                "timestamp": conversion_time.isoformat(),
                "touchpoint_count": len(user_journey),
                "attribution": attribution,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat()
            }

            self.conversions.append(conversion)

            # Update content revenue stats
            self._update_content_revenue(user_journey, revenue, attribution)

            logger.info(f"Tracked conversion: {conversion_type} - ${revenue}")
            return conversion

        except Exception as e:
            logger.error(f"Error tracking conversion: {str(e)}")
            raise

    def _get_user_journey(
        self,
        user_id: str,
        conversion_time: datetime,
        lookback_days: int = 30
    ) -> List[Dict]:
        """Get user's touchpoint journey leading to conversion"""
        cutoff_time = conversion_time - timedelta(days=lookback_days)

        journey = [
            tp for tp in self.touchpoints
            if tp["user_id"] == user_id
            and datetime.fromisoformat(tp["timestamp"]) <= conversion_time
            and datetime.fromisoformat(tp["timestamp"]) >= cutoff_time
        ]

        # Sort by timestamp
        journey.sort(key=lambda x: x["timestamp"])

        return journey

    def _calculate_attribution(
        self,
        journey: List[Dict],
        revenue: float
    ) -> Dict:
        """Calculate attribution using multiple models"""
        if not journey:
            return {
                AttributionModel.FIRST_TOUCH.value: {},
                AttributionModel.LAST_TOUCH.value: {},
                AttributionModel.LINEAR.value: {},
                AttributionModel.TIME_DECAY.value: {},
                AttributionModel.POSITION_BASED.value: {}
            }

        return {
            AttributionModel.FIRST_TOUCH.value: self._first_touch_attribution(journey, revenue),
            AttributionModel.LAST_TOUCH.value: self._last_touch_attribution(journey, revenue),
            AttributionModel.LINEAR.value: self._linear_attribution(journey, revenue),
            AttributionModel.TIME_DECAY.value: self._time_decay_attribution(journey, revenue),
            AttributionModel.POSITION_BASED.value: self._position_based_attribution(journey, revenue)
        }

    def _first_touch_attribution(self, journey: List[Dict], revenue: float) -> Dict:
        """First-touch attribution (100% to first touchpoint)"""
        if not journey:
            return {}

        first_content = journey[0]["content_id"]

        return {
            first_content: revenue
        }

    def _last_touch_attribution(self, journey: List[Dict], revenue: float) -> Dict:
        """Last-touch attribution (100% to last touchpoint)"""
        if not journey:
            return {}

        last_content = journey[-1]["content_id"]

        return {
            last_content: revenue
        }

    def _linear_attribution(self, journey: List[Dict], revenue: float) -> Dict:
        """Linear attribution (equal credit to all touchpoints)"""
        if not journey:
            return {}

        attribution = defaultdict(float)
        credit_per_touchpoint = revenue / len(journey)

        for touchpoint in journey:
            attribution[touchpoint["content_id"]] += credit_per_touchpoint

        return dict(attribution)

    def _time_decay_attribution(self, journey: List[Dict], revenue: float) -> Dict:
        """Time-decay attribution (more recent touchpoints get more credit)"""
        if not journey:
            return {}

        attribution = defaultdict(float)

        # Calculate decay factor (exponential decay with 7-day half-life)
        half_life_days = 7
        decay_constant = 0.693 / half_life_days  # ln(2) / half_life

        # Get conversion time (last touchpoint time)
        conversion_time = datetime.fromisoformat(journey[-1]["timestamp"])

        # Calculate weights
        weights = []
        for touchpoint in journey:
            tp_time = datetime.fromisoformat(touchpoint["timestamp"])
            days_before_conversion = (conversion_time - tp_time).days
            weight = 2 ** (-decay_constant * days_before_conversion)
            weights.append(weight)

        total_weight = sum(weights)

        # Distribute revenue based on weights
        for touchpoint, weight in zip(journey, weights):
            credit = revenue * (weight / total_weight)
            attribution[touchpoint["content_id"]] += credit

        return dict(attribution)

    def _position_based_attribution(self, journey: List[Dict], revenue: float) -> Dict:
        """Position-based attribution (40% first, 40% last, 20% middle)"""
        if not journey:
            return {}

        attribution = defaultdict(float)

        if len(journey) == 1:
            # Only one touchpoint gets 100%
            attribution[journey[0]["content_id"]] = revenue

        elif len(journey) == 2:
            # Two touchpoints: 50% each
            attribution[journey[0]["content_id"]] += revenue * 0.5
            attribution[journey[-1]["content_id"]] += revenue * 0.5

        else:
            # Multiple touchpoints: 40% first, 40% last, 20% split among middle
            attribution[journey[0]["content_id"]] += revenue * 0.4
            attribution[journey[-1]["content_id"]] += revenue * 0.4

            middle_credit = revenue * 0.2
            middle_touchpoints = journey[1:-1]
            credit_per_middle = middle_credit / len(middle_touchpoints)

            for touchpoint in middle_touchpoints:
                attribution[touchpoint["content_id"]] += credit_per_middle

        return dict(attribution)

    def _update_content_revenue(
        self,
        journey: List[Dict],
        revenue: float,
        attribution: Dict
    ) -> None:
        """Update content revenue statistics"""
        if not journey:
            return

        first_content = journey[0]["content_id"]
        last_content = journey[-1]["content_id"]

        # Update using linear attribution for main stats
        linear_attr = attribution.get(AttributionModel.LINEAR.value, {})

        for content_id, attributed_revenue in linear_attr.items():
            self.content_revenue[content_id]["total_revenue"] += attributed_revenue
            self.content_revenue[content_id]["conversions"] += (1 / len(linear_attr))

            # Track role in conversion
            if content_id == first_content:
                self.content_revenue[content_id]["first_touch_conversions"] += 1
            if content_id == last_content:
                self.content_revenue[content_id]["last_touch_conversions"] += 1
            if content_id != first_content and content_id != last_content:
                self.content_revenue[content_id]["assisted_conversions"] += 1

    async def get_content_attribution(
        self,
        content_id: str,
        attribution_model: str = AttributionModel.LINEAR.value,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get attribution data for specific content

        Args:
            content_id: Content identifier
            attribution_model: Attribution model to use
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Content attribution metrics
        """
        try:
            # Filter conversions by date if provided
            relevant_conversions = self.conversions

            if start_date or end_date:
                relevant_conversions = [
                    c for c in self.conversions
                    if self._is_in_date_range(
                        datetime.fromisoformat(c["timestamp"]),
                        start_date,
                        end_date
                    )
                ]

            # Calculate metrics for this content
            total_revenue = 0
            conversion_count = 0
            assisted_revenue = 0

            for conversion in relevant_conversions:
                model_attribution = conversion["attribution"].get(attribution_model, {})
                if content_id in model_attribution:
                    total_revenue += model_attribution[content_id]
                    conversion_count += 1

            # Get basic stats from stored data
            content_stats = self.content_revenue.get(content_id, {})

            return {
                "content_id": content_id,
                "attribution_model": attribution_model,
                "total_revenue": round(total_revenue, 2),
                "conversions": conversion_count,
                "avg_revenue_per_conversion": round(total_revenue / conversion_count, 2) if conversion_count > 0 else 0,
                "first_touch_conversions": content_stats.get("first_touch_conversions", 0),
                "last_touch_conversions": content_stats.get("last_touch_conversions", 0),
                "assisted_conversions": content_stats.get("assisted_conversions", 0),
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }

        except Exception as e:
            logger.error(f"Error getting content attribution: {str(e)}")
            raise

    def _is_in_date_range(
        self,
        date: datetime,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> bool:
        """Check if date is in specified range"""
        if start_date and date < start_date:
            return False
        if end_date and date > end_date:
            return False
        return True

    async def get_top_revenue_content(
        self,
        limit: int = 10,
        attribution_model: str = AttributionModel.LINEAR.value,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Get top revenue-generating content"""
        try:
            # Calculate revenue for all content
            content_revenues = {}

            for content_id in self.content_revenue.keys():
                attribution_data = await self.get_content_attribution(
                    content_id,
                    attribution_model,
                    start_date,
                    end_date
                )
                content_revenues[content_id] = attribution_data

            # Sort by total revenue
            sorted_content = sorted(
                content_revenues.items(),
                key=lambda x: x[1]["total_revenue"],
                reverse=True
            )

            return [
                {
                    "rank": idx + 1,
                    "content_id": content_id,
                    **data
                }
                for idx, (content_id, data) in enumerate(sorted_content[:limit])
            ]

        except Exception as e:
            logger.error(f"Error getting top revenue content: {str(e)}")
            raise

    async def calculate_roi(
        self,
        content_id: str,
        production_cost: float,
        attribution_model: str = AttributionModel.LINEAR.value
    ) -> Dict:
        """
        Calculate ROI for content

        Args:
            content_id: Content identifier
            production_cost: Cost to produce content
            attribution_model: Attribution model to use

        Returns:
            ROI metrics
        """
        try:
            attribution_data = await self.get_content_attribution(
                content_id,
                attribution_model
            )

            total_revenue = attribution_data["total_revenue"]
            roi = ((total_revenue - production_cost) / production_cost * 100) if production_cost > 0 else 0

            return {
                "content_id": content_id,
                "total_revenue": total_revenue,
                "production_cost": production_cost,
                "profit": total_revenue - production_cost,
                "roi_percentage": round(roi, 2),
                "payback_achieved": total_revenue >= production_cost,
                "conversions": attribution_data["conversions"],
                "revenue_per_dollar_spent": round(total_revenue / production_cost, 2) if production_cost > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            raise

    async def analyze_conversion_paths(
        self,
        min_touchpoints: int = 2,
        limit: int = 20
    ) -> List[Dict]:
        """
        Analyze common conversion paths

        Args:
            min_touchpoints: Minimum touchpoints to include
            limit: Maximum paths to return

        Returns:
            Common conversion paths with metrics
        """
        try:
            paths = defaultdict(lambda: {
                "count": 0,
                "total_revenue": 0,
                "avg_revenue": 0,
                "touchpoint_count": 0
            })

            for conversion in self.conversions:
                user_id = conversion["user_id"]
                conversion_time = datetime.fromisoformat(conversion["timestamp"])

                # Get journey
                journey = self._get_user_journey(user_id, conversion_time)

                if len(journey) >= min_touchpoints:
                    # Create path signature
                    path_signature = " -> ".join([tp["content_id"] for tp in journey])

                    paths[path_signature]["count"] += 1
                    paths[path_signature]["total_revenue"] += conversion["revenue"]
                    paths[path_signature]["touchpoint_count"] = len(journey)

            # Calculate averages and sort
            path_list = []
            for path, data in paths.items():
                data["avg_revenue"] = data["total_revenue"] / data["count"]
                data["path"] = path
                path_list.append(data)

            # Sort by count (most common paths)
            path_list.sort(key=lambda x: x["count"], reverse=True)

            return path_list[:limit]

        except Exception as e:
            logger.error(f"Error analyzing conversion paths: {str(e)}")
            raise

    async def get_customer_lifetime_value(
        self,
        user_id: str
    ) -> Dict:
        """Calculate customer lifetime value"""
        try:
            user_conversions = [
                c for c in self.conversions
                if c["user_id"] == user_id
            ]

            if not user_conversions:
                return {
                    "user_id": user_id,
                    "lifetime_value": 0,
                    "conversion_count": 0,
                    "avg_order_value": 0,
                    "first_purchase": None,
                    "last_purchase": None
                }

            total_revenue = sum(c["revenue"] for c in user_conversions)
            conversion_count = len(user_conversions)

            # Sort by timestamp
            user_conversions.sort(key=lambda x: x["timestamp"])

            return {
                "user_id": user_id,
                "lifetime_value": round(total_revenue, 2),
                "conversion_count": conversion_count,
                "avg_order_value": round(total_revenue / conversion_count, 2),
                "first_purchase": user_conversions[0]["timestamp"],
                "last_purchase": user_conversions[-1]["timestamp"],
                "customer_age_days": (
                    datetime.fromisoformat(user_conversions[-1]["timestamp"]) -
                    datetime.fromisoformat(user_conversions[0]["timestamp"])
                ).days
            }

        except Exception as e:
            logger.error(f"Error calculating CLV: {str(e)}")
            raise

    def get_attribution_summary(self) -> Dict:
        """Get overall attribution statistics"""
        try:
            total_revenue = sum(c["revenue"] for c in self.conversions)
            total_conversions = len(self.conversions)

            # Calculate average touchpoints
            touchpoint_counts = [c["touchpoint_count"] for c in self.conversions if c["touchpoint_count"] > 0]
            avg_touchpoints = statistics.mean(touchpoint_counts) if touchpoint_counts else 0

            # Top content by each attribution model
            top_by_model = {}
            for model in AttributionModel:
                model_revenue = defaultdict(float)
                for conversion in self.conversions:
                    model_attr = conversion["attribution"].get(model.value, {})
                    for content_id, revenue in model_attr.items():
                        model_revenue[content_id] += revenue

                if model_revenue:
                    top_content = max(model_revenue.items(), key=lambda x: x[1])
                    top_by_model[model.value] = {
                        "content_id": top_content[0],
                        "revenue": round(top_content[1], 2)
                    }

            return {
                "total_revenue": round(total_revenue, 2),
                "total_conversions": total_conversions,
                "avg_revenue_per_conversion": round(total_revenue / total_conversions, 2) if total_conversions > 0 else 0,
                "total_touchpoints": len(self.touchpoints),
                "unique_users": len(set(c["user_id"] for c in self.conversions)),
                "avg_touchpoints_per_conversion": round(avg_touchpoints, 1),
                "top_content_by_model": top_by_model
            }

        except Exception as e:
            logger.error(f"Error getting attribution summary: {str(e)}")
            raise
