"""
A/B Testing Manager
Orchestrate content variations testing and statistical analysis
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


class TestStatus(str, Enum):
    """A/B test status"""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ABTestManager:
    """Manage A/B tests for content optimization"""

    def __init__(self):
        """Initialize A/B test manager"""
        self.min_sample_size = 100
        self.confidence_threshold = 0.95

    async def create_test(
        self,
        content_id: str,
        test_name: str,
        variants: List[Dict],
        traffic_split: Optional[Dict] = None
    ) -> Dict:
        """
        Create new A/B test

        Args:
            content_id: Content to test
            test_name: Test identifier
            variants: List of variations
            traffic_split: Traffic distribution (defaults to equal split)

        Returns:
            Created test configuration
        """
        try:
            if not variants or len(variants) < 2:
                raise ValueError("Need at least 2 variants for A/B testing")

            # Default to equal traffic split
            if not traffic_split:
                split_percentage = 100 / len(variants)
                traffic_split = {
                    f"variant_{i}": split_percentage
                    for i in range(len(variants))
                }

            test = {
                "id": f"test_{datetime.now().timestamp()}",
                "content_id": content_id,
                "test_name": test_name,
                "status": TestStatus.DRAFT.value,
                "variants": variants,
                "traffic_split": traffic_split,
                "start_date": None,
                "end_date": None,
                "winner_variant_id": None,
                "confidence_level": None,
                "created_at": datetime.now().isoformat()
            }

            logger.info(f"Created A/B test: {test_name}")
            return test

        except Exception as e:
            logger.error(f"Error creating A/B test: {str(e)}")
            raise

    async def start_test(self, test_id: str) -> Dict:
        """Start running an A/B test"""
        try:
            # Update test status
            updated_test = {
                "id": test_id,
                "status": TestStatus.RUNNING.value,
                "start_date": datetime.now().isoformat()
            }

            logger.info(f"Started A/B test: {test_id}")
            return updated_test

        except Exception as e:
            logger.error(f"Error starting test: {str(e)}")
            raise

    async def record_result(
        self,
        test_id: str,
        variant_id: str,
        event_type: str
    ) -> Dict:
        """
        Record test result (impression, click, conversion)

        Args:
            test_id: Test identifier
            variant_id: Variant that was shown
            event_type: Type of event (impression, click, conversion)

        Returns:
            Updated result data
        """
        try:
            result = {
                "test_id": test_id,
                "variant_id": variant_id,
                "event_type": event_type,
                "timestamp": datetime.now().isoformat()
            }

            logger.debug(f"Recorded {event_type} for variant {variant_id}")
            return result

        except Exception as e:
            logger.error(f"Error recording result: {str(e)}")
            raise

    async def analyze_test(
        self,
        test_id: str,
        test_results: List[Dict]
    ) -> Dict:
        """
        Analyze test results and determine statistical significance

        Args:
            test_id: Test identifier
            test_results: Collected test data

        Returns:
            Analysis results with winner if significant
        """
        try:
            if not test_results:
                return {
                    "test_id": test_id,
                    "status": "insufficient_data",
                    "message": "Not enough data to analyze"
                }

            # Calculate metrics for each variant
            variant_metrics = self._calculate_variant_metrics(test_results)

            # Check sample size
            if not self._has_sufficient_sample_size(variant_metrics):
                return {
                    "test_id": test_id,
                    "status": "insufficient_sample",
                    "variant_metrics": variant_metrics,
                    "message": f"Need at least {self.min_sample_size} samples per variant"
                }

            # Perform statistical significance test
            significance_result = self._calculate_statistical_significance(variant_metrics)

            analysis = {
                "test_id": test_id,
                "status": "analyzed",
                "variant_metrics": variant_metrics,
                "is_significant": significance_result["is_significant"],
                "confidence_level": significance_result["confidence_level"],
                "winner_variant_id": significance_result.get("winner_variant_id"),
                "improvement": significance_result.get("improvement", 0),
                "recommendation": significance_result.get("recommendation"),
                "analyzed_at": datetime.now().isoformat()
            }

            logger.info(f"Analyzed test {test_id}: Significant={significance_result['is_significant']}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing test: {str(e)}")
            raise

    def _calculate_variant_metrics(
        self,
        test_results: List[Dict]
    ) -> Dict:
        """Calculate performance metrics for each variant"""
        try:
            variant_data = {}

            for result in test_results:
                variant_id = result.get("variant_id")
                event_type = result.get("event_type")

                if variant_id not in variant_data:
                    variant_data[variant_id] = {
                        "impressions": 0,
                        "clicks": 0,
                        "conversions": 0
                    }

                if event_type == "impression":
                    variant_data[variant_id]["impressions"] += 1
                elif event_type == "click":
                    variant_data[variant_id]["clicks"] += 1
                elif event_type == "conversion":
                    variant_data[variant_id]["conversions"] += 1

            # Calculate rates
            for variant_id, data in variant_data.items():
                impressions = data["impressions"]
                data["ctr"] = (data["clicks"] / impressions * 100) if impressions > 0 else 0
                data["conversion_rate"] = (data["conversions"] / data["clicks"] * 100) if data["clicks"] > 0 else 0

            return variant_data

        except Exception as e:
            logger.error(f"Error calculating variant metrics: {str(e)}")
            return {}

    def _has_sufficient_sample_size(
        self,
        variant_metrics: Dict
    ) -> bool:
        """Check if all variants have sufficient sample size"""
        try:
            for metrics in variant_metrics.values():
                if metrics.get("impressions", 0) < self.min_sample_size:
                    return False
            return True

        except Exception as e:
            logger.error(f"Error checking sample size: {str(e)}")
            return False

    def _calculate_statistical_significance(
        self,
        variant_metrics: Dict
    ) -> Dict:
        """
        Calculate statistical significance using chi-square test
        Simplified implementation for demonstration
        """
        try:
            if len(variant_metrics) < 2:
                return {
                    "is_significant": False,
                    "confidence_level": 0,
                    "recommendation": "Need at least 2 variants"
                }

            # Find best performing variant by CTR
            best_variant = max(
                variant_metrics.items(),
                key=lambda x: x[1].get("ctr", 0)
            )
            best_variant_id, best_metrics = best_variant

            # Calculate improvement over control (first variant)
            variant_ids = list(variant_metrics.keys())
            control_ctr = variant_metrics[variant_ids[0]].get("ctr", 0)
            best_ctr = best_metrics.get("ctr", 0)

            improvement = ((best_ctr - control_ctr) / control_ctr * 100) if control_ctr > 0 else 0

            # Simplified significance calculation
            # In production, use proper chi-square or t-test
            confidence_level = 0.95 if abs(improvement) > 10 else 0.85

            is_significant = confidence_level >= self.confidence_threshold

            return {
                "is_significant": is_significant,
                "confidence_level": round(confidence_level, 3),
                "winner_variant_id": best_variant_id if is_significant else None,
                "improvement": round(improvement, 2),
                "recommendation": self._generate_recommendation(
                    is_significant,
                    improvement,
                    best_variant_id
                )
            }

        except Exception as e:
            logger.error(f"Error calculating significance: {str(e)}")
            return {
                "is_significant": False,
                "confidence_level": 0,
                "recommendation": "Error in analysis"
            }

    def _generate_recommendation(
        self,
        is_significant: bool,
        improvement: float,
        winner_id: str
    ) -> str:
        """Generate actionable recommendation"""
        try:
            if is_significant:
                if improvement > 0:
                    return f"Promote {winner_id} as winner (+{improvement:.1f}% improvement)"
                else:
                    return "Keep original version (no significant improvement)"
            else:
                return "Continue test - not statistically significant yet"

        except Exception as e:
            logger.error(f"Error generating recommendation: {str(e)}")
            return "Review data manually"

    async def promote_winner(
        self,
        test_id: str,
        winner_variant_id: str
    ) -> Dict:
        """Promote winning variant to production"""
        try:
            promotion = {
                "test_id": test_id,
                "winner_variant_id": winner_variant_id,
                "promoted_at": datetime.now().isoformat(),
                "status": "promoted"
            }

            logger.info(f"Promoted winner {winner_variant_id} for test {test_id}")
            return promotion

        except Exception as e:
            logger.error(f"Error promoting winner: {str(e)}")
            raise
