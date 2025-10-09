"""
Topic Intelligence Engine
AI-powered topic suggestion system based on performance analysis
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging
import random

logger = logging.getLogger(__name__)


class TopicIntelligence:
    """Generate intelligent topic suggestions based on performance data"""

    def __init__(self):
        """Initialize topic intelligence engine"""
        self.min_confidence_score = 0.6

    async def suggest_topics(
        self,
        performance_data: List[Dict],
        keyword_opportunities: List[Dict],
        competitive_gaps: List[Dict],
        limit: int = 15
    ) -> List[Dict]:
        """
        Generate AI-powered topic suggestions

        Args:
            performance_data: Historical content performance
            keyword_opportunities: Available keyword opportunities
            competitive_gaps: Identified competitive gaps
            limit: Number of suggestions to return

        Returns:
            Ranked list of topic suggestions
        """
        try:
            suggestions = []

            # Analyze successful patterns
            success_patterns = self._analyze_success_patterns(performance_data)

            # Generate suggestions from keyword opportunities
            for opportunity in keyword_opportunities[:limit]:
                suggestion = self._create_topic_suggestion(
                    opportunity,
                    success_patterns,
                    source="keyword_opportunity"
                )
                suggestions.append(suggestion)

            # Generate suggestions from competitive gaps
            for gap in competitive_gaps[:limit]:
                suggestion = self._create_topic_suggestion(
                    gap,
                    success_patterns,
                    source="competitive_gap"
                )
                suggestions.append(suggestion)

            # Generate trend-based suggestions
            trend_suggestions = self._generate_trend_suggestions(
                success_patterns,
                limit=5
            )
            suggestions.extend(trend_suggestions)

            # Rank and filter suggestions
            ranked_suggestions = self._rank_suggestions(suggestions)

            logger.info(f"Generated {len(ranked_suggestions)} topic suggestions")
            return ranked_suggestions[:limit]

        except Exception as e:
            logger.error(f"Error generating topic suggestions: {str(e)}")
            raise

    def _analyze_success_patterns(
        self,
        performance_data: List[Dict]
    ) -> Dict:
        """
        Analyze patterns from high-performing content

        Returns:
            Success pattern insights
        """
        try:
            high_performers = [
                content for content in performance_data
                if content.get("performance_score", 0) >= 75
            ]

            if not high_performers:
                return {
                    "avg_length": 2000,
                    "common_formats": ["guide", "tutorial", "comparison"],
                    "avg_score": 0,
                    "best_topics": []
                }

            # Extract patterns
            total_score = sum(p.get("performance_score", 0) for p in high_performers)
            avg_score = total_score / len(high_performers) if high_performers else 0

            return {
                "avg_length": 2000,  # Placeholder
                "common_formats": ["complete guide", "step-by-step", "best practices"],
                "avg_score": round(avg_score, 2),
                "best_topics": [p.get("keyword", "") for p in high_performers[:5]],
                "success_count": len(high_performers)
            }

        except Exception as e:
            logger.error(f"Error analyzing success patterns: {str(e)}")
            return {}

    def _create_topic_suggestion(
        self,
        opportunity: Dict,
        success_patterns: Dict,
        source: str
    ) -> Dict:
        """
        Create a topic suggestion from an opportunity

        Args:
            opportunity: Opportunity data
            success_patterns: Success pattern insights
            source: Source of the suggestion

        Returns:
            Topic suggestion
        """
        try:
            keyword = opportunity.get("keyword", "")
            search_volume = opportunity.get("search_volume", 0)
            difficulty = opportunity.get("difficulty", 50)

            # Calculate confidence score
            confidence = self._calculate_confidence(
                search_volume,
                difficulty,
                success_patterns
            )

            # Estimate traffic potential
            traffic_potential = self._estimate_traffic_potential(
                search_volume,
                difficulty
            )

            # Generate content angle
            angle = self._generate_content_angle(keyword, success_patterns)

            return {
                "topic": keyword,
                "angle": angle,
                "confidence_score": confidence,
                "traffic_potential": traffic_potential,
                "difficulty": difficulty,
                "search_volume": search_volume,
                "source": source,
                "reasoning": self._generate_reasoning(
                    keyword,
                    confidence,
                    traffic_potential,
                    source
                ),
                "recommended_format": random.choice(success_patterns.get("common_formats", ["guide"])),
                "estimated_effort_hours": self._estimate_effort(difficulty),
                "priority": self._calculate_priority(confidence, traffic_potential, difficulty),
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error creating topic suggestion: {str(e)}")
            raise

    def _calculate_confidence(
        self,
        search_volume: int,
        difficulty: int,
        success_patterns: Dict
    ) -> float:
        """Calculate confidence score (0-1)"""
        try:
            # Higher search volume = higher confidence
            volume_score = min(1.0, search_volume / 10000)

            # Lower difficulty = higher confidence
            difficulty_score = (100 - difficulty) / 100

            # Pattern match bonus
            pattern_bonus = 0.2 if success_patterns.get("success_count", 0) > 3 else 0

            confidence = (volume_score * 0.4 + difficulty_score * 0.4 + pattern_bonus)

            return min(1.0, max(0.0, confidence))

        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.5

    def _estimate_traffic_potential(
        self,
        search_volume: int,
        difficulty: int
    ) -> int:
        """Estimate monthly traffic potential"""
        try:
            # Assume 30% CTR for position 1-3
            # Difficulty affects achievable position
            position_multiplier = (100 - difficulty) / 200

            estimated_traffic = int(search_volume * 0.3 * position_multiplier)

            return max(0, estimated_traffic)

        except Exception as e:
            logger.error(f"Error estimating traffic: {str(e)}")
            return 0

    def _generate_content_angle(
        self,
        keyword: str,
        success_patterns: Dict
    ) -> str:
        """Generate unique content angle"""
        try:
            angles = [
                f"The Complete Guide to {keyword}",
                f"{keyword}: Everything You Need to Know",
                f"How to Master {keyword} in 2025",
                f"{keyword} Best Practices",
                f"Ultimate {keyword} Tutorial",
                f"{keyword} vs Alternatives",
                f"Top 10 {keyword} Tips",
                f"{keyword} for Beginners"
            ]

            return random.choice(angles)

        except Exception as e:
            logger.error(f"Error generating angle: {str(e)}")
            return f"Guide to {keyword}"

    def _generate_reasoning(
        self,
        keyword: str,
        confidence: float,
        traffic_potential: int,
        source: str
    ) -> str:
        """Generate explanation for why this topic is suggested"""
        try:
            reasons = []

            if confidence >= 0.8:
                reasons.append("High confidence based on performance patterns")
            elif confidence >= 0.6:
                reasons.append("Moderate confidence with good potential")

            if traffic_potential >= 500:
                reasons.append(f"Estimated {traffic_potential} monthly visitors")
            elif traffic_potential >= 100:
                reasons.append(f"{traffic_potential} monthly visitors potential")

            if source == "competitive_gap":
                reasons.append("Competitors ranking well, we're missing coverage")
            elif source == "keyword_opportunity":
                reasons.append("Strong keyword opportunity identified")

            return " | ".join(reasons) if reasons else "Data-driven suggestion"

        except Exception as e:
            logger.error(f"Error generating reasoning: {str(e)}")
            return "AI-generated suggestion"

    def _estimate_effort(self, difficulty: int) -> float:
        """Estimate content creation effort in hours"""
        try:
            # Higher difficulty = more research and depth needed
            base_hours = 3.0
            difficulty_multiplier = 1 + (difficulty / 100)

            return round(base_hours * difficulty_multiplier, 1)

        except Exception as e:
            logger.error(f"Error estimating effort: {str(e)}")
            return 3.0

    def _calculate_priority(
        self,
        confidence: float,
        traffic_potential: int,
        difficulty: int
    ) -> str:
        """Calculate topic priority"""
        try:
            priority_score = confidence * 0.4 + (traffic_potential / 1000) * 0.3 + ((100 - difficulty) / 100) * 0.3

            if priority_score >= 0.7:
                return "high"
            elif priority_score >= 0.4:
                return "medium"
            else:
                return "low"

        except Exception as e:
            logger.error(f"Error calculating priority: {str(e)}")
            return "medium"

    def _generate_trend_suggestions(
        self,
        success_patterns: Dict,
        limit: int = 5
    ) -> List[Dict]:
        """Generate suggestions based on trending topics"""
        try:
            # Placeholder for trend-based suggestions
            # In production, this would query trending data sources
            trend_topics = [
                {"keyword": "AI content creation", "search_volume": 5000, "difficulty": 60},
                {"keyword": "voice search optimization", "search_volume": 3000, "difficulty": 55},
                {"keyword": "sustainable marketing", "search_volume": 2000, "difficulty": 50}
            ]

            suggestions = []
            for topic in trend_topics[:limit]:
                suggestion = self._create_topic_suggestion(
                    topic,
                    success_patterns,
                    source="trending"
                )
                suggestions.append(suggestion)

            return suggestions

        except Exception as e:
            logger.error(f"Error generating trend suggestions: {str(e)}")
            return []

    def _rank_suggestions(
        self,
        suggestions: List[Dict]
    ) -> List[Dict]:
        """Rank suggestions by confidence and potential"""
        try:
            def ranking_score(s: Dict) -> float:
                return (
                    s.get("confidence_score", 0) * 0.5 +
                    (s.get("traffic_potential", 0) / 1000) * 0.3 +
                    (100 - s.get("difficulty", 50)) / 100 * 0.2
                )

            ranked = sorted(
                suggestions,
                key=ranking_score,
                reverse=True
            )

            # Filter low confidence
            filtered = [
                s for s in ranked
                if s.get("confidence_score", 0) >= self.min_confidence_score
            ]

            return filtered

        except Exception as e:
            logger.error(f"Error ranking suggestions: {str(e)}")
            return suggestions
