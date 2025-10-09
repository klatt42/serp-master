"""
Brand Voice Engine
Learn and maintain consistent brand voice across all content
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging
import re
from collections import Counter
import statistics

logger = logging.getLogger(__name__)


class ToneAttribute(str, Enum):
    """Tone spectrum attributes"""
    FORMALITY = "formality"  # formal ↔ casual
    TECHNICALITY = "technicality"  # technical ↔ accessible
    AUTHORITY = "authority"  # authoritative ↔ conversational
    EMOTION = "emotion"  # empathetic ↔ neutral


class VoiceDeviation(str, Enum):
    """Types of voice deviations"""
    TONE_MISMATCH = "tone_mismatch"
    VOCABULARY_MISMATCH = "vocabulary_mismatch"
    SENTENCE_STRUCTURE = "sentence_structure"
    PERSONALITY_SHIFT = "personality_shift"


class BrandVoiceEngine:
    """Analyze and maintain brand voice consistency"""

    def __init__(self):
        """Initialize brand voice engine"""
        self.voice_profiles = {}

    async def create_voice_profile(
        self,
        profile_name: str,
        example_content: List[str],
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create brand voice profile from example content

        Args:
            profile_name: Name for this voice profile
            example_content: 3-5 example pieces representing ideal voice
            metadata: Additional profile information

        Returns:
            Voice profile with analyzed characteristics
        """
        try:
            if len(example_content) < 3:
                raise ValueError("Minimum 3 example pieces required for voice analysis")

            # Analyze tone parameters
            tone_params = self._extract_tone_parameters(example_content)

            # Extract vocabulary preferences
            vocabulary = self._analyze_vocabulary(example_content)

            # Analyze sentence structure
            sentence_structure = self._analyze_sentence_structure(example_content)

            # Identify personality traits
            personality = self._identify_personality_traits(example_content)

            profile = {
                "profile_name": profile_name,
                "tone_parameters": tone_params,
                "vocabulary_preferences": vocabulary,
                "sentence_structure": sentence_structure,
                "personality_traits": personality,
                "example_content": example_content,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "example_count": len(example_content),
                    "total_words": sum(len(content.split()) for content in example_content),
                    **(metadata or {})
                }
            }

            self.voice_profiles[profile_name] = profile
            logger.info(f"Created voice profile: {profile_name}")
            return profile

        except Exception as e:
            logger.error(f"Error creating voice profile: {str(e)}")
            raise

    def _extract_tone_parameters(self, content_list: List[str]) -> Dict:
        """Extract tone spectrum parameters from content"""
        try:
            tone_scores = {
                "formality": [],
                "technicality": [],
                "authority": [],
                "emotion": []
            }

            for content in content_list:
                # Formality score (0-100: casual to formal)
                formality = self._calculate_formality(content)
                tone_scores["formality"].append(formality)

                # Technicality score (0-100: accessible to technical)
                technicality = self._calculate_technicality(content)
                tone_scores["technicality"].append(technicality)

                # Authority score (0-100: conversational to authoritative)
                authority = self._calculate_authority(content)
                tone_scores["authority"].append(authority)

                # Emotion score (0-100: neutral to empathetic)
                emotion = self._calculate_emotion(content)
                tone_scores["emotion"].append(emotion)

            # Average scores across all examples
            return {
                "formality": {
                    "score": int(statistics.mean(tone_scores["formality"])),
                    "variance": round(statistics.variance(tone_scores["formality"]) if len(tone_scores["formality"]) > 1 else 0, 2)
                },
                "technicality": {
                    "score": int(statistics.mean(tone_scores["technicality"])),
                    "variance": round(statistics.variance(tone_scores["technicality"]) if len(tone_scores["technicality"]) > 1 else 0, 2)
                },
                "authority": {
                    "score": int(statistics.mean(tone_scores["authority"])),
                    "variance": round(statistics.variance(tone_scores["authority"]) if len(tone_scores["authority"]) > 1 else 0, 2)
                },
                "emotion": {
                    "score": int(statistics.mean(tone_scores["emotion"])),
                    "variance": round(statistics.variance(tone_scores["emotion"]) if len(tone_scores["emotion"]) > 1 else 0, 2)
                }
            }

        except Exception as e:
            logger.error(f"Error extracting tone parameters: {str(e)}")
            raise

    def _calculate_formality(self, content: str) -> int:
        """Calculate formality score (0=casual, 100=formal)"""
        score = 50  # Start neutral

        # Formal indicators
        formal_words = ["therefore", "furthermore", "consequently", "moreover", "thus", "henceforth"]
        contractions = ["'ll", "'ve", "'re", "'s", "'d", "n't"]

        # Count formal words (increases score)
        formal_count = sum(1 for word in formal_words if word in content.lower())
        score += min(20, formal_count * 5)

        # Count contractions (decreases score)
        contraction_count = sum(1 for cont in contractions if cont in content.lower())
        score -= min(20, contraction_count * 3)

        # Sentence length (longer = more formal)
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = statistics.mean([len(s.split()) for s in sentences if s.strip()])
        if avg_sentence_length > 20:
            score += 15
        elif avg_sentence_length < 12:
            score -= 15

        return max(0, min(100, score))

    def _calculate_technicality(self, content: str) -> int:
        """Calculate technicality score (0=accessible, 100=technical)"""
        score = 50  # Start neutral

        # Technical indicators
        technical_markers = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+\.js\b|\b\w+\.py\b',  # File extensions
            r'\bAPI\b|\bSDK\b|\bJSON\b|\bXML\b',  # Tech terms
        ]

        # Count technical patterns
        tech_count = sum(len(re.findall(pattern, content)) for pattern in technical_markers)
        score += min(30, tech_count * 5)

        # Jargon density (words > 12 characters)
        words = content.split()
        long_words = [w for w in words if len(w) > 12]
        jargon_density = len(long_words) / len(words) if words else 0
        score += int(jargon_density * 100)

        return max(0, min(100, score))

    def _calculate_authority(self, content: str) -> int:
        """Calculate authority score (0=conversational, 100=authoritative)"""
        score = 50  # Start neutral

        # Authoritative indicators
        authoritative_phrases = [
            "research shows", "studies indicate", "experts agree",
            "according to", "proven", "demonstrated", "established"
        ]

        # Count authoritative phrases
        auth_count = sum(1 for phrase in authoritative_phrases if phrase in content.lower())
        score += min(25, auth_count * 8)

        # Questions (decrease authority)
        question_count = content.count('?')
        score -= min(15, question_count * 3)

        # Declarative statements (increase authority)
        statements = content.count('.')
        if statements > question_count * 3:
            score += 10

        return max(0, min(100, score))

    def _calculate_emotion(self, content: str) -> int:
        """Calculate emotion score (0=neutral, 100=empathetic)"""
        score = 50  # Start neutral

        # Emotional words
        emotional_words = [
            "feel", "understand", "care", "help", "support", "excited",
            "love", "amazing", "wonderful", "challenging", "difficult"
        ]

        # Count emotional words
        emotion_count = sum(1 for word in emotional_words if word in content.lower())
        score += min(30, emotion_count * 5)

        # Exclamation marks (increase emotion)
        exclamation_count = content.count('!')
        score += min(15, exclamation_count * 5)

        # Personal pronouns (increase empathy)
        personal_pronouns = ["you", "your", "we", "us", "our"]
        pronoun_count = sum(content.lower().count(pronoun) for pronoun in personal_pronouns)
        score += min(20, pronoun_count * 2)

        return max(0, min(100, score))

    def _analyze_vocabulary(self, content_list: List[str]) -> Dict:
        """Analyze vocabulary preferences"""
        try:
            all_words = []
            for content in content_list:
                words = re.findall(r'\b[a-z]+\b', content.lower())
                all_words.extend(words)

            # Get word frequency
            word_freq = Counter(all_words)

            # Most common words (excluding stop words)
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "is", "was", "are", "be"}
            preferred_words = [
                word for word, _ in word_freq.most_common(50)
                if word not in stop_words and len(word) > 4
            ]

            # Calculate unique word ratio
            unique_ratio = len(set(all_words)) / len(all_words) if all_words else 0

            return {
                "preferred_terms": preferred_words[:20],
                "vocabulary_richness": round(unique_ratio, 2),
                "avg_word_length": round(statistics.mean([len(w) for w in all_words]) if all_words else 0, 1),
                "total_unique_words": len(set(all_words))
            }

        except Exception as e:
            logger.error(f"Error analyzing vocabulary: {str(e)}")
            raise

    def _analyze_sentence_structure(self, content_list: List[str]) -> Dict:
        """Analyze sentence structure patterns"""
        try:
            all_sentences = []
            for content in content_list:
                sentences = re.split(r'[.!?]+', content)
                sentences = [s.strip() for s in sentences if s.strip()]
                all_sentences.extend(sentences)

            # Calculate sentence metrics
            sentence_lengths = [len(s.split()) for s in all_sentences]

            return {
                "avg_sentence_length": round(statistics.mean(sentence_lengths) if sentence_lengths else 0, 1),
                "sentence_length_variance": round(statistics.variance(sentence_lengths) if len(sentence_lengths) > 1 else 0, 2),
                "min_sentence_length": min(sentence_lengths) if sentence_lengths else 0,
                "max_sentence_length": max(sentence_lengths) if sentence_lengths else 0,
                "complexity_level": self._determine_complexity(sentence_lengths)
            }

        except Exception as e:
            logger.error(f"Error analyzing sentence structure: {str(e)}")
            raise

    def _determine_complexity(self, sentence_lengths: List[int]) -> str:
        """Determine complexity level from sentence lengths"""
        if not sentence_lengths:
            return "unknown"

        avg_length = statistics.mean(sentence_lengths)

        if avg_length < 10:
            return "simple"
        elif avg_length < 15:
            return "moderate"
        elif avg_length < 20:
            return "complex"
        else:
            return "very_complex"

    def _identify_personality_traits(self, content_list: List[str]) -> Dict:
        """Identify personality traits from content"""
        try:
            traits = {
                "authoritative": 0,
                "friendly": 0,
                "humorous": 0,
                "empathetic": 0,
                "professional": 0
            }

            for content in content_list:
                content_lower = content.lower()

                # Authoritative: citations, facts, data
                if any(word in content_lower for word in ["research", "study", "data", "according"]):
                    traits["authoritative"] += 1

                # Friendly: personal pronouns, casual language
                if any(word in content_lower for word in ["you", "we", "us", "let's"]):
                    traits["friendly"] += 1

                # Humorous: exclamations, playful language
                if '!' in content or any(word in content_lower for word in ["fun", "exciting", "amazing"]):
                    traits["humorous"] += 1

                # Empathetic: understanding, supportive language
                if any(word in content_lower for word in ["understand", "help", "support", "feel"]):
                    traits["empathetic"] += 1

                # Professional: industry terms, formal structure
                if any(word in content_lower for word in ["therefore", "furthermore", "consequently"]):
                    traits["professional"] += 1

            # Normalize to percentages
            total = sum(traits.values())
            if total > 0:
                traits = {k: round((v / total) * 100, 1) for k, v in traits.items()}

            return {
                "primary_traits": [k for k, v in sorted(traits.items(), key=lambda x: x[1], reverse=True)[:3]],
                "trait_scores": traits
            }

        except Exception as e:
            logger.error(f"Error identifying personality traits: {str(e)}")
            raise

    async def analyze_voice_consistency(
        self,
        profile_name: str,
        content: str
    ) -> Dict:
        """
        Analyze content against voice profile

        Args:
            profile_name: Name of voice profile to check against
            content: Content to analyze

        Returns:
            Consistency score (0-100) and deviation details
        """
        try:
            if profile_name not in self.voice_profiles:
                raise ValueError(f"Voice profile '{profile_name}' not found")

            profile = self.voice_profiles[profile_name]

            # Analyze content tone
            content_tone = self._extract_tone_parameters([content])

            # Calculate tone deviation
            tone_deviation = self._calculate_tone_deviation(
                profile["tone_parameters"],
                content_tone
            )

            # Analyze vocabulary match
            vocab_score = self._calculate_vocabulary_match(
                profile["vocabulary_preferences"],
                content
            )

            # Analyze sentence structure match
            structure_score = self._calculate_structure_match(
                profile["sentence_structure"],
                content
            )

            # Calculate overall consistency score
            consistency_score = int(
                (100 - tone_deviation) * 0.40 +
                vocab_score * 0.30 +
                structure_score * 0.30
            )

            # Identify deviations
            deviations = self._identify_deviations(
                profile,
                content,
                tone_deviation,
                vocab_score,
                structure_score
            )

            return {
                "consistency_score": consistency_score,
                "profile_name": profile_name,
                "analysis": {
                    "tone_deviation": round(tone_deviation, 1),
                    "vocabulary_match": vocab_score,
                    "structure_match": structure_score
                },
                "deviations": deviations,
                "passes_threshold": consistency_score >= 70,
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing voice consistency: {str(e)}")
            raise

    def _calculate_tone_deviation(
        self,
        profile_tone: Dict,
        content_tone: Dict
    ) -> float:
        """Calculate deviation from profile tone (0=perfect match, 100=complete mismatch)"""
        try:
            deviations = []

            for attribute in ["formality", "technicality", "authority", "emotion"]:
                profile_score = profile_tone[attribute]["score"]
                content_score = content_tone[attribute]["score"]
                deviation = abs(profile_score - content_score)
                deviations.append(deviation)

            return statistics.mean(deviations)

        except Exception as e:
            logger.error(f"Error calculating tone deviation: {str(e)}")
            return 50.0

    def _calculate_vocabulary_match(self, profile_vocab: Dict, content: str) -> int:
        """Calculate vocabulary match score (0-100)"""
        try:
            # Extract words from content
            content_words = set(re.findall(r'\b[a-z]+\b', content.lower()))

            # Check how many preferred terms are used
            preferred_terms = set(profile_vocab.get("preferred_terms", []))
            if not preferred_terms:
                return 70  # Default score if no preferred terms

            matches = len(content_words.intersection(preferred_terms))
            match_ratio = matches / len(preferred_terms)

            # Calculate word length similarity
            avg_word_length = statistics.mean([len(w) for w in content_words]) if content_words else 0
            profile_avg = profile_vocab.get("avg_word_length", 5)
            length_diff = abs(avg_word_length - profile_avg)
            length_score = max(0, 100 - (length_diff * 10))

            # Combine scores
            return int((match_ratio * 100 * 0.6) + (length_score * 0.4))

        except Exception as e:
            logger.error(f"Error calculating vocabulary match: {str(e)}")
            return 50

    def _calculate_structure_match(self, profile_structure: Dict, content: str) -> int:
        """Calculate sentence structure match score (0-100)"""
        try:
            # Analyze content structure
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]

            if not sentences:
                return 0

            sentence_lengths = [len(s.split()) for s in sentences]
            avg_length = statistics.mean(sentence_lengths)

            # Compare to profile
            profile_avg = profile_structure.get("avg_sentence_length", 15)
            length_diff = abs(avg_length - profile_avg)

            # Calculate score (closer = better)
            score = max(0, 100 - (length_diff * 5))

            # Check complexity match
            content_complexity = self._determine_complexity(sentence_lengths)
            profile_complexity = profile_structure.get("complexity_level", "moderate")

            if content_complexity == profile_complexity:
                score += 10  # Bonus for matching complexity

            return min(100, int(score))

        except Exception as e:
            logger.error(f"Error calculating structure match: {str(e)}")
            return 50

    def _identify_deviations(
        self,
        profile: Dict,
        content: str,
        tone_deviation: float,
        vocab_score: int,
        structure_score: int
    ) -> List[Dict]:
        """Identify specific voice deviations"""
        deviations = []

        if tone_deviation > 30:
            deviations.append({
                "type": VoiceDeviation.TONE_MISMATCH.value,
                "severity": "high" if tone_deviation > 50 else "medium",
                "description": f"Tone differs from brand voice by {tone_deviation:.0f} points",
                "recommendation": "Adjust formality, technicality, or emotional tone"
            })

        if vocab_score < 50:
            deviations.append({
                "type": VoiceDeviation.VOCABULARY_MISMATCH.value,
                "severity": "high" if vocab_score < 30 else "medium",
                "description": "Vocabulary doesn't match brand preferred terms",
                "recommendation": f"Use more terms from brand vocabulary: {', '.join(profile['vocabulary_preferences']['preferred_terms'][:5])}"
            })

        if structure_score < 50:
            deviations.append({
                "type": VoiceDeviation.SENTENCE_STRUCTURE.value,
                "severity": "high" if structure_score < 30 else "medium",
                "description": "Sentence structure differs from brand style",
                "recommendation": f"Aim for avg sentence length of {profile['sentence_structure']['avg_sentence_length']} words"
            })

        return deviations

    async def suggest_voice_improvements(
        self,
        profile_name: str,
        content: str
    ) -> Dict:
        """
        Generate specific improvement suggestions

        Args:
            profile_name: Voice profile to match
            content: Content to improve

        Returns:
            Specific rewrite suggestions
        """
        try:
            # First analyze consistency
            analysis = await self.analyze_voice_consistency(profile_name, content)

            suggestions = []

            for deviation in analysis["deviations"]:
                if deviation["type"] == VoiceDeviation.TONE_MISMATCH.value:
                    suggestions.append({
                        "category": "tone",
                        "priority": "high",
                        "suggestion": "Adjust tone to match brand voice",
                        "examples": self._generate_tone_examples(profile_name)
                    })

                elif deviation["type"] == VoiceDeviation.VOCABULARY_MISMATCH.value:
                    suggestions.append({
                        "category": "vocabulary",
                        "priority": "medium",
                        "suggestion": "Use brand preferred terminology",
                        "examples": self._generate_vocabulary_examples(profile_name)
                    })

                elif deviation["type"] == VoiceDeviation.SENTENCE_STRUCTURE.value:
                    suggestions.append({
                        "category": "structure",
                        "priority": "medium",
                        "suggestion": "Adjust sentence length and complexity",
                        "examples": self._generate_structure_examples(profile_name)
                    })

            return {
                "consistency_score": analysis["consistency_score"],
                "suggestions": suggestions,
                "total_suggestions": len(suggestions),
                "priority_suggestions": [s for s in suggestions if s["priority"] == "high"]
            }

        except Exception as e:
            logger.error(f"Error suggesting improvements: {str(e)}")
            raise

    def _generate_tone_examples(self, profile_name: str) -> List[str]:
        """Generate tone adjustment examples"""
        profile = self.voice_profiles.get(profile_name)
        if not profile:
            return []

        return [
            "Review example content in brand voice profile",
            "Match formality and technical level of examples",
            "Maintain consistent emotional tone throughout"
        ]

    def _generate_vocabulary_examples(self, profile_name: str) -> List[str]:
        """Generate vocabulary examples"""
        profile = self.voice_profiles.get(profile_name)
        if not profile:
            return []

        preferred = profile["vocabulary_preferences"]["preferred_terms"][:5]
        return [
            f"Use terms like: {', '.join(preferred)}",
            "Avoid overly complex jargon unless technically appropriate",
            "Maintain consistent terminology across content"
        ]

    def _generate_structure_examples(self, profile_name: str) -> List[str]:
        """Generate structure examples"""
        profile = self.voice_profiles.get(profile_name)
        if not profile:
            return []

        avg_length = profile["sentence_structure"]["avg_sentence_length"]
        complexity = profile["sentence_structure"]["complexity_level"]

        return [
            f"Target average sentence length: {avg_length} words",
            f"Maintain {complexity} complexity level",
            "Vary sentence structure while staying within target range"
        ]

    def list_profiles(self) -> List[Dict]:
        """List all voice profiles"""
        return [
            {
                "profile_name": name,
                "created_at": profile["metadata"]["created_at"],
                "example_count": profile["metadata"]["example_count"]
            }
            for name, profile in self.voice_profiles.items()
        ]

    def get_profile(self, profile_name: str) -> Optional[Dict]:
        """Get specific voice profile"""
        return self.voice_profiles.get(profile_name)
