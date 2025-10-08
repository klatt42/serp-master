"""
Traditional SEO Scorer
Calculates 30-point traditional SEO score based on crawl data
Scoring dimensions: Technical SEO (10pts), On-Page SEO (10pts), Site Structure (10pts)
"""

import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOScorer:
    """
    Calculates traditional SEO scores from crawl data
    Total: 30 points (Technical 10 + On-Page 10 + Structure 10)
    """

    def __init__(self):
        """Initialize the SEO scorer"""
        logger.info("SEO Scorer initialized")

    def calculate_total_seo_score(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate complete SEO score breakdown

        Args:
            crawl_data: Parsed crawl data from SiteCrawler

        Returns:
            Complete scoring breakdown

        Example:
            {
                "total_score": 25,
                "max_score": 30,
                "percentage": 83.3,
                "technical_seo": {...},
                "onpage_seo": {...},
                "structure_seo": {...}
            }
        """
        try:
            logger.info("Calculating complete SEO score")

            # Calculate individual dimensions
            technical = self.calculate_technical_seo(crawl_data)
            onpage = self.calculate_onpage_seo(crawl_data)
            structure = self.calculate_structure_seo(crawl_data)

            # Calculate total
            total_score = technical["score"] + onpage["score"] + structure["score"]
            max_score = 30
            percentage = round((total_score / max_score) * 100, 1)

            result = {
                "total_score": total_score,
                "max_score": max_score,
                "percentage": percentage,
                "grade": self._get_grade(percentage),
                "technical_seo": technical,
                "onpage_seo": onpage,
                "structure_seo": structure,
                "summary": {
                    "total_pages_analyzed": len(crawl_data.get("pages", [])),
                    "pages_with_issues": crawl_data.get("summary", {}).get("pages_with_issues", 0),
                    "total_issues": crawl_data.get("summary", {}).get("total_issues", 0)
                }
            }

            logger.info(f"Total SEO Score: {total_score}/{max_score} ({percentage}%) - Grade: {result['grade']}")

            return result

        except Exception as e:
            logger.error(f"Error calculating SEO score: {str(e)}")
            raise

    def calculate_technical_seo(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Technical SEO score (10 points)

        Breakdown:
        - Page Speed (3 pts): <3s=3, 3-5s=2, >5s=1
        - Mobile Optimization (3 pts): All mobile=3, 90%+=2, <90%=1
        - HTTPS (2 pts): All HTTPS=2, Mixed=1, HTTP=0
        - XML Sitemap (1 pt): Present=1, Missing=0
        - Robots.txt (1 pt): Present=1, Missing=0

        Args:
            crawl_data: Parsed crawl data

        Returns:
            Technical SEO score breakdown
        """
        pages = crawl_data.get("pages", [])
        total_pages = len(pages)

        if total_pages == 0:
            return {"score": 0, "max_score": 10, "details": {}, "issues": ["No pages crawled"]}

        # === Page Speed (3 points) ===
        load_times = [p.get("page_metrics", {}).get("load_time_ms", 5000) for p in pages]
        avg_load_time = sum(load_times) / len(load_times) if load_times else 5000

        if avg_load_time < 3000:
            speed_score = 3
            speed_status = "Excellent"
        elif avg_load_time < 5000:
            speed_score = 2
            speed_status = "Good"
        else:
            speed_score = 1
            speed_status = "Needs Improvement"

        # === Mobile Optimization (3 points) ===
        # Note: DataForSEO checks this via page_timing and responsive design
        # For now, we'll use a heuristic based on viewport meta tag presence
        mobile_friendly_count = sum(
            1 for p in pages
            if p.get("checks", {}).get("is_mobile_friendly", True)
        )
        mobile_percentage = (mobile_friendly_count / total_pages * 100) if total_pages > 0 else 0

        if mobile_percentage == 100:
            mobile_score = 3
            mobile_status = "All pages mobile-friendly"
        elif mobile_percentage >= 90:
            mobile_score = 2
            mobile_status = f"{mobile_percentage:.0f}% mobile-friendly"
        else:
            mobile_score = 1
            mobile_status = f"Only {mobile_percentage:.0f}% mobile-friendly"

        # === HTTPS (2 points) ===
        https_count = sum(1 for p in pages if p.get("is_https", False))
        https_percentage = (https_count / total_pages * 100) if total_pages > 0 else 0

        if https_percentage == 100:
            https_score = 2
            https_status = "All pages secure (HTTPS)"
        elif https_percentage > 0:
            https_score = 1
            https_status = f"Mixed content ({https_percentage:.0f}% HTTPS)"
        else:
            https_score = 0
            https_status = "No HTTPS pages found"

        # === XML Sitemap (1 point) ===
        # Check if sitemap was found in crawl (look for sitemap.xml in URLs)
        has_sitemap = any("sitemap" in p.get("url", "").lower() for p in pages)
        sitemap_score = 1 if has_sitemap else 0
        sitemap_status = "Present" if has_sitemap else "Not found"

        # === Robots.txt (1 point) ===
        # Check if robots.txt was found
        has_robots = any("robots.txt" in p.get("url", "").lower() for p in pages)
        robots_score = 1 if has_robots else 0
        robots_status = "Present" if has_robots else "Not found"

        # Calculate total
        total_score = speed_score + mobile_score + https_score + sitemap_score + robots_score

        return {
            "score": total_score,
            "max_score": 10,
            "details": {
                "page_speed": {
                    "score": speed_score,
                    "max_score": 3,
                    "avg_load_time_ms": round(avg_load_time),
                    "status": speed_status
                },
                "mobile_optimization": {
                    "score": mobile_score,
                    "max_score": 3,
                    "mobile_friendly_percentage": round(mobile_percentage, 1),
                    "status": mobile_status
                },
                "https": {
                    "score": https_score,
                    "max_score": 2,
                    "https_percentage": round(https_percentage, 1),
                    "status": https_status
                },
                "xml_sitemap": {
                    "score": sitemap_score,
                    "max_score": 1,
                    "status": sitemap_status
                },
                "robots_txt": {
                    "score": robots_score,
                    "max_score": 1,
                    "status": robots_status
                }
            },
            "issues": self._get_technical_issues(
                speed_score, mobile_score, https_score, sitemap_score, robots_score
            )
        }

    def calculate_onpage_seo(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate On-Page SEO score (10 points)

        Breakdown:
        - Title Tags (3 pts): No missing/duplicates=3, <10% issues=2, >10%=1
        - Meta Descriptions (3 pts): No missing=3, <10%=2, >10%=1
        - H1 Tags (2 pts): All pages have H1=2, <10% missing=1, >10%=0
        - Image Alt Text (2 pts): <20% missing=2, 20-50%=1, >50%=0

        Args:
            crawl_data: Parsed crawl data

        Returns:
            On-Page SEO score breakdown
        """
        pages = crawl_data.get("pages", [])
        total_pages = len(pages)

        if total_pages == 0:
            return {"score": 0, "max_score": 10, "details": {}, "issues": ["No pages crawled"]}

        # === Title Tags (3 points) ===
        missing_titles = sum(1 for p in pages if not p.get("meta", {}).get("title"))
        duplicate_titles = self._count_duplicates([p.get("meta", {}).get("title", "") for p in pages])
        title_issues = missing_titles + duplicate_titles
        title_issue_percentage = (title_issues / total_pages * 100) if total_pages > 0 else 100

        if title_issue_percentage == 0:
            title_score = 3
            title_status = "All titles present and unique"
        elif title_issue_percentage < 10:
            title_score = 2
            title_status = f"{title_issue_percentage:.0f}% have issues"
        else:
            title_score = 1
            title_status = f"{title_issue_percentage:.0f}% have issues"

        # === Meta Descriptions (3 points) ===
        missing_descriptions = sum(1 for p in pages if not p.get("meta", {}).get("description"))
        desc_issue_percentage = (missing_descriptions / total_pages * 100) if total_pages > 0 else 100

        if desc_issue_percentage == 0:
            desc_score = 3
            desc_status = "All descriptions present"
        elif desc_issue_percentage < 10:
            desc_score = 2
            desc_status = f"{desc_issue_percentage:.0f}% missing"
        else:
            desc_score = 1
            desc_status = f"{desc_issue_percentage:.0f}% missing"

        # === H1 Tags (2 points) ===
        missing_h1 = sum(
            1 for p in pages
            if not p.get("meta", {}).get("h1") or len(p.get("meta", {}).get("h1", [])) == 0
        )
        h1_issue_percentage = (missing_h1 / total_pages * 100) if total_pages > 0 else 100

        if h1_issue_percentage == 0:
            h1_score = 2
            h1_status = "All pages have H1"
        elif h1_issue_percentage < 10:
            h1_score = 1
            h1_status = f"{h1_issue_percentage:.0f}% missing H1"
        else:
            h1_score = 0
            h1_status = f"{h1_issue_percentage:.0f}% missing H1"

        # === Image Alt Text (2 points) ===
        # Note: We need to check images with missing alt text
        # For now, we'll use a placeholder calculation
        # TODO: Extract image data from crawl results
        alt_missing_percentage = 30  # Placeholder

        if alt_missing_percentage < 20:
            alt_score = 2
            alt_status = "Most images have alt text"
        elif alt_missing_percentage < 50:
            alt_score = 1
            alt_status = f"{alt_missing_percentage:.0f}% missing alt text"
        else:
            alt_score = 0
            alt_status = f"{alt_missing_percentage:.0f}% missing alt text"

        # Calculate total
        total_score = title_score + desc_score + h1_score + alt_score

        return {
            "score": total_score,
            "max_score": 10,
            "details": {
                "title_tags": {
                    "score": title_score,
                    "max_score": 3,
                    "missing": missing_titles,
                    "duplicates": duplicate_titles,
                    "issue_percentage": round(title_issue_percentage, 1),
                    "status": title_status
                },
                "meta_descriptions": {
                    "score": desc_score,
                    "max_score": 3,
                    "missing": missing_descriptions,
                    "issue_percentage": round(desc_issue_percentage, 1),
                    "status": desc_status
                },
                "h1_tags": {
                    "score": h1_score,
                    "max_score": 2,
                    "missing": missing_h1,
                    "issue_percentage": round(h1_issue_percentage, 1),
                    "status": h1_status
                },
                "image_alt_text": {
                    "score": alt_score,
                    "max_score": 2,
                    "missing_percentage": alt_missing_percentage,
                    "status": alt_status
                }
            },
            "issues": self._get_onpage_issues(
                missing_titles, duplicate_titles, missing_descriptions, missing_h1
            )
        }

    def calculate_structure_seo(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Site Structure score (10 points)

        Breakdown:
        - Internal Linking (5 pts): No orphans=5, 1-5 orphans=3, >5=1
        - Broken Links (3 pts): Zero=3, 1-5=2, >5=0
        - URL Structure (2 pts): <10% long URLs=2, 10-30%=1, >30%=0

        Args:
            crawl_data: Parsed crawl data

        Returns:
            Site Structure score breakdown
        """
        pages = crawl_data.get("pages", [])
        total_pages = len(pages)

        if total_pages == 0:
            return {"score": 0, "max_score": 10, "details": {}, "issues": ["No pages crawled"]}

        # === Internal Linking (5 points) ===
        # Count orphan pages (pages with no internal links pointing to them)
        # This is a simplified check - in production we'd analyze link graph
        orphan_count = 0  # Placeholder - need to analyze internal links
        # TODO: Implement proper orphan page detection

        if orphan_count == 0:
            linking_score = 5
            linking_status = "No orphan pages"
        elif orphan_count <= 5:
            linking_score = 3
            linking_status = f"{orphan_count} orphan pages"
        else:
            linking_score = 1
            linking_status = f"{orphan_count} orphan pages"

        # === Broken Links (3 points) ===
        broken_count = sum(
            1 for p in pages
            if p.get("status_code") and p["status_code"] >= 400
        )

        if broken_count == 0:
            broken_score = 3
            broken_status = "No broken links"
        elif broken_count <= 5:
            broken_score = 2
            broken_status = f"{broken_count} broken links"
        else:
            broken_score = 0
            broken_status = f"{broken_count} broken links"

        # === URL Structure (2 points) ===
        long_urls = sum(1 for p in pages if len(p.get("url", "")) > 100)
        long_url_percentage = (long_urls / total_pages * 100) if total_pages > 0 else 0

        if long_url_percentage < 10:
            url_score = 2
            url_status = "Clean URL structure"
        elif long_url_percentage < 30:
            url_score = 1
            url_status = f"{long_url_percentage:.0f}% URLs too long"
        else:
            url_score = 0
            url_status = f"{long_url_percentage:.0f}% URLs too long"

        # Calculate total
        total_score = linking_score + broken_score + url_score

        return {
            "score": total_score,
            "max_score": 10,
            "details": {
                "internal_linking": {
                    "score": linking_score,
                    "max_score": 5,
                    "orphan_pages": orphan_count,
                    "status": linking_status
                },
                "broken_links": {
                    "score": broken_score,
                    "max_score": 3,
                    "broken_count": broken_count,
                    "status": broken_status
                },
                "url_structure": {
                    "score": url_score,
                    "max_score": 2,
                    "long_urls": long_urls,
                    "long_url_percentage": round(long_url_percentage, 1),
                    "status": url_status
                }
            },
            "issues": self._get_structure_issues(orphan_count, broken_count, long_urls)
        }

    def _get_grade(self, percentage: float) -> str:
        """Get letter grade from percentage"""
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

    def _count_duplicates(self, items: List[str]) -> int:
        """Count number of duplicate items in list"""
        seen = set()
        duplicates = 0
        for item in items:
            if item and item in seen:
                duplicates += 1
            seen.add(item)
        return duplicates

    def _get_technical_issues(
        self, speed_score: int, mobile_score: int, https_score: int,
        sitemap_score: int, robots_score: int
    ) -> List[str]:
        """Generate list of technical issues"""
        issues = []
        if speed_score < 3:
            issues.append("Page speed needs improvement")
        if mobile_score < 3:
            issues.append("Mobile optimization issues detected")
        if https_score < 2:
            issues.append("Not all pages use HTTPS")
        if sitemap_score < 1:
            issues.append("XML sitemap not found")
        if robots_score < 1:
            issues.append("robots.txt not found")
        return issues

    def _get_onpage_issues(
        self, missing_titles: int, duplicate_titles: int,
        missing_descriptions: int, missing_h1: int
    ) -> List[str]:
        """Generate list of on-page issues"""
        issues = []
        if missing_titles > 0:
            issues.append(f"{missing_titles} pages missing title tags")
        if duplicate_titles > 0:
            issues.append(f"{duplicate_titles} duplicate title tags")
        if missing_descriptions > 0:
            issues.append(f"{missing_descriptions} pages missing meta descriptions")
        if missing_h1 > 0:
            issues.append(f"{missing_h1} pages missing H1 tags")
        return issues

    def _get_structure_issues(
        self, orphan_count: int, broken_count: int, long_urls: int
    ) -> List[str]:
        """Generate list of structure issues"""
        issues = []
        if orphan_count > 0:
            issues.append(f"{orphan_count} orphan pages (no internal links)")
        if broken_count > 0:
            issues.append(f"{broken_count} broken links")
        if long_urls > 0:
            issues.append(f"{long_urls} URLs too long (>100 chars)")
        return issues


# Test function
def test_scorer():
    """Test the SEO scorer with mock data"""
    # Mock crawl data
    mock_data = {
        "summary": {
            "pages_crawled": 10,
            "pages_with_issues": 3,
            "total_issues": 8
        },
        "pages": [
            {
                "url": "https://example.com",
                "is_https": True,
                "meta": {"title": "Example", "description": "Test", "h1": ["Main Heading"]},
                "page_metrics": {"load_time_ms": 2500},
                "status_code": 200,
                "checks": {"is_mobile_friendly": True}
            },
            {
                "url": "https://example.com/page2",
                "is_https": True,
                "meta": {"title": "", "description": "Test 2", "h1": []},
                "page_metrics": {"load_time_ms": 4000},
                "status_code": 200,
                "checks": {"is_mobile_friendly": True}
            }
        ]
    }

    scorer = SEOScorer()
    result = scorer.calculate_total_seo_score(mock_data)

    print("\n=== SEO Score Report ===")
    print(f"Total Score: {result['total_score']}/{result['max_score']} ({result['percentage']}%)")
    print(f"Grade: {result['grade']}")
    print(f"\nTechnical SEO: {result['technical_seo']['score']}/10")
    print(f"On-Page SEO: {result['onpage_seo']['score']}/10")
    print(f"Site Structure: {result['structure_seo']['score']}/10")


if __name__ == "__main__":
    test_scorer()
