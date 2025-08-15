# Sentiment Analysis using NLP
from typing import Dict, Any, List, Optional
import numpy as np
from collections import defaultdict

class SentimentAnalyzer:
    def __init__(self):
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'awesome', 'brilliant', 'outstanding', 'perfect', 'best', 'love',
            'like', 'enjoy', 'happy', 'satisfied', 'pleased', 'impressed'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike',
            'disappointed', 'frustrated', 'angry', 'upset', 'sad', 'poor',
            'useless', 'broken', 'failed', 'problem', 'issue', 'error'
        }
        
        self.neutral_words = {
            'okay', 'fine', 'normal', 'average', 'standard', 'regular',
            'usual', 'typical', 'common', 'ordinary'
        }
        
        self.intensifiers = {
            'very': 2.0, 'really': 2.0, 'extremely': 3.0, 'absolutely': 3.0,
            'completely': 2.5, 'totally': 2.5, 'slightly': 0.5, 'somewhat': 0.7
        }
        
        self.negators = {
            'not', 'no', 'never', 'none', 'neither', 'nor', 'hardly', 'barely'
        }
    
    def analyze_sentiment(self, text: str, method: str = 'lexicon') -> Dict[str, Any]:
        """Analyze sentiment of text using specified method"""
        if method == 'lexicon':
            return self._lexicon_based_analysis(text)
        elif method == 'rule_based':
            return self._rule_based_analysis(text)
        elif method == 'hybrid':
            return self._hybrid_analysis(text)
        else:
            return self._basic_analysis(text)
    
    def _basic_analysis(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis"""
        words = text.lower().split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        neutral_count = sum(1 for word in words if word in self.neutral_words)
        
        total_words = len(words)
        
        if total_words == 0:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0,
                'neutral_ratio': 0.0
            }
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        neutral_ratio = neutral_count / total_words
        
        # Calculate sentiment score
        score = positive_ratio - negative_ratio
        
        # Determine sentiment
        if score > 0.05:
            sentiment = 'positive'
        elif score < -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Calculate confidence
        confidence = abs(score)
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence,
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio,
            'neutral_ratio': neutral_ratio
        }
    
    def _lexicon_based_analysis(self, text: str) -> Dict[str, Any]:
        """Lexicon-based sentiment analysis"""
        words = text.lower().split()
        
        sentiment_score = 0.0
        word_scores = {}
        
        for i, word in enumerate(words):
            word_score = 0.0
            
            # Check for positive words
            if word in self.positive_words:
                word_score = 1.0
            # Check for negative words
            elif word in self.negative_words:
                word_score = -1.0
            # Check for neutral words
            elif word in self.neutral_words:
                word_score = 0.0
            
            # Apply intensifiers
            if i > 0 and words[i-1] in self.intensifiers:
                intensifier = self.intensifiers[words[i-1]]
                word_score *= intensifier
            
            # Apply negators
            if i > 0 and words[i-1] in self.negators:
                word_score *= -1
            
            word_scores[word] = word_score
            sentiment_score += word_score
        
        # Normalize score
        if len(words) > 0:
            normalized_score = sentiment_score / len(words)
        else:
            normalized_score = 0.0
        
        # Determine sentiment
        if normalized_score > 0.1:
            sentiment = 'positive'
        elif normalized_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': normalized_score,
            'confidence': abs(normalized_score),
            'word_scores': word_scores,
            'total_score': sentiment_score
        }
    
    def _rule_based_analysis(self, text: str) -> Dict[str, Any]:
        """Rule-based sentiment analysis"""
        # Split into sentences
        sentences = text.split('.')
        
        sentence_sentiments = []
        overall_score = 0.0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Analyze each sentence
            sentence_analysis = self._analyze_sentence(sentence)
            sentence_sentiments.append(sentence_analysis)
            overall_score += sentence_analysis['score']
        
        # Calculate overall sentiment
        if len(sentence_sentiments) > 0:
            avg_score = overall_score / len(sentence_sentiments)
        else:
            avg_score = 0.0
        
        if avg_score > 0.1:
            sentiment = 'positive'
        elif avg_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': avg_score,
            'confidence': abs(avg_score),
            'sentence_sentiments': sentence_sentiments,
            'sentence_count': len(sentence_sentiments)
        }
    
    def _analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        """Analyze sentiment of a single sentence"""
        words = sentence.lower().split()
        
        # Count sentiment words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Check for negation patterns
        negation_impact = self._check_negation_patterns(words)
        
        # Calculate score
        base_score = positive_count - negative_count
        final_score = base_score * negation_impact
        
        # Normalize
        if len(words) > 0:
            normalized_score = final_score / len(words)
        else:
            normalized_score = 0.0
        
        return {
            'sentence': sentence,
            'score': normalized_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'negation_impact': negation_impact
        }
    
    def _check_negation_patterns(self, words: List[str]) -> float:
        """Check for negation patterns in words"""
        negation_impact = 1.0
        
        for i, word in enumerate(words):
            if word in self.negators:
                # Look ahead for sentiment words
                for j in range(i + 1, min(i + 3, len(words))):
                    if words[j] in self.positive_words or words[j] in self.negative_words:
                        negation_impact *= -1
                        break
        
        return negation_impact
    
    def _hybrid_analysis(self, text: str) -> Dict[str, Any]:
        """Hybrid sentiment analysis combining multiple approaches"""
        # Get results from different methods
        lexicon_result = self._lexicon_based_analysis(text)
        rule_result = self._rule_based_analysis(text)
        basic_result = self._basic_analysis(text)
        
        # Combine scores (weighted average)
        lexicon_weight = 0.4
        rule_weight = 0.4
        basic_weight = 0.2
        
        combined_score = (
            lexicon_result['score'] * lexicon_weight +
            rule_result['score'] * rule_weight +
            basic_result['score'] * basic_weight
        )
        
        # Determine sentiment
        if combined_score > 0.1:
            sentiment = 'positive'
        elif combined_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': combined_score,
            'confidence': abs(combined_score),
            'lexicon_score': lexicon_result['score'],
            'rule_score': rule_result['score'],
            'basic_score': basic_result['score'],
            'method_agreement': self._calculate_method_agreement([
                lexicon_result['sentiment'],
                rule_result['sentiment'],
                basic_result['sentiment']
            ])
        }
    
    def _calculate_method_agreement(self, sentiments: List[str]) -> float:
        """Calculate agreement between different analysis methods"""
        if not sentiments:
            return 0.0
        
        # Count each sentiment
        sentiment_counts = defaultdict(int)
        for sentiment in sentiments:
            sentiment_counts[sentiment] += 1
        
        # Calculate agreement ratio
        max_count = max(sentiment_counts.values())
        agreement = max_count / len(sentiments)
        
        return agreement
    
    def analyze_sentiment_trends(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze sentiment trends across multiple texts"""
        if not texts:
            return {}
        
        sentiments = []
        scores = []
        
        for text in texts:
            analysis = self.analyze_sentiment(text, method='hybrid')
            sentiments.append(analysis['sentiment'])
            scores.append(analysis['score'])
        
        # Calculate trends
        sentiment_counts = defaultdict(int)
        for sentiment in sentiments:
            sentiment_counts[sentiment] += 1
        
        # Calculate average score
        avg_score = np.mean(scores) if scores else 0.0
        
        # Calculate trend direction
        if len(scores) >= 2:
            trend = 'increasing' if scores[-1] > scores[0] else 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'total_texts': len(texts),
            'sentiment_distribution': dict(sentiment_counts),
            'average_score': avg_score,
            'trend': trend,
            'score_volatility': np.std(scores) if len(scores) > 1 else 0.0,
            'dominant_sentiment': max(sentiment_counts, key=sentiment_counts.get) if sentiment_counts else 'neutral'
        }
    
    def extract_sentiment_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract keywords based on sentiment"""
        words = text.lower().split()
        
        positive_keywords = [word for word in words if word in self.positive_words]
        negative_keywords = [word for word in words if word in self.negative_words]
        neutral_keywords = [word for word in words if word in self.neutral_words]
        
        return {
            'positive': list(set(positive_keywords)),
            'negative': list(set(negative_keywords)),
            'neutral': list(set(neutral_keywords))
        }
    
    def get_sentiment_summary(self, text: str) -> Dict[str, Any]:
        """Get comprehensive sentiment summary"""
        # Basic analysis
        basic = self._basic_analysis(text)
        
        # Hybrid analysis
        hybrid = self._hybrid_analysis(text)
        
        # Extract sentiment keywords
        keywords = self.extract_sentiment_keywords(text)
        
        return {
            'overall_sentiment': hybrid['sentiment'],
            'confidence': hybrid['confidence'],
            'score': hybrid['score'],
            'positive_keywords': keywords['positive'],
            'negative_keywords': keywords['negative'],
            'neutral_keywords': keywords['neutral'],
            'positive_ratio': basic['positive_ratio'],
            'negative_ratio': basic['negative_ratio'],
            'neutral_ratio': basic['neutral_ratio'],
            'text_length': len(text.split()),
            'analysis_methods': ['lexicon', 'rule_based', 'hybrid']
        }

# Example usage
sentiment_analyzer = SentimentAnalyzer()

# Analyze sentiment of sample text
sample_text = "This product is absolutely amazing! I love how it works and it's very easy to use."
sentiment_result = sentiment_analyzer.analyze_sentiment(sample_text, method='hybrid') 