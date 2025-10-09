"""
SEO Auto-Optimizer
Automatically optimize content for search engines
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging
import re
from collections import Counter
import json

logger = logging.getLogger(__name__)


class SchemaType(str, Enum):
    """Schema.org markup types"""
    ARTICLE = "Article"
    BLOG_POSTING = "BlogPosting"
    HOW_TO = "HowTo"
    FAQ = "FAQPage"
    PRODUCT = "Product"
    ORGANIZATION = "Organization"


class OptimizationLevel(str, Enum):
    """Optimization aggressiveness levels"""
    MINIMAL = "minimal"  # Only critical fixes
    BALANCED = "balanced"  # Standard optimization
    AGGRESSIVE = "aggressive"  # Maximum SEO optimization


class SEOAutoOptimizer:
    """Automatically optimize content for SEO"""

    def __init__(self):
        """Initialize SEO optimizer"""
        self.max_title_length = 60
        self.max_description_length = 155
        self.ideal_keyword_density = 0.02  # 2%
        self.min_content_length = 300

    async def optimize_content(
        self,
        content: str,
        target_keywords: List[str],
        title: Optional[str] = None,
        optimization_level: str = OptimizationLevel.BALANCED.value
    ) -> Dict:
        """
        Perform comprehensive SEO optimization

        Args:
            content: Content to optimize
            target_keywords: Target keywords to optimize for
            title: Optional title (will be optimized or generated)
            optimization_level: How aggressive to optimize

        Returns:
            Optimized content with SEO improvements
        """
        try:
            primary_keyword = target_keywords[0] if target_keywords else ""

            # Generate/optimize meta tags
            meta_tags = self._generate_meta_tags(
                content,
                title,
                target_keywords,
                primary_keyword
            )

            # Optimize header structure
            optimized_content, header_analysis = self._optimize_headers(
                content,
                target_keywords
            )

            # Analyze and optimize keyword usage
            keyword_analysis = self._analyze_keywords(
                optimized_content,
                target_keywords
            )

            # Generate schema markup
            schema_markup = self._generate_schema_markup(
                meta_tags["title"],
                meta_tags["description"],
                optimized_content,
                SchemaType.ARTICLE
            )

            # Suggest internal links
            internal_links = self._suggest_internal_links(
                optimized_content,
                target_keywords
            )

            # Analyze readability
            readability = self._analyze_readability(optimized_content)

            # Generate optimization recommendations
            recommendations = self._generate_recommendations(
                keyword_analysis,
                header_analysis,
                readability,
                optimization_level
            )

            # Calculate overall SEO score
            seo_score = self._calculate_seo_score(
                keyword_analysis,
                header_analysis,
                readability,
                len(optimized_content.split())
            )

            return {
                "optimized_content": optimized_content,
                "meta_tags": meta_tags,
                "schema_markup": schema_markup,
                "internal_links": internal_links,
                "analysis": {
                    "seo_score": seo_score,
                    "keywords": keyword_analysis,
                    "headers": header_analysis,
                    "readability": readability
                },
                "recommendations": recommendations,
                "optimization_level": optimization_level,
                "optimized_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error optimizing content: {str(e)}")
            raise

    def _generate_meta_tags(
        self,
        content: str,
        title: Optional[str],
        keywords: List[str],
        primary_keyword: str
    ) -> Dict:
        """Generate SEO-optimized meta tags"""
        try:
            # Optimize or generate title
            if title:
                optimized_title = self._optimize_title(title, primary_keyword)
            else:
                optimized_title = self._generate_title_from_content(content, primary_keyword)

            # Generate meta description
            meta_description = self._generate_meta_description(content, keywords)

            # Generate Open Graph tags
            og_tags = {
                "og:title": optimized_title,
                "og:description": meta_description,
                "og:type": "article",
                "og:site_name": "Your Site Name"
            }

            # Generate Twitter Card tags
            twitter_tags = {
                "twitter:card": "summary_large_image",
                "twitter:title": optimized_title,
                "twitter:description": meta_description
            }

            return {
                "title": optimized_title,
                "description": meta_description,
                "keywords": ", ".join(keywords[:5]),
                "robots": "index, follow",
                "canonical": "",  # To be set by application
                "open_graph": og_tags,
                "twitter": twitter_tags
            }

        except Exception as e:
            logger.error(f"Error generating meta tags: {str(e)}")
            raise

    def _optimize_title(self, title: str, primary_keyword: str) -> str:
        """Optimize existing title for SEO"""
        # Ensure keyword is in title
        if primary_keyword.lower() not in title.lower() and primary_keyword:
            title = f"{primary_keyword} - {title}"

        # Truncate if too long
        if len(title) > self.max_title_length:
            title = title[:self.max_title_length - 3] + "..."

        # Capitalize properly
        title = title.title()

        return title

    def _generate_title_from_content(self, content: str, primary_keyword: str) -> str:
        """Generate title from content"""
        # Extract first heading if present
        heading_match = re.search(r'^#+\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            base_title = heading_match.group(1)
        else:
            # Use first sentence
            first_sentence = content.split('.')[0] if '.' in content else content[:50]
            base_title = first_sentence.strip()

        # Ensure keyword is included
        if primary_keyword and primary_keyword.lower() not in base_title.lower():
            base_title = f"{primary_keyword}: {base_title}"

        # Truncate if needed
        if len(base_title) > self.max_title_length:
            base_title = base_title[:self.max_title_length - 3] + "..."

        return base_title

    def _generate_meta_description(self, content: str, keywords: List[str]) -> str:
        """Generate SEO-optimized meta description"""
        # Extract first paragraph or sentences
        paragraphs = content.split('\n\n')
        first_para = paragraphs[0] if paragraphs else content[:200]

        # Remove markdown formatting
        first_para = re.sub(r'[#*_`]', '', first_para)

        # Ensure primary keywords are included
        description = first_para.strip()

        # Add keywords if not present
        if keywords:
            primary_keyword = keywords[0]
            if primary_keyword.lower() not in description.lower():
                description = f"{primary_keyword} - {description}"

        # Truncate to proper length
        if len(description) > self.max_description_length:
            description = description[:self.max_description_length - 3] + "..."

        return description

    def _optimize_headers(self, content: str, keywords: List[str]) -> Tuple[str, Dict]:
        """Optimize header structure for SEO"""
        try:
            # Find all headers
            headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)

            header_analysis = {
                "h1_count": 0,
                "h2_count": 0,
                "h3_count": 0,
                "total_headers": len(headers),
                "keyword_in_headers": 0,
                "header_hierarchy_valid": True
            }

            optimized_content = content
            primary_keyword = keywords[0] if keywords else ""

            for level, text in headers:
                h_level = len(level)

                # Count header levels
                if h_level == 1:
                    header_analysis["h1_count"] += 1
                elif h_level == 2:
                    header_analysis["h2_count"] += 1
                elif h_level == 3:
                    header_analysis["h3_count"] += 1

                # Check keyword presence
                if primary_keyword and primary_keyword.lower() in text.lower():
                    header_analysis["keyword_in_headers"] += 1

            # Validate hierarchy (should have exactly one H1)
            if header_analysis["h1_count"] != 1:
                header_analysis["header_hierarchy_valid"] = False

            return optimized_content, header_analysis

        except Exception as e:
            logger.error(f"Error optimizing headers: {str(e)}")
            return content, {}

    def _analyze_keywords(self, content: str, target_keywords: List[str]) -> Dict:
        """Analyze keyword usage and density"""
        try:
            # Clean content (remove markdown, special chars)
            clean_content = re.sub(r'[#*_`\[\]]', '', content)
            words = clean_content.lower().split()
            total_words = len(words)

            keyword_data = []

            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                count = clean_content.lower().count(keyword_lower)
                density = (count / total_words) if total_words > 0 else 0

                # Check positions (beginning, middle, end)
                positions = {
                    "in_first_paragraph": keyword_lower in content[:200].lower(),
                    "in_last_paragraph": keyword_lower in content[-200:].lower(),
                    "in_headers": keyword_lower in ' '.join(re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)).lower()
                }

                keyword_data.append({
                    "keyword": keyword,
                    "count": count,
                    "density": round(density * 100, 2),
                    "density_percentage": f"{round(density * 100, 2)}%",
                    "positions": positions,
                    "optimal": 0.01 <= density <= 0.03  # 1-3% is good
                })

            return {
                "total_words": total_words,
                "keyword_analysis": keyword_data,
                "primary_keyword_density": keyword_data[0]["density"] if keyword_data else 0,
                "overall_keyword_optimization": self._calculate_keyword_score(keyword_data)
            }

        except Exception as e:
            logger.error(f"Error analyzing keywords: {str(e)}")
            raise

    def _calculate_keyword_score(self, keyword_data: List[Dict]) -> int:
        """Calculate overall keyword optimization score (0-100)"""
        if not keyword_data:
            return 0

        score = 0
        primary = keyword_data[0]

        # Primary keyword density (40 points)
        if primary["optimal"]:
            score += 40
        elif primary["density"] > 0:
            score += 20

        # Primary keyword in strategic positions (30 points)
        positions = primary["positions"]
        if positions["in_first_paragraph"]:
            score += 10
        if positions["in_headers"]:
            score += 10
        if positions["in_last_paragraph"]:
            score += 10

        # Secondary keywords usage (30 points)
        if len(keyword_data) > 1:
            secondary_used = sum(1 for kw in keyword_data[1:] if kw["count"] > 0)
            score += min(30, secondary_used * 10)

        return min(100, score)

    def _generate_schema_markup(
        self,
        title: str,
        description: str,
        content: str,
        schema_type: SchemaType
    ) -> Dict:
        """Generate Schema.org JSON-LD markup"""
        try:
            word_count = len(content.split())
            reading_time = word_count // 200  # Avg reading speed

            if schema_type == SchemaType.ARTICLE or schema_type == SchemaType.BLOG_POSTING:
                schema = {
                    "@context": "https://schema.org",
                    "@type": schema_type.value,
                    "headline": title,
                    "description": description,
                    "author": {
                        "@type": "Person",
                        "name": "Author Name"  # To be populated by application
                    },
                    "datePublished": datetime.now().isoformat(),
                    "dateModified": datetime.now().isoformat(),
                    "wordCount": word_count,
                    "timeRequired": f"PT{reading_time}M",
                    "articleBody": content[:500] + "..."  # Truncated
                }

            elif schema_type == SchemaType.HOW_TO:
                # Extract steps from content
                steps = self._extract_howto_steps(content)
                schema = {
                    "@context": "https://schema.org",
                    "@type": "HowTo",
                    "name": title,
                    "description": description,
                    "step": steps
                }

            elif schema_type == SchemaType.FAQ:
                # Extract Q&A from content
                qa_pairs = self._extract_faq_pairs(content)
                schema = {
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "mainEntity": qa_pairs
                }

            else:
                # Default Article schema
                schema = {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": title,
                    "description": description
                }

            return {
                "json_ld": schema,
                "schema_type": schema_type.value,
                "html": f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'
            }

        except Exception as e:
            logger.error(f"Error generating schema markup: {str(e)}")
            raise

    def _extract_howto_steps(self, content: str) -> List[Dict]:
        """Extract HowTo steps from content"""
        steps = []
        # Look for numbered lists or step patterns
        step_patterns = re.findall(r'(?:Step \d+:|^\d+\.)\s*(.+)', content, re.MULTILINE)

        for idx, step_text in enumerate(step_patterns, 1):
            steps.append({
                "@type": "HowToStep",
                "position": idx,
                "name": f"Step {idx}",
                "text": step_text.strip()
            })

        return steps if steps else [{
            "@type": "HowToStep",
            "position": 1,
            "text": "See article for details"
        }]

    def _extract_faq_pairs(self, content: str) -> List[Dict]:
        """Extract FAQ question-answer pairs"""
        qa_pairs = []

        # Look for question patterns (lines ending with ?)
        lines = content.split('\n')
        current_question = None

        for line in lines:
            if '?' in line:
                current_question = line.strip()
            elif current_question and line.strip():
                qa_pairs.append({
                    "@type": "Question",
                    "name": current_question,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": line.strip()
                    }
                })
                current_question = None

        return qa_pairs if qa_pairs else []

    def _suggest_internal_links(
        self,
        content: str,
        keywords: List[str]
    ) -> List[Dict]:
        """Suggest internal linking opportunities"""
        try:
            suggestions = []

            # Find key phrases that could link to other content
            for keyword in keywords:
                # Count occurrences
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                matches = list(pattern.finditer(content))

                if matches:
                    # Suggest linking first occurrence
                    first_match = matches[0]
                    context_start = max(0, first_match.start() - 50)
                    context_end = min(len(content), first_match.end() + 50)
                    context = content[context_start:context_end]

                    suggestions.append({
                        "anchor_text": keyword,
                        "occurrences": len(matches),
                        "context": f"...{context}...",
                        "position": first_match.start(),
                        "suggestion": f"Link '{keyword}' to related content",
                        "link_type": "internal"
                    })

            # Sort by occurrence count (more = better linking opportunity)
            suggestions.sort(key=lambda x: x["occurrences"], reverse=True)

            return suggestions[:10]  # Top 10 suggestions

        except Exception as e:
            logger.error(f"Error suggesting internal links: {str(e)}")
            return []

    def _analyze_readability(self, content: str) -> Dict:
        """Analyze content readability"""
        try:
            # Clean content
            clean_content = re.sub(r'[#*_`]', '', content)

            # Calculate basic metrics
            sentences = re.split(r'[.!?]+', clean_content)
            sentences = [s.strip() for s in sentences if s.strip()]

            words = clean_content.split()
            total_words = len(words)
            total_sentences = len(sentences)

            # Average sentence length
            avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0

            # Average word length
            avg_word_length = sum(len(w) for w in words) / total_words if total_words > 0 else 0

            # Count syllables (simplified)
            total_syllables = sum(self._count_syllables(word) for word in words)

            # Flesch Reading Ease (simplified)
            if total_sentences > 0 and total_words > 0:
                flesch_score = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
                flesch_score = max(0, min(100, flesch_score))
            else:
                flesch_score = 50

            # Determine grade level
            grade_level = self._calculate_grade_level(avg_sentence_length, avg_word_length)

            return {
                "total_words": total_words,
                "total_sentences": total_sentences,
                "avg_sentence_length": round(avg_sentence_length, 1),
                "avg_word_length": round(avg_word_length, 1),
                "flesch_reading_ease": round(flesch_score, 1),
                "readability_level": self._interpret_flesch_score(flesch_score),
                "grade_level": grade_level,
                "reading_time_minutes": total_words // 200
            }

        except Exception as e:
            logger.error(f"Error analyzing readability: {str(e)}")
            raise

    def _count_syllables(self, word: str) -> int:
        """Count syllables in word (simplified)"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1

        return max(1, syllable_count)

    def _calculate_grade_level(self, avg_sentence_length: float, avg_word_length: float) -> str:
        """Calculate reading grade level"""
        # Simplified grade level calculation
        score = (avg_sentence_length * 0.5) + (avg_word_length * 4)

        if score < 6:
            return "Elementary (5-6th grade)"
        elif score < 9:
            return "Middle School (7-9th grade)"
        elif score < 13:
            return "High School (10-12th grade)"
        else:
            return "College Level"

    def _interpret_flesch_score(self, score: float) -> str:
        """Interpret Flesch Reading Ease score"""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"

    def _generate_recommendations(
        self,
        keyword_analysis: Dict,
        header_analysis: Dict,
        readability: Dict,
        optimization_level: str
    ) -> List[Dict]:
        """Generate SEO improvement recommendations"""
        recommendations = []

        # Keyword recommendations
        primary_kw = keyword_analysis["keyword_analysis"][0] if keyword_analysis["keyword_analysis"] else None

        if primary_kw:
            if not primary_kw["optimal"]:
                if primary_kw["density"] < 1:
                    recommendations.append({
                        "category": "keywords",
                        "priority": "high",
                        "issue": "Primary keyword density too low",
                        "recommendation": f"Increase usage of '{primary_kw['keyword']}' to 1-3% density",
                        "current_value": f"{primary_kw['density']}%",
                        "target_value": "1-3%"
                    })
                elif primary_kw["density"] > 3:
                    recommendations.append({
                        "category": "keywords",
                        "priority": "medium",
                        "issue": "Primary keyword density too high",
                        "recommendation": f"Reduce usage of '{primary_kw['keyword']}' to avoid keyword stuffing",
                        "current_value": f"{primary_kw['density']}%",
                        "target_value": "1-3%"
                    })

            if not primary_kw["positions"]["in_first_paragraph"]:
                recommendations.append({
                    "category": "keywords",
                    "priority": "high",
                    "issue": "Primary keyword missing from introduction",
                    "recommendation": f"Include '{primary_kw['keyword']}' in first paragraph",
                    "current_value": "Not present",
                    "target_value": "Present in first 100 words"
                })

        # Header recommendations
        if header_analysis["h1_count"] != 1:
            recommendations.append({
                "category": "structure",
                "priority": "high",
                "issue": "Incorrect H1 count",
                "recommendation": "Use exactly one H1 heading",
                "current_value": f"{header_analysis['h1_count']} H1 tags",
                "target_value": "1 H1 tag"
            })

        if header_analysis["keyword_in_headers"] == 0:
            recommendations.append({
                "category": "structure",
                "priority": "medium",
                "issue": "Keywords missing from headers",
                "recommendation": "Include target keywords in H2/H3 headings",
                "current_value": "0 headers with keywords",
                "target_value": "At least 2-3 headers"
            })

        # Readability recommendations
        if readability["flesch_reading_ease"] < 50:
            recommendations.append({
                "category": "readability",
                "priority": "medium",
                "issue": "Content difficult to read",
                "recommendation": "Simplify sentences and use shorter words",
                "current_value": f"Flesch score: {readability['flesch_reading_ease']}",
                "target_value": "Score above 60"
            })

        if readability["avg_sentence_length"] > 25:
            recommendations.append({
                "category": "readability",
                "priority": "low",
                "issue": "Sentences too long",
                "recommendation": "Break up long sentences for better readability",
                "current_value": f"{readability['avg_sentence_length']} words/sentence",
                "target_value": "15-20 words/sentence"
            })

        # Content length
        if readability["total_words"] < self.min_content_length:
            recommendations.append({
                "category": "content",
                "priority": "high",
                "issue": "Content too short",
                "recommendation": "Expand content for better SEO performance",
                "current_value": f"{readability['total_words']} words",
                "target_value": f"{self.min_content_length}+ words"
            })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order[x["priority"]])

        return recommendations

    def _calculate_seo_score(
        self,
        keyword_analysis: Dict,
        header_analysis: Dict,
        readability: Dict,
        word_count: int
    ) -> int:
        """Calculate overall SEO score (0-100)"""
        score = 0

        # Keyword optimization (40 points)
        score += keyword_analysis.get("overall_keyword_optimization", 0) * 0.4

        # Header structure (20 points)
        if header_analysis.get("h1_count") == 1:
            score += 10
        if header_analysis.get("keyword_in_headers", 0) > 0:
            score += 10

        # Readability (20 points)
        flesch_score = readability.get("flesch_reading_ease", 50)
        if flesch_score >= 60:
            score += 20
        elif flesch_score >= 50:
            score += 15
        else:
            score += 10

        # Content length (20 points)
        if word_count >= 2000:
            score += 20
        elif word_count >= 1000:
            score += 15
        elif word_count >= 500:
            score += 10
        elif word_count >= 300:
            score += 5

        return min(100, int(score))

    async def optimize_for_featured_snippet(
        self,
        content: str,
        question: str
    ) -> Dict:
        """
        Optimize content to win featured snippets

        Args:
            content: Content to optimize
            question: Target question to answer

        Returns:
            Optimized answer format
        """
        try:
            # Extract relevant paragraph
            paragraphs = content.split('\n\n')

            # Format for different snippet types
            formats = {
                "paragraph": self._format_paragraph_snippet(question, paragraphs),
                "list": self._format_list_snippet(question, content),
                "table": self._format_table_snippet(question, content)
            }

            return {
                "question": question,
                "formats": formats,
                "recommendation": "Use paragraph format for definitions, list for steps/tips, table for comparisons"
            }

        except Exception as e:
            logger.error(f"Error optimizing for featured snippet: {str(e)}")
            raise

    def _format_paragraph_snippet(self, question: str, paragraphs: List[str]) -> str:
        """Format answer as paragraph snippet"""
        # Find most relevant paragraph (simple: first non-empty)
        answer = next((p.strip() for p in paragraphs if p.strip()), "")

        # Truncate to 50-60 words
        words = answer.split()
        if len(words) > 60:
            answer = ' '.join(words[:58]) + "..."

        return f"{question}\n\n{answer}"

    def _format_list_snippet(self, question: str, content: str) -> str:
        """Format answer as list snippet"""
        # Extract numbered or bulleted lists
        lists = re.findall(r'(?:^|\n)(?:\d+\.|[-*])\s*(.+)', content)

        if lists:
            formatted_list = '\n'.join(f"{i+1}. {item}" for i, item in enumerate(lists[:8]))
            return f"{question}\n\n{formatted_list}"

        return ""

    def _format_table_snippet(self, question: str, content: str) -> str:
        """Format answer as table snippet (placeholder)"""
        # Table formatting would require structured data
        return f"{question}\n\n[Table format requires structured comparison data]"
