"""
Competitor Analysis Engine
Compares multiple sites and identifies competitive gaps and opportunities
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .site_crawler import SiteCrawler
from .seo_scorer import SEOScorer
from .aeo_scorer import AEOScorer
from .issue_analyzer import IssueAnalyzer

logger = logging.getLogger(__name__)


class CompetitorAnalyzer:
    """
    Analyzes multiple sites and provides competitive intelligence

    Features:
    - Parallel multi-site auditing
    - Score comparison across dimensions
    - Gap analysis
    - Competitive strategy generation
    - Quick wins identification
    """

    def __init__(self):
        self.crawler = SiteCrawler()
        self.seo_scorer = SEOScorer()
        self.aeo_scorer = AEOScorer()
        self.issue_analyzer = IssueAnalyzer()

    async def analyze_competitors(
        self,
        user_url: str,
        competitor_urls: List[str],
        max_pages: int = 50
    ) -> Dict[str, Any]:
        """
        Main method to analyze user site vs competitors

        Args:
            user_url: User's website URL
            competitor_urls: List of competitor URLs (max 3)
            max_pages: Max pages to crawl per site

        Returns:
            Complete comparison analysis
        """
        try:
            # Validate inputs
            if len(competitor_urls) > 3:
                raise ValueError("Maximum 3 competitors allowed")

            if user_url in competitor_urls:
                raise ValueError("User URL cannot be in competitor list")

            # Audit all sites in parallel
            logger.info(f"Starting competitive analysis: {user_url} vs {len(competitor_urls)} competitors")

            all_urls = [user_url] + competitor_urls
            audits = await self.audit_multiple_sites(all_urls, max_pages)

            # Separate user audit from competitor audits
            user_audit = audits[0]
            competitor_audits = audits[1:]

            # Compare scores
            comparison = self.compare_scores(user_audit, competitor_audits)

            # Calculate gaps
            gaps = self.calculate_gaps(user_audit, competitor_audits)

            # Generate competitive strategy
            strategy = self.generate_competitive_strategy(gaps, user_audit, competitor_audits)

            # Identify quick wins
            quick_wins = self.identify_quick_wins_vs_competitors(gaps, strategy)

            return {
                "user_site": {
                    "url": user_url,
                    "total_score": user_audit.get("total_score", 0),
                    "rank": comparison["user_rank"],
                    "scores": user_audit.get("scores", {}),
                    "audit_data": user_audit
                },
                "competitors": [
                    {
                        "url": audit.get("url"),
                        "total_score": audit.get("total_score", 0),
                        "rank": i + 1 if i < comparison["user_rank"] - 1 else i + 2,
                        "scores": audit.get("scores", {}),
                        "audit_data": audit
                    }
                    for i, audit in enumerate(competitor_audits)
                ],
                "comparison": comparison,
                "gaps": gaps,
                "competitive_strategy": strategy,
                "quick_wins": quick_wins,
                "analysis_date": datetime.utcnow().isoformat(),
                "sites_analyzed": len(all_urls)
            }

        except Exception as e:
            logger.error(f"Error in competitor analysis: {str(e)}")
            raise

    async def audit_site(self, url: str, max_pages: int = 50) -> Dict[str, Any]:
        """
        Audit a single site

        Args:
            url: Website URL
            max_pages: Max pages to crawl

        Returns:
            Complete audit results
        """
        try:
            # For now, using mock data approach similar to existing implementation
            # In production, this would integrate with DataForSEO

            # Crawl site
            crawl_result = await self.crawler.crawl_site(url, max_pages)

            # Validate crawl result has expected structure
            if not crawl_result.get("summary") or not isinstance(crawl_result.get("summary"), dict):
                return {
                    "url": url,
                    "status": "failed",
                    "error": "Invalid crawl result structure",
                    "total_score": 0,
                    "scores": {}
                }

            # Score SEO
            seo_results = self.seo_scorer.calculate_total_seo_score(crawl_result)

            # Score AEO
            aeo_results = self.aeo_scorer.calculate_aeo_score(crawl_result)

            # Calculate total score
            total_score = seo_results.get("total_score", 0) + aeo_results.get("aeo_score", 0)

            # Analyze issues
            all_issues = {
                "seo_issues": seo_results.get("issues", []),
                "aeo_issues": aeo_results.get("issues", [])
            }

            return {
                "url": url,
                "status": "complete",
                "total_score": total_score,
                "scores": {
                    "seo": seo_results,
                    "aeo": aeo_results,
                    "geo": {"score": 0, "max": 45}  # Stub for Phase 2
                },
                "issues": all_issues,
                "crawl_data": crawl_result
            }

        except Exception as e:
            logger.error(f"Error auditing site {url}: {str(e)}")
            return {
                "url": url,
                "status": "failed",
                "error": str(e),
                "total_score": 0,
                "scores": {}
            }

    async def audit_multiple_sites(
        self,
        urls: List[str],
        max_pages: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Audit multiple sites in parallel using asyncio

        Args:
            urls: List of URLs to audit
            max_pages: Max pages per site

        Returns:
            List of audit results (same order as input)
        """
        try:
            # Create tasks for parallel execution
            tasks = [
                self.audit_site(url, max_pages)
                for url in urls
            ]

            # Run all audits in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to audit {urls[i]}: {str(result)}")
                    processed_results.append({
                        "url": urls[i],
                        "status": "failed",
                        "error": str(result),
                        "total_score": 0,
                        "scores": {}
                    })
                else:
                    processed_results.append(result)

            return processed_results

        except Exception as e:
            logger.error(f"Error in parallel audits: {str(e)}")
            raise

    def compare_scores(
        self,
        user_audit: Dict[str, Any],
        competitor_audits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare scores across all sites

        Args:
            user_audit: User's audit results
            competitor_audits: List of competitor audit results

        Returns:
            Score comparison data
        """
        try:
            all_audits = [user_audit] + competitor_audits

            # Sort by total score (descending)
            sorted_audits = sorted(
                all_audits,
                key=lambda x: x.get("total_score", 0),
                reverse=True
            )

            # Find user's rank
            user_rank = next(
                (i + 1 for i, audit in enumerate(sorted_audits)
                 if audit.get("url") == user_audit.get("url")),
                len(sorted_audits)
            )

            # Calculate score statistics
            user_score = user_audit.get("total_score", 0)
            competitor_scores = [a.get("total_score", 0) for a in competitor_audits if a.get("status") == "complete"]

            return {
                "user_rank": user_rank,
                "total_sites": len(all_audits),
                "user_score": user_score,
                "highest_competitor_score": max(competitor_scores) if competitor_scores else 0,
                "lowest_competitor_score": min(competitor_scores) if competitor_scores else 0,
                "average_competitor_score": sum(competitor_scores) / len(competitor_scores) if competitor_scores else 0,
                "score_gap_to_first": sorted_audits[0].get("total_score", 0) - user_score,
                "rankings": [
                    {
                        "rank": i + 1,
                        "url": audit.get("url"),
                        "score": audit.get("total_score", 0)
                    }
                    for i, audit in enumerate(sorted_audits)
                ]
            }

        except Exception as e:
            logger.error(f"Error comparing scores: {str(e)}")
            return {"error": str(e)}

    def calculate_gaps(
        self,
        user_audit: Dict[str, Any],
        competitor_audits: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify gaps where competitors are stronger

        Args:
            user_audit: User's audit results
            competitor_audits: List of competitor audits

        Returns:
            List of gaps with details
        """
        gaps = []

        try:
            user_scores = user_audit.get("scores", {})

            for comp_audit in competitor_audits:
                if comp_audit.get("status") != "complete":
                    continue

                comp_scores = comp_audit.get("scores", {})
                comp_url = comp_audit.get("url")

                # SEO gaps
                user_seo = user_scores.get("seo", {}).get("total_score", 0)
                comp_seo = comp_scores.get("seo", {}).get("total_score", 0)

                if comp_seo > user_seo:
                    gaps.append({
                        "dimension": "SEO",
                        "issue": "Lower overall SEO score",
                        "user_score": user_seo,
                        "competitor_score": comp_seo,
                        "competitor_url": comp_url,
                        "gap": comp_seo - user_seo,
                        "category": "overall",
                        "priority": "high" if comp_seo - user_seo > 5 else "medium"
                    })

                # AEO gaps
                user_aeo = user_scores.get("aeo", {}).get("aeo_score", 0)
                comp_aeo = comp_scores.get("aeo", {}).get("aeo_score", 0)

                if comp_aeo > user_aeo:
                    gaps.append({
                        "dimension": "AEO",
                        "issue": "Lower AEO optimization",
                        "user_score": user_aeo,
                        "competitor_score": comp_aeo,
                        "competitor_url": comp_url,
                        "gap": comp_aeo - user_aeo,
                        "category": "overall",
                        "priority": "high" if comp_aeo - user_aeo > 3 else "medium"
                    })

                # Detailed AEO gaps
                user_aeo_data = user_scores.get("aeo", {})
                comp_aeo_data = comp_scores.get("aeo", {})

                # Schema gap
                user_schema = user_aeo_data.get("schema_markup", {}).get("score", 0)
                comp_schema = comp_aeo_data.get("schema_markup", {}).get("score", 0)

                if comp_schema > user_schema:
                    gaps.append({
                        "dimension": "AEO",
                        "issue": "Missing schema markup",
                        "user_score": user_schema,
                        "competitor_score": comp_schema,
                        "competitor_url": comp_url,
                        "gap": comp_schema - user_schema,
                        "category": "schema",
                        "fix_impact": comp_schema - user_schema,
                        "priority": "high"
                    })

            # Sort gaps by priority and gap size
            gaps.sort(key=lambda x: (
                0 if x["priority"] == "high" else 1,
                -x["gap"]
            ))

            return gaps

        except Exception as e:
            logger.error(f"Error calculating gaps: {str(e)}")
            return []

    def generate_competitive_strategy(
        self,
        gaps: List[Dict[str, Any]],
        user_audit: Dict[str, Any],
        competitor_audits: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable competitive strategy

        Args:
            gaps: List of competitive gaps
            user_audit: User's audit
            competitor_audits: Competitor audits

        Returns:
            Prioritized list of strategic actions
        """
        strategy = []

        try:
            user_score = user_audit.get("total_score", 0)

            # Group gaps by fix action
            for gap in gaps[:10]:  # Top 10 gaps
                action = self._gap_to_action(gap)

                if action:
                    # Calculate impact
                    potential_score = user_score + gap.get("gap", 0)

                    # Determine which competitors this would beat
                    beats = []
                    new_rank = 1
                    for comp in competitor_audits:
                        if comp.get("status") == "complete":
                            comp_score = comp.get("total_score", 0)
                            if potential_score > comp_score:
                                beats.append(comp.get("url"))
                            elif potential_score <= comp_score:
                                new_rank += 1

                    strategy.append({
                        "action": action["title"],
                        "description": action["description"],
                        "dimension": gap.get("dimension"),
                        "impact": gap.get("gap", 0),
                        "effort": action.get("effort", "medium"),
                        "beats": beats,
                        "current_rank": self._get_user_rank(user_audit, competitor_audits),
                        "potential_rank": new_rank,
                        "priority": gap.get("priority", "medium"),
                        "related_competitor": gap.get("competitor_url")
                    })

            # Sort by impact and priority
            strategy.sort(key=lambda x: (
                0 if x["priority"] == "high" else 1,
                -x["impact"]
            ))

            return strategy

        except Exception as e:
            logger.error(f"Error generating strategy: {str(e)}")
            return []

    def identify_quick_wins_vs_competitors(
        self,
        gaps: List[Dict[str, Any]],
        strategy: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify high-impact, low-effort wins against competitors

        Args:
            gaps: Competitive gaps
            strategy: Competitive strategy

        Returns:
            List of quick wins
        """
        quick_wins = []

        try:
            # Find high impact + low effort items
            for item in strategy:
                if item.get("effort") == "low" and item.get("impact", 0) >= 2:
                    quick_wins.append({
                        "fix": item["action"],
                        "description": item.get("description", ""),
                        "beats": item.get("beats", []),
                        "impact": item["impact"],
                        "effort": item["effort"],
                        "dimension": item.get("dimension"),
                        "rank_improvement": item.get("current_rank", 0) - item.get("potential_rank", 0)
                    })

            # Sort by rank improvement and impact
            quick_wins.sort(key=lambda x: (
                -x.get("rank_improvement", 0),
                -x["impact"]
            ))

            return quick_wins[:5]  # Top 5 quick wins

        except Exception as e:
            logger.error(f"Error identifying quick wins: {str(e)}")
            return []

    def _gap_to_action(self, gap: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert a gap into an actionable recommendation

        Args:
            gap: Gap data

        Returns:
            Action recommendation
        """
        dimension = gap.get("dimension")
        category = gap.get("category")

        actions = {
            ("AEO", "schema"): {
                "title": "Add schema markup",
                "description": "Implement JSON-LD structured data for better answer engine visibility",
                "effort": "low"
            },
            ("AEO", "overall"): {
                "title": "Improve AEO optimization",
                "description": "Add FAQ schema, question headers, and improve content readability",
                "effort": "medium"
            },
            ("SEO", "overall"): {
                "title": "Improve technical SEO",
                "description": "Fix page speed, mobile optimization, and on-page elements",
                "effort": "medium"
            }
        }

        return actions.get((dimension, category), {
            "title": f"Improve {dimension}",
            "description": f"Address {gap.get('issue', 'issues')} to close competitive gap",
            "effort": "medium"
        })

    def _get_user_rank(
        self,
        user_audit: Dict[str, Any],
        competitor_audits: List[Dict[str, Any]]
    ) -> int:
        """Get user's current rank"""
        user_score = user_audit.get("total_score", 0)
        rank = 1

        for comp in competitor_audits:
            if comp.get("status") == "complete":
                if comp.get("total_score", 0) > user_score:
                    rank += 1

        return rank
