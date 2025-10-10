"""
NAP Consistency Auditor
Analyzes Name, Address, Phone consistency across citation sources
"""

import logging
import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from fuzzywuzzy import fuzz
from pathlib import Path

from app.models.local_models import (
    CitationSource,
    NAPInconsistency,
    CitationAuditRequest,
    CitationAuditResponse
)

logger = logging.getLogger(__name__)


class NAPAuditor:
    """Audit NAP consistency across local citation sources"""

    def __init__(self):
        """Initialize NAP auditor"""
        # Load citation sources
        sources_path = Path(__file__).parent.parent.parent.parent / "data" / "citation_sources.json"
        with open(sources_path, 'r') as f:
            self.citation_data = json.load(f)

        # Major platforms that are critical
        self.major_platforms = [
            "Google Business Profile",
            "Yelp",
            "Facebook Business",
            "Apple Maps",
            "Bing Places",
            "Better Business Bureau",
            "LinkedIn Company",
            "Yellow Pages",
            "Foursquare",
            "TripAdvisor"
        ]

        # Similarity thresholds
        self.name_threshold = 85  # 85% similarity required
        self.address_threshold = 80  # 80% similarity required
        self.phone_threshold = 90  # 90% similarity required

    async def audit_citations(
        self,
        request: CitationAuditRequest,
        site_data: Optional[Dict] = None
    ) -> CitationAuditResponse:
        """
        Perform comprehensive citation audit

        Args:
            request: Citation audit request with NAP data
            site_data: Optional additional site data

        Returns:
            Citation audit response with findings
        """
        try:
            # Extract business info
            business_info = {
                "name": request.business_name,
                "address": request.address,
                "phone": request.phone,
                "website": request.site_url
            }

            # Simulate citation search (in production would query APIs/scrape)
            citations_found = self._simulate_citation_search(business_info)

            # Analyze consistency
            inconsistencies = self._analyze_consistency(
                business_info,
                citations_found
            )

            # Calculate scores
            consistency_score = self._calculate_consistency_score(
                len(citations_found),
                inconsistencies
            )

            citation_score = self._calculate_citation_score(
                len(citations_found),
                consistency_score
            )

            # Identify major platform coverage
            major_found = [c for c in citations_found if c.name in self.major_platforms]
            major_coverage = len(major_found)

            missing_major = [p for p in self.major_platforms
                            if p not in [c.name for c in citations_found]]

            # Generate recommendations
            recommendations = self._generate_recommendations(
                citations_found,
                inconsistencies,
                missing_major,
                consistency_score
            )

            return CitationAuditResponse(
                citations_found=citations_found,
                total_citations=len(citations_found),
                major_platform_coverage=major_coverage,
                inconsistencies=inconsistencies,
                consistency_score=consistency_score,
                citation_score=citation_score,
                missing_major_platforms=missing_major,
                recommendations=recommendations,
                analyzed_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error auditing citations: {str(e)}")
            raise

    def _simulate_citation_search(
        self,
        business_info: Dict
    ) -> List[CitationSource]:
        """
        Simulate citation search across platforms
        In production, this would query APIs or scrape directories
        """
        citations = []

        # Simulate finding business on major platforms with slight variations
        variations = [
            # Google Business Profile - exact match
            {
                "name": "Google Business Profile",
                "business_name": business_info["name"],
                "address": business_info["address"],
                "phone": business_info["phone"],
                "importance": 10
            },
            # Yelp - slight name variation
            {
                "name": "Yelp",
                "business_name": business_info["name"].replace("LLC", "").strip(),
                "address": business_info["address"],
                "phone": self._format_phone_variation(business_info["phone"], 1),
                "importance": 9
            },
            # Facebook - different address format
            {
                "name": "Facebook Business",
                "business_name": business_info["name"],
                "address": self._format_address_variation(business_info["address"], 1),
                "phone": business_info["phone"],
                "importance": 9
            },
            # Apple Maps - good match
            {
                "name": "Apple Maps",
                "business_name": business_info["name"],
                "address": business_info["address"],
                "phone": business_info["phone"],
                "importance": 8
            },
            # BBB - slight variations
            {
                "name": "Better Business Bureau",
                "business_name": business_info["name"] + ", LLC",
                "address": self._format_address_variation(business_info["address"], 2),
                "phone": self._format_phone_variation(business_info["phone"], 2),
                "importance": 8
            },
            # Yellow Pages
            {
                "name": "Yellow Pages",
                "business_name": business_info["name"],
                "address": business_info["address"],
                "phone": business_info["phone"],
                "importance": 7
            }
        ]

        for var in variations:
            citation = CitationSource(
                name=var["name"],
                category="major",
                importance=var["importance"],
                business_name=var["business_name"],
                address=var["address"],
                phone=var["phone"],
                website=business_info.get("website")
            )
            citations.append(citation)

        return citations

    def _format_phone_variation(self, phone: str, variation: int) -> str:
        """Create phone number format variations"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)

        if variation == 1:
            # Format: (XXX) XXX-XXXX
            if len(digits) >= 10:
                return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
        elif variation == 2:
            # Format: XXX-XXX-XXXX
            if len(digits) >= 10:
                return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"
        elif variation == 3:
            # Format: XXX.XXX.XXXX
            if len(digits) >= 10:
                return f"{digits[0:3]}.{digits[3:6]}.{digits[6:10]}"

        return phone

    def _format_address_variation(self, address: str, variation: int) -> str:
        """Create address format variations"""
        if variation == 1:
            # Abbreviate Street, Avenue, etc.
            address = address.replace("Street", "St")
            address = address.replace("Avenue", "Ave")
            address = address.replace("Boulevard", "Blvd")
            address = address.replace("Road", "Rd")
        elif variation == 2:
            # Full word versions
            address = address.replace("St", "Street")
            address = address.replace("Ave", "Avenue")
            address = address.replace("Blvd", "Boulevard")
            address = address.replace("Rd", "Road")

        return address

    def _analyze_consistency(
        self,
        business_info: Dict,
        citations: List[CitationSource]
    ) -> List[NAPInconsistency]:
        """Analyze NAP consistency across citations"""
        inconsistencies = []

        # Compare each citation against the business info
        for citation in citations:
            # Check business name
            if citation.business_name:
                name_similarity = fuzz.ratio(
                    business_info["name"].lower(),
                    citation.business_name.lower()
                )

                if name_similarity < self.name_threshold:
                    severity = "critical" if name_similarity < 70 else "high" if name_similarity < 80 else "medium"

                    inconsistencies.append(NAPInconsistency(
                        field="name",
                        source1="Website",
                        source2=citation.name,
                        value1=business_info["name"],
                        value2=citation.business_name,
                        similarity=name_similarity / 100,
                        severity=severity,
                        suggestion=f"Standardize business name to: {business_info['name']}"
                    ))

            # Check address
            if citation.address:
                address_similarity = fuzz.ratio(
                    self._normalize_address(business_info["address"]).lower(),
                    self._normalize_address(citation.address).lower()
                )

                if address_similarity < self.address_threshold:
                    severity = "high" if address_similarity < 70 else "medium"

                    inconsistencies.append(NAPInconsistency(
                        field="address",
                        source1="Website",
                        source2=citation.name,
                        value1=business_info["address"],
                        value2=citation.address,
                        similarity=address_similarity / 100,
                        severity=severity,
                        suggestion=f"Standardize address format across all platforms"
                    ))

            # Check phone
            if citation.phone:
                phone1_normalized = self._normalize_phone(business_info["phone"])
                phone2_normalized = self._normalize_phone(citation.phone)

                phone_similarity = fuzz.ratio(phone1_normalized, phone2_normalized)

                if phone_similarity < self.phone_threshold:
                    severity = "critical" if phone_similarity < 80 else "high"

                    inconsistencies.append(NAPInconsistency(
                        field="phone",
                        source1="Website",
                        source2=citation.name,
                        value1=business_info["phone"],
                        value2=citation.phone,
                        similarity=phone_similarity / 100,
                        severity=severity,
                        suggestion=f"Use consistent phone format: {business_info['phone']}"
                    ))

        return inconsistencies

    def _normalize_address(self, address: str) -> str:
        """Normalize address for comparison"""
        # Remove extra spaces
        address = ' '.join(address.split())

        # Common abbreviations mapping
        abbrev_map = {
            'street': 'st', 'avenue': 'ave', 'boulevard': 'blvd',
            'road': 'rd', 'drive': 'dr', 'lane': 'ln', 'court': 'ct',
            'place': 'pl', 'suite': 'ste', 'apartment': 'apt'
        }

        address_lower = address.lower()
        for full, abbr in abbrev_map.items():
            address_lower = address_lower.replace(full, abbr)

        return address_lower

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for comparison"""
        # Remove all non-digits
        return re.sub(r'\D', '', phone)

    def _calculate_consistency_score(
        self,
        total_citations: int,
        inconsistencies: List[NAPInconsistency]
    ) -> int:
        """Calculate consistency score (0-100)"""
        if total_citations == 0:
            return 0

        # Count severity of inconsistencies
        critical_count = len([i for i in inconsistencies if i.severity == "critical"])
        high_count = len([i for i in inconsistencies if i.severity == "high"])
        medium_count = len([i for i in inconsistencies if i.severity == "medium"])
        low_count = len([i for i in inconsistencies if i.severity == "low"])

        # Start with perfect score
        score = 100

        # Deduct points based on severity
        score -= critical_count * 20
        score -= high_count * 10
        score -= medium_count * 5
        score -= low_count * 2

        return max(0, score)

    def _calculate_citation_score(
        self,
        total_citations: int,
        consistency_score: int
    ) -> int:
        """
        Calculate citation score (0-8 points for GEO score)

        4 points for NAP consistency
        4 points for citation count
        """
        # NAP consistency score (0-4 points)
        if consistency_score >= 95:
            nap_points = 4
        elif consistency_score >= 85:
            nap_points = 3
        elif consistency_score >= 75:
            nap_points = 2
        elif consistency_score >= 60:
            nap_points = 1
        else:
            nap_points = 0

        # Citation count score (0-4 points)
        # Major platforms coverage
        if total_citations >= 8:  # 8+ citations
            count_points = 4
        elif total_citations >= 6:  # 6-7 citations
            count_points = 3
        elif total_citations >= 4:  # 4-5 citations
            count_points = 2
        elif total_citations >= 2:  # 2-3 citations
            count_points = 1
        else:
            count_points = 0

        return nap_points + count_points

    def _generate_recommendations(
        self,
        citations: List[CitationSource],
        inconsistencies: List[NAPInconsistency],
        missing_platforms: List[str],
        consistency_score: int
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Consistency recommendations
        if consistency_score < 80:
            recommendations.append(
                "⚠️ CRITICAL: NAP inconsistencies detected. Fix these immediately to improve local SEO."
            )

            # Group inconsistencies by field
            name_issues = [i for i in inconsistencies if i.field == "name"]
            address_issues = [i for i in inconsistencies if i.field == "address"]
            phone_issues = [i for i in inconsistencies if i.field == "phone"]

            if name_issues:
                recommendations.append(
                    f"Business name varies across {len(name_issues)} platforms. Standardize to exact legal name."
                )

            if address_issues:
                recommendations.append(
                    f"Address format inconsistent on {len(address_issues)} platforms. Use full format with standard abbreviations."
                )

            if phone_issues:
                recommendations.append(
                    f"Phone number format varies on {len(phone_issues)} platforms. Use (XXX) XXX-XXXX format consistently."
                )

        # Missing platform recommendations
        if missing_platforms:
            recommendations.append(
                f"Not found on {len(missing_platforms)} major platforms. Add your business to: {', '.join(missing_platforms[:3])}"
            )

        # Citation count recommendations
        if len(citations) < 5:
            recommendations.append(
                "Build more citations. Target 10+ high-quality directories for your industry."
            )

        # Data aggregator recommendation
        if len(citations) < 10:
            recommendations.append(
                "Consider using data aggregators (Neustar Localeze, Data Axle) to distribute NAP to 100+ directories automatically."
            )

        # Best practices
        recommendations.append(
            "Ensure NAP on website footer exactly matches Google Business Profile."
        )

        if consistency_score >= 95:
            recommendations.append(
                "✅ Excellent NAP consistency! Maintain this across all future citations."
            )

        return recommendations
