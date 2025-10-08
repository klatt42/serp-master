"""
Opportunity Scoring Engine
Calculates keyword value scores based on multiple factors
"""
import math
from typing import List, Optional
import logging
from app.models.keyword import KeywordData
from app.models.opportunity import (
    KeywordOpportunity,
    OpportunityLevel,
    OpportunityFilters
)

logger = logging.getLogger(__name__)


class OpportunityScorer:
    """Scores keywords based on opportunity potential"""

    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        "volume": 0.35,      # Search volume importance
        "difficulty": 0.30,  # Ease of ranking
        "cpc": 0.20,         # Monetization potential
        "competition": 0.15  # Market saturation
    }

    # Volume thresholds for scoring
    VOLUME_THRESHOLDS = {
        "excellent": 10000,  # 10K+ monthly searches
        "good": 1000,        # 1K-10K monthly searches
        "moderate": 100,     # 100-1K monthly searches
        "low": 0             # <100 monthly searches
    }

    def __init__(self, filters: Optional[OpportunityFilters] = None):
        """
        Initialize scorer with optional filters

        Args:
            filters: Criteria for filtering opportunities
        """
        self.filters = filters or OpportunityFilters()

    def score_keywords(self, keywords: List[KeywordData]) -> List[KeywordOpportunity]:
        """
        Score all keywords and return opportunities

        Args:
            keywords: List of keyword data to score

        Returns:
            List of scored opportunities, sorted by opportunity_score descending
        """
        opportunities = []

        for keyword in keywords:
            # Skip if doesn't meet filter criteria
            if not self._meets_filters(keyword):
                continue

            # Calculate component scores
            volume_score = self._score_volume(keyword.search_volume)
            difficulty_score = self._score_difficulty(keyword.keyword_difficulty)
            cpc_score = self._score_cpc(keyword.cpc)
            competition_score = self._score_competition(keyword.competition)

            # Calculate weighted opportunity score
            opportunity_score = (
                volume_score * self.WEIGHTS["volume"] +
                difficulty_score * self.WEIGHTS["difficulty"] +
                cpc_score * self.WEIGHTS["cpc"] +
                competition_score * self.WEIGHTS["competition"]
            )

            # Calculate ROI potential
            roi_potential = self._calculate_roi(
                keyword.search_volume,
                keyword.cpc or 0,
                keyword.keyword_difficulty or 50
            )

            # Determine opportunity level
            opportunity_level = self._classify_opportunity(opportunity_score)

            # Generate recommendations
            content_type = self._recommend_content_type(keyword)
            estimated_traffic = self._estimate_traffic(keyword.search_volume, keyword.keyword_difficulty)
            effort_level = self._estimate_effort(keyword.keyword_difficulty)

            # Create opportunity object
            opportunity = KeywordOpportunity(
                keyword=keyword.keyword,
                search_volume=keyword.search_volume,
                keyword_difficulty=keyword.keyword_difficulty or 50,
                cpc=keyword.cpc or 0,
                competition=keyword.competition or 0.5,
                volume_score=volume_score,
                difficulty_score=difficulty_score,
                cpc_score=cpc_score,
                competition_score=competition_score,
                opportunity_score=opportunity_score,
                roi_potential=roi_potential,
                opportunity_level=opportunity_level,
                recommended_content_type=content_type,
                estimated_traffic=estimated_traffic,
                effort_level=effort_level
            )

            opportunities.append(opportunity)

        # Sort by opportunity score descending
        opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)

        logger.info(f"Scored {len(opportunities)} opportunities from {len(keywords)} keywords")
        return opportunities

    def _meets_filters(self, keyword: KeywordData) -> bool:
        """Check if keyword meets filter criteria"""
        # Volume filter
        if keyword.search_volume < self.filters.min_volume:
            return False

        # Difficulty filter
        if keyword.keyword_difficulty and keyword.keyword_difficulty > self.filters.max_difficulty:
            return False

        # CPC filters
        if self.filters.min_cpc and (not keyword.cpc or keyword.cpc < self.filters.min_cpc):
            return False
        if self.filters.max_cpc and keyword.cpc and keyword.cpc > self.filters.max_cpc:
            return False

        # Intent filter
        if self.filters.intents and keyword.intent and keyword.intent.value not in self.filters.intents:
            return False

        return True

    def _score_volume(self, volume: int) -> float:
        """
        Score search volume 0-100
        Uses logarithmic scaling to handle wide range of volumes
        """
        if volume <= 0:
            return 0

        # Logarithmic scoring with base 10
        # 10 searches = 10 score, 100 = 20, 1000 = 30, 10000 = 40, etc.
        score = 10 * math.log10(volume)

        # Cap at 100
        return min(100, score)

    def _score_difficulty(self, difficulty: Optional[int]) -> float:
        """
        Score keyword difficulty 0-100 (inverse scoring - lower difficulty = higher score)
        """
        if difficulty is None:
            return 50  # Default mid-range score

        # Inverse scoring: difficulty 0 = score 100, difficulty 100 = score 0
        return 100 - difficulty

    def _score_cpc(self, cpc: Optional[float]) -> float:
        """
        Score CPC potential 0-100
        Higher CPC = more valuable keyword
        """
        if not cpc or cpc <= 0:
            return 0

        # Logarithmic scoring for CPC
        # $0.10 = 10, $1 = 20, $10 = 30, etc.
        score = 10 * math.log10(cpc * 10)

        # Cap at 100
        return min(100, max(0, score))

    def _score_competition(self, competition: Optional[float]) -> float:
        """
        Score competition 0-100 (inverse scoring - lower competition = higher score)
        """
        if competition is None:
            return 50  # Default mid-range score

        # Inverse scoring: competition 0 = score 100, competition 1 = score 0
        return 100 * (1 - competition)

    def _calculate_roi(self, volume: int, cpc: float, difficulty: int) -> float:
        """
        Calculate ROI potential metric
        Formula: (Volume * CPC) / (Difficulty + 1)
        """
        if difficulty == 0:
            difficulty = 1  # Avoid division by zero

        return (volume * cpc) / difficulty

    def _classify_opportunity(self, score: float) -> OpportunityLevel:
        """Classify opportunity level based on score"""
        if score >= 80:
            return OpportunityLevel.EXCELLENT
        elif score >= 60:
            return OpportunityLevel.GOOD
        elif score >= 40:
            return OpportunityLevel.MODERATE
        else:
            return OpportunityLevel.LOW

    def _recommend_content_type(self, keyword: KeywordData) -> str:
        """Recommend content type based on keyword characteristics"""
        intent = keyword.intent
        volume = keyword.search_volume

        # Handle both enum and string intent values
        intent_value = intent.value if hasattr(intent, 'value') else intent

        if intent_value == "transactional":
            return "Landing Page / Sales Page"
        elif intent_value == "commercial":
            return "Product/Service Comparison Page"
        elif volume > 1000:
            return "Comprehensive Blog Post (2000+ words)"
        else:
            return "Focused Blog Post (800-1200 words)"

    def _estimate_traffic(self, volume: int, difficulty: Optional[int]) -> int:
        """
        Estimate monthly traffic if ranked on page 1
        Assumes CTR decreases with difficulty
        """
        if not difficulty:
            difficulty = 50

        # Base CTR for position 1-10 (average ~30%)
        base_ctr = 0.30

        # Adjust CTR based on difficulty (harder = lower effective CTR)
        difficulty_factor = 1 - (difficulty / 200)  # 0.5 to 1.0 range

        estimated_ctr = base_ctr * difficulty_factor

        return int(volume * estimated_ctr)

    def _estimate_effort(self, difficulty: Optional[int]) -> str:
        """Estimate content creation effort"""
        if not difficulty:
            return "Medium"

        if difficulty < 30:
            return "Low"
        elif difficulty < 60:
            return "Medium"
        else:
            return "High"
