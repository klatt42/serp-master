"""
Conversational Content Analyzer
Analyzes content for AEO (Answer Engine Optimization) scoring
Focuses on FAQ pages, question headers, and readability
"""

import logging
import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
import textstat

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """
    Analyzes content for conversational patterns and readability

    Scoring breakdown (8 points total):
    - FAQ pages: 4 points
    - Question headers: 2 points
    - Readability: 2 points
    """

    # Question words that indicate conversational content
    QUESTION_WORDS = [
        'who', 'what', 'when', 'where', 'why', 'how',
        'can', 'does', 'is', 'should', 'will', 'would',
        'could', 'are', 'do', 'did', 'has', 'have'
    ]

    # FAQ page indicators
    FAQ_INDICATORS = [
        'faq', 'faqs', 'frequently-asked-questions',
        'questions', 'q&a', 'q-and-a', 'help', 'support'
    ]

    def calculate_conversational_score(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to calculate conversational content score

        Args:
            site_data: Mock site data or real crawl data

        Returns:
            Dictionary with conversational score and details
        """
        try:
            pages = site_data.get('pages', [])
            html_content = site_data.get('html', '')

            # Analyze FAQ pages
            faq_analysis = self.detect_faq_pages(pages, html_content)

            # Analyze question headers
            question_analysis = self.find_question_headers(html_content)

            # Analyze readability
            readability_analysis = self.calculate_readability(html_content)

            # Calculate total score
            total_score = (
                faq_analysis['points'] +
                question_analysis['points'] +
                readability_analysis['points']
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                faq_analysis,
                question_analysis,
                readability_analysis
            )

            return {
                "conversational_score": total_score,
                "max_score": 8,
                "faq_analysis": faq_analysis,
                "question_headers": question_analysis,
                "readability": readability_analysis,
                "recommendations": recommendations
            }

        except Exception as e:
            logger.error(f"Error analyzing conversational content: {str(e)}")
            return {
                "conversational_score": 0,
                "max_score": 8,
                "error": str(e),
                "recommendations": ["Fix content parsing errors before analyzing conversational patterns"]
            }

    def detect_faq_pages(self, pages: List[Dict], html_content: str = "") -> Dict[str, Any]:
        """
        Detect FAQ pages and schema markup

        Args:
            pages: List of page data
            html_content: HTML to check for FAQ schema

        Returns:
            FAQ analysis with score
        """
        faq_pages = []
        has_faq_schema = False

        # Check for FAQ pages in URLs
        if pages:
            for page in pages:
                if page is None:
                    continue

                url = page.get('url', '').lower()
                title = page.get('title', '').lower()

                # Check if URL or title indicates FAQ page
                is_faq = any(indicator in url or indicator in title for indicator in self.FAQ_INDICATORS)

                if is_faq:
                    faq_pages.append(page.get('url', ''))

        # Check for FAQ schema in HTML
        if html_content:
            soup = BeautifulSoup(html_content, 'lxml')

            # Check for FAQPage schema in JSON-LD
            jsonld_scripts = soup.find_all('script', type='application/ld+json')
            for script in jsonld_scripts:
                try:
                    import json
                    schema_data = json.loads(script.string)

                    # Handle both single schema and array
                    schemas_to_check = schema_data if isinstance(schema_data, list) else [schema_data]

                    for schema in schemas_to_check:
                        if isinstance(schema, dict):
                            schema_type = schema.get('@type', '')
                            if schema_type == 'FAQPage':
                                has_faq_schema = True
                                break
                except:
                    continue

        # Calculate score
        points = 0
        if has_faq_schema and len(faq_pages) > 0:
            points = 4  # Perfect: FAQ page with schema
        elif len(faq_pages) > 0:
            points = 3  # Good: FAQ page without schema
        elif self._has_scattered_faq_content(html_content):
            points = 2  # Fair: FAQ content but not dedicated page
        else:
            points = 0  # None: No FAQ content

        return {
            "has_faq_page": len(faq_pages) > 0,
            "faq_pages": faq_pages,
            "has_schema": has_faq_schema,
            "points": points,
            "status": self._get_faq_status(points)
        }

    def _has_scattered_faq_content(self, html_content: str) -> bool:
        """Check if content has FAQ-like Q&A patterns"""
        if not html_content:
            return False

        soup = BeautifulSoup(html_content, 'lxml')
        text = soup.get_text().lower()

        # Look for Q&A patterns
        qa_patterns = [
            r'q:', r'a:', r'question:', r'answer:',
            r'q\d+:', r'frequently asked'
        ]

        for pattern in qa_patterns:
            if re.search(pattern, text):
                return True

        return False

    def _get_faq_status(self, points: int) -> str:
        """Get human-readable FAQ status"""
        if points == 4:
            return "Excellent: FAQ page with schema"
        elif points == 3:
            return "Good: FAQ page present"
        elif points == 2:
            return "Fair: FAQ content scattered"
        else:
            return "Missing: No FAQ content"

    def find_question_headers(self, html_content: str) -> Dict[str, Any]:
        """
        Find headers that are formatted as questions

        Args:
            html_content: HTML to analyze

        Returns:
            Question header analysis with score
        """
        if not html_content:
            return {
                "count": 0,
                "examples": [],
                "points": 0
            }

        soup = BeautifulSoup(html_content, 'lxml')

        # Find all headers (H2, H3 are most common for questions)
        headers = soup.find_all(['h2', 'h3'])

        question_headers = []

        for header in headers:
            text = header.get_text().strip()

            # Check if it's a question
            if self.is_question(text):
                question_headers.append(text)

        # Calculate score
        count = len(question_headers)
        if count >= 10:
            points = 2
        elif count >= 5:
            points = 1
        else:
            points = 0

        return {
            "count": count,
            "examples": question_headers[:5],  # Return first 5 examples
            "points": points,
            "status": self._get_question_status(count)
        }

    def is_question(self, text: str) -> bool:
        """
        Check if text is formatted as a question

        Args:
            text: Text to check

        Returns:
            True if text appears to be a question
        """
        if not text:
            return False

        text_lower = text.lower().strip()

        # Check if ends with question mark
        if text.endswith('?'):
            return True

        # Check if starts with question word
        first_word = text_lower.split()[0] if text_lower.split() else ""

        return first_word in self.QUESTION_WORDS

    def _get_question_status(self, count: int) -> str:
        """Get human-readable question header status"""
        if count >= 10:
            return "Excellent: 10+ question headers"
        elif count >= 5:
            return "Good: 5-9 question headers"
        else:
            return "Low: Less than 5 question headers"

    def calculate_readability(self, html_content: str) -> Dict[str, Any]:
        """
        Calculate readability score using Flesch Reading Ease

        Args:
            html_content: HTML to analyze

        Returns:
            Readability analysis with score
        """
        if not html_content:
            return {
                "flesch_score": 0,
                "grade_level": "N/A",
                "difficulty": "unknown",
                "points": 0
            }

        try:
            # Extract text from HTML
            text = self.extract_text_from_html(html_content)

            if not text or len(text.strip()) < 100:
                return {
                    "flesch_score": 0,
                    "grade_level": "N/A",
                    "difficulty": "insufficient_text",
                    "points": 0
                }

            # Calculate Flesch Reading Ease
            flesch_score = textstat.flesch_reading_ease(text)

            # Calculate grade level
            grade_level = textstat.flesch_kincaid_grade(text)

            # Determine difficulty and points
            if flesch_score >= 60:
                difficulty = "easy"
                points = 2
                description = "Easy to read (good for voice search)"
            elif flesch_score >= 30:
                difficulty = "moderate"
                points = 1
                description = "Moderate difficulty"
            else:
                difficulty = "difficult"
                points = 0
                description = "Difficult to read (may hurt AEO)"

            return {
                "flesch_score": round(flesch_score, 1),
                "grade_level": round(grade_level, 1),
                "difficulty": difficulty,
                "description": description,
                "points": points,
                "word_count": len(text.split())
            }

        except Exception as e:
            logger.error(f"Error calculating readability: {str(e)}")
            return {
                "flesch_score": 0,
                "grade_level": "N/A",
                "difficulty": "error",
                "points": 0,
                "error": str(e)
            }

    def extract_text_from_html(self, html: str) -> str:
        """
        Extract clean text from HTML

        Args:
            html: HTML content

        Returns:
            Plain text content
        """
        soup = BeautifulSoup(html, 'lxml')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    def _generate_recommendations(
        self,
        faq_analysis: Dict[str, Any],
        question_analysis: Dict[str, Any],
        readability_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # FAQ recommendations
        faq_points = faq_analysis.get('points', 0)
        if faq_points == 0:
            recommendations.append(
                "Create a dedicated FAQ page to improve voice search visibility (+4 points). "
                "Include common customer questions and clear answers."
            )
        elif faq_points <= 3:
            recommendations.append(
                f"Add FAQPage schema to your FAQ page for maximum AEO benefit "
                f"(+{4 - faq_points} points)."
            )

        # Question header recommendations
        question_count = question_analysis.get('count', 0)
        if question_count < 5:
            recommendations.append(
                f"Add {5 - question_count} more question-format headers (e.g., 'How does...?', "
                f"'What is...?') to improve conversational content score."
            )
        elif question_count < 10:
            recommendations.append(
                f"Add {10 - question_count} more question headers to reach excellent level (+1 point)."
            )

        # Readability recommendations
        readability_points = readability_analysis.get('points', 0)
        flesch_score = readability_analysis.get('flesch_score', 0)

        if readability_points < 2:
            if flesch_score < 30:
                recommendations.append(
                    "Simplify your content for better readability (+2 points). "
                    "Use shorter sentences and simpler words. "
                    "Target Flesch score of 60+ for voice search optimization."
                )
            elif flesch_score < 60:
                recommendations.append(
                    "Improve readability slightly for voice search (+1 point). "
                    "Aim for Flesch score above 60 by simplifying some complex sentences."
                )

        # Perfect score congratulations
        total_points = faq_points + question_analysis.get('points', 0) + readability_points
        if total_points == 8:
            recommendations.append(
                "Perfect conversational content! Your site is well-optimized for voice search and AI assistants."
            )

        return recommendations
