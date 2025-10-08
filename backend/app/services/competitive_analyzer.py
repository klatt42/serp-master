"""
SERP competitive intelligence analyzer
Identifies top competitors and their strategies
"""

from typing import List, Dict, Any
from urllib.parse import urlparse
import logging

from app.models.competitor import Competitor

logger = logging.getLogger(__name__)


class CompetitiveAnalyzer:
    """Analyze SERP competition and identify key players"""

    def __init__(self):
        pass

    async def analyze_competitors(
        self,
        keywords_with_serp: List[Dict[str, Any]],
        max_competitors: int = 10
    ) -> List[Competitor]:
        """
        Identify and analyze top competitors from SERP data

        Args:
            keywords_with_serp: Keywords with SERP data already fetched
            max_competitors: Maximum number of competitors to return

        Returns:
            List of Competitor objects with insights
        """
        logger.info(f"Analyzing competitors for {len(keywords_with_serp)} keywords")

        # Extract competitor domains
        competitor_domains = self._extract_competitors(keywords_with_serp)

        # Analyze each competitor
        competitors = []
        for domain, data in competitor_domains.items():
            competitor = Competitor(
                domain=domain,
                appearances=data['appearances'],
                avg_position=data['total_position'] / data['appearances'] if data['appearances'] > 0 else 0,
                keywords_ranked=data['keywords'],
                estimated_traffic=data['estimated_traffic'],
                domain_authority=data.get('domain_authority', 0),
                content_types=data.get('content_types', []),
                strengths=self._identify_strengths(data),
                weaknesses=self._identify_weaknesses(data)
            )
            competitors.append(competitor)

        # Sort by relevance
        competitors.sort(key=lambda c: (c.appearances, -c.avg_position), reverse=True)

        logger.info(f"Identified {len(competitors)} competitors")
        return competitors[:max_competitors]

    def _extract_competitors(
        self,
        keywords_with_serp: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Extract competitor domains and aggregate data"""

        competitors = {}

        for item in keywords_with_serp:
            keyword = item.get('keyword', '')
            search_volume = item.get('search_volume', 0)

            # Simulate SERP results - in real implementation, this would come from DataForSEO
            # For now, generate sample competitors
            sample_domains = self._get_sample_competitors(keyword)

            for i, domain in enumerate(sample_domains):
                position = i + 1

                if domain not in competitors:
                    competitors[domain] = {
                        'appearances': 0,
                        'total_position': 0,
                        'keywords': [],
                        'estimated_traffic': 0,
                        'content_types': set()
                    }

                competitors[domain]['appearances'] += 1
                competitors[domain]['total_position'] += position
                competitors[domain]['keywords'].append(keyword)

                # Estimate traffic (simplified)
                ctr = self._estimate_ctr(position)
                competitors[domain]['estimated_traffic'] += int(search_volume * ctr)

                # Identify content type
                content_type = self._identify_content_type(domain)
                competitors[domain]['content_types'].add(content_type)

        # Convert sets to lists
        for domain in competitors:
            competitors[domain]['content_types'] = list(competitors[domain]['content_types'])

        return competitors

    @staticmethod
    def _get_sample_competitors(keyword: str) -> List[str]:
        """Generate sample competitor domains based on keyword"""
        # In real implementation, this would come from actual SERP data
        base_domains = [
            "moz.com",
            "searchenginejournal.com",
            "ahrefs.com",
            "semrush.com",
            "backlinko.com",
            "neilpatel.com",
            "hubspot.com",
            "wordstream.com"
        ]
        return base_domains[:5]

    @staticmethod
    def _estimate_ctr(position: int) -> float:
        """Estimate CTR based on SERP position"""
        ctr_map = {
            1: 0.28, 2: 0.15, 3: 0.11, 4: 0.08, 5: 0.07,
            6: 0.05, 7: 0.04, 8: 0.03, 9: 0.03, 10: 0.02
        }
        return ctr_map.get(position, 0.01)

    @staticmethod
    def _identify_content_type(domain: str) -> str:
        """Identify content type from domain"""
        domain_lower = domain.lower()

        if 'blog' in domain_lower:
            return 'blog_post'
        elif 'video' in domain_lower or 'youtube' in domain_lower:
            return 'video'
        elif 'tool' in domain_lower:
            return 'tool'
        else:
            return 'article'

    def _identify_strengths(self, data: Dict[str, Any]) -> List[str]:
        """Identify competitor strengths"""
        strengths = []

        if data['appearances'] >= 5:
            strengths.append("Strong keyword coverage")

        avg_position = data['total_position'] / data['appearances'] if data['appearances'] > 0 else 0
        if avg_position <= 3:
            strengths.append("Excellent average rankings")

        if data['estimated_traffic'] >= 10000:
            strengths.append("High organic traffic")

        if len(data['content_types']) >= 3:
            strengths.append("Diverse content strategy")

        return strengths

    def _identify_weaknesses(self, data: Dict[str, Any]) -> List[str]:
        """Identify potential competitor weaknesses"""
        weaknesses = []

        if data['appearances'] < 3:
            weaknesses.append("Limited keyword targeting")

        avg_position = data['total_position'] / data['appearances'] if data['appearances'] > 0 else 0
        if avg_position > 5:
            weaknesses.append("Lower average rankings")

        if len(data['content_types']) <= 1:
            weaknesses.append("Single content type dependency")

        return weaknesses
