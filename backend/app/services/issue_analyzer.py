"""
Issue Prioritization Engine
Analyzes SEO scoring data to identify, categorize, and prioritize issues
Provides actionable recommendations with effort/impact analysis
"""

import logging
from typing import Dict, Any, List
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IssueSeverity(str, Enum):
    """Issue severity levels"""
    CRITICAL = "CRITICAL"  # Major problems affecting score >5 points
    WARNING = "WARNING"    # Medium issues affecting 2-5 points
    INFO = "INFO"          # Minor improvements affecting <2 points


class IssueEffort(str, Enum):
    """Effort required to fix issue"""
    LOW = "low"       # Quick fixes, <1 hour
    MEDIUM = "medium"  # Moderate effort, 1-4 hours
    HIGH = "high"      # Significant work, >4 hours


class IssueAnalyzer:
    """
    Analyzes SEO scores to identify issues, categorize by severity,
    and provide actionable recommendations
    """

    def __init__(self):
        """Initialize the issue analyzer"""
        logger.info("Issue Analyzer initialized")

    def analyze_issues(self, score_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze scoring data to identify and prioritize all issues

        Args:
            score_data: Complete SEO score breakdown from SEOScorer

        Returns:
            Categorized and prioritized issues with recommendations

        Example:
            {
                "critical_issues": [...],
                "warnings": [...],
                "info": [...],
                "quick_wins": [...],
                "summary": {...}
            }
        """
        try:
            logger.info("Analyzing SEO issues")

            all_issues = []

            # Analyze Technical SEO issues
            all_issues.extend(self._analyze_technical_issues(score_data.get("technical_seo", {})))

            # Analyze On-Page SEO issues
            all_issues.extend(self._analyze_onpage_issues(score_data.get("onpage_seo", {})))

            # Analyze Site Structure issues
            all_issues.extend(self._analyze_structure_issues(score_data.get("structure_seo", {})))

            # Categorize by severity
            critical = [i for i in all_issues if i["severity"] == IssueSeverity.CRITICAL]
            warnings = [i for i in all_issues if i["severity"] == IssueSeverity.WARNING]
            info = [i for i in all_issues if i["severity"] == IssueSeverity.INFO]

            # Identify quick wins (high impact, low effort)
            quick_wins = [
                i for i in all_issues
                if i["impact"] >= 2 and i["effort"] == IssueEffort.LOW
            ]

            # Sort each category by impact (descending)
            critical = sorted(critical, key=lambda x: x["impact"], reverse=True)
            warnings = sorted(warnings, key=lambda x: x["impact"], reverse=True)
            info = sorted(info, key=lambda x: x["impact"], reverse=True)
            quick_wins = sorted(quick_wins, key=lambda x: x["impact"], reverse=True)

            result = {
                "critical_issues": critical,
                "warnings": warnings,
                "info": info,
                "quick_wins": quick_wins,
                "summary": {
                    "total_issues": len(all_issues),
                    "critical_count": len(critical),
                    "warning_count": len(warnings),
                    "info_count": len(info),
                    "quick_win_count": len(quick_wins),
                    "total_potential_gain": sum(i["impact"] for i in all_issues)
                }
            }

            logger.info(
                f"Found {len(critical)} critical, {len(warnings)} warnings, "
                f"{len(info)} info issues ({len(quick_wins)} quick wins)"
            )

            return result

        except Exception as e:
            logger.error(f"Error analyzing issues: {str(e)}")
            raise

    def _analyze_technical_issues(self, technical_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze technical SEO issues"""
        issues = []
        details = technical_data.get("details", {})

        # Page Speed
        speed = details.get("page_speed", {})
        if speed.get("score", 0) < 3:
            avg_time = speed.get("avg_load_time_ms", 0)
            issues.append({
                "issue": "Slow page load time",
                "severity": IssueSeverity.CRITICAL if speed.get("score", 0) == 1 else IssueSeverity.WARNING,
                "impact": 3 - speed.get("score", 0),
                "effort": IssueEffort.MEDIUM,
                "pages_affected": "All pages",
                "current_value": f"{avg_time}ms average",
                "target_value": "<3000ms",
                "recommendation": self._get_speed_recommendation(avg_time),
                "quick_win": False
            })

        # Mobile Optimization
        mobile = details.get("mobile_optimization", {})
        if mobile.get("score", 0) < 3:
            issues.append({
                "issue": "Mobile optimization issues",
                "severity": IssueSeverity.CRITICAL if mobile.get("score", 0) == 1 else IssueSeverity.WARNING,
                "impact": 3 - mobile.get("score", 0),
                "effort": IssueEffort.MEDIUM,
                "pages_affected": f"{100 - mobile.get('mobile_friendly_percentage', 0):.0f}% of pages",
                "current_value": f"{mobile.get('mobile_friendly_percentage', 0):.0f}% mobile-friendly",
                "target_value": "100% mobile-friendly",
                "recommendation": "Add responsive viewport meta tag and test on mobile devices. Use CSS media queries for responsive design.",
                "quick_win": False
            })

        # HTTPS
        https = details.get("https", {})
        if https.get("score", 0) < 2:
            issues.append({
                "issue": "Not all pages use HTTPS",
                "severity": IssueSeverity.CRITICAL,
                "impact": 2 - https.get("score", 0),
                "effort": IssueEffort.MEDIUM,
                "pages_affected": f"{100 - https.get('https_percentage', 0):.0f}% of pages",
                "current_value": f"{https.get('https_percentage', 0):.0f}% HTTPS",
                "target_value": "100% HTTPS",
                "recommendation": "Install SSL certificate and redirect all HTTP traffic to HTTPS. Update all internal links to use HTTPS.",
                "quick_win": False
            })

        # XML Sitemap
        sitemap = details.get("xml_sitemap", {})
        if sitemap.get("score", 0) == 0:
            issues.append({
                "issue": "XML sitemap not found",
                "severity": IssueSeverity.WARNING,
                "impact": 1,
                "effort": IssueEffort.LOW,
                "pages_affected": "Site-wide",
                "current_value": "Missing",
                "target_value": "Present at /sitemap.xml",
                "recommendation": "Generate and submit XML sitemap to Google Search Console. Update robots.txt to reference sitemap location.",
                "quick_win": True
            })

        # Robots.txt
        robots = details.get("robots_txt", {})
        if robots.get("score", 0) == 0:
            issues.append({
                "issue": "robots.txt not found",
                "severity": IssueSeverity.INFO,
                "impact": 1,
                "effort": IssueEffort.LOW,
                "pages_affected": "Site-wide",
                "current_value": "Missing",
                "target_value": "Present at /robots.txt",
                "recommendation": "Create robots.txt file with sitemap reference and crawl directives for search engines.",
                "quick_win": True
            })

        return issues

    def _analyze_onpage_issues(self, onpage_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze on-page SEO issues"""
        issues = []
        details = onpage_data.get("details", {})

        # Title Tags
        titles = details.get("title_tags", {})
        if titles.get("score", 0) < 3:
            missing = titles.get("missing", 0)
            duplicates = titles.get("duplicates", 0)

            if missing > 0:
                issues.append({
                    "issue": "Missing title tags",
                    "severity": IssueSeverity.CRITICAL,
                    "impact": 3,
                    "effort": IssueEffort.LOW,
                    "pages_affected": f"{missing} pages",
                    "current_value": f"{missing} pages missing titles",
                    "target_value": "All pages have unique titles",
                    "recommendation": "Add unique, descriptive title tags (50-60 characters) to all pages. Include primary keywords near the beginning.",
                    "quick_win": True
                })

            if duplicates > 0:
                issues.append({
                    "issue": "Duplicate title tags",
                    "severity": IssueSeverity.WARNING,
                    "impact": 2,
                    "effort": IssueEffort.LOW,
                    "pages_affected": f"{duplicates} pages",
                    "current_value": f"{duplicates} duplicate titles",
                    "target_value": "All titles unique",
                    "recommendation": "Make all title tags unique. Each page should have a distinct, descriptive title relevant to its content.",
                    "quick_win": True
                })

        # Meta Descriptions
        descriptions = details.get("meta_descriptions", {})
        if descriptions.get("score", 0) < 3:
            missing = descriptions.get("missing", 0)
            issues.append({
                "issue": "Missing meta descriptions",
                "severity": IssueSeverity.WARNING,
                "impact": 3 - descriptions.get("score", 0),
                "effort": IssueEffort.LOW,
                "pages_affected": f"{missing} pages",
                "current_value": f"{missing} pages missing",
                "target_value": "All pages have descriptions",
                "recommendation": "Add compelling meta descriptions (150-160 characters) to all pages. Include target keywords naturally.",
                "quick_win": True
            })

        # H1 Tags
        h1 = details.get("h1_tags", {})
        if h1.get("score", 0) < 2:
            missing = h1.get("missing", 0)
            issues.append({
                "issue": "Missing H1 tags",
                "severity": IssueSeverity.WARNING,
                "impact": 2 - h1.get("score", 0),
                "effort": IssueEffort.LOW,
                "pages_affected": f"{missing} pages",
                "current_value": f"{missing} pages missing H1",
                "target_value": "All pages have H1",
                "recommendation": "Add a single, clear H1 tag to each page. H1 should describe the main topic and include primary keyword.",
                "quick_win": True
            })

        # Image Alt Text
        alt = details.get("image_alt_text", {})
        if alt.get("score", 0) < 2:
            missing_pct = alt.get("missing_percentage", 0)
            issues.append({
                "issue": "Missing image alt text",
                "severity": IssueSeverity.INFO if alt.get("score", 0) == 1 else IssueSeverity.WARNING,
                "impact": 2 - alt.get("score", 0),
                "effort": IssueEffort.MEDIUM,
                "pages_affected": f"{missing_pct:.0f}% of images",
                "current_value": f"{missing_pct:.0f}% missing alt text",
                "target_value": "<20% missing",
                "recommendation": "Add descriptive alt text to all images. Alt text should describe the image content for accessibility and SEO.",
                "quick_win": False
            })

        return issues

    def _analyze_structure_issues(self, structure_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze site structure issues"""
        issues = []
        details = structure_data.get("details", {})

        # Internal Linking
        linking = details.get("internal_linking", {})
        orphan_count = linking.get("orphan_pages", 0)
        if linking.get("score", 0) < 5 and orphan_count > 0:
            issues.append({
                "issue": "Orphan pages (no internal links)",
                "severity": IssueSeverity.WARNING if orphan_count <= 5 else IssueSeverity.CRITICAL,
                "impact": 5 - linking.get("score", 0),
                "effort": IssueEffort.MEDIUM,
                "pages_affected": f"{orphan_count} pages",
                "current_value": f"{orphan_count} orphan pages",
                "target_value": "0 orphan pages",
                "recommendation": "Add internal links to orphan pages from related content. Ensure all pages are accessible via navigation or contextual links.",
                "quick_win": False
            })

        # Broken Links
        broken = details.get("broken_links", {})
        broken_count = broken.get("broken_count", 0)
        if broken.get("score", 0) < 3 and broken_count > 0:
            issues.append({
                "issue": "Broken links detected",
                "severity": IssueSeverity.CRITICAL if broken_count > 5 else IssueSeverity.WARNING,
                "impact": 3 - broken.get("score", 0),
                "effort": IssueEffort.LOW,
                "pages_affected": f"{broken_count} broken links",
                "current_value": f"{broken_count} broken links",
                "target_value": "0 broken links",
                "recommendation": "Fix or remove all broken links. Update links to point to correct URLs or remove if no longer needed.",
                "quick_win": True
            })

        # URL Structure
        urls = details.get("url_structure", {})
        long_urls = urls.get("long_urls", 0)
        if urls.get("score", 0) < 2 and long_urls > 0:
            issues.append({
                "issue": "URLs too long",
                "severity": IssueSeverity.INFO,
                "impact": 2 - urls.get("score", 0),
                "effort": IssueEffort.HIGH,
                "pages_affected": f"{long_urls} pages",
                "current_value": f"{long_urls} long URLs (>100 chars)",
                "target_value": "<10% URLs >100 chars",
                "recommendation": "Shorten URLs by removing unnecessary parameters and using clean, descriptive paths. Implement 301 redirects when changing URLs.",
                "quick_win": False
            })

        return issues

    def _get_speed_recommendation(self, avg_load_time: int) -> str:
        """Get specific speed recommendation based on load time"""
        if avg_load_time > 7000:
            return (
                "Critical speed issues detected. Optimize images, enable compression, "
                "minimize CSS/JS, and consider using a CDN. Reduce server response time."
            )
        elif avg_load_time > 5000:
            return (
                "Optimize images, enable browser caching, minify CSS/JS files, "
                "and reduce number of HTTP requests."
            )
        else:
            return (
                "Minor speed improvements possible. Consider lazy loading images "
                "and optimizing third-party scripts."
            )


# Test function
def test_analyzer():
    """Test the issue analyzer with mock score data"""
    # Mock score data
    mock_scores = {
        "total_score": 18,
        "technical_seo": {
            "score": 6,
            "details": {
                "page_speed": {"score": 1, "avg_load_time_ms": 6500},
                "mobile_optimization": {"score": 2, "mobile_friendly_percentage": 85},
                "https": {"score": 1, "https_percentage": 60},
                "xml_sitemap": {"score": 1},
                "robots_txt": {"score": 1}
            }
        },
        "onpage_seo": {
            "score": 5,
            "details": {
                "title_tags": {"score": 1, "missing": 5, "duplicates": 3},
                "meta_descriptions": {"score": 2, "missing": 8},
                "h1_tags": {"score": 1, "missing": 4},
                "image_alt_text": {"score": 1, "missing_percentage": 45}
            }
        },
        "structure_seo": {
            "score": 7,
            "details": {
                "internal_linking": {"score": 3, "orphan_pages": 4},
                "broken_links": {"score": 2, "broken_count": 3},
                "url_structure": {"score": 2, "long_urls": 12}
            }
        }
    }

    analyzer = IssueAnalyzer()
    result = analyzer.analyze_issues(mock_scores)

    print("\n=== Issue Analysis Report ===")
    print(f"\nTotal Issues: {result['summary']['total_issues']}")
    print(f"Critical: {result['summary']['critical_count']}")
    print(f"Warnings: {result['summary']['warning_count']}")
    print(f"Info: {result['summary']['info_count']}")
    print(f"Quick Wins: {result['summary']['quick_win_count']}")

    print("\n=== Top 3 Quick Wins ===")
    for i, issue in enumerate(result['quick_wins'][:3], 1):
        print(f"\n{i}. {issue['issue']}")
        print(f"   Impact: +{issue['impact']} points")
        print(f"   Effort: {issue['effort']}")
        print(f"   Recommendation: {issue['recommendation']}")


if __name__ == "__main__":
    test_analyzer()
