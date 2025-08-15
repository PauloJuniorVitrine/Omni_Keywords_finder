# Smart Keyword Suggestions
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class KeywordSuggestions:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.keyword_database = []
        self.keyword_vectors = None
        
    def add_keywords(self, keywords: List[str], category: str = None) -> None:
        """Add keywords to the database"""
        for keyword in keywords:
            self.keyword_database.append({
                'keyword': keyword,
                'category': category,
                'frequency': 1,
                'difficulty': self._calculate_difficulty(keyword)
            })
    
    def _calculate_difficulty(self, keyword: str) -> float:
        """Calculate keyword difficulty score"""
        # Simple difficulty calculation based on word length and competition
        base_difficulty = len(keyword.split()) * 0.3
        competition_factor = np.random.uniform(0.1, 0.9)  # Simulated competition
        return min(1.0, base_difficulty + competition_factor)
    
    def get_suggestions(self, seed_keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get keyword suggestions based on seed keyword"""
        suggestions = []
        
        # Find similar keywords
        similar_keywords = self._find_similar_keywords(seed_keyword)
        
        # Filter and rank suggestions
        for keyword_data in similar_keywords:
            if keyword_data['keyword'] != seed_keyword:
                suggestions.append({
                    'keyword': keyword_data['keyword'],
                    'relevance_score': keyword_data.get('similarity', 0.0),
                    'difficulty': keyword_data['difficulty'],
                    'search_volume': self._estimate_search_volume(keyword_data['keyword']),
                    'category': keyword_data['category']
                })
        
        # Sort by relevance and return top suggestions
        suggestions.sort(key=lambda x: x['relevance_score'], reverse=True)
        return suggestions[:limit]
    
    def _find_similar_keywords(self, seed_keyword: str) -> List[Dict[str, Any]]:
        """Find keywords similar to the seed keyword"""
        # Simple similarity calculation
        similar_keywords = []
        
        for keyword_data in self.keyword_database:
            similarity = self._calculate_similarity(seed_keyword, keyword_data['keyword'])
            if similarity > 0.3:  # Threshold for similarity
                keyword_data['similarity'] = similarity
                similar_keywords.append(keyword_data)
        
        return similar_keywords
    
    def _calculate_similarity(self, keyword1: str, keyword2: str) -> float:
        """Calculate similarity between two keywords"""
        # Simple word overlap similarity
        words1 = set(keyword1.lower().split())
        words2 = set(keyword2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume for a keyword"""
        # Simulated search volume estimation
        base_volume = len(keyword) * 100
        random_factor = np.random.uniform(0.5, 2.0)
        return int(base_volume * random_factor)
    
    def get_long_tail_suggestions(self, main_keyword: str, limit: int = 5) -> List[str]:
        """Get long-tail keyword suggestions"""
        long_tail_keywords = []
        
        # Generate long-tail variations
        variations = [
            f"best {main_keyword}",
            f"how to {main_keyword}",
            f"{main_keyword} guide",
            f"{main_keyword} tips",
            f"{main_keyword} examples"
        ]
        
        return variations[:limit]
    
    def get_related_keywords(self, keyword: str, limit: int = 5) -> List[str]:
        """Get related keywords"""
        related_keywords = []
        
        # Find keywords in the same category
        for keyword_data in self.keyword_database:
            if keyword_data['category'] and keyword_data['keyword'] != keyword:
                related_keywords.append(keyword_data['keyword'])
        
        return related_keywords[:limit]

# Example usage
keyword_suggestions = KeywordSuggestions()

# Add sample keywords
sample_keywords = [
    "python programming", "machine learning", "data science",
    "web development", "javascript", "react", "node.js",
    "artificial intelligence", "deep learning", "neural networks"
]

keyword_suggestions.add_keywords(sample_keywords, "programming") 