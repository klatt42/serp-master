"""
Platform Orchestrator - Unify all platform analyzers
Coordinates analysis across YouTube, TikTok, Amazon, and Reddit
"""

from typing import List, Dict
from datetime import datetime
import logging

from app.services.platform_intelligence.youtube_analyzer import YouTubeAnalyzer
from app.services.platform_intelligence.platform_analyzers import (
    TikTokAnalyzer,
    AmazonAnalyzer,
    RedditAnalyzer
)

logger = logging.getLogger(__name__)


class PlatformOrchestrator:
    """Orchestrate all platform analyzers and unify results"""

    def __init__(self, dataforseo_client=None):
        self.youtube = YouTubeAnalyzer(dataforseo_client)
        self.tiktok = TikTokAnalyzer(dataforseo_client)
        self.amazon = AmazonAnalyzer(dataforseo_client)
        self.reddit = RedditAnalyzer(dataforseo_client)

    async def analyze_all_platforms(
        self,
        seed_keywords: List[str],
        platforms: List[str],
        location: str = "United States"
    ) -> Dict:
        """
        Run analysis across all requested platforms

        Args:
            seed_keywords: Keywords to analyze
            platforms: List of platforms ('youtube', 'tiktok', 'amazon', 'reddit')
            location: Geographic location

        Returns:
            Unified analysis results across all platforms
        """
        results = {
            "platforms": {},
            "cross_platform_opportunities": [],
            "metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
                "platforms_analyzed": platforms,
                "seed_keywords": seed_keywords
            }
        }

        # Run platform-specific analyses
        if "youtube" in platforms:
            results["platforms"]["youtube"] = await self.youtube.discover_video_keywords(
                seed_keywords, location
            )

        if "tiktok" in platforms:
            results["platforms"]["tiktok"] = await self.tiktok.discover_trending_topics(
                seed_keywords, location
            )

        if "amazon" in platforms:
            results["platforms"]["amazon"] = await self.amazon.discover_product_keywords(
                seed_keywords, location
            )

        if "reddit" in platforms:
            results["platforms"]["reddit"] = await self.reddit.discover_discussion_topics(
                seed_keywords, location
            )

        # Identify cross-platform opportunities
        results["cross_platform_opportunities"] = self._find_cross_platform_opportunities(
            results["platforms"]
        )

        return results

    def _find_cross_platform_opportunities(self, platform_data: Dict) -> List[Dict]:
        """Identify keywords that work across multiple platforms"""
        opportunities = []

        # Extract all keywords from all platforms
        all_keywords = {}

        for platform, data in platform_data.items():
            if platform == "youtube":
                for kw in data.get("keywords", []):
                    keyword = kw["keyword"]
                    if keyword not in all_keywords:
                        all_keywords[keyword] = {"platforms": [], "data": {}}
                    all_keywords[keyword]["platforms"].append("youtube")
                    all_keywords[keyword]["data"]["youtube"] = kw

            elif platform == "tiktok":
                for idea in data.get("content_ideas", []):
                    keyword = idea["keyword"]
                    if keyword not in all_keywords:
                        all_keywords[keyword] = {"platforms": [], "data": {}}
                    all_keywords[keyword]["platforms"].append("tiktok")
                    all_keywords[keyword]["data"]["tiktok"] = idea

            elif platform == "amazon":
                for kw in data.get("product_keywords", []):
                    keyword = kw["keyword"]
                    if keyword not in all_keywords:
                        all_keywords[keyword] = {"platforms": [], "data": {}}
                    all_keywords[keyword]["platforms"].append("amazon")
                    all_keywords[keyword]["data"]["amazon"] = kw

            elif platform == "reddit":
                for topic in data.get("discussion_topics", []):
                    keyword = topic["keyword"]
                    if keyword not in all_keywords:
                        all_keywords[keyword] = {"platforms": [], "data": {}}
                    all_keywords[keyword]["platforms"].append("reddit")
                    all_keywords[keyword]["data"]["reddit"] = topic

        # Find keywords on 2+ platforms
        for keyword, info in all_keywords.items():
            if len(info["platforms"]) >= 2:
                opportunities.append({
                    "keyword": keyword,
                    "platforms": info["platforms"],
                    "platform_count": len(info["platforms"]),
                    "opportunity_type": "cross-platform",
                    "recommendation": "Create platform-specific versions of this content",
                    "data": info["data"]
                })

        return sorted(opportunities, key=lambda x: x["platform_count"], reverse=True)
