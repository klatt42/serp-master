"""
Entity Clarity Checker
Analyzes entity consistency and clarity for AEO scoring
UNIQUE FEATURE - No other SEO tool analyzes entity clarity!
"""

import logging
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from collections import Counter

logger = logging.getLogger(__name__)


class EntityChecker:
    """
    Analyzes business entity clarity and consistency
    AI search engines think in entities, not keywords!

    Scoring breakdown (7 points total):
    - Business name consistency: 2 points
    - Clear business description: 2 points
    - Entity relationships: 2 points
    - About page quality: 1 point
    """

    def check_entity_clarity(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to analyze entity clarity across the site

        Args:
            site_data: Mock site data or real crawl data

        Returns:
            Dictionary with entity clarity score and details
        """
        try:
            pages = site_data.get('pages', [])
            html_content = site_data.get('html', '')
            business_name = site_data.get('business_name', '')

            # Analyze business name consistency
            name_analysis = self.check_name_consistency(pages, html_content, business_name)

            # Analyze business description clarity
            description_analysis = self.check_description_clarity(pages, html_content)

            # Analyze entity relationships
            relationship_analysis = self.check_entity_relationships(html_content)

            # Analyze about page quality
            about_analysis = self.check_about_page(pages)

            # Calculate total score
            total_score = (
                name_analysis['points'] +
                description_analysis['points'] +
                relationship_analysis['points'] +
                about_analysis['points']
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                name_analysis,
                description_analysis,
                relationship_analysis,
                about_analysis
            )

            return {
                "entity_clarity_score": total_score,
                "max_score": 7,
                "name_consistency": name_analysis,
                "description_clarity": description_analysis,
                "entity_relationships": relationship_analysis,
                "about_page": about_analysis,
                "recommendations": recommendations
            }

        except Exception as e:
            logger.error(f"Error checking entity clarity: {str(e)}")
            return {
                "entity_clarity_score": 0,
                "max_score": 7,
                "error": str(e),
                "recommendations": ["Fix content parsing errors before analyzing entity clarity"]
            }

    def check_name_consistency(
        self,
        pages: List[Dict],
        html_content: str,
        known_name: str = ""
    ) -> Dict[str, Any]:
        """
        Check if business name is consistent across the site

        Args:
            pages: List of page data
            html_content: HTML to analyze
            known_name: Known business name (if available)

        Returns:
            Name consistency analysis with score
        """
        names_found = []

        # Extract from HTML
        if html_content:
            soup = BeautifulSoup(html_content, 'lxml')

            # Extract from title tag
            title = soup.find('title')
            if title:
                name = self._extract_name_from_title(title.get_text())
                if name:
                    names_found.append(name)

            # Extract from H1 tags
            h1_tags = soup.find_all('h1')
            for h1 in h1_tags:
                text = h1.get_text().strip()
                if text and len(text) < 100:  # Reasonable business name length
                    names_found.append(text)

            # Extract from Organization schema
            jsonld_scripts = soup.find_all('script', type='application/ld+json')
            for script in jsonld_scripts:
                try:
                    import json
                    schema_data = json.loads(script.string)
                    schemas_to_check = schema_data if isinstance(schema_data, list) else [schema_data]

                    for schema in schemas_to_check:
                        if isinstance(schema, dict):
                            schema_type = schema.get('@type', '')
                            if schema_type in ['Organization', 'LocalBusiness']:
                                name = schema.get('name', '')
                                if name:
                                    names_found.append(name)
                except:
                    continue

            # Extract from copyright text
            copyright_patterns = [
                r'©\s*\d{4}\s+([^.]+)',
                r'Copyright\s+\d{4}\s+([^.]+)',
                r'&copy;\s*\d{4}\s+([^.]+)'
            ]
            text = soup.get_text()
            for pattern in copyright_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    clean_name = match.strip().split('.')[0].strip()
                    if clean_name and len(clean_name) < 100:
                        names_found.append(clean_name)

            # Extract from navigation (look for brand/logo text)
            nav = soup.find('nav')
            if nav:
                # First link is often the brand
                first_link = nav.find('a')
                if first_link:
                    text = first_link.get_text().strip()
                    if text and len(text) < 50:
                        names_found.append(text)

        # Add known name if provided
        if known_name:
            names_found.append(known_name)

        # Analyze consistency
        if not names_found:
            return {
                "consistent": False,
                "primary_name": None,
                "variations": [],
                "occurrences": 0,
                "points": 0,
                "status": "Missing: No business name found"
            }

        # Count occurrences (case-insensitive)
        name_counter = Counter([name.lower().strip() for name in names_found])
        most_common = name_counter.most_common(1)[0]
        primary_name = most_common[0]
        occurrences = most_common[1]

        # Find the original casing of the primary name
        for name in names_found:
            if name.lower().strip() == primary_name:
                primary_name = name
                break

        # Check for variations
        unique_names = set([name.lower().strip() for name in names_found])
        variations = [name for name in unique_names if name != primary_name.lower()]

        # Calculate consistency
        consistency_ratio = occurrences / len(names_found)
        is_consistent = consistency_ratio >= 0.75  # 75% of mentions use same name

        # Calculate score
        if is_consistent and occurrences >= 3:
            points = 2  # Perfect: Consistent name used 3+ times
        elif is_consistent:
            points = 1  # Good: Consistent but few mentions
        else:
            points = 0  # Poor: Multiple name variations

        return {
            "consistent": is_consistent,
            "primary_name": primary_name,
            "variations": variations,
            "occurrences": occurrences,
            "consistency_ratio": round(consistency_ratio, 2),
            "points": points,
            "status": self._get_name_status(points)
        }

    def _extract_name_from_title(self, title: str) -> Optional[str]:
        """Extract business name from page title"""
        # Common patterns: "Business Name | Tagline" or "Page - Business Name"
        separators = [' | ', ' - ', ' – ', ' — ']

        for sep in separators:
            if sep in title:
                parts = title.split(sep)
                # Usually the last part is the business name
                name = parts[-1].strip()
                if name and len(name) < 50:
                    return name

        # If no separator, use the whole title if it's short enough
        if len(title) < 50:
            return title.strip()

        return None

    def _get_name_status(self, points: int) -> str:
        """Get human-readable name consistency status"""
        if points == 2:
            return "Excellent: Consistent business name"
        elif points == 1:
            return "Good: Name present but limited"
        else:
            return "Poor: Inconsistent or missing name"

    def check_description_clarity(
        self,
        pages: List[Dict],
        html_content: str
    ) -> Dict[str, Any]:
        """
        Check for clear, consistent business descriptions

        Args:
            pages: List of page data
            html_content: HTML to analyze

        Returns:
            Description clarity analysis with score
        """
        descriptions = []

        if html_content:
            soup = BeautifulSoup(html_content, 'lxml')

            # Extract from meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                descriptions.append({
                    'source': 'meta_description',
                    'text': meta_desc.get('content').strip()
                })

            # Extract from Organization schema
            jsonld_scripts = soup.find_all('script', type='application/ld+json')
            for script in jsonld_scripts:
                try:
                    import json
                    schema_data = json.loads(script.string)
                    schemas_to_check = schema_data if isinstance(schema_data, list) else [schema_data]

                    for schema in schemas_to_check:
                        if isinstance(schema, dict):
                            schema_type = schema.get('@type', '')
                            if schema_type in ['Organization', 'LocalBusiness']:
                                desc = schema.get('description', '')
                                if desc:
                                    descriptions.append({
                                        'source': 'schema',
                                        'text': desc.strip()
                                    })
                except:
                    continue

            # Extract from homepage intro (first paragraph in main)
            main = soup.find('main') or soup.find('body')
            if main:
                first_p = main.find('p')
                if first_p:
                    text = first_p.get_text().strip()
                    if len(text) > 50:  # Meaningful description
                        descriptions.append({
                            'source': 'homepage_intro',
                            'text': text
                        })

        # Check pages for about page description
        if pages:
            for page in pages:
                if page is None:
                    continue

                url = page.get('url', '').lower()
                if 'about' in url:
                    # Look for description in about page
                    page_html = page.get('html', '')
                    if page_html:
                        soup = BeautifulSoup(page_html, 'lxml')
                        paragraphs = soup.find_all('p')
                        if paragraphs:
                            # Get first substantial paragraph
                            for p in paragraphs[:3]:
                                text = p.get_text().strip()
                                if len(text) > 100:
                                    descriptions.append({
                                        'source': 'about_page',
                                        'text': text
                                    })
                                    break

        # Analyze quality
        if not descriptions:
            return {
                "has_description": False,
                "sources": [],
                "primary_description": None,
                "word_count": 0,
                "points": 0,
                "status": "Missing: No business description found"
            }

        # Get primary description (prefer schema, then meta, then content)
        source_priority = {'schema': 3, 'meta_description': 2, 'about_page': 1, 'homepage_intro': 1}
        descriptions.sort(key=lambda x: source_priority.get(x['source'], 0), reverse=True)

        primary = descriptions[0]
        word_count = len(primary['text'].split())

        # Calculate score
        sources = list(set([d['source'] for d in descriptions]))
        if len(sources) >= 2 and word_count >= 20:
            points = 2  # Perfect: Description in multiple places, substantial
        elif len(sources) >= 2 or word_count >= 20:
            points = 1  # Good: Either multi-source or substantial
        else:
            points = 0  # Poor: Single short description

        return {
            "has_description": True,
            "sources": sources,
            "primary_description": primary['text'][:200] + "..." if len(primary['text']) > 200 else primary['text'],
            "word_count": word_count,
            "points": points,
            "status": self._get_description_status(points)
        }

    def _get_description_status(self, points: int) -> str:
        """Get human-readable description status"""
        if points == 2:
            return "Excellent: Clear description in multiple places"
        elif points == 1:
            return "Good: Description present"
        else:
            return "Limited: Minimal description"

    def check_entity_relationships(self, html_content: str) -> Dict[str, Any]:
        """
        Detect entity relationships mentioned on the site

        Args:
            html_content: HTML to analyze

        Returns:
            Entity relationships analysis with score
        """
        relationships = {
            'certifications': [],
            'awards': [],
            'affiliations': [],
            'service_areas': [],
            'associations': []
        }

        if not html_content:
            return {
                "relationships_found": 0,
                "categories": [],
                "examples": [],
                "points": 0,
                "status": "Missing: No entity relationships found"
            }

        soup = BeautifulSoup(html_content, 'lxml')
        text = soup.get_text().lower()

        # Certification indicators
        cert_patterns = [
            r'certified by ([^.,]+)',
            r'([A-Z]{2,})\s*certified',
            r'certification[s]?[:\s]+([^.,]+)',
            r'licensed by ([^.,]+)',
            r'accredited by ([^.,]+)'
        ]

        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean = match.strip()
                if clean and len(clean) < 100:
                    relationships['certifications'].append(clean)

        # Award indicators
        award_patterns = [
            r'winner of ([^.,]+)',
            r'awarded ([^.,]+)',
            r'award[s]?[:\s]+([^.,]+)',
            r'recognized by ([^.,]+)'
        ]

        for pattern in award_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean = match.strip()
                if clean and len(clean) < 100:
                    relationships['awards'].append(clean)

        # Affiliation/partnership indicators
        affiliation_keywords = ['partner', 'affiliation', 'affiliated', 'member of', 'partnership']
        for keyword in affiliation_keywords:
            if keyword in text:
                relationships['affiliations'].append(f"Mentions {keyword}")

        # Service area indicators (for local businesses)
        area_patterns = [
            r'serving ([A-Z][a-z]+(?:,?\s+[A-Z][a-z]+)*)',
            r'locations? in ([^.,]+)',
            r'([A-Z][a-z]+)\s+area'
        ]

        for pattern in area_patterns:
            matches = re.findall(pattern, soup.get_text())
            for match in matches:
                clean = match.strip()
                if clean and len(clean) < 50:
                    relationships['service_areas'].append(clean)

        # Industry association indicators
        assoc_patterns = [
            r'member of ([^.,]+association[^.,]*)',
            r'([^.,]*association[^.,]+)',
            r'chamber of commerce'
        ]

        for pattern in assoc_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean = match.strip()
                if 'association' in clean.lower() or 'chamber' in clean.lower():
                    if len(clean) < 100:
                        relationships['associations'].append(clean)

        # Count relationships
        total_relationships = sum(len(v) for v in relationships.values())
        categories_found = [k for k, v in relationships.items() if len(v) > 0]

        # Get examples
        examples = []
        for category, items in relationships.items():
            if items:
                examples.append(f"{category}: {items[0]}")

        # Calculate score
        if total_relationships >= 5 and len(categories_found) >= 3:
            points = 2  # Excellent: Multiple relationships across categories
        elif total_relationships >= 3 or len(categories_found) >= 2:
            points = 1  # Good: Some relationships
        else:
            points = 0  # Poor: Few or no relationships

        return {
            "relationships_found": total_relationships,
            "categories": categories_found,
            "examples": examples[:5],  # Top 5 examples
            "breakdown": {k: len(v) for k, v in relationships.items()},
            "points": points,
            "status": self._get_relationship_status(points)
        }

    def _get_relationship_status(self, points: int) -> str:
        """Get human-readable relationship status"""
        if points == 2:
            return "Excellent: Strong entity relationships"
        elif points == 1:
            return "Good: Some relationships mentioned"
        else:
            return "Limited: Few entity relationships"

    def check_about_page(self, pages: List[Dict]) -> Dict[str, Any]:
        """
        Check for quality about page

        Args:
            pages: List of page data

        Returns:
            About page analysis with score
        """
        if not pages:
            return {
                "has_about_page": False,
                "word_count": 0,
                "has_history": False,
                "has_team": False,
                "has_mission": False,
                "points": 0,
                "status": "Missing: No about page found"
            }

        # Find about page
        about_page = None
        about_indicators = ['about', 'about-us', 'company', 'our-story', 'who-we-are']

        for page in pages:
            if page is None:
                continue

            url = page.get('url', '').lower()
            title = page.get('title', '').lower()

            # Check if URL or title indicates about page
            is_about = any(indicator in url or indicator in title for indicator in about_indicators)

            if is_about:
                about_page = page
                break

        if not about_page:
            return {
                "has_about_page": False,
                "word_count": 0,
                "has_history": False,
                "has_team": False,
                "has_mission": False,
                "points": 0,
                "status": "Missing: No about page found"
            }

        # Analyze about page content
        html = about_page.get('html', '')
        if not html:
            return {
                "has_about_page": True,
                "word_count": 0,
                "has_history": False,
                "has_team": False,
                "has_mission": False,
                "points": 0,
                "status": "Poor: About page is empty"
            }

        soup = BeautifulSoup(html, 'lxml')

        # Remove navigation, footer, etc.
        for element in soup(['nav', 'footer', 'header', 'script', 'style']):
            element.decompose()

        text = soup.get_text()
        word_count = len(text.split())

        # Check for quality indicators
        text_lower = text.lower()

        # History indicators
        history_keywords = ['founded', 'established', 'started', 'began', 'history', 'since']
        has_history = any(keyword in text_lower for keyword in history_keywords)

        # Team indicators
        team_keywords = ['team', 'staff', 'employee', 'founder', 'ceo', 'president', 'owner']
        has_team = any(keyword in text_lower for keyword in team_keywords)

        # Mission/values indicators
        mission_keywords = ['mission', 'vision', 'values', 'believe', 'commitment', 'dedicated']
        has_mission = any(keyword in text_lower for keyword in mission_keywords)

        # Calculate score
        quality_indicators = sum([has_history, has_team, has_mission])

        if word_count >= 500 and quality_indicators >= 2:
            points = 1  # Perfect: Substantial about page with quality content
        else:
            points = 0  # Poor: Short or low-quality about page

        return {
            "has_about_page": True,
            "url": about_page.get('url', ''),
            "word_count": word_count,
            "has_history": has_history,
            "has_team": has_team,
            "has_mission": has_mission,
            "quality_indicators": quality_indicators,
            "points": points,
            "status": self._get_about_status(points, word_count)
        }

    def _get_about_status(self, points: int, word_count: int) -> str:
        """Get human-readable about page status"""
        if points == 1:
            return f"Excellent: Quality about page ({word_count} words)"
        else:
            return f"Limited: About page needs improvement ({word_count} words)"

    def _generate_recommendations(
        self,
        name_analysis: Dict[str, Any],
        description_analysis: Dict[str, Any],
        relationship_analysis: Dict[str, Any],
        about_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Name consistency recommendations
        name_points = name_analysis.get('points', 0)
        if name_points == 0:
            recommendations.append(
                "Establish consistent business name across all pages (+2 points). "
                "Use the same exact name in titles, headers, schema markup, and copyright text."
            )
        elif name_points == 1:
            recommendations.append(
                "Increase business name mentions for stronger entity recognition (+1 point). "
                f"Current name '{name_analysis.get('primary_name', '')}' should appear in schema, "
                "navigation, and key pages."
            )

        # Description recommendations
        desc_points = description_analysis.get('points', 0)
        if desc_points == 0:
            recommendations.append(
                "Add clear business description in multiple places (+2 points). "
                "Include in meta description, Organization schema, and homepage intro. "
                "Aim for 20+ words explaining what your business does."
            )
        elif desc_points == 1:
            recommendations.append(
                "Expand business description coverage (+1 point). "
                "Add to Organization schema and ensure it appears in meta description. "
                "Make it substantial (20+ words) and consistent across sources."
            )

        # Relationship recommendations
        rel_points = relationship_analysis.get('points', 0)
        if rel_points == 0:
            recommendations.append(
                "Highlight entity relationships to build authority (+2 points). "
                "Mention certifications, awards, industry affiliations, partnerships, "
                "and service areas. AI engines use these to understand your business context."
            )
        elif rel_points == 1:
            recommendations.append(
                "Add more entity relationships for stronger authority signals (+1 point). "
                "Include additional certifications, awards, or industry associations. "
                "Aim for 5+ relationships across 3+ categories."
            )

        # About page recommendations
        about_points = about_analysis.get('points', 0)
        if not about_analysis.get('has_about_page', False):
            recommendations.append(
                "Create a dedicated About page (+1 point). "
                "Include company history (when founded), team information, and mission/values. "
                "Aim for 500+ words to establish strong entity identity."
            )
        elif about_points == 0:
            recommendations.append(
                "Improve About page quality (+1 point). "
                "Add company history, team information, and mission/values. "
                "Expand to 500+ words to strengthen entity clarity."
            )

        # Perfect score congratulations
        total_points = name_points + desc_points + rel_points + about_points
        if total_points == 7:
            recommendations.append(
                "Perfect entity clarity! AI search engines have a clear understanding of your business identity and relationships."
            )

        return recommendations
