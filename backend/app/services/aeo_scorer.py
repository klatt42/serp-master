"""
AEO Scorer - Answer Engine Optimization
Combines all AEO components into a comprehensive score
Integrates with traditional SEO for total site score
"""

import logging
from typing import Dict, Any, List
from .schema_detector import SchemaDetector
from .content_analyzer import ContentAnalyzer
from .entity_checker import EntityChecker

logger = logging.getLogger(__name__)


class AEOScorer:
    """
    Orchestrates all AEO scoring components

    AEO Components (25 points total):
    - Schema Markup: 10 points (SchemaDetector)
    - Conversational Content: 8 points (ContentAnalyzer)
    - Entity Clarity: 7 points (EntityChecker)

    Combined with Traditional SEO (30 points):
    - Total Score: 55/100 points
    """

    def __init__(self):
        self.schema_detector = SchemaDetector()
        self.content_analyzer = ContentAnalyzer()
        self.entity_checker = EntityChecker()

    def calculate_aeo_score(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive AEO score

        Args:
            site_data: Mock site data or real crawl data

        Returns:
            Complete AEO analysis with score and recommendations
        """
        try:
            html_content = site_data.get('html', '')
            pages = site_data.get('pages', [])

            # Run all AEO analyzers
            schema_results = self.schema_detector.detect_schemas(html_content)
            content_results = self.content_analyzer.calculate_conversational_score(site_data)
            entity_results = self.entity_checker.check_entity_clarity(site_data)

            # Calculate total AEO score
            schema_score = schema_results.get('schema_score', 0)
            conversational_score = content_results.get('conversational_score', 0)
            entity_score = entity_results.get('entity_clarity_score', 0)

            total_aeo_score = schema_score + conversational_score + entity_score
            max_aeo_score = 25

            # Calculate percentage
            aeo_percentage = (total_aeo_score / max_aeo_score * 100) if max_aeo_score > 0 else 0

            # Determine overall grade
            grade = self._calculate_grade(total_aeo_score, max_aeo_score)

            # Combine all recommendations
            all_recommendations = self._prioritize_recommendations(
                schema_results.get('recommendations', []),
                content_results.get('recommendations', []),
                entity_results.get('recommendations', [])
            )

            # Generate summary insights
            insights = self._generate_insights(
                schema_score,
                conversational_score,
                entity_score
            )

            return {
                "aeo_score": total_aeo_score,
                "max_score": max_aeo_score,
                "percentage": round(aeo_percentage, 1),
                "grade": grade,
                "breakdown": {
                    "schema_markup": {
                        "score": schema_score,
                        "max": 10,
                        "percentage": round((schema_score / 10 * 100), 1),
                        "details": schema_results
                    },
                    "conversational_content": {
                        "score": conversational_score,
                        "max": 8,
                        "percentage": round((conversational_score / 8 * 100), 1),
                        "details": content_results
                    },
                    "entity_clarity": {
                        "score": entity_score,
                        "max": 7,
                        "percentage": round((entity_score / 7 * 100), 1),
                        "details": entity_results
                    }
                },
                "recommendations": all_recommendations,
                "insights": insights,
                "readiness": self._assess_readiness(total_aeo_score)
            }

        except Exception as e:
            logger.error(f"Error calculating AEO score: {str(e)}")
            return {
                "aeo_score": 0,
                "max_score": 25,
                "percentage": 0,
                "grade": "F",
                "error": str(e),
                "recommendations": ["Fix errors before calculating AEO score"],
                "insights": ["Unable to analyze site due to errors"]
            }

    def calculate_combined_score(
        self,
        site_data: Dict[str, Any],
        seo_score: int = 0,
        geo_score: int = 0
    ) -> Dict[str, Any]:
        """
        Calculate combined score: SEO + AEO + GEO

        Args:
            site_data: Site data for AEO analysis
            seo_score: Traditional SEO score (0-30)
            geo_score: Geographic optimization score (0-45, Phase 2)

        Returns:
            Combined score out of 100
        """
        # Get AEO score
        aeo_results = self.calculate_aeo_score(site_data)
        aeo_score = aeo_results.get('aeo_score', 0)

        # Calculate total
        total_score = seo_score + aeo_score + geo_score
        max_total = 100

        # Calculate percentage
        percentage = (total_score / max_total * 100) if max_total > 0 else 0

        # Determine grade
        grade = self._calculate_grade(total_score, max_total)

        return {
            "total_score": total_score,
            "max_score": max_total,
            "percentage": round(percentage, 1),
            "grade": grade,
            "component_scores": {
                "seo": {
                    "score": seo_score,
                    "max": 30,
                    "percentage": round((seo_score / 30 * 100), 1) if seo_score > 0 else 0
                },
                "aeo": {
                    "score": aeo_score,
                    "max": 25,
                    "percentage": round((aeo_score / 25 * 100), 1) if aeo_score > 0 else 0,
                    "breakdown": aeo_results.get('breakdown', {})
                },
                "geo": {
                    "score": geo_score,
                    "max": 45,
                    "percentage": round((geo_score / 45 * 100), 1) if geo_score > 0 else 0,
                    "status": "Phase 2 - Coming Soon"
                }
            },
            "aeo_details": aeo_results,
            "strengths": self._identify_strengths(seo_score, aeo_score, geo_score),
            "weaknesses": self._identify_weaknesses(seo_score, aeo_score, geo_score)
        }

    def _calculate_grade(self, score: int, max_score: int) -> str:
        """Calculate letter grade based on percentage"""
        if max_score == 0:
            return "F"

        percentage = (score / max_score) * 100

        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"

    def _prioritize_recommendations(
        self,
        schema_recs: List[str],
        content_recs: List[str],
        entity_recs: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Combine and prioritize recommendations by impact

        Returns recommendations with category and priority
        """
        recommendations = []

        # Categorize schema recommendations (high impact)
        for rec in schema_recs:
            if "Organization" in rec or "LocalBusiness" in rec:
                priority = "high"
            elif "FAQ" in rec:
                priority = "medium"
            else:
                priority = "low"

            recommendations.append({
                "category": "Schema Markup",
                "priority": priority,
                "recommendation": rec
            })

        # Categorize content recommendations (medium impact)
        for rec in content_recs:
            if "FAQ" in rec:
                priority = "high"
            elif "readability" in rec.lower():
                priority = "medium"
            else:
                priority = "low"

            recommendations.append({
                "category": "Conversational Content",
                "priority": priority,
                "recommendation": rec
            })

        # Categorize entity recommendations (high impact - unique feature!)
        for rec in entity_recs:
            if "name" in rec.lower() or "description" in rec.lower():
                priority = "high"
            else:
                priority = "medium"

            recommendations.append({
                "category": "Entity Clarity",
                "priority": priority,
                "recommendation": rec
            })

        # Sort by priority: high > medium > low
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return recommendations

    def _generate_insights(
        self,
        schema_score: int,
        conversational_score: int,
        entity_score: int
    ) -> List[str]:
        """Generate high-level insights about AEO readiness"""
        insights = []

        # Schema insights
        if schema_score >= 8:
            insights.append("✓ Strong schema markup foundation for AI understanding")
        elif schema_score >= 5:
            insights.append("⚠ Schema markup present but could be improved")
        else:
            insights.append("✗ Missing critical schema markup for AI engines")

        # Conversational insights
        if conversational_score >= 6:
            insights.append("✓ Well-optimized for voice search and conversational queries")
        elif conversational_score >= 4:
            insights.append("⚠ Some conversational content, needs enhancement")
        else:
            insights.append("✗ Lacks conversational content structure for AI assistants")

        # Entity insights
        if entity_score >= 5:
            insights.append("✓ Clear entity identity - AI engines understand your business")
        elif entity_score >= 3:
            insights.append("⚠ Entity clarity needs improvement for better AI recognition")
        else:
            insights.append("✗ Weak entity signals - AI engines may struggle to understand your business")

        # Overall readiness
        total = schema_score + conversational_score + entity_score
        if total >= 20:
            insights.append("🎯 Overall: Excellent AEO - Ready for AI search engines!")
        elif total >= 15:
            insights.append("📈 Overall: Good AEO foundation - Some improvements needed")
        elif total >= 10:
            insights.append("⚡ Overall: Basic AEO - Significant opportunities for improvement")
        else:
            insights.append("🔧 Overall: Poor AEO - Critical work needed for AI visibility")

        return insights

    def _assess_readiness(self, aeo_score: int) -> Dict[str, Any]:
        """Assess readiness for different AI platforms"""
        percentage = (aeo_score / 25) * 100

        # Determine readiness level
        if percentage >= 80:
            level = "Excellent"
            status = "ready"
            message = "Your site is well-optimized for AI search engines and voice assistants"
        elif percentage >= 60:
            level = "Good"
            status = "mostly_ready"
            message = "Your site has good AEO foundations with room for improvement"
        elif percentage >= 40:
            level = "Fair"
            status = "needs_work"
            message = "Your site needs AEO improvements to compete in AI search"
        else:
            level = "Poor"
            status = "not_ready"
            message = "Your site is not optimized for AI search engines"

        return {
            "level": level,
            "status": status,
            "message": message,
            "platforms": {
                "google_assistant": {
                    "ready": percentage >= 60,
                    "requirements": "Schema markup + FAQ content + readability"
                },
                "alexa": {
                    "ready": percentage >= 60,
                    "requirements": "Conversational content + clear entities"
                },
                "chatgpt": {
                    "ready": percentage >= 50,
                    "requirements": "Entity clarity + structured content"
                },
                "perplexity": {
                    "ready": percentage >= 70,
                    "requirements": "Strong schema + entity relationships"
                }
            }
        }

    def _identify_strengths(self, seo: int, aeo: int, geo: int) -> List[str]:
        """Identify scoring strengths"""
        strengths = []

        # Check each component (>70% of max)
        if seo >= 21:  # 21/30 = 70%
            strengths.append("Traditional SEO is strong")

        if aeo >= 18:  # 18/25 = 72%
            strengths.append("Excellent AEO optimization")
        elif aeo >= 15:  # 15/25 = 60%
            strengths.append("Good AEO foundation")

        if geo >= 32:  # 32/45 = 71%
            strengths.append("Strong geographic optimization")

        if not strengths:
            strengths.append("Opportunities for improvement across all areas")

        return strengths

    def _identify_weaknesses(self, seo: int, aeo: int, geo: int) -> List[str]:
        """Identify areas needing improvement"""
        weaknesses = []

        # Check each component (<50% of max)
        if seo < 15:  # 15/30 = 50%
            weaknesses.append("Traditional SEO needs attention")

        if aeo < 13:  # 13/25 = 52%
            weaknesses.append("AEO optimization is below average")

        if geo < 23 and geo > 0:  # 23/45 = 51%, only if GEO is active
            weaknesses.append("Geographic optimization needs work")

        if not weaknesses:
            weaknesses.append("No critical weaknesses - focus on optimization")

        return weaknesses

    def get_quick_wins(self, site_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify quick wins - high impact, low effort improvements

        Returns:
            List of quick win recommendations with effort and impact estimates
        """
        aeo_results = self.calculate_aeo_score(site_data)
        quick_wins = []

        # Check schema quick wins
        schema_details = aeo_results.get('breakdown', {}).get('schema_markup', {}).get('details', {})
        missing_schemas = schema_details.get('missing_schemas', [])

        if 'Organization' in missing_schemas:
            quick_wins.append({
                "title": "Add Organization Schema",
                "impact": "high",
                "effort": "low",
                "points": 3,
                "description": "Add basic Organization schema with name, URL, and logo. Takes 5 minutes, major AI visibility boost."
            })

        if 'FAQPage' in missing_schemas:
            quick_wins.append({
                "title": "Add FAQ Schema to Existing FAQ Page",
                "impact": "medium",
                "effort": "low",
                "points": 2,
                "description": "If you have FAQ content, just add FAQPage schema markup. 10 minutes for voice search optimization."
            })

        # Check content quick wins
        content_details = aeo_results.get('breakdown', {}).get('conversational_content', {}).get('details', {})
        question_count = content_details.get('question_headers', {}).get('count', 0)

        if question_count < 5:
            quick_wins.append({
                "title": "Add Question-Format Headers",
                "impact": "medium",
                "effort": "low",
                "points": 2,
                "description": f"Add {5 - question_count} more headers like 'How does...?' or 'What is...?' to improve conversational optimization."
            })

        # Check entity quick wins
        entity_details = aeo_results.get('breakdown', {}).get('entity_clarity', {}).get('details', {})
        name_consistent = entity_details.get('name_consistency', {}).get('consistent', False)

        if not name_consistent:
            quick_wins.append({
                "title": "Standardize Business Name",
                "impact": "high",
                "effort": "low",
                "points": 2,
                "description": "Use the exact same business name everywhere - titles, headers, schema, footer. Critical for AI recognition."
            })

        # Sort by impact (high first) then points (highest first)
        impact_order = {"high": 0, "medium": 1, "low": 2}
        quick_wins.sort(key=lambda x: (impact_order.get(x["impact"], 3), -x["points"]))

        return quick_wins[:5]  # Return top 5 quick wins
