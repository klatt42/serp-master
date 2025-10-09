"""
Entity Relationship Analyzer
Identifies and scores entity relationships for authority building
"""

import logging
import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import defaultdict

from app.models.entity_models import (
    EntityRelationship,
    RelationshipAnalysisRequest,
    RelationshipAnalysisResponse
)

logger = logging.getLogger(__name__)


class RelationshipAnalyzer:
    """Analyze and identify entity relationships for SEO"""

    def __init__(self):
        """Initialize relationship analyzer"""
        # Known authority entities by category
        self.authority_entities = {
            "certifications": [
                "BBB", "Better Business Bureau",
                "ISO 9001", "ISO certified",
                "Google Certified", "Google Partner",
                "Microsoft Certified", "Microsoft Partner",
                "AWS Certified", "Amazon Partner",
                "Salesforce Certified",
                "LEED Certified",
                "Certified Public Accountant", "CPA",
                "Licensed Professional",
                "Board Certified",
                "Accredited",
            ],
            "associations": [
                "Chamber of Commerce",
                "Trade Association",
                "Professional Association",
                "Industry Association",
                "National Association",
                "American Bar Association",
                "American Medical Association",
                "IEEE", "ACM",
            ],
            "partnerships": [
                "Official Partner",
                "Authorized Dealer",
                "Authorized Reseller",
                "Certified Partner",
                "Strategic Partner",
                "Technology Partner",
            ],
            "awards": [
                "Award Winner",
                "Top Rated",
                "Best in Class",
                "Industry Leader",
                "Inc. 5000",
                "Forbes",
                "Gartner",
                "Top Company",
                "Excellence Award",
            ],
            "media": [
                "Featured in",
                "As seen in",
                "Published in",
                "Quoted in",
                "New York Times",
                "Wall Street Journal",
                "Forbes",
                "TechCrunch",
                "Wired",
            ],
            "education": [
                "Harvard", "MIT", "Stanford",
                "University", "College",
                "Alumni",
                "Graduate",
                "Degree from",
            ]
        }

        # Authority scoring weights
        self.authority_weights = {
            "certifications": 9,
            "associations": 7,
            "partnerships": 8,
            "awards": 6,
            "media": 7,
            "education": 6
        }

    async def analyze_relationships(
        self,
        request: RelationshipAnalysisRequest,
        site_data: Optional[Dict] = None
    ) -> RelationshipAnalysisResponse:
        """
        Analyze entity relationships on a website

        Args:
            request: Relationship analysis request
            site_data: Optional pre-analyzed site data

        Returns:
            Response with relationship analysis
        """
        try:
            # Extract relationships from content
            relationships = await self._extract_relationships(
                request.site_url,
                site_data,
                request.focus_areas
            )

            # Score and prioritize relationships
            scored_relationships = self._score_relationships(relationships)

            # Identify missing opportunities
            missing_opportunities = self._identify_missing_opportunities(
                scored_relationships,
                site_data
            )

            # Generate recommendations
            recommendations = self._generate_relationship_recommendations(
                scored_relationships,
                missing_opportunities
            )

            # Create authority summary
            authority_summary = self._create_authority_summary(scored_relationships)

            return RelationshipAnalysisResponse(
                relationships=scored_relationships,
                missing_opportunities=missing_opportunities,
                recommendations=recommendations,
                authority_summary=authority_summary,
                analyzed_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error analyzing relationships: {str(e)}")
            raise

    async def _extract_relationships(
        self,
        site_url: str,
        site_data: Optional[Dict],
        focus_areas: Optional[List[str]]
    ) -> List[Dict]:
        """Extract relationships from site content"""
        relationships = []

        if not site_data:
            return relationships

        # Combine all text content
        content_sources = {
            "homepage": site_data.get("content", ""),
            "about_page": site_data.get("about_content", ""),
            "certifications_page": site_data.get("certifications_content", ""),
            "partners_page": site_data.get("partners_content", ""),
            "meta_description": site_data.get("meta_description", ""),
            "team_bios": " ".join(site_data.get("team_bios", []))
        }

        # Determine which categories to search
        categories = focus_areas if focus_areas else list(self.authority_entities.keys())

        # Search for known entities
        for category in categories:
            if category not in self.authority_entities:
                continue

            for source_name, content in content_sources.items():
                if not content:
                    continue

                for entity in self.authority_entities[category]:
                    # Case-insensitive search with word boundaries
                    pattern = r'\b' + re.escape(entity) + r'\b'
                    matches = re.finditer(pattern, content, re.IGNORECASE)

                    for match in matches:
                        # Extract context around match
                        start = max(0, match.start() - 100)
                        end = min(len(content), match.end() + 100)
                        context = content[start:end].strip()

                        relationships.append({
                            "entity_name": entity,
                            "category": category,
                            "context": context,
                            "source": source_name,
                            "match_text": match.group()
                        })

        # Look for additional entities using pattern matching
        additional_relationships = self._detect_additional_relationships(content_sources)
        relationships.extend(additional_relationships)

        # Deduplicate relationships
        relationships = self._deduplicate_relationships(relationships)

        return relationships

    def _detect_additional_relationships(
        self,
        content_sources: Dict[str, str]
    ) -> List[Dict]:
        """Detect relationships using pattern matching"""
        relationships = []

        # Patterns for common relationship indicators
        patterns = {
            "certifications": [
                r'certified by ([A-Z][a-zA-Z\s&]+)',
                r'([A-Z][a-zA-Z\s&]+) certified',
                r'licensed by ([A-Z][a-zA-Z\s&]+)',
            ],
            "partnerships": [
                r'partner with ([A-Z][a-zA-Z\s&]+)',
                r'partnership with ([A-Z][a-zA-Z\s&]+)',
                r'authorized by ([A-Z][a-zA-Z\s&]+)',
            ],
            "awards": [
                r'winner of ([A-Z][a-zA-Z\s&]+)',
                r'received ([A-Z][a-zA-Z\s&]+(?:Award|Prize))',
                r'recognized by ([A-Z][a-zA-Z\s&]+)',
            ],
            "associations": [
                r'member of ([A-Z][a-zA-Z\s&]+(?:Association|Society|Institute))',
                r'affiliated with ([A-Z][a-zA-Z\s&]+)',
            ],
            "media": [
                r'featured (?:in|on) ([A-Z][a-zA-Z\s&]+)',
                r'as seen (?:in|on) ([A-Z][a-zA-Z\s&]+)',
                r'published in ([A-Z][a-zA-Z\s&]+)',
            ]
        }

        for source_name, content in content_sources.items():
            if not content:
                continue

            for category, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.finditer(pattern, content, re.IGNORECASE)

                    for match in matches:
                        entity_name = match.group(1).strip()

                        # Filter out very long or short matches
                        if 3 <= len(entity_name) <= 50:
                            # Extract context
                            start = max(0, match.start() - 100)
                            end = min(len(content), match.end() + 100)
                            context = content[start:end].strip()

                            relationships.append({
                                "entity_name": entity_name,
                                "category": category,
                                "context": context,
                                "source": source_name,
                                "match_text": match.group()
                            })

        return relationships

    def _deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Remove duplicate relationships"""
        seen = set()
        deduplicated = []

        for rel in relationships:
            # Create unique key
            key = (
                rel["entity_name"].lower(),
                rel["category"]
            )

            if key not in seen:
                seen.add(key)
                deduplicated.append(rel)

        return deduplicated

    def _score_relationships(
        self,
        relationships: List[Dict]
    ) -> List[EntityRelationship]:
        """Score and prioritize relationships"""
        scored_relationships = []

        for rel in relationships:
            # Base authority score from category
            authority_score = self.authority_weights.get(rel["category"], 5)

            # Adjust based on entity prominence
            if any(entity.lower() in rel["entity_name"].lower()
                   for entity in ["Google", "Microsoft", "Amazon", "IBM"]):
                authority_score = min(10, authority_score + 2)

            if any(entity.lower() in rel["entity_name"].lower()
                   for entity in ["Forbes", "Inc", "Harvard", "MIT", "Stanford"]):
                authority_score = min(10, authority_score + 1)

            # Relevance score based on context
            relevance_score = self._calculate_relevance_score(rel)

            # Trust signal strength
            trust_signal_strength = self._determine_trust_signal_strength(
                authority_score,
                relevance_score
            )

            # Schema opportunity
            schema_opportunity = self._has_schema_opportunity(rel)

            # Create description
            description = self._create_relationship_description(rel)

            scored_relationships.append(EntityRelationship(
                relationship_type=rel["category"],
                entity_name=rel["entity_name"],
                description=description,
                authority_score=authority_score,
                relevance_score=relevance_score,
                trust_signal_strength=trust_signal_strength,
                schema_opportunity=schema_opportunity,
                detected_from=rel["source"]
            ))

        # Sort by authority score, then relevance
        scored_relationships.sort(
            key=lambda x: (x.authority_score, x.relevance_score),
            reverse=True
        )

        return scored_relationships

    def _calculate_relevance_score(self, relationship: Dict) -> int:
        """Calculate relevance score based on context"""
        context = relationship.get("context", "").lower()
        score = 5  # Base score

        # Positive indicators
        positive_indicators = [
            "official", "certified", "recognized", "accredited",
            "member", "partner", "winner", "featured", "published"
        ]
        for indicator in positive_indicators:
            if indicator in context:
                score += 1

        # Check for years or dates (indicates recent/ongoing)
        if re.search(r'\b(20\d{2}|since|years)\b', context):
            score += 1

        # Check if on dedicated page (more relevant)
        if relationship.get("source") in ["certifications_page", "partners_page", "about_page"]:
            score += 2

        return min(10, score)

    def _determine_trust_signal_strength(
        self,
        authority_score: int,
        relevance_score: int
    ) -> str:
        """Determine trust signal strength"""
        combined_score = (authority_score + relevance_score) / 2

        if combined_score >= 8:
            return "high"
        elif combined_score >= 6:
            return "medium"
        else:
            return "low"

    def _has_schema_opportunity(self, relationship: Dict) -> bool:
        """Check if relationship has schema markup opportunity"""
        # Certifications, awards, and affiliations can be marked up
        schema_friendly_categories = [
            "certifications",
            "awards",
            "associations",
            "education"
        ]

        return relationship["category"] in schema_friendly_categories

    def _create_relationship_description(self, relationship: Dict) -> str:
        """Create human-readable relationship description"""
        category = relationship["category"]
        entity = relationship["entity_name"]
        source = relationship["source"].replace("_", " ").title()

        descriptions = {
            "certifications": f"Certified by {entity}",
            "partnerships": f"Official partner with {entity}",
            "awards": f"Awarded {entity}",
            "associations": f"Member of {entity}",
            "media": f"Featured in {entity}",
            "education": f"Alumni/graduate of {entity}"
        }

        base_desc = descriptions.get(category, f"Associated with {entity}")
        return f"{base_desc} (found on {source})"

    def _identify_missing_opportunities(
        self,
        relationships: List[EntityRelationship],
        site_data: Optional[Dict]
    ) -> List[str]:
        """Identify missing relationship opportunities"""
        opportunities = []

        # Check what categories are missing
        present_categories = {rel.relationship_type for rel in relationships}

        if "certifications" not in present_categories:
            opportunities.append(
                "Add industry certifications to build authority (e.g., ISO, BBB, professional licenses)"
            )

        if "associations" not in present_categories:
            opportunities.append(
                "Join and display professional associations or industry groups"
            )

        if "awards" not in present_categories:
            opportunities.append(
                "Showcase any awards, recognitions, or top rankings you've received"
            )

        if "media" not in present_categories:
            opportunities.append(
                "Highlight media mentions, publications, or press coverage"
            )

        # Check for weak signals
        high_authority = [rel for rel in relationships if rel.authority_score >= 8]
        if len(high_authority) < 3:
            opportunities.append(
                "Focus on obtaining high-authority certifications or partnerships (Google, Microsoft, industry leaders)"
            )

        # Check if relationships are visible
        if site_data:
            if not site_data.get("certifications_content"):
                opportunities.append(
                    "Create a dedicated certifications/credentials page"
                )

            if not site_data.get("partners_content"):
                opportunities.append(
                    "Create a dedicated partners/affiliations page"
                )

        return opportunities

    def _generate_relationship_recommendations(
        self,
        relationships: List[EntityRelationship],
        missing_opportunities: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []

        # High-value relationships to highlight
        high_value = [rel for rel in relationships if rel.authority_score >= 8]
        if high_value:
            recommendations.append({
                "priority": "high",
                "category": "highlighting",
                "title": "Prominently Display High-Authority Relationships",
                "description": f"You have {len(high_value)} high-authority relationships. Display these prominently on your homepage and about page.",
                "entities": [rel.entity_name for rel in high_value[:5]],
                "impact": "High authority signals boost trust and entity recognition"
            })

        # Schema markup opportunities
        schema_opportunities = [rel for rel in relationships if rel.schema_opportunity]
        if schema_opportunities:
            recommendations.append({
                "priority": "high",
                "category": "schema",
                "title": "Add Schema Markup for Certifications and Awards",
                "description": f"{len(schema_opportunities)} relationships can be marked up with structured data for enhanced visibility.",
                "entities": [rel.entity_name for rel in schema_opportunities[:5]],
                "impact": "Schema markup helps Google understand your credentials"
            })

        # Trust signals on key pages
        if relationships:
            recommendations.append({
                "priority": "medium",
                "category": "placement",
                "title": "Add Trust Signals to Key Pages",
                "description": "Display certifications and awards on your homepage, about page, and service pages.",
                "action_items": [
                    "Add certification logos to homepage footer",
                    "Create dedicated 'Certifications' section on about page",
                    "Include relevant certifications on service pages"
                ],
                "impact": "Increases visitor trust and conversion rates"
            })

        # Link to authority entities
        external_relationships = [rel for rel in relationships if rel.authority_score >= 7]
        if external_relationships:
            recommendations.append({
                "priority": "medium",
                "category": "linking",
                "title": "Link to Authority Entities",
                "description": "Add contextual links to the organizations you're certified by or partnered with.",
                "entities": [rel.entity_name for rel in external_relationships[:5]],
                "impact": "External links to authority sites strengthen entity relationships"
            })

        # Address missing opportunities
        if missing_opportunities:
            recommendations.append({
                "priority": "high",
                "category": "opportunities",
                "title": "Address Missing Relationship Opportunities",
                "description": "Expand your authority signals by addressing these gaps.",
                "action_items": missing_opportunities[:5],
                "impact": "Diversified authority signals strengthen overall entity trust"
            })

        return recommendations

    def _create_authority_summary(
        self,
        relationships: List[EntityRelationship]
    ) -> Dict[str, int]:
        """Create summary of authority signals by category"""
        summary = defaultdict(int)

        for rel in relationships:
            summary[rel.relationship_type] += 1

        # Add authority strength counts
        summary["total_relationships"] = len(relationships)
        summary["high_authority"] = len([r for r in relationships if r.authority_score >= 8])
        summary["medium_authority"] = len([r for r in relationships if 6 <= r.authority_score < 8])
        summary["low_authority"] = len([r for r in relationships if r.authority_score < 6])
        summary["schema_opportunities"] = len([r for r in relationships if r.schema_opportunity])

        return dict(summary)
