# Content Optimization using NLP
from typing import Dict, Any, List, Optional
import numpy as np
from collections import Counter

class ContentOptimizer:
    def __init__(self):
        self.readability_metrics = {}
        self.seo_guidelines = {}
        self.content_patterns = {}
        
    def optimize_content(self, content: str, target_keyword: str) -> Dict[str, Any]:
        """Optimize content for SEO and readability"""
        analysis = self.analyze_content(content, target_keyword)
        recommendations = self.generate_recommendations(analysis)
        optimized_content = self.apply_optimizations(content, recommendations)
        
        return {
            'original_content': content,
            'optimized_content': optimized_content,
            'analysis': analysis,
            'recommendations': recommendations,
            'improvement_score': self.calculate_improvement_score(analysis)
        }
    
    def analyze_content(self, content: str, target_keyword: str) -> Dict[str, Any]:
        """Analyze content for optimization opportunities"""
        return {
            'readability': self.analyze_readability(content),
            'seo_analysis': self.analyze_seo_elements(content, target_keyword),
            'content_structure': self.analyze_content_structure(content),
            'keyword_usage': self.analyze_keyword_usage(content, target_keyword),
            'content_quality': self.analyze_content_quality(content)
        }
    
    def analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability"""
        sentences = content.split('.')
        words = content.split()
        
        # Calculate readability metrics
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        avg_word_length = np.mean([len(word) for word in words]) if words else 0
        
        # Flesch Reading Ease (simplified)
        syllables = self.count_syllables(content)
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (syllables / len(words))) if words else 0
        
        # Determine readability level
        if flesch_score >= 90:
            readability_level = 'very_easy'
        elif flesch_score >= 80:
            readability_level = 'easy'
        elif flesch_score >= 70:
            readability_level = 'fairly_easy'
        elif flesch_score >= 60:
            readability_level = 'standard'
        elif flesch_score >= 50:
            readability_level = 'fairly_difficult'
        elif flesch_score >= 30:
            readability_level = 'difficult'
        else:
            readability_level = 'very_difficult'
        
        return {
            'flesch_score': flesch_score,
            'readability_level': readability_level,
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'syllable_count': syllables,
            'word_count': len(words),
            'sentence_count': len(sentences)
        }
    
    def count_syllables(self, text: str) -> int:
        """Count syllables in text (simplified)"""
        # Simplified syllable counting
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
            
            # Ensure at least one syllable per word
            if word_count == 0:
                word_count = 1
            
            count += word_count
        
        return count
    
    def analyze_seo_elements(self, content: str, target_keyword: str) -> Dict[str, Any]:
        """Analyze SEO elements in content"""
        # Check keyword density
        keyword_density = self.calculate_keyword_density(content, target_keyword)
        
        # Check keyword placement
        keyword_placement = self.analyze_keyword_placement(content, target_keyword)
        
        # Check content length
        content_length = len(content)
        
        # Check heading structure
        heading_analysis = self.analyze_headings(content)
        
        return {
            'keyword_density': keyword_density,
            'keyword_placement': keyword_placement,
            'content_length': content_length,
            'heading_structure': heading_analysis,
            'seo_score': self.calculate_seo_score(keyword_density, keyword_placement, content_length)
        }
    
    def calculate_keyword_density(self, content: str, keyword: str) -> float:
        """Calculate keyword density"""
        words = content.lower().split()
        keyword_count = content.lower().count(keyword.lower())
        
        return keyword_count / len(words) if words else 0
    
    def analyze_keyword_placement(self, content: str, keyword: str) -> Dict[str, Any]:
        """Analyze keyword placement in content"""
        content_lower = content.lower()
        keyword_lower = keyword.lower()
        
        # Find keyword positions
        positions = []
        start = 0
        while True:
            pos = content_lower.find(keyword_lower, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        # Analyze placement
        placement_score = 0
        placement_issues = []
        
        if not positions:
            placement_issues.append("Keyword not found in content")
        else:
            # Check first paragraph
            first_third = len(content) // 3
            if positions[0] > first_third:
                placement_issues.append("Keyword not in first paragraph")
            else:
                placement_score += 0.3
            
            # Check title/heading
            if keyword_lower in content_lower[:100]:  # First 100 characters
                placement_score += 0.2
            
            # Check distribution
            if len(positions) > 1:
                placement_score += 0.2
            
            # Check natural usage
            if len(positions) <= 3:  # Not over-optimized
                placement_score += 0.3
        
        return {
            'positions': positions,
            'placement_score': placement_score,
            'issues': placement_issues
        }
    
    def analyze_headings(self, content: str) -> Dict[str, Any]:
        """Analyze heading structure"""
        lines = content.split('\n')
        headings = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                headings.append({'level': level, 'text': text})
        
        # Analyze heading structure
        structure_score = 0
        issues = []
        
        if not headings:
            issues.append("No headings found")
        else:
            # Check for H1
            h1_count = sum(1 for h in headings if h['level'] == 1)
            if h1_count == 0:
                issues.append("No H1 heading found")
            elif h1_count > 1:
                issues.append("Multiple H1 headings found")
            else:
                structure_score += 0.3
            
            # Check heading hierarchy
            for i in range(len(headings) - 1):
                if headings[i+1]['level'] - headings[i]['level'] > 1:
                    issues.append("Skipped heading level")
            
            # Check heading distribution
            if len(headings) >= 3:
                structure_score += 0.3
            
            # Check heading length
            for heading in headings:
                if len(heading['text']) > 60:
                    issues.append("Heading too long")
                elif len(heading['text']) < 3:
                    issues.append("Heading too short")
        
        return {
            'headings': headings,
            'structure_score': structure_score,
            'issues': issues
        }
    
    def calculate_seo_score(self, keyword_density: float, keyword_placement: Dict[str, Any], content_length: int) -> float:
        """Calculate overall SEO score"""
        score = 0.0
        
        # Keyword density score (optimal: 1-2%)
        if 0.01 <= keyword_density <= 0.02:
            score += 0.3
        elif 0.005 <= keyword_density <= 0.03:
            score += 0.2
        else:
            score += 0.1
        
        # Keyword placement score
        score += keyword_placement.get('placement_score', 0)
        
        # Content length score
        if content_length >= 300:
            score += 0.2
        if content_length >= 1000:
            score += 0.2
        
        return min(1.0, score)
    
    def analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        paragraphs = content.split('\n\n')
        sentences = content.split('.')
        
        # Calculate structure metrics
        avg_paragraph_length = len(sentences) / len(paragraphs) if paragraphs else 0
        
        # Check for lists
        list_items = content.count('\n-') + content.count('\n*') + content.count('\n1.')
        
        # Check for images (placeholder)
        image_count = content.count('[image]') + content.count('<img')
        
        return {
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': avg_paragraph_length,
            'list_items': list_items,
            'image_count': image_count,
            'structure_score': self.calculate_structure_score(paragraphs, list_items, image_count)
        }
    
    def calculate_structure_score(self, paragraphs: List[str], list_items: int, image_count: int) -> float:
        """Calculate content structure score"""
        score = 0.0
        
        # Paragraph count score
        if 3 <= len(paragraphs) <= 10:
            score += 0.3
        elif len(paragraphs) > 10:
            score += 0.2
        
        # List items score
        if list_items >= 3:
            score += 0.2
        
        # Image score
        if image_count >= 1:
            score += 0.2
        
        return min(1.0, score)
    
    def analyze_keyword_usage(self, content: str, target_keyword: str) -> Dict[str, Any]:
        """Analyze keyword usage patterns"""
        content_lower = content.lower()
        keyword_lower = target_keyword.lower()
        
        # Find all keyword variations
        keyword_variations = self.find_keyword_variations(keyword_lower)
        
        usage_analysis = {}
        for variation in keyword_variations:
            count = content_lower.count(variation)
            usage_analysis[variation] = count
        
        # Calculate usage score
        total_usage = sum(usage_analysis.values())
        usage_score = min(1.0, total_usage / 10)  # Normalize to 10 occurrences
        
        return {
            'keyword_variations': keyword_variations,
            'usage_counts': usage_analysis,
            'total_usage': total_usage,
            'usage_score': usage_score
        }
    
    def find_keyword_variations(self, keyword: str) -> List[str]:
        """Find keyword variations"""
        variations = [keyword]
        
        # Add singular/plural variations
        if keyword.endswith('s'):
            variations.append(keyword[:-1])
        else:
            variations.append(keyword + 's')
        
        # Add common variations
        words = keyword.split()
        if len(words) > 1:
            # Add partial matches
            variations.extend(words)
        
        return list(set(variations))
    
    def analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """Analyze content quality"""
        # Check for common issues
        issues = []
        quality_score = 1.0
        
        # Check for duplicate content
        sentences = content.split('.')
        unique_sentences = set(sentences)
        if len(sentences) > len(unique_sentences):
            issues.append("Duplicate sentences detected")
            quality_score -= 0.2
        
        # Check for grammar issues (simplified)
        if content.count('  ') > 0:
            issues.append("Multiple spaces detected")
            quality_score -= 0.1
        
        # Check for proper punctuation
        if content.count('!') + content.count('?') == 0:
            issues.append("Limited punctuation variety")
            quality_score -= 0.1
        
        return {
            'quality_score': max(0.0, quality_score),
            'issues': issues,
            'unique_sentences_ratio': len(unique_sentences) / len(sentences) if sentences else 1.0
        }
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Readability recommendations
        readability = analysis['readability']
        if readability['flesch_score'] < 60:
            recommendations.append({
                'type': 'readability',
                'priority': 'high',
                'action': 'Simplify sentence structure and use shorter words',
                'reason': f"Readability score is {readability['flesch_score']:.1f} (difficult)"
            })
        
        # SEO recommendations
        seo = analysis['seo_analysis']
        if seo['keyword_density'] < 0.01:
            recommendations.append({
                'type': 'seo',
                'priority': 'high',
                'action': 'Increase keyword density naturally',
                'reason': f"Keyword density is {seo['keyword_density']:.3f} (too low)"
            })
        
        # Content structure recommendations
        structure = analysis['content_structure']
        if structure['paragraph_count'] < 3:
            recommendations.append({
                'type': 'structure',
                'priority': 'medium',
                'action': 'Add more paragraphs to improve readability',
                'reason': f"Only {structure['paragraph_count']} paragraphs found"
            })
        
        return recommendations
    
    def apply_optimizations(self, content: str, recommendations: List[Dict[str, Any]]) -> str:
        """Apply optimizations to content"""
        optimized_content = content
        
        for rec in recommendations:
            if rec['type'] == 'readability':
                optimized_content = self._apply_readability_optimizations(optimized_content)
            elif rec['type'] == 'seo':
                optimized_content = self._apply_seo_optimizations(optimized_content)
            elif rec['type'] == 'structure':
                optimized_content = self._apply_structure_optimizations(optimized_content)
        
        return optimized_content
    
    def _apply_readability_optimizations(self, content: str) -> str:
        """Apply readability optimizations"""
        # This would implement actual text simplification
        # For now, return the original content
        return content
    
    def _apply_seo_optimizations(self, content: str) -> str:
        """Apply SEO optimizations"""
        # This would implement actual SEO improvements
        # For now, return the original content
        return content
    
    def _apply_structure_optimizations(self, content: str) -> str:
        """Apply structure optimizations"""
        # This would implement actual structure improvements
        # For now, return the original content
        return content
    
    def calculate_improvement_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate potential improvement score"""
        scores = []
        
        # Readability score
        readability = analysis['readability']
        if readability['flesch_score'] < 70:
            scores.append(0.3)
        
        # SEO score
        seo = analysis['seo_analysis']
        if seo['seo_score'] < 0.7:
            scores.append(0.3)
        
        # Structure score
        structure = analysis['content_structure']
        if structure['structure_score'] < 0.7:
            scores.append(0.2)
        
        # Quality score
        quality = analysis['content_quality']
        if quality['quality_score'] < 0.8:
            scores.append(0.2)
        
        return sum(scores)

# Example usage
content_optimizer = ContentOptimizer()

# Optimize sample content
sample_content = """
Python programming is a versatile language. It is used for web development.
Python is also used for data science. Machine learning uses Python too.
"""

optimization_result = content_optimizer.optimize_content(sample_content, "python programming") 