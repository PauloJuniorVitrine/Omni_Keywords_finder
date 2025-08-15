# Automated Content Optimizer using Machine Learning
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime
import re

class ContentOptimizer:
    def __init__(self):
        self.optimization_rules = {}
        self.content_templates = {}
        self.performance_metrics = {}
        self.optimization_history = []
        
    def optimize_content(self, content: str, target_keyword: str, 
                        optimization_goals: List[str]) -> Dict[str, Any]:
        """Automatically optimize content based on goals"""
        original_content = content
        optimization_results = {
            'original_content': original_content,
            'optimized_content': content,
            'optimizations_applied': [],
            'improvement_score': 0.0,
            'recommendations': []
        }
        
        # Analyze current content
        content_analysis = self._analyze_content(content, target_keyword)
        
        # Apply optimizations based on goals
        for goal in optimization_goals:
            if goal == 'seo':
                content, seo_optimizations = self._apply_seo_optimizations(content, target_keyword, content_analysis)
                optimization_results['optimizations_applied'].extend(seo_optimizations)
            
            elif goal == 'readability':
                content, readability_optimizations = self._apply_readability_optimizations(content, content_analysis)
                optimization_results['optimizations_applied'].extend(readability_optimizations)
            
            elif goal == 'engagement':
                content, engagement_optimizations = self._apply_engagement_optimizations(content, content_analysis)
                optimization_results['optimizations_applied'].extend(engagement_optimizations)
            
            elif goal == 'conversion':
                content, conversion_optimizations = self._apply_conversion_optimizations(content, content_analysis)
                optimization_results['optimizations_applied'].extend(conversion_optimizations)
        
        # Update optimized content
        optimization_results['optimized_content'] = content
        
        # Calculate improvement score
        optimization_results['improvement_score'] = self._calculate_improvement_score(
            original_content, content, content_analysis
        )
        
        # Generate recommendations
        optimization_results['recommendations'] = self._generate_optimization_recommendations(
            content_analysis, optimization_results['optimizations_applied']
        )
        
        # Store optimization history
        self._store_optimization_history(optimization_results)
        
        return optimization_results
    
    def _analyze_content(self, content: str, target_keyword: str) -> Dict[str, Any]:
        """Analyze content for optimization opportunities"""
        analysis = {
            'word_count': len(content.split()),
            'sentence_count': len(content.split('.')),
            'paragraph_count': len(content.split('\n\n')),
            'keyword_density': self._calculate_keyword_density(content, target_keyword),
            'readability_score': self._calculate_readability_score(content),
            'heading_structure': self._analyze_heading_structure(content),
            'content_structure': self._analyze_content_structure(content),
            'keyword_placement': self._analyze_keyword_placement(content, target_keyword),
            'engagement_indicators': self._analyze_engagement_indicators(content),
            'conversion_elements': self._analyze_conversion_elements(content)
        }
        
        return analysis
    
    def _calculate_keyword_density(self, content: str, keyword: str) -> float:
        """Calculate keyword density"""
        words = content.lower().split()
        keyword_count = content.lower().count(keyword.lower())
        
        return keyword_count / len(words) if words else 0
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score (Flesch Reading Ease)"""
        sentences = content.split('.')
        words = content.split()
        
        if not sentences or not words:
            return 0.0
        
        # Simplified Flesch score calculation
        avg_sentence_length = len(words) / len(sentences)
        syllables = self._count_syllables(content)
        avg_syllables_per_word = syllables / len(words) if words else 0
        
        # Flesch Reading Ease formula
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        return max(0.0, min(100.0, flesch_score))
    
    def _count_syllables(self, text: str) -> int:
        """Count syllables in text"""
        vowels = 'aeiouy'
        count = 0
        text = text.lower()
        
        for word in text.split():
            word_count = 0
            prev_vowel = False
            
            for char in word:
                if char in vowels:
                    if not prev_vowel:
                        word_count += 1
                    prev_vowel = True
                else:
                    prev_vowel = False
            
            if word_count == 0:
                word_count = 1
            
            count += word_count
        
        return count
    
    def _analyze_heading_structure(self, content: str) -> Dict[str, Any]:
        """Analyze heading structure"""
        lines = content.split('\n')
        headings = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                headings.append({'level': level, 'text': text})
        
        return {
            'headings': headings,
            'has_h1': any(h['level'] == 1 for h in headings),
            'heading_count': len(headings),
            'structure_score': self._calculate_heading_structure_score(headings)
        }
    
    def _calculate_heading_structure_score(self, headings: List[Dict[str, Any]]) -> float:
        """Calculate heading structure score"""
        if not headings:
            return 0.0
        
        score = 0.0
        
        # Check for H1
        if any(h['level'] == 1 for h in headings):
            score += 0.3
        
        # Check heading hierarchy
        for i in range(len(headings) - 1):
            if headings[i+1]['level'] - headings[i]['level'] <= 1:
                score += 0.1
        
        # Check heading length
        for heading in headings:
            if 3 <= len(heading['text']) <= 60:
                score += 0.1
        
        return min(1.0, score)
    
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        paragraphs = content.split('\n\n')
        
        return {
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': np.mean([len(p.split()) for p in paragraphs]) if paragraphs else 0,
            'has_lists': '•' in content or '-' in content or re.search(r'\d+\.', content),
            'has_images': '[image]' in content or '<img' in content,
            'structure_score': self._calculate_content_structure_score(paragraphs)
        }
    
    def _calculate_content_structure_score(self, paragraphs: List[str]) -> float:
        """Calculate content structure score"""
        if not paragraphs:
            return 0.0
        
        score = 0.0
        
        # Paragraph count score
        if 3 <= len(paragraphs) <= 10:
            score += 0.3
        elif len(paragraphs) > 10:
            score += 0.2
        
        # Paragraph length score
        avg_length = np.mean([len(p.split()) for p in paragraphs])
        if 50 <= avg_length <= 200:
            score += 0.3
        elif 20 <= avg_length <= 300:
            score += 0.2
        
        return min(1.0, score)
    
    def _analyze_keyword_placement(self, content: str, keyword: str) -> Dict[str, Any]:
        """Analyze keyword placement"""
        content_lower = content.lower()
        keyword_lower = keyword.lower()
        
        positions = []
        start = 0
        while True:
            pos = content_lower.find(keyword_lower, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        placement_score = 0.0
        issues = []
        
        if not positions:
            issues.append("Keyword not found in content")
        else:
            # Check first paragraph
            first_third = len(content) // 3
            if positions[0] > first_third:
                issues.append("Keyword not in first paragraph")
            else:
                placement_score += 0.3
            
            # Check title/heading
            if keyword_lower in content_lower[:100]:
                placement_score += 0.2
            
            # Check distribution
            if len(positions) > 1:
                placement_score += 0.2
        
        return {
            'positions': positions,
            'placement_score': placement_score,
            'issues': issues
        }
    
    def _analyze_engagement_indicators(self, content: str) -> Dict[str, Any]:
        """Analyze engagement indicators"""
        engagement_words = [
            'amazing', 'incredible', 'unbelievable', 'fantastic', 'wonderful',
            'excellent', 'outstanding', 'brilliant', 'perfect', 'best'
        ]
        
        question_words = ['what', 'how', 'why', 'when', 'where', 'who']
        
        engagement_count = sum(content.lower().count(word) for word in engagement_words)
        question_count = sum(content.lower().count(word) for word in question_words)
        
        return {
            'engagement_words': engagement_count,
            'questions': question_count,
            'engagement_score': min(1.0, (engagement_count + question_count) / 10)
        }
    
    def _analyze_conversion_elements(self, content: str) -> Dict[str, Any]:
        """Analyze conversion elements"""
        cta_words = ['buy', 'download', 'sign up', 'subscribe', 'get', 'try', 'start']
        cta_count = sum(content.lower().count(word) for word in cta_words)
        
        return {
            'cta_count': cta_count,
            'conversion_score': min(1.0, cta_count / 5)
        }
    
    def _apply_seo_optimizations(self, content: str, target_keyword: str, 
                               analysis: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Apply SEO optimizations"""
        optimizations = []
        
        # Optimize keyword density
        current_density = analysis['keyword_density']
        if current_density < 0.01:  # Too low
            content = self._increase_keyword_density(content, target_keyword)
            optimizations.append("Increased keyword density")
        elif current_density > 0.03:  # Too high
            content = self._decrease_keyword_density(content, target_keyword)
            optimizations.append("Decreased keyword density")
        
        # Optimize heading structure
        if not analysis['heading_structure']['has_h1']:
            content = self._add_h1_heading(content, target_keyword)
            optimizations.append("Added H1 heading with target keyword")
        
        # Optimize keyword placement
        if analysis['keyword_placement']['placement_score'] < 0.5:
            content = self._improve_keyword_placement(content, target_keyword)
            optimizations.append("Improved keyword placement")
        
        return content, optimizations
    
    def _apply_readability_optimizations(self, content: str, 
                                       analysis: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Apply readability optimizations"""
        optimizations = []
        
        # Improve readability score
        readability_score = analysis['readability_score']
        if readability_score < 60:
            content = self._improve_readability(content)
            optimizations.append("Improved readability")
        
        # Optimize sentence length
        if analysis['sentence_count'] > 0:
            avg_sentence_length = analysis['word_count'] / analysis['sentence_count']
            if avg_sentence_length > 20:
                content = self._shorten_sentences(content)
                optimizations.append("Shortened sentences")
        
        # Optimize paragraph structure
        if analysis['content_structure']['paragraph_count'] < 3:
            content = self._improve_paragraph_structure(content)
            optimizations.append("Improved paragraph structure")
        
        return content, optimizations
    
    def _apply_engagement_optimizations(self, content: str, 
                                      analysis: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Apply engagement optimizations"""
        optimizations = []
        
        # Add engagement words
        if analysis['engagement_indicators']['engagement_score'] < 0.3:
            content = self._add_engagement_words(content)
            optimizations.append("Added engagement words")
        
        # Add questions
        if analysis['engagement_indicators']['questions'] < 2:
            content = self._add_questions(content)
            optimizations.append("Added engaging questions")
        
        # Improve content structure
        if not analysis['content_structure']['has_lists']:
            content = self._add_lists(content)
            optimizations.append("Added bullet points and lists")
        
        return content, optimizations
    
    def _apply_conversion_optimizations(self, content: str, 
                                      analysis: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Apply conversion optimizations"""
        optimizations = []
        
        # Add call-to-action elements
        if analysis['conversion_elements']['cta_count'] < 2:
            content = self._add_cta_elements(content)
            optimizations.append("Added call-to-action elements")
        
        # Add social proof elements
        content = self._add_social_proof(content)
        optimizations.append("Added social proof elements")
        
        return content, optimizations
    
    def _increase_keyword_density(self, content: str, keyword: str) -> str:
        """Increase keyword density naturally"""
        # Add keyword in strategic places
        sentences = content.split('.')
        
        # Add to first paragraph
        if sentences:
            first_sentence = sentences[0]
            if keyword.lower() not in first_sentence.lower():
                sentences[0] = f"{keyword} is an important topic. {first_sentence}"
        
        return '.'.join(sentences)
    
    def _decrease_keyword_density(self, content: str, keyword: str) -> str:
        """Decrease keyword density"""
        # Replace some instances with synonyms or remove
        # This is a simplified approach
        return content
    
    def _add_h1_heading(self, content: str, keyword: str) -> str:
        """Add H1 heading with target keyword"""
        return f"# {keyword.title()}\n\n{content}"
    
    def _improve_keyword_placement(self, content: str, keyword: str) -> str:
        """Improve keyword placement"""
        # Move keyword to beginning if not present
        if keyword.lower() not in content.lower()[:100]:
            content = f"{keyword} is a key topic. {content}"
        
        return content
    
    def _improve_readability(self, content: str) -> str:
        """Improve readability"""
        # Break long sentences
        sentences = content.split('.')
        improved_sentences = []
        
        for sentence in sentences:
            if len(sentence.split()) > 20:
                # Split long sentences
                words = sentence.split()
                mid_point = len(words) // 2
                improved_sentences.append(' '.join(words[:mid_point]) + '.')
                improved_sentences.append(' '.join(words[mid_point:]))
            else:
                improved_sentences.append(sentence)
        
        return '. '.join(improved_sentences)
    
    def _shorten_sentences(self, content: str) -> str:
        """Shorten sentences"""
        return self._improve_readability(content)
    
    def _improve_paragraph_structure(self, content: str) -> str:
        """Improve paragraph structure"""
        sentences = content.split('.')
        
        # Group sentences into paragraphs
        paragraphs = []
        current_paragraph = []
        
        for sentence in sentences:
            current_paragraph.append(sentence)
            if len(current_paragraph) >= 3:
                paragraphs.append('. '.join(current_paragraph))
                current_paragraph = []
        
        if current_paragraph:
            paragraphs.append('. '.join(current_paragraph))
        
        return '\n\n'.join(paragraphs)
    
    def _add_engagement_words(self, content: str) -> str:
        """Add engagement words"""
        engagement_phrases = [
            "amazing results", "incredible benefits", "fantastic opportunities",
            "excellent performance", "outstanding quality"
        ]
        
        # Add engagement phrase to first paragraph
        first_paragraph_end = content.find('\n\n')
        if first_paragraph_end == -1:
            first_paragraph_end = len(content)
        
        engagement_phrase = np.random.choice(engagement_phrases)
        content = content[:first_paragraph_end] + f" {engagement_phrase}." + content[first_paragraph_end:]
        
        return content
    
    def _add_questions(self, content: str) -> str:
        """Add engaging questions"""
        questions = [
            "Have you ever wondered about this?",
            "What if you could improve your results?",
            "Are you ready to take the next step?"
        ]
        
        # Add question after first paragraph
        first_paragraph_end = content.find('\n\n')
        if first_paragraph_end == -1:
            first_paragraph_end = len(content)
        
        question = np.random.choice(questions)
        content = content[:first_paragraph_end] + f"\n\n{question}" + content[first_paragraph_end:]
        
        return content
    
    def _add_lists(self, content: str) -> str:
        """Add bullet points and lists"""
        # Add a simple list
        list_content = "\n\nKey benefits:\n• Improved performance\n• Better results\n• Enhanced experience"
        
        # Insert list after first paragraph
        first_paragraph_end = content.find('\n\n')
        if first_paragraph_end == -1:
            first_paragraph_end = len(content)
        
        content = content[:first_paragraph_end] + list_content + content[first_paragraph_end:]
        
        return content
    
    def _add_cta_elements(self, content: str) -> str:
        """Add call-to-action elements"""
        cta_phrases = [
            "Get started today!",
            "Try it now for better results",
            "Download your free guide"
        ]
        
        cta = np.random.choice(cta_phrases)
        content += f"\n\n{cta}"
        
        return content
    
    def _add_social_proof(self, content: str) -> str:
        """Add social proof elements"""
        social_proof = "\n\nJoin thousands of satisfied users who have already improved their results."
        content += social_proof
        
        return content
    
    def _calculate_improvement_score(self, original_content: str, optimized_content: str,
                                   analysis: Dict[str, Any]) -> float:
        """Calculate improvement score"""
        score = 0.0
        
        # Content length improvement
        original_length = len(original_content.split())
        optimized_length = len(optimized_content.split())
        if optimized_length >= 300:  # Minimum recommended length
            score += 0.2
        
        # Readability improvement
        original_readability = self._calculate_readability_score(original_content)
        optimized_readability = self._calculate_readability_score(optimized_content)
        if optimized_readability > original_readability:
            score += 0.2
        
        # Structure improvement
        if analysis['heading_structure']['has_h1']:
            score += 0.2
        
        if analysis['content_structure']['paragraph_count'] >= 3:
            score += 0.2
        
        # Engagement improvement
        if analysis['engagement_indicators']['engagement_score'] > 0.3:
            score += 0.2
        
        return min(1.0, score)
    
    def _generate_optimization_recommendations(self, analysis: Dict[str, Any],
                                            optimizations_applied: List[str]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # SEO recommendations
        if analysis['keyword_density'] < 0.01:
            recommendations.append("Consider increasing keyword density naturally")
        
        if not analysis['heading_structure']['has_h1']:
            recommendations.append("Add an H1 heading with your target keyword")
        
        # Readability recommendations
        if analysis['readability_score'] < 60:
            recommendations.append("Simplify language and shorten sentences")
        
        # Structure recommendations
        if analysis['content_structure']['paragraph_count'] < 3:
            recommendations.append("Break content into more paragraphs")
        
        # Engagement recommendations
        if analysis['engagement_indicators']['engagement_score'] < 0.3:
            recommendations.append("Add more engaging and emotional language")
        
        return recommendations
    
    def _store_optimization_history(self, optimization_result: Dict[str, Any]) -> None:
        """Store optimization history"""
        self.optimization_history.append({
            'timestamp': datetime.now().isoformat(),
            'improvement_score': optimization_result['improvement_score'],
            'optimizations_applied': optimization_result['optimizations_applied']
        })

# Example usage
content_optimizer = ContentOptimizer()

# Optimize sample content
sample_content = """
Python programming is a versatile language. It is used for web development and data science.
Machine learning uses Python too. Python is popular among developers.
"""

optimization_result = content_optimizer.optimize_content(
    sample_content, 
    target_keyword="python programming",
    optimization_goals=['seo', 'readability', 'engagement']
) 