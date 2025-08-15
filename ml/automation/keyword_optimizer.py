# Automated Keyword Optimizer using Machine Learning
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter

class KeywordOptimizer:
    def __init__(self):
        self.keyword_database = {}
        self.optimization_rules = {}
        self.performance_history = {}
        self.optimization_strategies = {}
        
    def optimize_keywords(self, keywords: List[str], target_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize keyword list based on target metrics"""
        optimization_results = {
            'original_keywords': keywords,
            'optimized_keywords': [],
            'keyword_suggestions': [],
            'optimization_strategies': [],
            'performance_predictions': {},
            'improvement_score': 0.0
        }
        
        # Analyze current keywords
        keyword_analysis = self._analyze_keywords(keywords)
        
        # Generate optimization strategies
        strategies = self._generate_optimization_strategies(keyword_analysis, target_metrics)
        optimization_results['optimization_strategies'] = strategies
        
        # Apply optimizations
        optimized_keywords = self._apply_keyword_optimizations(keywords, strategies)
        optimization_results['optimized_keywords'] = optimized_keywords
        
        # Generate keyword suggestions
        suggestions = self._generate_keyword_suggestions(keywords, target_metrics)
        optimization_results['keyword_suggestions'] = suggestions
        
        # Predict performance improvements
        performance_predictions = self._predict_performance_improvements(
            keywords, optimized_keywords, target_metrics
        )
        optimization_results['performance_predictions'] = performance_predictions
        
        # Calculate improvement score
        optimization_results['improvement_score'] = self._calculate_improvement_score(
            keyword_analysis, performance_predictions
        )
        
        return optimization_results
    
    def _analyze_keywords(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyze keyword list for optimization opportunities"""
        analysis = {
            'keyword_count': len(keywords),
            'keyword_categories': self._categorize_keywords(keywords),
            'keyword_difficulty_distribution': self._analyze_difficulty_distribution(keywords),
            'search_volume_analysis': self._analyze_search_volume(keywords),
            'competition_analysis': self._analyze_competition(keywords),
            'keyword_gaps': self._identify_keyword_gaps(keywords),
            'optimization_opportunities': self._identify_optimization_opportunities(keywords)
        }
        
        return analysis
    
    def _categorize_keywords(self, keywords: List[str]) -> Dict[str, int]:
        """Categorize keywords by type"""
        categories = {
            'informational': 0,
            'transactional': 0,
            'navigational': 0,
            'long_tail': 0
        }
        
        for keyword in keywords:
            if any(word in keyword.lower() for word in ['how', 'what', 'why', 'guide', 'tips', 'tutorial']):
                categories['informational'] += 1
            elif any(word in keyword.lower() for word in ['buy', 'price', 'cost', 'purchase', 'order']):
                categories['transactional'] += 1
            elif any(word in keyword.lower() for word in ['brand', 'company', 'official', 'login']):
                categories['navigational'] += 1
            elif len(keyword.split()) > 2:
                categories['long_tail'] += 1
            else:
                categories['informational'] += 1  # Default category
        
        return categories
    
    def _analyze_difficulty_distribution(self, keywords: List[str]) -> Dict[str, int]:
        """Analyze keyword difficulty distribution"""
        difficulties = {
            'easy': 0,
            'medium': 0,
            'hard': 0
        }
        
        for keyword in keywords:
            difficulty = self._calculate_keyword_difficulty(keyword)
            if difficulty < 0.4:
                difficulties['easy'] += 1
            elif difficulty < 0.7:
                difficulties['medium'] += 1
            else:
                difficulties['hard'] += 1
        
        return difficulties
    
    def _calculate_keyword_difficulty(self, keyword: str) -> float:
        """Calculate keyword difficulty score"""
        # Simplified difficulty calculation
        word_count = len(keyword.split())
        base_difficulty = word_count * 0.1
        
        # Add competition factor
        competition_words = ['best', 'top', 'cheap', 'free', 'review']
        competition_factor = sum(1 for word in competition_words if word in keyword.lower()) * 0.2
        
        # Add length factor
        length_factor = min(0.3, len(keyword) * 0.01)
        
        total_difficulty = base_difficulty + competition_factor + length_factor
        return min(1.0, total_difficulty)
    
    def _analyze_search_volume(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyze search volume patterns"""
        volumes = [self._estimate_search_volume(keyword) for keyword in keywords]
        
        return {
            'total_volume': sum(volumes),
            'average_volume': np.mean(volumes),
            'high_volume_keywords': [kw for kw, vol in zip(keywords, volumes) if vol > 10000],
            'low_volume_keywords': [kw for kw, vol in zip(keywords, volumes) if vol < 1000],
            'volume_distribution': {
                'high': len([v for v in volumes if v > 10000]),
                'medium': len([v for v in volumes if 1000 <= v <= 10000]),
                'low': len([v for v in volumes if v < 1000])
            }
        }
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume for a keyword"""
        # Simplified search volume estimation
        base_volume = len(keyword) * 200
        
        # Adjust for keyword type
        if any(word in keyword.lower() for word in ['how', 'what', 'why']):
            base_volume *= 1.5  # Informational keywords get more searches
        
        if len(keyword.split()) > 2:
            base_volume *= 0.7  # Long-tail keywords get fewer searches
        
        # Add some randomness
        random_factor = np.random.uniform(0.5, 2.0)
        return int(base_volume * random_factor)
    
    def _analyze_competition(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyze competition levels"""
        competition_scores = [self._calculate_competition_score(keyword) for keyword in keywords]
        
        return {
            'average_competition': np.mean(competition_scores),
            'high_competition_keywords': [kw for kw, score in zip(keywords, competition_scores) if score > 0.7],
            'low_competition_keywords': [kw for kw, score in zip(keywords, competition_scores) if score < 0.3],
            'competition_distribution': {
                'high': len([s for s in competition_scores if s > 0.7]),
                'medium': len([s for s in competition_scores if 0.3 <= s <= 0.7]),
                'low': len([s for s in competition_scores if s < 0.3])
            }
        }
    
    def _calculate_competition_score(self, keyword: str) -> float:
        """Calculate competition score for a keyword"""
        # Simplified competition calculation
        competition_score = 0.0
        
        # Generic terms are more competitive
        generic_terms = ['best', 'top', 'cheap', 'free', 'online', 'buy']
        for term in generic_terms:
            if term in keyword.lower():
                competition_score += 0.2
        
        # Shorter keywords are more competitive
        word_count = len(keyword.split())
        if word_count == 1:
            competition_score += 0.4
        elif word_count == 2:
            competition_score += 0.2
        
        # Brand terms are less competitive
        if any(word in keyword.lower() for word in ['brand', 'company', 'official']):
            competition_score -= 0.3
        
        return max(0.0, min(1.0, competition_score))
    
    def _identify_keyword_gaps(self, keywords: List[str]) -> List[str]:
        """Identify gaps in keyword coverage"""
        gaps = []
        
        # Check for missing keyword types
        categories = self._categorize_keywords(keywords)
        
        if categories['informational'] < 2:
            gaps.append("Need more informational keywords")
        
        if categories['transactional'] < 1:
            gaps.append("Need transactional keywords")
        
        if categories['long_tail'] < 3:
            gaps.append("Need more long-tail keywords")
        
        # Check for missing question keywords
        question_keywords = [kw for kw in keywords if any(word in kw.lower() for word in ['how', 'what', 'why'])]
        if len(question_keywords) < 2:
            gaps.append("Need more question-based keywords")
        
        return gaps
    
    def _identify_optimization_opportunities(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities"""
        opportunities = []
        
        for keyword in keywords:
            difficulty = self._calculate_keyword_difficulty(keyword)
            volume = self._estimate_search_volume(keyword)
            competition = self._calculate_competition_score(keyword)
            
            # High difficulty, low volume keywords
            if difficulty > 0.7 and volume < 5000:
                opportunities.append({
                    'keyword': keyword,
                    'type': 'replace',
                    'reason': 'High difficulty, low volume',
                    'suggestion': 'Consider replacing with easier, higher-volume alternatives'
                })
            
            # Low competition, high volume opportunities
            if competition < 0.3 and volume > 5000:
                opportunities.append({
                    'keyword': keyword,
                    'type': 'expand',
                    'reason': 'Low competition, high volume',
                    'suggestion': 'Expand with related keywords'
                })
        
        return opportunities
    
    def _generate_optimization_strategies(self, analysis: Dict[str, Any], 
                                        target_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization strategies"""
        strategies = []
        
        # Volume optimization strategy
        if target_metrics.get('min_volume', 0) > 0:
            low_volume_count = analysis['search_volume_analysis']['volume_distribution']['low']
            if low_volume_count > len(analysis['original_keywords']) * 0.3:
                strategies.append({
                    'type': 'volume_optimization',
                    'description': 'Replace low-volume keywords with higher-volume alternatives',
                    'priority': 'high',
                    'expected_impact': 'medium'
                })
        
        # Difficulty optimization strategy
        if target_metrics.get('max_difficulty', 1.0) < 0.8:
            high_difficulty_count = analysis['keyword_difficulty_distribution']['hard']
            if high_difficulty_count > len(analysis['original_keywords']) * 0.4:
                strategies.append({
                    'type': 'difficulty_optimization',
                    'description': 'Replace high-difficulty keywords with easier alternatives',
                    'priority': 'medium',
                    'expected_impact': 'high'
                })
        
        # Competition optimization strategy
        if target_metrics.get('max_competition', 1.0) < 0.7:
            high_competition_count = analysis['competition_analysis']['competition_distribution']['high']
            if high_competition_count > len(analysis['original_keywords']) * 0.3:
                strategies.append({
                    'type': 'competition_optimization',
                    'description': 'Focus on low-competition keywords',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Long-tail optimization strategy
        if analysis['keyword_categories']['long_tail'] < 3:
            strategies.append({
                'type': 'long_tail_expansion',
                'description': 'Add more long-tail keywords for better targeting',
                'priority': 'low',
                'expected_impact': 'medium'
            })
        
        return strategies
    
    def _apply_keyword_optimizations(self, keywords: List[str], 
                                   strategies: List[Dict[str, Any]]) -> List[str]:
        """Apply keyword optimizations based on strategies"""
        optimized_keywords = keywords.copy()
        
        for strategy in strategies:
            if strategy['type'] == 'volume_optimization':
                optimized_keywords = self._apply_volume_optimization(optimized_keywords)
            elif strategy['type'] == 'difficulty_optimization':
                optimized_keywords = self._apply_difficulty_optimization(optimized_keywords)
            elif strategy['type'] == 'competition_optimization':
                optimized_keywords = self._apply_competition_optimization(optimized_keywords)
            elif strategy['type'] == 'long_tail_expansion':
                optimized_keywords = self._apply_long_tail_expansion(optimized_keywords)
        
        return optimized_keywords
    
    def _apply_volume_optimization(self, keywords: List[str]) -> List[str]:
        """Apply volume optimization"""
        optimized = []
        
        for keyword in keywords:
            volume = self._estimate_search_volume(keyword)
            
            if volume < 1000:
                # Replace with higher-volume alternative
                alternative = self._generate_volume_alternative(keyword)
                if alternative:
                    optimized.append(alternative)
                else:
                    optimized.append(keyword)
            else:
                optimized.append(keyword)
        
        return optimized
    
    def _generate_volume_alternative(self, keyword: str) -> Optional[str]:
        """Generate higher-volume alternative for a keyword"""
        # Simplified alternative generation
        alternatives = {
            'python tutorial': 'python programming tutorial',
            'web development': 'web development guide',
            'machine learning': 'machine learning tutorial',
            'data science': 'data science course'
        }
        
        return alternatives.get(keyword.lower(), None)
    
    def _apply_difficulty_optimization(self, keywords: List[str]) -> List[str]:
        """Apply difficulty optimization"""
        optimized = []
        
        for keyword in keywords:
            difficulty = self._calculate_keyword_difficulty(keyword)
            
            if difficulty > 0.7:
                # Replace with easier alternative
                alternative = self._generate_easier_alternative(keyword)
                if alternative:
                    optimized.append(alternative)
                else:
                    optimized.append(keyword)
            else:
                optimized.append(keyword)
        
        return optimized
    
    def _generate_easier_alternative(self, keyword: str) -> Optional[str]:
        """Generate easier alternative for a keyword"""
        # Simplified alternative generation
        alternatives = {
            'best python tutorial': 'python tutorial',
            'cheap web hosting': 'web hosting',
            'free machine learning course': 'machine learning course'
        }
        
        return alternatives.get(keyword.lower(), None)
    
    def _apply_competition_optimization(self, keywords: List[str]) -> List[str]:
        """Apply competition optimization"""
        optimized = []
        
        for keyword in keywords:
            competition = self._calculate_competition_score(keyword)
            
            if competition > 0.7:
                # Replace with less competitive alternative
                alternative = self._generate_less_competitive_alternative(keyword)
                if alternative:
                    optimized.append(alternative)
                else:
                    optimized.append(keyword)
            else:
                optimized.append(keyword)
        
        return optimized
    
    def _generate_less_competitive_alternative(self, keyword: str) -> Optional[str]:
        """Generate less competitive alternative for a keyword"""
        # Simplified alternative generation
        alternatives = {
            'best python': 'python programming guide',
            'cheap hosting': 'affordable hosting',
            'free course': 'online course'
        }
        
        return alternatives.get(keyword.lower(), None)
    
    def _apply_long_tail_expansion(self, keywords: List[str]) -> List[str]:
        """Apply long-tail expansion"""
        expanded = keywords.copy()
        
        # Add long-tail variations
        long_tail_variations = [
            'how to learn python programming',
            'best python programming tutorial for beginners',
            'python programming course online',
            'machine learning with python tutorial',
            'data science python programming guide'
        ]
        
        # Add variations that aren't already in the list
        for variation in long_tail_variations:
            if variation not in expanded and len(expanded) < 15:  # Limit total keywords
                expanded.append(variation)
        
        return expanded
    
    def _generate_keyword_suggestions(self, keywords: List[str], 
                                    target_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate keyword suggestions"""
        suggestions = []
        
        # Generate related keywords
        for keyword in keywords:
            related_keywords = self._generate_related_keywords(keyword)
            for related in related_keywords:
                if related not in keywords:
                    suggestions.append({
                        'keyword': related,
                        'type': 'related',
                        'source_keyword': keyword,
                        'estimated_volume': self._estimate_search_volume(related),
                        'difficulty': self._calculate_keyword_difficulty(related),
                        'competition': self._calculate_competition_score(related)
                    })
        
        # Generate question-based keywords
        question_keywords = self._generate_question_keywords(keywords)
        for question in question_keywords:
            suggestions.append({
                'keyword': question,
                'type': 'question',
                'estimated_volume': self._estimate_search_volume(question),
                'difficulty': self._calculate_keyword_difficulty(question),
                'competition': self._calculate_competition_score(question)
            })
        
        # Filter suggestions based on target metrics
        filtered_suggestions = self._filter_suggestions(suggestions, target_metrics)
        
        return filtered_suggestions[:10]  # Return top 10 suggestions
    
    def _generate_related_keywords(self, keyword: str) -> List[str]:
        """Generate related keywords"""
        # Simplified related keyword generation
        related_keywords = {
            'python programming': [
                'python tutorial', 'python course', 'learn python',
                'python for beginners', 'python development'
            ],
            'machine learning': [
                'ml tutorial', 'machine learning course', 'ai tutorial',
                'deep learning', 'artificial intelligence'
            ],
            'web development': [
                'web design', 'frontend development', 'backend development',
                'full stack development', 'web programming'
            ]
        }
        
        return related_keywords.get(keyword.lower(), [])
    
    def _generate_question_keywords(self, keywords: List[str]) -> List[str]:
        """Generate question-based keywords"""
        question_keywords = []
        
        question_starters = ['how to', 'what is', 'why use', 'when to', 'where to']
        
        for keyword in keywords:
            for starter in question_starters:
                question = f"{starter} {keyword}"
                question_keywords.append(question)
        
        return question_keywords[:5]  # Limit to 5 questions
    
    def _filter_suggestions(self, suggestions: List[Dict[str, Any]], 
                          target_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter suggestions based on target metrics"""
        filtered = []
        
        for suggestion in suggestions:
            # Check volume requirements
            min_volume = target_metrics.get('min_volume', 0)
            if suggestion['estimated_volume'] < min_volume:
                continue
            
            # Check difficulty requirements
            max_difficulty = target_metrics.get('max_difficulty', 1.0)
            if suggestion['difficulty'] > max_difficulty:
                continue
            
            # Check competition requirements
            max_competition = target_metrics.get('max_competition', 1.0)
            if suggestion['competition'] > max_competition:
                continue
            
            filtered.append(suggestion)
        
        # Sort by estimated volume
        filtered.sort(key=lambda x: x['estimated_volume'], reverse=True)
        
        return filtered
    
    def _predict_performance_improvements(self, original_keywords: List[str],
                                        optimized_keywords: List[str],
                                        target_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Predict performance improvements"""
        # Analyze original performance
        original_analysis = self._analyze_keywords(original_keywords)
        optimized_analysis = self._analyze_keywords(optimized_keywords)
        
        # Calculate improvements
        volume_improvement = (
            optimized_analysis['search_volume_analysis']['total_volume'] -
            original_analysis['search_volume_analysis']['total_volume']
        ) / original_analysis['search_volume_analysis']['total_volume'] if original_analysis['search_volume_analysis']['total_volume'] > 0 else 0
        
        difficulty_improvement = (
            original_analysis['keyword_difficulty_distribution']['hard'] -
            optimized_analysis['keyword_difficulty_distribution']['hard']
        ) / len(original_keywords) if len(original_keywords) > 0 else 0
        
        competition_improvement = (
            original_analysis['competition_analysis']['competition_distribution']['high'] -
            optimized_analysis['competition_analysis']['competition_distribution']['high']
        ) / len(original_keywords) if len(original_keywords) > 0 else 0
        
        return {
            'volume_improvement': volume_improvement,
            'difficulty_improvement': difficulty_improvement,
            'competition_improvement': competition_improvement,
            'overall_improvement': (volume_improvement + difficulty_improvement + competition_improvement) / 3
        }
    
    def _calculate_improvement_score(self, analysis: Dict[str, Any],
                                   performance_predictions: Dict[str, Any]) -> float:
        """Calculate overall improvement score"""
        score = 0.0
        
        # Volume improvement
        if performance_predictions['volume_improvement'] > 0:
            score += 0.3
        
        # Difficulty improvement
        if performance_predictions['difficulty_improvement'] > 0:
            score += 0.3
        
        # Competition improvement
        if performance_predictions['competition_improvement'] > 0:
            score += 0.2
        
        # Overall improvement
        if performance_predictions['overall_improvement'] > 0.1:
            score += 0.2
        
        return min(1.0, score)

# Example usage
keyword_optimizer = KeywordOptimizer()

# Optimize sample keywords
sample_keywords = [
    "python programming",
    "machine learning",
    "web development",
    "data science"
]

target_metrics = {
    'min_volume': 1000,
    'max_difficulty': 0.7,
    'max_competition': 0.6
}

optimization_result = keyword_optimizer.optimize_keywords(sample_keywords, target_metrics) 