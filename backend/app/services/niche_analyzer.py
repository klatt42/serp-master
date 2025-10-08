"""
Niche Analysis Service
Analyzes market dynamics, competition, and opportunities
"""
from typing import List, Dict, Optional
from collections import Counter
from statistics import mean
import logging

from app.models.keyword import KeywordData
from app.models.cluster import KeywordCluster
from app.models.niche import (
    NicheAnalysis,
    MarketSize,
    CompetitionLevel,
    ContentGap,
    MarketOpportunity
)

logger = logging.getLogger(__name__)


class NicheAnalyzer:
    """
    Analyzes niche market dynamics and identifies opportunities
    """

    # Market size thresholds (monthly search volume)
    MARKET_THRESHOLDS = {
        "small": 10000,
        "medium": 50000,
        "large": 200000,
        "huge": 1000000
    }

    # Competition level thresholds (avg keyword difficulty)
    COMPETITION_THRESHOLDS = {
        "low": 30,
        "medium": 50,
        "high": 70,
        "very_high": 100
    }

    def __init__(self):
        pass

    def analyze_niche(
        self,
        seed_keyword: str,
        keywords: List[KeywordData],
        clusters: List[KeywordCluster]
    ) -> NicheAnalysis:
        """
        Perform comprehensive niche analysis

        Args:
            seed_keyword: Original seed keyword
            keywords: All discovered keywords
            clusters: Keyword clusters

        Returns:
            Complete niche analysis with recommendations
        """
        logger.info(f"Analyzing niche for seed: {seed_keyword}")

        # Step 1: Calculate market metrics
        total_volume = sum(kw.search_volume for kw in keywords)
        market_size = self._classify_market_size(total_volume)
        logger.info(f"Market size: {market_size} (volume: {total_volume:,})")

        # Step 2: Assess competition
        difficulties = [kw.keyword_difficulty for kw in keywords if kw.keyword_difficulty]
        avg_difficulty = mean(difficulties) if difficulties else 50
        competition_level = self._classify_competition(avg_difficulty)
        logger.info(f"Competition: {competition_level} (avg difficulty: {avg_difficulty:.2f})")

        # Step 3: Calculate monetization potential
        cpcs = [kw.cpc for kw in keywords if kw.cpc]
        monetization_potential = sum(cpcs) * len(keywords) if cpcs else 0

        # Step 4: Identify SERP features
        all_features = []
        for kw in keywords:
            all_features.extend(kw.serp_features)
        top_serp_features = [f[0] for f in Counter(all_features).most_common(5)]

        # Step 5: Identify content gaps
        content_gaps = self._identify_content_gaps(keywords, clusters)
        logger.info(f"Identified {len(content_gaps)} content gaps")

        # Step 6: Generate strategy recommendation
        strategy = self._generate_strategy(
            market_size,
            competition_level,
            monetization_potential,
            content_gaps
        )

        # Step 7: Calculate confidence score
        confidence = self._calculate_confidence(keywords)

        # Step 8: Identify market opportunities
        opportunities = self._identify_opportunities(
            clusters,
            market_size,
            competition_level
        )
        logger.info(f"Identified {len(opportunities)} market opportunities")

        return NicheAnalysis(
            seed_keyword=seed_keyword,
            total_keywords=len(keywords),
            total_search_volume=total_volume,
            market_size=market_size,
            competition_level=competition_level,
            avg_keyword_difficulty=round(avg_difficulty, 2),
            monetization_potential=round(monetization_potential, 2),
            top_serp_features=top_serp_features,
            content_gaps=content_gaps,
            recommended_strategy=strategy,
            confidence_score=confidence,
            opportunities=opportunities,
            cluster_count=len(clusters)
        )

    def _classify_market_size(self, total_volume: int) -> MarketSize:
        """Classify market size based on total search volume"""
        if total_volume >= self.MARKET_THRESHOLDS["huge"]:
            return MarketSize.HUGE
        elif total_volume >= self.MARKET_THRESHOLDS["large"]:
            return MarketSize.LARGE
        elif total_volume >= self.MARKET_THRESHOLDS["medium"]:
            return MarketSize.MEDIUM
        else:
            return MarketSize.SMALL

    def _classify_competition(self, avg_difficulty: float) -> CompetitionLevel:
        """Classify competition level based on average difficulty"""
        if avg_difficulty >= self.COMPETITION_THRESHOLDS["very_high"]:
            return CompetitionLevel.VERY_HIGH
        elif avg_difficulty >= self.COMPETITION_THRESHOLDS["high"]:
            return CompetitionLevel.HIGH
        elif avg_difficulty >= self.COMPETITION_THRESHOLDS["medium"]:
            return CompetitionLevel.MEDIUM
        else:
            return CompetitionLevel.LOW

    def _identify_content_gaps(
        self,
        keywords: List[KeywordData],
        clusters: List[KeywordCluster]
    ) -> List[ContentGap]:
        """Identify missing content opportunities"""
        gaps = []

        # Gap 1: High-volume, low-competition keywords
        quick_wins = [
            kw for kw in keywords
            if kw.search_volume > 500
            and kw.keyword_difficulty
            and kw.keyword_difficulty < 40
        ]

        if quick_wins:
            gaps.append(ContentGap(
                gap_type="quick_wins",
                description=f"{len(quick_wins)} high-volume, low-competition keywords available",
                keywords=[kw.keyword for kw in quick_wins[:5]],
                estimated_impact="high",
                priority="high"
            ))

        # Gap 2: Informational content opportunities
        info_keywords = []
        for kw in keywords:
            if kw.intent:
                intent_val = kw.intent.value if hasattr(kw.intent, 'value') else kw.intent
                if intent_val == "informational":
                    info_keywords.append(kw)

        if len(info_keywords) > 10:
            gaps.append(ContentGap(
                gap_type="educational_content",
                description=f"{len(info_keywords)} informational keyword opportunities for guides and tutorials",
                keywords=[kw.keyword for kw in info_keywords[:5]],
                estimated_impact="medium",
                priority="medium"
            ))

        # Gap 3: Commercial content opportunities
        commercial_keywords = []
        for kw in keywords:
            if kw.intent:
                intent_val = kw.intent.value if hasattr(kw.intent, 'value') else kw.intent
                if intent_val == "commercial":
                    commercial_keywords.append(kw)

        if len(commercial_keywords) > 5:
            gaps.append(ContentGap(
                gap_type="comparison_content",
                description=f"{len(commercial_keywords)} commercial keywords for comparison and review content",
                keywords=[kw.keyword for kw in commercial_keywords[:5]],
                estimated_impact="high",
                priority="high"
            ))

        # Gap 4: Long-tail opportunities
        long_tail = [kw for kw in keywords if len(kw.keyword.split()) >= 4]
        if len(long_tail) > 20:
            gaps.append(ContentGap(
                gap_type="long_tail",
                description=f"{len(long_tail)} long-tail keyword opportunities for specific topics",
                keywords=[kw.keyword for kw in long_tail[:5]],
                estimated_impact="medium",
                priority="medium"
            ))

        return gaps

    def _generate_strategy(
        self,
        market_size: MarketSize,
        competition: CompetitionLevel,
        monetization: float,
        gaps: List[ContentGap]
    ) -> str:
        """Generate strategic recommendation"""
        strategies = []

        # Market-based strategy
        if market_size == MarketSize.HUGE and competition == CompetitionLevel.HIGH:
            strategies.append("Large, competitive market - focus on specific sub-niches and long-tail keywords")
        elif market_size == MarketSize.LARGE and competition == CompetitionLevel.MEDIUM:
            strategies.append("Excellent opportunity - significant traffic potential with manageable competition")
        elif market_size == MarketSize.MEDIUM and competition == CompetitionLevel.LOW:
            strategies.append("Sweet spot - moderate traffic with low competition, ideal for quick wins")
        elif market_size == MarketSize.SMALL:
            strategies.append("Niche market - focus on highly targeted content and building authority")

        # Gap-based strategy
        if gaps:
            top_gap = max(gaps, key=lambda g: 1 if g.priority == "high" else 0)
            strategies.append(f"Priority: {top_gap.description}")

        # Monetization strategy
        if monetization > 1000:
            strategies.append("High monetization potential - prioritize commercial and transactional content")

        return " | ".join(strategies) if strategies else "Analyze competition and create targeted content"

    def _calculate_confidence(self, keywords: List[KeywordData]) -> float:
        """Calculate confidence score based on data quality"""
        # More keywords = higher confidence
        keyword_score = min(len(keywords) / 100, 1.0) * 0.4

        # More complete data = higher confidence
        complete_data = sum(1 for kw in keywords if kw.keyword_difficulty and kw.cpc)
        data_completeness = (complete_data / len(keywords)) * 0.6 if keywords else 0

        total_confidence = keyword_score + data_completeness

        return round(total_confidence, 2)

    def _identify_opportunities(
        self,
        clusters: List[KeywordCluster],
        market_size: MarketSize,
        competition: CompetitionLevel
    ) -> List[MarketOpportunity]:
        """Identify specific market opportunities"""
        opportunities = []

        for cluster in clusters:
            # Calculate opportunity score
            volume_score = min(cluster.total_search_volume / 10000, 1.0) * 40
            difficulty_score = (100 - cluster.avg_difficulty) * 0.3
            cpc_score = min(cluster.avg_cpc * 10, 30)

            total_score = volume_score + difficulty_score + cpc_score

            # Classify opportunity
            if total_score >= 70:
                opportunity_level = "excellent"
            elif total_score >= 50:
                opportunity_level = "good"
            else:
                opportunity_level = "moderate"

            opportunities.append(MarketOpportunity(
                cluster_name=cluster.cluster_name,
                cluster_theme=cluster.theme.description,
                opportunity_score=round(total_score, 2),
                opportunity_level=opportunity_level,
                total_search_volume=cluster.total_search_volume,
                avg_difficulty=cluster.avg_difficulty,
                recommended_action=self._recommend_action(cluster, total_score)
            ))

        # Sort by score
        opportunities.sort(key=lambda o: o.opportunity_score, reverse=True)

        return opportunities[:10]  # Top 10 opportunities

    def _recommend_action(self, cluster: KeywordCluster, score: float) -> str:
        """Recommend specific action for cluster"""
        if score >= 70:
            return f"High priority: Create comprehensive content targeting '{cluster.cluster_name}' cluster"
        elif score >= 50:
            return f"Medium priority: Develop focused content for '{cluster.cluster_name}' keywords"
        else:
            return f"Low priority: Consider after higher-value opportunities"
