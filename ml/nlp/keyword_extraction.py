# Keyword Extraction using NLP
from typing import List, Dict, Any, Optional
import re
from collections import Counter
import numpy as np

class KeywordExtractor:
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        self.keyword_patterns = []
        
    def extract_keywords(self, text: str, method: str = 'tfidf', top_k: int = 10) -> List[Dict[str, Any]]:
        """Extract keywords from text using specified method"""
        if method == 'tfidf':
            return self._extract_tfidf_keywords(text, top_k)
        elif method == 'rake':
            return self._extract_rake_keywords(text, top_k)
        elif method == 'yake':
            return self._extract_yake_keywords(text, top_k)
        else:
            return self._extract_basic_keywords(text, top_k)
    
    def _extract_basic_keywords(self, text: str, top_k: int) -> List[Dict[str, Any]]:
        """Extract keywords using basic frequency analysis"""
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Tokenize
        words = cleaned_text.lower().split()
        
        # Remove stop words and short words
        filtered_words = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        
        # Count frequencies
        word_freq = Counter(filtered_words)
        
        # Get top keywords
        top_keywords = word_freq.most_common(top_k)
        
        return [
            {
                'keyword': keyword,
                'frequency': freq,
                'score': freq / len(filtered_words),
                'method': 'frequency'
            }
            for keyword, freq in top_keywords
        ]
    
    def _extract_tfidf_keywords(self, text: str, top_k: int) -> List[Dict[str, Any]]:
        """Extract keywords using TF-IDF approach"""
        # This is a simplified TF-IDF implementation
        # In practice, you'd use scikit-learn's TfidfVectorizer
        
        # Clean and tokenize
        cleaned_text = self._clean_text(text)
        words = cleaned_text.lower().split()
        
        # Remove stop words
        filtered_words = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        
        # Calculate TF-IDF scores (simplified)
        word_freq = Counter(filtered_words)
        total_words = len(filtered_words)
        
        # Simple TF-IDF calculation
        tfidf_scores = {}
        for word, freq in word_freq.items():
            tf = freq / total_words
            # Simplified IDF (in practice, you'd use a corpus)
            idf = np.log(1000 / (freq + 1))  # Assuming 1000 documents
            tfidf_scores[word] = tf * idf
        
        # Get top keywords by TF-IDF score
        top_keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return [
            {
                'keyword': keyword,
                'tfidf_score': score,
                'frequency': word_freq[keyword],
                'method': 'tfidf'
            }
            for keyword, score in top_keywords
        ]
    
    def _extract_rake_keywords(self, text: str, top_k: int) -> List[Dict[str, Any]]:
        """Extract keywords using RAKE (Rapid Automatic Keyword Extraction)"""
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Extract candidate phrases
        candidate_phrases = self._extract_candidate_phrases(cleaned_text)
        
        # Calculate RAKE scores
        rake_scores = {}
        for phrase in candidate_phrases:
            score = self._calculate_rake_score(phrase, cleaned_text)
            rake_scores[phrase] = score
        
        # Get top keywords
        top_keywords = sorted(rake_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return [
            {
                'keyword': keyword,
                'rake_score': score,
                'method': 'rake'
            }
            for keyword, score in top_keywords
        ]
    
    def _extract_candidate_phrases(self, text: str) -> List[str]:
        """Extract candidate phrases for RAKE"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        candidate_phrases = []
        for sentence in sentences:
            # Extract noun phrases (simplified)
            words = sentence.split()
            phrases = []
            
            for i in range(len(words)):
                for j in range(i + 1, min(i + 4, len(words) + 1)):
                    phrase = ' '.join(words[i:j])
                    if len(phrase.split()) >= 1 and len(phrase.split()) <= 3:
                        phrases.append(phrase.lower())
            
            candidate_phrases.extend(phrases)
        
        return list(set(candidate_phrases))
    
    def _calculate_rake_score(self, phrase: str, text: str) -> float:
        """Calculate RAKE score for a phrase"""
        # Simplified RAKE score calculation
        words = phrase.split()
        
        # Calculate word scores (degree / frequency)
        word_scores = {}
        for word in words:
            if word not in self.stop_words:
                degree = self._calculate_word_degree(word, text)
                frequency = text.lower().count(word)
                word_scores[word] = degree / frequency if frequency > 0 else 0
        
        # Phrase score is sum of word scores
        return sum(word_scores.values())
    
    def _calculate_word_degree(self, word: str, text: str) -> int:
        """Calculate word degree (number of unique words it co-occurs with)"""
        # Simplified degree calculation
        words = text.lower().split()
        co_occurring_words = set()
        
        for i, w in enumerate(words):
            if w == word:
                # Look at surrounding words
                start = max(0, i - 2)
                end = min(len(words), i + 3)
                for j in range(start, end):
                    if j != i and words[j] not in self.stop_words:
                        co_occurring_words.add(words[j])
        
        return len(co_occurring_words)
    
    def _extract_yake_keywords(self, text: str, top_k: int) -> List[Dict[str, Any]]:
        """Extract keywords using YAKE (Yet Another Keyword Extractor) approach"""
        # Simplified YAKE implementation
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Extract candidate keywords
        candidates = self._extract_candidate_keywords(cleaned_text)
        
        # Calculate YAKE scores
        yake_scores = {}
        for candidate in candidates:
            score = self._calculate_yake_score(candidate, cleaned_text)
            yake_scores[candidate] = score
        
        # Get top keywords (lower score is better in YAKE)
        top_keywords = sorted(yake_scores.items(), key=lambda x: x[1])[:top_k]
        
        return [
            {
                'keyword': keyword,
                'yake_score': score,
                'method': 'yake'
            }
            for keyword, score in top_keywords
        ]
    
    def _extract_candidate_keywords(self, text: str) -> List[str]:
        """Extract candidate keywords for YAKE"""
        # Extract single words and phrases
        words = text.lower().split()
        candidates = []
        
        # Single words
        for word in words:
            if word not in self.stop_words and len(word) > 2:
                candidates.append(word)
        
        # Phrases (up to 3 words)
        for i in range(len(words) - 1):
            for j in range(i + 1, min(i + 3, len(words))):
                phrase = ' '.join(words[i:j + 1])
                if len(phrase.split()) <= 3:
                    candidates.append(phrase)
        
        return list(set(candidates))
    
    def _calculate_yake_score(self, candidate: str, text: str) -> float:
        """Calculate YAKE score for a candidate"""
        # Simplified YAKE score calculation
        words = candidate.split()
        
        # Term frequency
        tf = text.lower().count(candidate)
        
        # Term length
        length = len(words)
        
        # Position score (earlier is better)
        position = text.lower().find(candidate)
        position_score = 1.0 / (1.0 + position / 1000)
        
        # Simplified YAKE score (lower is better)
        score = tf * length * position_score
        
        return score
    
    def _clean_text(self, text: str) -> str:
        """Clean text for keyword extraction"""
        # Remove special characters but keep spaces
        cleaned = re.sub(r'[^\w\s]', ' ', text)
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def extract_keywords_from_url(self, url: str) -> List[str]:
        """Extract keywords from URL"""
        # Extract domain and path
        domain = url.split('/')[2] if len(url.split('/')) > 2 else url
        path = '/'.join(url.split('/')[3:]) if len(url.split('/')) > 3 else ''
        
        keywords = []
        
        # Extract from domain
        domain_words = domain.replace('.', ' ').split()
        keywords.extend([word for word in domain_words if word not in ['www', 'com', 'org', 'net']])
        
        # Extract from path
        path_words = path.replace('-', ' ').replace('_', ' ').split()
        keywords.extend([word for word in path_words if word])
        
        return keywords
    
    def extract_keywords_from_title(self, title: str) -> List[str]:
        """Extract keywords from title"""
        # Clean title
        cleaned_title = self._clean_text(title)
        
        # Extract keywords using basic method
        keywords = self._extract_basic_keywords(cleaned_title, 5)
        
        return [kw['keyword'] for kw in keywords]
    
    def get_keyword_suggestions(self, seed_keyword: str, text: str) -> List[str]:
        """Get keyword suggestions based on seed keyword and context"""
        # Extract all keywords from text
        all_keywords = self.extract_keywords(text, method='tfidf', top_k=20)
        
        # Find related keywords
        related_keywords = []
        seed_words = seed_keyword.lower().split()
        
        for kw_data in all_keywords:
            keyword = kw_data['keyword']
            keyword_words = keyword.split()
            
            # Check for word overlap
            overlap = len(set(seed_words) & set(keyword_words))
            if overlap > 0 and keyword != seed_keyword:
                related_keywords.append(keyword)
        
        return related_keywords[:10]

# Example usage
keyword_extractor = KeywordExtractor()

# Extract keywords from sample text
sample_text = """
Python programming is a versatile language used for web development, 
data science, machine learning, and artificial intelligence. 
It's known for its simplicity and readability.
"""

keywords = keyword_extractor.extract_keywords(sample_text, method='tfidf', top_k=5) 