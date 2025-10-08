"""
Keyword Discovery Service
Fetches keyword data from DataForSEO Keywords API
"""
import asyncio
import aiohttp
from typing import List, Optional, Dict
from datetime import datetime
import os
import logging
from app.models.keyword import KeywordData, KeywordBatch, SearchIntent, KeywordTrend

logger = logging.getLogger(__name__)


class KeywordDiscoverer:
    """Discovers keyword opportunities using DataForSEO Keywords API"""

    BASE_URL = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_suggestions/live"

    def __init__(self):
        self.username = os.getenv("DATAFORSEO_LOGIN") or os.getenv("DATAFORSEO_USERNAME")
        self.password = os.getenv("DATAFORSEO_PASSWORD")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(self.username, self.password),
            headers={"Content-Type": "application/json"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def discover_keywords(
        self,
        seed_keyword: str,
        location_code: int = 2840,  # USA
        language_code: str = "en",
        limit: int = 100
    ) -> KeywordBatch:
        """
        Discover keyword suggestions from seed keyword

        Args:
            seed_keyword: Starting keyword for discovery
            location_code: Geographic location (2840 = USA)
            language_code: Language code
            limit: Max keywords to return

        Returns:
            KeywordBatch with discovered keywords
        """
        if not self.session:
            raise RuntimeError("KeywordDiscoverer must be used as async context manager")

        # Build API request
        payload = [{
            "keyword": seed_keyword,
            "location_code": location_code,
            "language_code": language_code,
            "include_serp_info": True,
            "include_seed_keyword": True,
            "limit": limit,
            "filters": [
                ["keyword_info.search_volume", ">", 0]  # Only keywords with volume
            ],
            "order_by": ["keyword_info.search_volume,desc"]
        }]

        try:
            logger.info(f"Discovering keywords for seed: '{seed_keyword}'")
            async with self.session.post(self.BASE_URL, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    batch = self._parse_response(data, seed_keyword)
                    logger.info(f"Found {batch.total_found} keywords for '{seed_keyword}'")
                    return batch
                elif response.status == 429:
                    # Rate limited - wait and retry
                    logger.warning("Rate limited, waiting 2 seconds...")
                    await asyncio.sleep(2)
                    return await self.discover_keywords(seed_keyword, location_code, language_code, limit)
                else:
                    error_text = await response.text()
                    logger.error(f"DataForSEO API error {response.status}: {error_text}")
                    raise Exception(f"DataForSEO API error {response.status}: {error_text}")

        except Exception as e:
            logger.error(f"Error discovering keywords for '{seed_keyword}': {e}")
            raise

    def _parse_response(self, api_response: dict, seed_keyword: str) -> KeywordBatch:
        """Parse DataForSEO response into KeywordBatch"""
        keywords = []

        if api_response.get("tasks"):
            task = api_response["tasks"][0]
            if task.get("result") and task["result"]:
                result = task["result"][0]
                if result:
                    items = result.get("items", [])

                    for item in items:
                        if not item:
                            continue

                        keyword_info = item.get("keyword_info") or {}
                        serp_info = item.get("serp_info") or {}

                        # Extract keyword data
                        keyword_data = KeywordData(
                            keyword=item.get("keyword", ""),
                            search_volume=keyword_info.get("search_volume", 0),
                            keyword_difficulty=serp_info.get("keyword_difficulty", None),
                            cpc=keyword_info.get("cpc", None),
                            competition=keyword_info.get("competition", None),
                            intent=self._classify_intent(keyword_info),
                            serp_features=self._extract_serp_features(serp_info),
                            trend=self._extract_trends(keyword_info)
                        )
                        keywords.append(keyword_data)

        return KeywordBatch(
            seed_keyword=seed_keyword,
            keywords=keywords,
            total_found=len(keywords),
            processed_at=datetime.now()
        )

    def _classify_intent(self, keyword_info: dict) -> SearchIntent:
        """Classify search intent based on keyword characteristics"""
        # Simple intent classification logic
        # Can be enhanced with ML model in future

        cpc = keyword_info.get("cpc", 0) or 0
        competition = keyword_info.get("competition", 0) or 0

        if cpc > 2.0 and competition > 0.7:
            return SearchIntent.TRANSACTIONAL
        elif cpc > 1.0 and competition > 0.4:
            return SearchIntent.COMMERCIAL
        else:
            return SearchIntent.INFORMATIONAL

    def _extract_serp_features(self, serp_info: dict) -> List[str]:
        """Extract SERP features present for this keyword"""
        features = []

        if serp_info.get("se_results_count"):
            features.append("organic_results")
        if serp_info.get("local_pack"):
            features.append("local_pack")
        if serp_info.get("knowledge_graph"):
            features.append("knowledge_graph")
        if serp_info.get("featured_snippet"):
            features.append("featured_snippet")
        if serp_info.get("shopping"):
            features.append("shopping")

        return features

    def _extract_trends(self, keyword_info: dict) -> List[KeywordTrend]:
        """Extract monthly trend data if available"""
        trends = []
        monthly_searches = keyword_info.get("monthly_searches", [])

        for month_data in monthly_searches:
            month_value = month_data.get("month", "")
            # Convert month to string if it's an integer
            if isinstance(month_value, int):
                month_value = str(month_value)

            trends.append(KeywordTrend(
                month=month_value,
                volume=month_data.get("search_volume", 0)
            ))

        return trends


# Usage example
async def discover_niche(seed: str):
    async with KeywordDiscoverer() as discoverer:
        batch = await discoverer.discover_keywords(seed, limit=100)
        print(f"Found {batch.total_found} keywords for '{seed}'")
        return batch
