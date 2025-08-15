# Topic Modeling using NLP
from typing import List, Dict, Any, Optional
import numpy as np
from collections import Counter, defaultdict
import random

class TopicModeler:
    def __init__(self, num_topics: int = 5):
        self.num_topics = num_topics
        self.vocabulary = set()
        self.topic_word_distributions = {}
        self.document_topic_distributions = {}
        self.topic_names = {}
        
    def fit(self, documents: List[str]) -> Dict[str, Any]:
        """Fit topic model to documents"""
        # Preprocess documents
        processed_docs = [self._preprocess_document(doc) for doc in documents]
        
        # Build vocabulary
        self._build_vocabulary(processed_docs)
        
        # Initialize topic distributions
        self._initialize_topic_distributions()
        
        # Run topic modeling (simplified LDA-like algorithm)
        self._run_topic_modeling(processed_docs)
        
        # Name topics
        self._name_topics()
        
        return {
            'num_topics': self.num_topics,
            'vocabulary_size': len(self.vocabulary),
            'topic_names': self.topic_names,
            'convergence': True  # Simplified
        }
    
    def _preprocess_document(self, document: str) -> List[str]:
        """Preprocess a document"""
        # Convert to lowercase
        doc = document.lower()
        
        # Remove punctuation
        import re
        doc = re.sub(r'[^\w\s]', '', doc)
        
        # Split into words
        words = doc.split()
        
        # Remove stop words (simplified)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return words
    
    def _build_vocabulary(self, processed_docs: List[List[str]]) -> None:
        """Build vocabulary from processed documents"""
        self.vocabulary = set()
        for doc in processed_docs:
            self.vocabulary.update(doc)
    
    def _initialize_topic_distributions(self) -> None:
        """Initialize topic-word and document-topic distributions"""
        vocab_list = list(self.vocabulary)
        
        # Initialize topic-word distributions
        for topic_id in range(self.num_topics):
            # Random initialization
            topic_dist = np.random.dirichlet([0.1] * len(vocab_list))
            self.topic_word_distributions[topic_id] = {
                word: prob for word, prob in zip(vocab_list, topic_dist)
            }
    
    def _run_topic_modeling(self, processed_docs: List[List[str]]) -> None:
        """Run topic modeling algorithm (simplified)"""
        # Simplified topic modeling - in practice, you'd use LDA or similar
        vocab_list = list(self.vocabulary)
        
        # Update topic-word distributions based on document content
        for topic_id in range(self.num_topics):
            # Simulate learning from documents
            topic_words = self._get_topic_words(topic_id, processed_docs)
            
            # Update distribution
            word_counts = Counter(topic_words)
            total_words = sum(word_counts.values())
            
            if total_words > 0:
                for word in self.vocabulary:
                    count = word_counts.get(word, 0)
                    self.topic_word_distributions[topic_id][word] = count / total_words
            else:
                # Fallback to uniform distribution
                for word in self.vocabulary:
                    self.topic_word_distributions[topic_id][word] = 1.0 / len(self.vocabulary)
    
    def _get_topic_words(self, topic_id: int, processed_docs: List[List[str]]) -> List[str]:
        """Get words associated with a topic (simplified)"""
        # This is a simplified approach - in practice, you'd use the actual topic modeling results
        all_words = []
        for doc in processed_docs:
            all_words.extend(doc)
        
        # Simulate topic-specific word selection
        topic_words = []
        for word in all_words:
            if random.random() < 0.3:  # 30% chance of being in this topic
                topic_words.append(word)
        
        return topic_words
    
    def _name_topics(self) -> None:
        """Assign names to topics based on top words"""
        for topic_id in range(self.num_topics):
            # Get top words for this topic
            topic_dist = self.topic_word_distributions[topic_id]
            top_words = sorted(topic_dist.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Create topic name from top words
            topic_name = '_'.join([word for word, _ in top_words[:3]])
            self.topic_names[topic_id] = topic_name
    
    def get_topics(self, top_n: int = 10) -> Dict[int, List[tuple]]:
        """Get top words for each topic"""
        topics = {}
        
        for topic_id in range(self.num_topics):
            topic_dist = self.topic_word_distributions[topic_id]
            top_words = sorted(topic_dist.items(), key=lambda x: x[1], reverse=True)[:top_n]
            topics[topic_id] = top_words
        
        return topics
    
    def predict_topics(self, document: str) -> Dict[int, float]:
        """Predict topic distribution for a new document"""
        processed_doc = self._preprocess_document(document)
        
        # Calculate document-topic probabilities
        doc_topic_probs = {}
        
        for topic_id in range(self.num_topics):
            topic_prob = 0.0
            
            for word in processed_doc:
                if word in self.vocabulary:
                    word_prob = self.topic_word_distributions[topic_id].get(word, 0.0)
                    topic_prob += word_prob
            
            # Normalize
            if len(processed_doc) > 0:
                topic_prob /= len(processed_doc)
            
            doc_topic_probs[topic_id] = topic_prob
        
        # Normalize probabilities
        total_prob = sum(doc_topic_probs.values())
        if total_prob > 0:
            for topic_id in doc_topic_probs:
                doc_topic_probs[topic_id] /= total_prob
        
        return doc_topic_probs
    
    def get_related_topics(self, topic_id: int, top_n: int = 3) -> List[tuple]:
        """Get topics related to a given topic"""
        if topic_id not in self.topic_word_distributions:
            return []
        
        topic_dist = self.topic_word_distributions[topic_id]
        similarities = []
        
        for other_topic_id in range(self.num_topics):
            if other_topic_id != topic_id:
                other_dist = self.topic_word_distributions[other_topic_id]
                
                # Calculate cosine similarity
                similarity = self._calculate_cosine_similarity(topic_dist, other_dist)
                similarities.append((other_topic_id, similarity))
        
        # Return top similar topics
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]
    
    def _calculate_cosine_similarity(self, dist1: Dict[str, float], dist2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two distributions"""
        # Get all words
        all_words = set(dist1.keys()) | set(dist2.keys())
        
        # Calculate dot product and magnitudes
        dot_product = 0.0
        mag1 = 0.0
        mag2 = 0.0
        
        for word in all_words:
            val1 = dist1.get(word, 0.0)
            val2 = dist2.get(word, 0.0)
            
            dot_product += val1 * val2
            mag1 += val1 * val1
            mag2 += val2 * val2
        
        # Calculate cosine similarity
        if mag1 > 0 and mag2 > 0:
            return dot_product / (np.sqrt(mag1) * np.sqrt(mag2))
        else:
            return 0.0
    
    def get_topic_coherence(self, topic_id: int) -> float:
        """Calculate topic coherence score"""
        if topic_id not in self.topic_word_distributions:
            return 0.0
        
        topic_dist = self.topic_word_distributions[topic_id]
        top_words = sorted(topic_dist.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Simplified coherence calculation
        # In practice, you'd use more sophisticated measures
        word_probs = [prob for _, prob in top_words]
        coherence = np.mean(word_probs)
        
        return coherence
    
    def get_document_clusters(self, documents: List[str]) -> Dict[int, List[int]]:
        """Cluster documents by dominant topic"""
        clusters = defaultdict(list)
        
        for doc_id, document in enumerate(documents):
            topic_probs = self.predict_topics(document)
            dominant_topic = max(topic_probs, key=topic_probs.get)
            clusters[dominant_topic].append(doc_id)
        
        return dict(clusters)
    
    def analyze_topic_evolution(self, documents_by_time: List[List[str]]) -> Dict[str, Any]:
        """Analyze how topics evolve over time"""
        evolution_data = {}
        
        for time_period, documents in enumerate(documents_by_time):
            # Fit model for this time period
            period_modeler = TopicModeler(self.num_topics)
            period_modeler.fit(documents)
            
            # Get topics for this period
            topics = period_modeler.get_topics()
            
            evolution_data[f'period_{time_period}'] = {
                'topics': topics,
                'topic_names': period_modeler.topic_names
            }
        
        return evolution_data
    
    def get_topic_keywords(self, topic_id: int, min_probability: float = 0.01) -> List[str]:
        """Get keywords for a specific topic"""
        if topic_id not in self.topic_word_distributions:
            return []
        
        topic_dist = self.topic_word_distributions[topic_id]
        keywords = [
            word for word, prob in topic_dist.items() 
            if prob >= min_probability
        ]
        
        return sorted(keywords, key=lambda w: topic_dist[w], reverse=True)
    
    def get_topic_summary(self, topic_id: int) -> Dict[str, Any]:
        """Get comprehensive summary for a topic"""
        if topic_id not in self.topic_word_distributions:
            return {}
        
        topic_dist = self.topic_word_distributions[topic_id]
        top_words = sorted(topic_dist.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'topic_id': topic_id,
            'topic_name': self.topic_names.get(topic_id, f'topic_{topic_id}'),
            'top_words': top_words,
            'coherence_score': self.get_topic_coherence(topic_id),
            'related_topics': self.get_related_topics(topic_id),
            'total_probability': sum(topic_dist.values())
        }
    
    def visualize_topics(self) -> Dict[str, Any]:
        """Generate visualization data for topics"""
        visualization_data = {
            'topics': {},
            'topic_relationships': [],
            'topic_coherence': {}
        }
        
        # Topic data
        for topic_id in range(self.num_topics):
            topic_summary = self.get_topic_summary(topic_id)
            visualization_data['topics'][topic_id] = topic_summary
        
        # Topic relationships
        for topic_id in range(self.num_topics):
            related = self.get_related_topics(topic_id)
            for related_id, similarity in related:
                visualization_data['topic_relationships'].append({
                    'source': topic_id,
                    'target': related_id,
                    'similarity': similarity
                })
        
        # Coherence scores
        for topic_id in range(self.num_topics):
            visualization_data['topic_coherence'][topic_id] = self.get_topic_coherence(topic_id)
        
        return visualization_data

# Example usage
topic_modeler = TopicModeler(num_topics=3)

# Sample documents
sample_documents = [
    "Python programming is great for data science and machine learning",
    "Machine learning algorithms use Python for implementation",
    "Data science involves Python programming and statistics",
    "Web development with Python is popular and efficient",
    "Python web frameworks like Django are widely used",
    "Programming in Python is easy to learn and powerful"
]

# Fit the model
model_result = topic_modeler.fit(sample_documents)

# Get topics
topics = topic_modeler.get_topics()

# Predict topics for new document
new_doc = "Python is used for artificial intelligence and deep learning"
topic_probs = topic_modeler.predict_topics(new_doc) 