# Semantic Search using NLP
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from collections import defaultdict
import math

class SemanticSearch:
    def __init__(self):
        self.documents = []
        self.document_embeddings = {}
        self.vocabulary = set()
        self.word_embeddings = {}
        self.document_vectors = {}
        
    def add_documents(self, documents: List[str], doc_ids: Optional[List[str]] = None) -> None:
        """Add documents to the search index"""
        if doc_ids is None:
            doc_ids = [f"doc_{i}" for i in range(len(documents))]
        
        for doc_id, document in zip(doc_ids, documents):
            self.documents.append({
                'id': doc_id,
                'text': document,
                'processed': self._preprocess_document(document)
            })
        
        # Update vocabulary
        self._update_vocabulary()
        
        # Generate embeddings
        self._generate_embeddings()
    
    def _preprocess_document(self, document: str) -> List[str]:
        """Preprocess a document for semantic search"""
        # Convert to lowercase
        doc = document.lower()
        
        # Remove punctuation
        import re
        doc = re.sub(r'[^\w\s]', '', doc)
        
        # Split into words
        words = doc.split()
        
        # Remove stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could'
        }
        words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return words
    
    def _update_vocabulary(self) -> None:
        """Update vocabulary from all documents"""
        self.vocabulary = set()
        for doc in self.documents:
            self.vocabulary.update(doc['processed'])
    
    def _generate_embeddings(self) -> None:
        """Generate embeddings for documents and words"""
        # Generate word embeddings (simplified)
        self._generate_word_embeddings()
        
        # Generate document embeddings
        self._generate_document_embeddings()
    
    def _generate_word_embeddings(self) -> None:
        """Generate word embeddings (simplified TF-IDF approach)"""
        vocab_list = list(self.vocabulary)
        embedding_dim = min(100, len(vocab_list))  # Limit embedding dimension
        
        for word in self.vocabulary:
            # Generate random embedding (in practice, you'd use pre-trained embeddings)
            embedding = np.random.normal(0, 1, embedding_dim)
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            self.word_embeddings[word] = embedding
    
    def _generate_document_embeddings(self) -> None:
        """Generate document embeddings from word embeddings"""
        for doc in self.documents:
            doc_id = doc['id']
            words = doc['processed']
            
            if not words:
                # Empty document
                self.document_embeddings[doc_id] = np.zeros(100)
                continue
            
            # Calculate document vector as weighted average of word embeddings
            doc_vector = np.zeros(100)
            word_weights = self._calculate_word_weights(words)
            
            for word, weight in word_weights.items():
                if word in self.word_embeddings:
                    doc_vector += weight * self.word_embeddings[word]
            
            # Normalize document vector
            norm = np.linalg.norm(doc_vector)
            if norm > 0:
                doc_vector = doc_vector / norm
            
            self.document_embeddings[doc_id] = doc_vector
            self.document_vectors[doc_id] = word_weights
    
    def _calculate_word_weights(self, words: List[str]) -> Dict[str, float]:
        """Calculate word weights using TF-IDF"""
        # Calculate term frequency
        word_freq = defaultdict(int)
        for word in words:
            word_freq[word] += 1
        
        # Calculate TF-IDF weights
        word_weights = {}
        total_words = len(words)
        
        for word, freq in word_freq.items():
            # Term frequency
            tf = freq / total_words
            
            # Inverse document frequency (simplified)
            doc_freq = sum(1 for doc in self.documents if word in doc['processed'])
            idf = math.log(len(self.documents) / (doc_freq + 1))
            
            word_weights[word] = tf * idf
        
        return word_weights
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for documents semantically similar to query"""
        # Preprocess query
        query_words = self._preprocess_document(query)
        
        # Generate query embedding
        query_embedding = self._generate_query_embedding(query_words)
        
        # Calculate similarities
        similarities = []
        for doc in self.documents:
            doc_id = doc['id']
            doc_embedding = self.document_embeddings[doc_id]
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            
            similarities.append({
                'doc_id': doc_id,
                'text': doc['text'],
                'similarity': similarity,
                'matched_words': self._find_matched_words(query_words, doc['processed'])
            })
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def _generate_query_embedding(self, query_words: List[str]) -> np.ndarray:
        """Generate embedding for query"""
        if not query_words:
            return np.zeros(100)
        
        # Calculate query vector as weighted average of word embeddings
        query_vector = np.zeros(100)
        word_weights = self._calculate_word_weights(query_words)
        
        for word, weight in word_weights.items():
            if word in self.word_embeddings:
                query_vector += weight * self.word_embeddings[word]
        
        # Normalize query vector
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm
        
        return query_vector
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 > 0 and norm2 > 0:
            return dot_product / (norm1 * norm2)
        else:
            return 0.0
    
    def _find_matched_words(self, query_words: List[str], doc_words: List[str]) -> List[str]:
        """Find words that match between query and document"""
        query_set = set(query_words)
        doc_set = set(doc_words)
        return list(query_set & doc_set)
    
    def search_by_keywords(self, keywords: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for documents containing specific keywords"""
        keyword_set = set(keywords)
        results = []
        
        for doc in self.documents:
            doc_words = set(doc['processed'])
            matched_keywords = keyword_set & doc_words
            
            if matched_keywords:
                # Calculate relevance score based on keyword matches
                relevance_score = len(matched_keywords) / len(keyword_set)
                
                results.append({
                    'doc_id': doc['id'],
                    'text': doc['text'],
                    'relevance_score': relevance_score,
                    'matched_keywords': list(matched_keywords),
                    'total_keywords': len(keyword_set)
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:top_k]
    
    def find_similar_documents(self, doc_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find documents similar to a given document"""
        if doc_id not in self.document_embeddings:
            return []
        
        target_embedding = self.document_embeddings[doc_id]
        similarities = []
        
        for doc in self.documents:
            if doc['id'] == doc_id:
                continue
            
            doc_embedding = self.document_embeddings[doc['id']]
            similarity = self._cosine_similarity(target_embedding, doc_embedding)
            
            similarities.append({
                'doc_id': doc['id'],
                'text': doc['text'],
                'similarity': similarity
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def get_document_clusters(self, num_clusters: int = 3) -> Dict[int, List[str]]:
        """Cluster documents based on semantic similarity"""
        if len(self.documents) < num_clusters:
            return {}
        
        # Simple clustering using similarity matrix
        doc_ids = [doc['id'] for doc in self.documents]
        similarity_matrix = np.zeros((len(doc_ids), len(doc_ids)))
        
        # Calculate similarity matrix
        for i, doc_id1 in enumerate(doc_ids):
            for j, doc_id2 in enumerate(doc_ids):
                if i != j:
                    emb1 = self.document_embeddings[doc_id1]
                    emb2 = self.document_embeddings[doc_id2]
                    similarity_matrix[i][j] = self._cosine_similarity(emb1, emb2)
        
        # Simple clustering (in practice, you'd use K-means or similar)
        clusters = defaultdict(list)
        
        # Assign documents to clusters based on similarity
        for i, doc_id in enumerate(doc_ids):
            cluster_id = i % num_clusters
            clusters[cluster_id].append(doc_id)
        
        return dict(clusters)
    
    def get_semantic_keywords(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Get semantically related keywords for a query"""
        query_words = self._preprocess_document(query)
        keyword_scores = defaultdict(float)
        
        for doc in self.documents:
            doc_words = set(doc['processed'])
            
            # Check if document is relevant to query
            query_relevance = len(set(query_words) & doc_words) / len(set(query_words)) if query_words else 0
            
            if query_relevance > 0:
                # Add words from relevant documents
                for word in doc_words:
                    if word not in query_words:
                        keyword_scores[word] += query_relevance
        
        # Convert to list and sort
        keywords = [
            {'keyword': word, 'score': score}
            for word, score in keyword_scores.items()
        ]
        keywords.sort(key=lambda x: x['score'], reverse=True)
        
        return keywords[:top_k]
    
    def get_search_suggestions(self, partial_query: str, top_k: int = 5) -> List[str]:
        """Get search suggestions based on partial query"""
        suggestions = []
        partial_lower = partial_query.lower()
        
        # Find words that start with the partial query
        for word in self.vocabulary:
            if word.startswith(partial_lower):
                suggestions.append(word)
        
        # Sort by frequency in documents
        word_freq = defaultdict(int)
        for doc in self.documents:
            for word in doc['processed']:
                if word in suggestions:
                    word_freq[word] += 1
        
        suggestions = sorted(suggestions, key=lambda w: word_freq[w], reverse=True)
        return suggestions[:top_k]
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """Get analytics about the search index"""
        total_documents = len(self.documents)
        total_words = sum(len(doc['processed']) for doc in self.documents)
        avg_doc_length = total_words / total_documents if total_documents > 0 else 0
        
        # Word frequency analysis
        word_freq = defaultdict(int)
        for doc in self.documents:
            for word in doc['processed']:
                word_freq[word] += 1
        
        most_common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_documents': total_documents,
            'vocabulary_size': len(self.vocabulary),
            'total_words': total_words,
            'average_document_length': avg_doc_length,
            'most_common_words': most_common_words,
            'embedding_dimension': 100
        }
    
    def update_document(self, doc_id: str, new_text: str) -> bool:
        """Update a document in the search index"""
        # Find and update document
        for doc in self.documents:
            if doc['id'] == doc_id:
                doc['text'] = new_text
                doc['processed'] = self._preprocess_document(new_text)
                
                # Regenerate embeddings
                self._update_vocabulary()
                self._generate_embeddings()
                return True
        
        return False
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the search index"""
        # Remove document
        self.documents = [doc for doc in self.documents if doc['id'] != doc_id]
        
        # Remove from embeddings
        if doc_id in self.document_embeddings:
            del self.document_embeddings[doc_id]
        if doc_id in self.document_vectors:
            del self.document_vectors[doc_id]
        
        # Regenerate embeddings
        self._update_vocabulary()
        self._generate_embeddings()
        
        return True

# Example usage
semantic_search = SemanticSearch()

# Add sample documents
sample_docs = [
    "Python programming is great for data science and machine learning",
    "Machine learning algorithms use Python for implementation",
    "Data science involves Python programming and statistics",
    "Web development with Python is popular and efficient",
    "Python web frameworks like Django are widely used"
]

doc_ids = ["doc1", "doc2", "doc3", "doc4", "doc5"]
semantic_search.add_documents(sample_docs, doc_ids)

# Search for documents
search_results = semantic_search.search("artificial intelligence", top_k=3) 