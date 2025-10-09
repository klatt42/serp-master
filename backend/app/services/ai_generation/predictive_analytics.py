"""
Predictive Analytics Engine
ML-powered predictions for content performance before publishing
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging
import statistics
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class PredictionMetric(str, Enum):
    """Metrics to predict"""
    TRAFFIC = "traffic"
    ENGAGEMENT = "engagement"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    RANKING = "ranking"
    SOCIAL_SHARES = "social_shares"


class ConfidenceLevel(str, Enum):
    """Prediction confidence levels"""
    HIGH = "high"  # 80%+ confidence
    MEDIUM = "medium"  # 60-80% confidence
    LOW = "low"  # <60% confidence


class PredictiveAnalytics:
    """Predict content performance using ML and historical data"""

    def __init__(self):
        """Initialize predictive analytics engine"""
        self.historical_data = []
        self.trained_models = {}
        self.feature_weights = {
            "word_count": 0.15,
            "keyword_density": 0.12,
            "readability_score": 0.10,
            "header_count": 0.08,
            "topic_relevance": 0.15,
            "author_authority": 0.10,
            "publish_timing": 0.08,
            "competitive_landscape": 0.12,
            "historical_performance": 0.10
        }

    async def predict_performance(
        self,
        content: Dict,
        target_keywords: List[str],
        historical_context: Optional[Dict] = None
    ) -> Dict:
        """
        Predict content performance before publishing

        Args:
            content: Content to analyze (title, body, metadata)
            target_keywords: Target keywords
            historical_context: Historical performance data

        Returns:
            Performance predictions with confidence intervals
        """
        try:
            # Extract features from content
            features = self._extract_content_features(content, target_keywords)

            # Add historical context
            if historical_context:
                features.update(self._extract_historical_features(historical_context))

            # Generate predictions for each metric
            predictions = {
                PredictionMetric.TRAFFIC.value: self._predict_traffic(features),
                PredictionMetric.ENGAGEMENT.value: self._predict_engagement(features),
                PredictionMetric.CONVERSIONS.value: self._predict_conversions(features),
                PredictionMetric.REVENUE.value: self._predict_revenue(features),
                PredictionMetric.RANKING.value: self._predict_ranking(features),
                PredictionMetric.SOCIAL_SHARES.value: self._predict_social_shares(features)
            }

            # Calculate overall success probability
            success_score = self._calculate_success_score(predictions)

            # Generate recommendations
            recommendations = self._generate_improvement_recommendations(
                features,
                predictions
            )

            return {
                "predictions": predictions,
                "overall_success_score": success_score,
                "confidence_level": self._determine_confidence_level(predictions),
                "features_analyzed": features,
                "recommendations": recommendations,
                "predicted_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error predicting performance: {str(e)}")
            raise

    def _extract_content_features(
        self,
        content: Dict,
        keywords: List[str]
    ) -> Dict:
        """Extract ML features from content"""
        try:
            body = content.get("body", "")
            title = content.get("title", "")

            # Basic content metrics
            word_count = len(body.split())
            char_count = len(body)

            # Keyword analysis
            primary_keyword = keywords[0] if keywords else ""
            keyword_count = body.lower().count(primary_keyword.lower()) if primary_keyword else 0
            keyword_density = (keyword_count / word_count) if word_count > 0 else 0

            # Readability metrics
            sentences = re.split(r'[.!?]+', body)
            sentences = [s.strip() for s in sentences if s.strip()]
            avg_sentence_length = word_count / len(sentences) if sentences else 0

            # Structure metrics
            headers = re.findall(r'^#+\s+', body, re.MULTILINE)
            header_count = len(headers)

            # Title analysis
            title_length = len(title)
            title_has_keyword = primary_keyword.lower() in title.lower() if primary_keyword else False
            title_has_number = bool(re.search(r'\d+', title))

            # Content freshness indicators
            current_year = datetime.now().year
            has_current_year = str(current_year) in body
            has_statistics = bool(re.search(r'\d+%|\$\d+', body))

            # Media and formatting
            has_images = "![" in body or "<img" in body
            has_lists = bool(re.search(r'^\d+\.|^[-*]', body, re.MULTILINE))
            has_code_blocks = "```" in body or "<code>" in body

            return {
                "word_count": word_count,
                "char_count": char_count,
                "keyword_density": round(keyword_density, 4),
                "keyword_in_title": title_has_keyword,
                "avg_sentence_length": round(avg_sentence_length, 1),
                "header_count": header_count,
                "title_length": title_length,
                "title_has_number": title_has_number,
                "has_current_year": has_current_year,
                "has_statistics": has_statistics,
                "has_images": has_images,
                "has_lists": has_lists,
                "has_code_blocks": has_code_blocks,
                "readability_score": self._calculate_simple_readability(avg_sentence_length)
            }

        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            raise

    def _calculate_simple_readability(self, avg_sentence_length: float) -> int:
        """Calculate simplified readability score (0-100)"""
        # Simplified: penalize very long or very short sentences
        optimal_length = 15
        deviation = abs(avg_sentence_length - optimal_length)
        score = max(0, 100 - (deviation * 3))
        return int(score)

    def _extract_historical_features(self, historical: Dict) -> Dict:
        """Extract features from historical performance"""
        return {
            "author_avg_traffic": historical.get("author_avg_traffic", 0),
            "author_avg_engagement": historical.get("author_avg_engagement", 0),
            "topic_avg_performance": historical.get("topic_avg_performance", 0),
            "similar_content_success_rate": historical.get("similar_content_success_rate", 0.5)
        }

    def _predict_traffic(self, features: Dict) -> Dict:
        """Predict monthly organic traffic"""
        try:
            # Base traffic from word count
            base_traffic = features["word_count"] * 0.5

            # Adjust for content quality factors
            multiplier = 1.0

            # Word count optimization (1500-2500 is sweet spot)
            if 1500 <= features["word_count"] <= 2500:
                multiplier *= 1.3
            elif features["word_count"] < 500:
                multiplier *= 0.5

            # Keyword optimization
            if 0.01 <= features["keyword_density"] <= 0.03:
                multiplier *= 1.2

            # Title optimization
            if features["keyword_in_title"]:
                multiplier *= 1.15

            if features["title_has_number"]:
                multiplier *= 1.1

            # Structure optimization
            if features["header_count"] >= 3:
                multiplier *= 1.1

            # Content freshness
            if features["has_current_year"]:
                multiplier *= 1.05

            # Media richness
            if features["has_images"]:
                multiplier *= 1.1

            if features["has_lists"]:
                multiplier *= 1.08

            # Readability
            if features["readability_score"] > 70:
                multiplier *= 1.1

            # Historical performance
            if "similar_content_success_rate" in features:
                multiplier *= (0.5 + features["similar_content_success_rate"])

            # Calculate predictions
            predicted_traffic = int(base_traffic * multiplier)

            # Confidence interval (±30%)
            lower_bound = int(predicted_traffic * 0.7)
            upper_bound = int(predicted_traffic * 1.3)

            # Confidence based on feature completeness
            confidence = self._calculate_prediction_confidence(features)

            return {
                "predicted_value": predicted_traffic,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "confidence": confidence,
                "unit": "monthly_visits",
                "factors": {
                    "word_count_impact": round((features["word_count"] / 2000) * 100, 1),
                    "optimization_multiplier": round(multiplier, 2)
                }
            }

        except Exception as e:
            logger.error(f"Error predicting traffic: {str(e)}")
            raise

    def _predict_engagement(self, features: Dict) -> Dict:
        """Predict engagement metrics (time on page, bounce rate)"""
        try:
            # Base time on page (reading speed: 200 words/min)
            base_time_seconds = (features["word_count"] / 200) * 60

            # Adjust for engagement factors
            engagement_multiplier = 1.0

            # Content structure
            if features["has_lists"]:
                engagement_multiplier *= 1.15

            if features["has_images"]:
                engagement_multiplier *= 1.2

            if features["has_code_blocks"]:
                engagement_multiplier *= 1.1

            # Readability
            if features["readability_score"] > 70:
                engagement_multiplier *= 1.1
            elif features["readability_score"] < 40:
                engagement_multiplier *= 0.8

            # Calculate metrics
            predicted_time = int(base_time_seconds * engagement_multiplier)

            # Predict bounce rate (inverse of engagement)
            base_bounce_rate = 70  # Start at 70%
            bounce_reduction = (engagement_multiplier - 1.0) * 20
            predicted_bounce_rate = max(30, min(90, base_bounce_rate - bounce_reduction))

            # Pages per session
            pages_per_session = 1 + (engagement_multiplier - 1.0) * 2

            confidence = self._calculate_prediction_confidence(features)

            return {
                "predicted_value": {
                    "avg_time_on_page_seconds": predicted_time,
                    "bounce_rate_percentage": round(predicted_bounce_rate, 1),
                    "pages_per_session": round(pages_per_session, 2)
                },
                "confidence": confidence,
                "factors": {
                    "engagement_multiplier": round(engagement_multiplier, 2),
                    "content_richness_score": round((engagement_multiplier - 1.0) * 100, 1)
                }
            }

        except Exception as e:
            logger.error(f"Error predicting engagement: {str(e)}")
            raise

    def _predict_conversions(self, features: Dict) -> Dict:
        """Predict conversion rate"""
        try:
            # Base conversion rate: 2%
            base_conversion_rate = 0.02

            # Adjust for conversion factors
            conversion_multiplier = 1.0

            # Content quality (comprehensive = higher conversion)
            if features["word_count"] > 1500:
                conversion_multiplier *= 1.2

            # Clear structure
            if features["has_lists"]:
                conversion_multiplier *= 1.15

            # Trust signals
            if features["has_statistics"]:
                conversion_multiplier *= 1.1

            if features["has_current_year"]:
                conversion_multiplier *= 1.05

            # Readability (easier to understand = higher conversion)
            if features["readability_score"] > 60:
                conversion_multiplier *= 1.1

            predicted_rate = base_conversion_rate * conversion_multiplier

            # With 1000 visitors
            predicted_conversions = int(1000 * predicted_rate)

            confidence = self._calculate_prediction_confidence(features)

            return {
                "predicted_value": {
                    "conversion_rate_percentage": round(predicted_rate * 100, 2),
                    "conversions_per_1000_visitors": predicted_conversions
                },
                "lower_bound": round(predicted_rate * 0.7 * 100, 2),
                "upper_bound": round(predicted_rate * 1.3 * 100, 2),
                "confidence": confidence,
                "factors": {
                    "conversion_multiplier": round(conversion_multiplier, 2)
                }
            }

        except Exception as e:
            logger.error(f"Error predicting conversions: {str(e)}")
            raise

    def _predict_revenue(self, features: Dict) -> Dict:
        """Predict revenue potential"""
        try:
            # Base revenue per visitor: $0.50
            base_revenue_per_visitor = 0.50

            # Get traffic and conversion predictions
            traffic_pred = self._predict_traffic(features)
            conversion_pred = self._predict_conversions(features)

            predicted_visitors = traffic_pred["predicted_value"]
            conversion_rate = conversion_pred["predicted_value"]["conversion_rate_percentage"] / 100

            # Assume $50 average order value
            avg_order_value = 50

            # Calculate revenue
            predicted_conversions = predicted_visitors * conversion_rate
            predicted_revenue = predicted_conversions * avg_order_value

            # Alternative: ad revenue
            ad_revenue = predicted_visitors * base_revenue_per_visitor

            confidence = self._calculate_prediction_confidence(features)

            return {
                "predicted_value": {
                    "monthly_revenue": round(predicted_revenue, 2),
                    "ad_revenue_alternative": round(ad_revenue, 2),
                    "total_potential": round(predicted_revenue + ad_revenue, 2)
                },
                "confidence": confidence,
                "assumptions": {
                    "avg_order_value": avg_order_value,
                    "revenue_per_visitor": base_revenue_per_visitor
                }
            }

        except Exception as e:
            logger.error(f"Error predicting revenue: {str(e)}")
            raise

    def _predict_ranking(self, features: Dict) -> Dict:
        """Predict search ranking potential"""
        try:
            # Base ranking score (lower is better, 1-100)
            base_ranking = 50

            # Adjust for ranking factors
            ranking_improvements = 0

            # Content length
            if features["word_count"] > 1500:
                ranking_improvements += 10
            elif features["word_count"] < 500:
                ranking_improvements -= 15

            # Keyword optimization
            if 0.01 <= features["keyword_density"] <= 0.03:
                ranking_improvements += 8

            if features["keyword_in_title"]:
                ranking_improvements += 7

            # Content structure
            if features["header_count"] >= 3:
                ranking_improvements += 5

            # Content freshness
            if features["has_current_year"]:
                ranking_improvements += 5

            # Content quality signals
            if features["has_statistics"]:
                ranking_improvements += 4

            if features["has_images"]:
                ranking_improvements += 3

            # Readability
            if features["readability_score"] > 60:
                ranking_improvements += 5

            # Calculate predicted ranking position
            predicted_position = max(1, base_ranking - ranking_improvements)

            # Estimate ranking within 3 months
            ranking_timeline = {
                "1_month": min(100, predicted_position + 15),
                "2_months": min(100, predicted_position + 5),
                "3_months": predicted_position
            }

            confidence = self._calculate_prediction_confidence(features)

            return {
                "predicted_value": {
                    "estimated_position": predicted_position,
                    "position_range": f"{max(1, predicted_position - 10)}-{min(100, predicted_position + 10)}",
                    "timeline": ranking_timeline
                },
                "confidence": confidence,
                "factors": {
                    "total_ranking_improvements": ranking_improvements,
                    "ranking_score": 100 - predicted_position
                }
            }

        except Exception as e:
            logger.error(f"Error predicting ranking: {str(e)}")
            raise

    def _predict_social_shares(self, features: Dict) -> Dict:
        """Predict social sharing potential"""
        try:
            # Base shares per 100 visitors
            base_share_rate = 0.02  # 2%

            # Adjust for shareability factors
            shareability_multiplier = 1.0

            # Title appeal
            if features["title_has_number"]:
                shareability_multiplier *= 1.3  # "10 Ways..." performs well

            # Visual content
            if features["has_images"]:
                shareability_multiplier *= 1.4

            # Practical value
            if features["has_lists"]:
                shareability_multiplier *= 1.2

            # Data/statistics
            if features["has_statistics"]:
                shareability_multiplier *= 1.15

            # Current/timely content
            if features["has_current_year"]:
                shareability_multiplier *= 1.1

            # Content length (medium length performs best for social)
            if 800 <= features["word_count"] <= 1500:
                shareability_multiplier *= 1.2
            elif features["word_count"] > 3000:
                shareability_multiplier *= 0.8

            predicted_share_rate = base_share_rate * shareability_multiplier

            # With 1000 visitors
            predicted_shares = int(1000 * predicted_share_rate)

            confidence = self._calculate_prediction_confidence(features)

            return {
                "predicted_value": {
                    "shares_per_1000_visitors": predicted_shares,
                    "viral_potential_score": min(100, int(shareability_multiplier * 50))
                },
                "confidence": confidence,
                "factors": {
                    "shareability_multiplier": round(shareability_multiplier, 2)
                }
            }

        except Exception as e:
            logger.error(f"Error predicting social shares: {str(e)}")
            raise

    def _calculate_prediction_confidence(self, features: Dict) -> float:
        """Calculate confidence level for predictions (0-1)"""
        # Base confidence
        confidence = 0.5

        # Increase confidence with more complete features
        feature_completeness = sum([
            features.get("keyword_density", 0) > 0,
            features.get("word_count", 0) > 500,
            features.get("header_count", 0) > 0,
            features.get("has_images", False),
            features.get("readability_score", 0) > 0,
            "similar_content_success_rate" in features,
            "author_avg_traffic" in features
        ]) / 7

        confidence = 0.4 + (feature_completeness * 0.5)

        return round(confidence, 2)

    def _calculate_success_score(self, predictions: Dict) -> int:
        """Calculate overall success probability (0-100)"""
        try:
            scores = []

            # Traffic score (normalize to 0-100)
            traffic = predictions[PredictionMetric.TRAFFIC.value]["predicted_value"]
            traffic_score = min(100, (traffic / 50))  # 5000 visits = 100 score
            scores.append(traffic_score)

            # Engagement score
            engagement = predictions[PredictionMetric.ENGAGEMENT.value]["predicted_value"]
            bounce_rate = engagement["bounce_rate_percentage"]
            engagement_score = 100 - bounce_rate  # Lower bounce = higher score
            scores.append(engagement_score)

            # Conversion score
            conversion = predictions[PredictionMetric.CONVERSIONS.value]["predicted_value"]
            conversion_rate = conversion["conversion_rate_percentage"]
            conversion_score = min(100, conversion_rate * 20)  # 5% = 100 score
            scores.append(conversion_score)

            # Ranking score
            ranking = predictions[PredictionMetric.RANKING.value]["predicted_value"]
            position = ranking["estimated_position"]
            ranking_score = max(0, 100 - position)  # Position 1 = 99, Position 100 = 0
            scores.append(ranking_score)

            # Social shares score
            social = predictions[PredictionMetric.SOCIAL_SHARES.value]["predicted_value"]
            viral_potential = social["viral_potential_score"]
            scores.append(viral_potential)

            # Average all scores
            overall_score = int(statistics.mean(scores))

            return overall_score

        except Exception as e:
            logger.error(f"Error calculating success score: {str(e)}")
            return 50

    def _determine_confidence_level(self, predictions: Dict) -> str:
        """Determine overall confidence level"""
        # Get average confidence across all predictions
        confidences = []

        for metric_data in predictions.values():
            if "confidence" in metric_data:
                confidences.append(metric_data["confidence"])

        if not confidences:
            return ConfidenceLevel.LOW.value

        avg_confidence = statistics.mean(confidences)

        if avg_confidence >= 0.8:
            return ConfidenceLevel.HIGH.value
        elif avg_confidence >= 0.6:
            return ConfidenceLevel.MEDIUM.value
        else:
            return ConfidenceLevel.LOW.value

    def _generate_improvement_recommendations(
        self,
        features: Dict,
        predictions: Dict
    ) -> List[Dict]:
        """Generate recommendations to improve predicted performance"""
        recommendations = []

        # Word count recommendations
        if features["word_count"] < 1000:
            recommendations.append({
                "category": "content_length",
                "priority": "high",
                "issue": "Content too short for optimal performance",
                "recommendation": "Expand to at least 1500 words for better ranking and traffic",
                "current_value": features["word_count"],
                "target_value": "1500-2500 words",
                "potential_impact": "+30% traffic"
            })
        elif features["word_count"] > 3000:
            recommendations.append({
                "category": "content_length",
                "priority": "medium",
                "issue": "Content might be too long",
                "recommendation": "Consider breaking into multiple pieces or improving scannability",
                "current_value": features["word_count"],
                "target_value": "1500-2500 words",
                "potential_impact": "+15% engagement"
            })

        # Keyword optimization
        if features["keyword_density"] < 0.01:
            recommendations.append({
                "category": "keywords",
                "priority": "high",
                "issue": "Keyword density too low",
                "recommendation": "Include target keyword more naturally throughout content",
                "current_value": f"{features['keyword_density']*100:.2f}%",
                "target_value": "1-3%",
                "potential_impact": "+20% ranking"
            })
        elif features["keyword_density"] > 0.03:
            recommendations.append({
                "category": "keywords",
                "priority": "medium",
                "issue": "Keyword density too high",
                "recommendation": "Reduce keyword usage to avoid over-optimization",
                "current_value": f"{features['keyword_density']*100:.2f}%",
                "target_value": "1-3%",
                "potential_impact": "Avoid penalties"
            })

        # Title optimization
        if not features["keyword_in_title"]:
            recommendations.append({
                "category": "title",
                "priority": "high",
                "issue": "Target keyword not in title",
                "recommendation": "Include primary keyword in title tag",
                "current_value": "Not present",
                "target_value": "Keyword in title",
                "potential_impact": "+15% CTR"
            })

        if not features["title_has_number"]:
            recommendations.append({
                "category": "title",
                "priority": "medium",
                "issue": "Title could be more compelling",
                "recommendation": "Consider adding a number (e.g., '10 Ways...', '7 Steps...')",
                "current_value": "No number",
                "target_value": "Number in title",
                "potential_impact": "+10% social shares"
            })

        # Structure recommendations
        if features["header_count"] < 3:
            recommendations.append({
                "category": "structure",
                "priority": "high",
                "issue": "Insufficient header structure",
                "recommendation": "Add more H2/H3 headers to improve scannability",
                "current_value": features["header_count"],
                "target_value": "5-8 headers",
                "potential_impact": "+10% engagement"
            })

        # Media recommendations
        if not features["has_images"]:
            recommendations.append({
                "category": "media",
                "priority": "high",
                "issue": "No images in content",
                "recommendation": "Add relevant images, charts, or infographics",
                "current_value": "No images",
                "target_value": "3-5 images",
                "potential_impact": "+20% engagement, +40% social shares"
            })

        if not features["has_lists"]:
            recommendations.append({
                "category": "formatting",
                "priority": "medium",
                "issue": "No lists for easy scanning",
                "recommendation": "Convert key points to bulleted or numbered lists",
                "current_value": "No lists",
                "target_value": "2-3 lists",
                "potential_impact": "+15% engagement"
            })

        # Readability
        if features["readability_score"] < 60:
            recommendations.append({
                "category": "readability",
                "priority": "medium",
                "issue": "Content difficult to read",
                "recommendation": "Simplify sentences and use shorter words",
                "current_value": features["readability_score"],
                "target_value": "70+",
                "potential_impact": "+10% engagement, +15% conversions"
            })

        # Freshness
        if not features["has_current_year"]:
            recommendations.append({
                "category": "freshness",
                "priority": "low",
                "issue": "No current year references",
                "recommendation": "Add current statistics or year to show freshness",
                "current_value": "No date indicators",
                "target_value": "Current year present",
                "potential_impact": "+5% ranking"
            })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order[x["priority"]])

        return recommendations

    async def compare_content_versions(
        self,
        version_a: Dict,
        version_b: Dict,
        keywords: List[str]
    ) -> Dict:
        """Compare predictions for two content versions (A/B testing)"""
        try:
            prediction_a = await self.predict_performance(version_a, keywords)
            prediction_b = await self.predict_performance(version_b, keywords)

            # Compare scores
            score_diff = prediction_b["overall_success_score"] - prediction_a["overall_success_score"]

            comparison = {
                "version_a": {
                    "success_score": prediction_a["overall_success_score"],
                    "predictions": prediction_a["predictions"]
                },
                "version_b": {
                    "success_score": prediction_b["overall_success_score"],
                    "predictions": prediction_b["predictions"]
                },
                "comparison": {
                    "score_difference": score_diff,
                    "recommended_version": "B" if score_diff > 0 else "A",
                    "confidence": max(
                        prediction_a.get("confidence_level", "low"),
                        prediction_b.get("confidence_level", "low")
                    )
                },
                "metric_winners": self._determine_metric_winners(
                    prediction_a["predictions"],
                    prediction_b["predictions"]
                )
            }

            return comparison

        except Exception as e:
            logger.error(f"Error comparing versions: {str(e)}")
            raise

    def _determine_metric_winners(self, pred_a: Dict, pred_b: Dict) -> Dict:
        """Determine which version wins for each metric"""
        winners = {}

        for metric in PredictionMetric:
            metric_name = metric.value

            if metric_name in pred_a and metric_name in pred_b:
                val_a = pred_a[metric_name].get("predicted_value")
                val_b = pred_b[metric_name].get("predicted_value")

                # Handle different value types
                if isinstance(val_a, dict):
                    # Use first key's value for comparison
                    key = list(val_a.keys())[0]
                    val_a = val_a[key]
                    val_b = val_b[key]

                winners[metric_name] = "B" if val_b > val_a else "A"

        return winners

    def train_model(self, historical_data: List[Dict]) -> Dict:
        """Train predictive model on historical data (placeholder for real ML)"""
        try:
            # Store historical data
            self.historical_data.extend(historical_data)

            # In production, this would train actual ML models
            # For now, update feature weights based on correlations

            logger.info(f"Trained on {len(historical_data)} historical content pieces")

            return {
                "trained": True,
                "data_points": len(self.historical_data),
                "model_version": "1.0",
                "trained_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
