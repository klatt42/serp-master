"""
NAP Consistency Validator
Validates Name, Address, Phone consistency across web presence
"""

import logging
import re
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from difflib import SequenceMatcher

from app.models.entity_models import (
    NAPData,
    NAPInconsistency,
    NAPValidationRequest,
    NAPValidationResponse
)

logger = logging.getLogger(__name__)


class NAPValidator:
    """Validate NAP consistency for local SEO and entity recognition"""

    def __init__(self):
        """Initialize NAP validator"""
        # US state abbreviations
        self.state_abbr = {
            "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
            "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
            "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
            "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
            "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
            "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
            "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
            "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
            "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
            "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
            "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
            "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
            "Wisconsin": "WI", "Wyoming": "WY"
        }

    async def validate_nap(
        self,
        request: NAPValidationRequest,
        site_data: Optional[Dict] = None
    ) -> NAPValidationResponse:
        """
        Validate NAP consistency across web presence

        Args:
            request: NAP validation request
            site_data: Optional pre-analyzed site data

        Returns:
            Response with NAP validation results
        """
        try:
            # Extract NAP data from various sources
            nap_data_found = await self._extract_nap_data(
                request.site_url,
                site_data
            )

            # Detect inconsistencies
            inconsistencies = self._detect_inconsistencies(
                nap_data_found,
                request.expected_nap
            )

            # Calculate consistency score
            consistency_score = self._calculate_consistency_score(
                nap_data_found,
                inconsistencies
            )

            # Create standardized NAP
            standardized_nap = self._create_standardized_nap(
                nap_data_found,
                request.expected_nap
            )

            # Generate recommendations
            recommendations = self._generate_nap_recommendations(
                inconsistencies,
                consistency_score,
                nap_data_found
            )

            # Identify citation opportunities
            citation_opportunities = self._identify_citation_opportunities(
                nap_data_found
            )

            return NAPValidationResponse(
                nap_data_found=nap_data_found,
                inconsistencies=inconsistencies,
                consistency_score=consistency_score,
                standardized_nap=standardized_nap,
                recommendations=recommendations,
                citation_opportunities=citation_opportunities,
                validated_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error validating NAP: {str(e)}")
            raise

    async def _extract_nap_data(
        self,
        site_url: str,
        site_data: Optional[Dict]
    ) -> List[NAPData]:
        """Extract NAP data from various sources"""
        nap_data = []

        if not site_data:
            return nap_data

        # Extract from homepage
        if site_data.get("content"):
            homepage_nap = self._extract_from_content(
                site_data["content"],
                "homepage"
            )
            if homepage_nap:
                nap_data.append(homepage_nap)

        # Extract from contact page
        if site_data.get("contact_content"):
            contact_nap = self._extract_from_content(
                site_data["contact_content"],
                "contact page"
            )
            if contact_nap:
                nap_data.append(contact_nap)

        # Extract from footer
        if site_data.get("footer_content"):
            footer_nap = self._extract_from_content(
                site_data["footer_content"],
                "footer"
            )
            if footer_nap:
                nap_data.append(footer_nap)

        # Extract from schema markup
        if site_data.get("existing_schema"):
            for schema in site_data["existing_schema"]:
                schema_nap = self._extract_from_schema(schema)
                if schema_nap:
                    nap_data.append(schema_nap)

        # Extract from meta tags
        if site_data.get("meta_tags"):
            meta_nap = self._extract_from_meta(site_data["meta_tags"])
            if meta_nap:
                nap_data.append(meta_nap)

        # Use provided data
        if site_data.get("business_name") or site_data.get("address") or site_data.get("phone"):
            nap_data.append(NAPData(
                business_name=site_data.get("business_name", ""),
                address=self._format_address_string(site_data.get("address", "")),
                phone=self._format_phone(site_data.get("phone", "")),
                hours=site_data.get("hours"),
                source="site data"
            ))

        return nap_data

    def _extract_from_content(self, content: str, source: str) -> Optional[NAPData]:
        """Extract NAP from text content"""
        if not content:
            return None

        # Extract business name (capitalized words at start)
        name_match = re.search(r'^([A-Z][a-zA-Z\s&]+(?:LLC|Inc|Corp)?)', content)
        business_name = name_match.group(1).strip() if name_match else ""

        # Extract phone
        phone_pattern = r'(?:phone|tel|call)?\s*:?\s*(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
        phone_match = re.search(phone_pattern, content, re.IGNORECASE)
        phone = self._format_phone(phone_match.group(1)) if phone_match else ""

        # Extract address
        address = self._extract_address(content)

        # Extract hours
        hours = self._extract_hours(content)

        # Only create if we found something
        if business_name or phone or address:
            return NAPData(
                business_name=business_name,
                address=address,
                phone=phone,
                hours=hours,
                source=source
            )

        return None

    def _extract_from_schema(self, schema: Dict) -> Optional[NAPData]:
        """Extract NAP from schema markup"""
        business_name = schema.get("name", "")
        phone = ""
        address = ""
        hours = ""

        # Get phone
        if schema.get("telephone"):
            phone = self._format_phone(schema["telephone"])

        # Get address
        if schema.get("address"):
            addr = schema["address"]
            if isinstance(addr, dict):
                address = self._format_address_dict(addr)
            elif isinstance(addr, str):
                address = addr

        # Get hours
        if schema.get("openingHours"):
            hours = str(schema["openingHours"])
        elif schema.get("openingHoursSpecification"):
            hours = "See schema"

        if business_name or phone or address:
            return NAPData(
                business_name=business_name,
                address=address,
                phone=phone,
                hours=hours,
                source="schema markup"
            )

        return None

    def _extract_from_meta(self, meta_tags: Dict) -> Optional[NAPData]:
        """Extract NAP from meta tags"""
        business_name = ""
        phone = ""
        address = ""

        # Check various meta tag patterns
        for key, value in meta_tags.items():
            if "business" in key.lower() or "company" in key.lower():
                business_name = value
            elif "phone" in key.lower() or "tel" in key.lower():
                phone = self._format_phone(value)
            elif "address" in key.lower():
                address = value

        if business_name or phone or address:
            return NAPData(
                business_name=business_name,
                address=address,
                phone=phone,
                source="meta tags"
            )

        return None

    def _extract_address(self, content: str) -> str:
        """Extract address from content"""
        # Pattern for street address
        street_pattern = r'\b\d+\s+[A-Z][a-zA-Z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)\b'
        street_match = re.search(street_pattern, content, re.IGNORECASE)

        if not street_match:
            return ""

        # Find city, state, zip after street address
        remaining = content[street_match.end():]
        city_state_zip = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)'
        location_match = re.search(city_state_zip, remaining)

        if location_match:
            return f"{street_match.group()}, {location_match.group(1)}, {location_match.group(2)} {location_match.group(3)}"
        else:
            return street_match.group()

    def _extract_hours(self, content: str) -> str:
        """Extract business hours from content"""
        # Pattern for hours
        hours_pattern = r'(?:hours?|open):\s*([^\n]{10,100})'
        hours_match = re.search(hours_pattern, content, re.IGNORECASE)

        if hours_match:
            return hours_match.group(1).strip()

        return ""

    def _format_phone(self, phone: str) -> str:
        """Format phone number to standard format"""
        if not phone:
            return ""

        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)

        # Format as (XXX) XXX-XXXX
        if len(digits) == 10:
            return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
        else:
            return phone  # Return as-is if can't format

    def _format_address_string(self, address: Any) -> str:
        """Format address to string"""
        if isinstance(address, str):
            return address
        elif isinstance(address, dict):
            return self._format_address_dict(address)
        else:
            return str(address)

    def _format_address_dict(self, address: Dict) -> str:
        """Format address dictionary to string"""
        parts = []

        if address.get("streetAddress"):
            parts.append(address["streetAddress"])

        if address.get("addressLocality"):
            parts.append(address["addressLocality"])

        state_zip = []
        if address.get("addressRegion"):
            state_zip.append(address["addressRegion"])
        if address.get("postalCode"):
            state_zip.append(address["postalCode"])

        if state_zip:
            parts.append(" ".join(state_zip))

        return ", ".join(parts)

    def _detect_inconsistencies(
        self,
        nap_data: List[NAPData],
        expected_nap: Optional[NAPData]
    ) -> List[NAPInconsistency]:
        """Detect inconsistencies in NAP data"""
        inconsistencies = []

        if len(nap_data) < 2:
            return inconsistencies

        # Compare all pairs
        for i in range(len(nap_data)):
            for j in range(i + 1, len(nap_data)):
                nap1 = nap_data[i]
                nap2 = nap_data[j]

                # Check business name
                if nap1.business_name and nap2.business_name:
                    similarity = self._calculate_similarity(
                        nap1.business_name,
                        nap2.business_name
                    )
                    if similarity < 0.9:  # 90% similarity threshold
                        inconsistencies.append(NAPInconsistency(
                            field="business_name",
                            issue_type="spelling",
                            sources=[nap1.source, nap2.source],
                            severity="high",
                            suggestion=f"Standardize to: {self._get_most_complete(nap1.business_name, nap2.business_name)}"
                        ))

                # Check phone
                if nap1.phone and nap2.phone:
                    if nap1.phone != nap2.phone:
                        inconsistencies.append(NAPInconsistency(
                            field="phone",
                            issue_type="format",
                            sources=[nap1.source, nap2.source],
                            severity="high",
                            suggestion=f"Standardize to: {nap1.phone}"
                        ))

                # Check address
                if nap1.address and nap2.address:
                    similarity = self._calculate_similarity(
                        nap1.address,
                        nap2.address
                    )
                    if similarity < 0.85:  # 85% similarity threshold
                        inconsistencies.append(NAPInconsistency(
                            field="address",
                            issue_type="format",
                            sources=[nap1.source, nap2.source],
                            severity="high",
                            suggestion=f"Standardize format. Check: abbreviations, spacing, punctuation"
                        ))

        # Check against expected NAP
        if expected_nap:
            for nap in nap_data:
                if expected_nap.business_name and nap.business_name:
                    similarity = self._calculate_similarity(
                        expected_nap.business_name,
                        nap.business_name
                    )
                    if similarity < 0.9:
                        inconsistencies.append(NAPInconsistency(
                            field="business_name",
                            issue_type="outdated",
                            sources=[nap.source],
                            severity="high",
                            suggestion=f"Update to match expected: {expected_nap.business_name}"
                        ))

                if expected_nap.phone and nap.phone:
                    if expected_nap.phone != nap.phone:
                        inconsistencies.append(NAPInconsistency(
                            field="phone",
                            issue_type="outdated",
                            sources=[nap.source],
                            severity="high",
                            suggestion=f"Update to match expected: {expected_nap.phone}"
                        ))

        # Deduplicate inconsistencies
        return self._deduplicate_inconsistencies(inconsistencies)

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def _get_most_complete(self, str1: str, str2: str) -> str:
        """Get the more complete version of two strings"""
        return str1 if len(str1) >= len(str2) else str2

    def _deduplicate_inconsistencies(
        self,
        inconsistencies: List[NAPInconsistency]
    ) -> List[NAPInconsistency]:
        """Remove duplicate inconsistencies"""
        seen = set()
        deduplicated = []

        for inc in inconsistencies:
            key = (inc.field, inc.issue_type, tuple(sorted(inc.sources)))
            if key not in seen:
                seen.add(key)
                deduplicated.append(inc)

        return deduplicated

    def _calculate_consistency_score(
        self,
        nap_data: List[NAPData],
        inconsistencies: List[NAPInconsistency]
    ) -> int:
        """Calculate consistency score (0-100)"""
        if not nap_data:
            return 0

        score = 100

        # Deduct for inconsistencies
        for inc in inconsistencies:
            if inc.severity == "high":
                score -= 15
            elif inc.severity == "medium":
                score -= 10
            else:
                score -= 5

        # Bonus for having NAP in multiple places
        if len(nap_data) >= 4:
            score = min(100, score + 10)

        # Deduct if missing from key locations
        sources = {nap.source for nap in nap_data}
        if "schema markup" not in sources:
            score -= 10
        if "homepage" not in sources and "footer" not in sources:
            score -= 5

        return max(0, score)

    def _create_standardized_nap(
        self,
        nap_data: List[NAPData],
        expected_nap: Optional[NAPData]
    ) -> NAPData:
        """Create standardized NAP recommendation"""
        if expected_nap:
            return expected_nap

        if not nap_data:
            return NAPData(
                business_name="",
                address="",
                phone="",
                source="standardized"
            )

        # Find most complete versions
        business_names = [n.business_name for n in nap_data if n.business_name]
        addresses = [n.address for n in nap_data if n.address]
        phones = [n.phone for n in nap_data if n.phone]
        hours_list = [n.hours for n in nap_data if n.hours]

        # Select longest/most complete
        business_name = max(business_names, key=len) if business_names else ""
        address = max(addresses, key=len) if addresses else ""
        phone = phones[0] if phones else ""
        hours = max(hours_list, key=len) if hours_list else None

        return NAPData(
            business_name=business_name,
            address=address,
            phone=phone,
            hours=hours,
            source="standardized"
        )

    def _generate_nap_recommendations(
        self,
        inconsistencies: List[NAPInconsistency],
        consistency_score: int,
        nap_data: List[NAPData]
    ) -> List[str]:
        """Generate NAP recommendations"""
        recommendations = []

        # Overall assessment
        if consistency_score >= 90:
            recommendations.append(
                "Excellent NAP consistency! Your business information is consistent across all sources."
            )
        elif consistency_score >= 70:
            recommendations.append(
                "Good NAP consistency with minor issues to address."
            )
        else:
            recommendations.append(
                "⚠️ Critical: NAP inconsistencies detected. This hurts local SEO and entity recognition."
            )

        # Specific issues
        if inconsistencies:
            for inc in inconsistencies[:5]:  # Top 5
                if inc.severity == "high":
                    recommendations.append(
                        f"🔴 {inc.field.replace('_', ' ').title()}: {inc.suggestion}"
                    )
                else:
                    recommendations.append(
                        f"🟡 {inc.field.replace('_', ' ').title()}: {inc.suggestion}"
                    )

        # Check coverage
        sources = {nap.source for nap in nap_data}
        if "schema markup" not in sources:
            recommendations.append(
                "Add schema markup with complete NAP data"
            )
        if "homepage" not in sources and "footer" not in sources:
            recommendations.append(
                "Add NAP to homepage or footer for better visibility"
            )
        if "contact page" not in sources:
            recommendations.append(
                "Create dedicated contact page with complete NAP"
            )

        # Format recommendations
        if any("format" in inc.issue_type for inc in inconsistencies):
            recommendations.append(
                "Use consistent formatting: (XXX) XXX-XXXX for phone, full address format"
            )

        # Google Business Profile
        recommendations.append(
            "Ensure NAP exactly matches your Google Business Profile"
        )

        return recommendations

    def _identify_citation_opportunities(
        self,
        nap_data: List[NAPData]
    ) -> List[str]:
        """Identify citation building opportunities"""
        opportunities = [
            "Google Business Profile (critical - ensure exact NAP match)",
            "Bing Places for Business",
            "Apple Maps",
            "Yelp",
            "Facebook Business Page",
            "Better Business Bureau (BBB)",
            "Chamber of Commerce",
            "YellowPages",
            "Angie's List / Angi",
            "HomeAdvisor (for home services)",
            "Industry-specific directories",
            "Local business associations",
            "News sites and local media",
            "Professional associations"
        ]

        # Check if NAP is complete enough for citations
        if nap_data:
            standardized = self._create_standardized_nap(nap_data, None)
            if not standardized.business_name or not standardized.phone:
                opportunities.insert(0,
                    "⚠️ Complete your NAP data before building citations"
                )

        return opportunities
