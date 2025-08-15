# Arquitetura de ML

Este documento detalha a arquitetura de ML do Omni Keywords Finder.

## Modelos

### Embeddings
```python
# ml/embeddings.py
class KeywordEmbedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.cache = RedisCache()

    def get_embedding(self, text: str) -> np.ndarray:
        cache_key = f"embedding:{text}"
        if cached := self.cache.get(cache_key):
            return np.frombuffer(cached)
        
        embedding = self.model.encode(text)
        self.cache.set(cache_key, embedding.tobytes())
        return embedding

    def batch_embed(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, batch_size=32)
```

### Clustering
```python
# ml/clustering.py
class KeywordClusterer:
    def __init__(self):
        self.model = HDBSCAN(
            min_cluster_size=5,
            min_samples=3,
            metric='euclidean'
        )

    def cluster_keywords(self, embeddings: np.ndarray) -> List[int]:
        return self.model.fit_predict(embeddings)

    def get_cluster_centers(self, embeddings: np.ndarray, labels: np.ndarray) -> np.ndarray:
        centers = []
        for label in set(labels):
            if label != -1:  # Skip noise
                cluster_embeddings = embeddings[labels == label]
                centers.append(np.mean(cluster_embeddings, axis=0))
        return np.array(centers)
```

### Classificação
```python
# ml/classification.py
class KeywordClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

    def train(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)
```

## Pipeline

### Treinamento
```python
# ml/training.py
class MLPipeline:
    def __init__(self):
        self.embedder = KeywordEmbedder()
        self.clusterer = KeywordClusterer()
        self.classifier = KeywordClassifier()

    def train(self, keywords: List[Keyword]):
        # Preparar dados
        texts = [k.text for k in keywords]
        embeddings = self.embedder.batch_embed(texts)
        
        # Clustering
        cluster_labels = self.clusterer.cluster_keywords(embeddings)
        
        # Classificação
        self.classifier.train(embeddings, cluster_labels)
        
        # Salvar modelo
        self.save_model()

    def save_model(self):
        model_path = "models/keyword_classifier.joblib"
        joblib.dump(self.classifier, model_path)
```

### Inferência
```python
# ml/inference.py
class MLInference:
    def __init__(self):
        self.embedder = KeywordEmbedder()
        self.classifier = joblib.load("models/keyword_classifier.joblib")

    def process_keyword(self, keyword: str) -> Dict:
        # Gerar embedding
        embedding = self.embedder.get_embedding(keyword)
        
        # Classificar
        cluster = self.classifier.predict([embedding])[0]
        confidence = self.classifier.predict_proba([embedding])[0]
        
        return {
            "keyword": keyword,
            "cluster": int(cluster),
            "confidence": float(max(confidence))
        }

    def batch_process(self, keywords: List[str]) -> List[Dict]:
        embeddings = self.embedder.batch_embed(keywords)
        clusters = self.classifier.predict(embeddings)
        confidences = self.classifier.predict_proba(embeddings)
        
        return [
            {
                "keyword": k,
                "cluster": int(c),
                "confidence": float(max(conf))
            }
            for k, c, conf in zip(keywords, clusters, confidences)
        ]
```

## Avaliação

### Métricas
```python
# ml/evaluation.py
class MLEvaluator:
    def evaluate_model(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average='weighted'),
            "recall": recall_score(y_true, y_pred, average='weighted'),
            "f1": f1_score(y_true, y_pred, average='weighted')
        }

    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray):
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.show()
```

### Validação
```python
# ml/validation.py
class MLValidator:
    def cross_validate(self, X: np.ndarray, y: np.ndarray) -> Dict:
        cv_results = cross_val_score(
            self.classifier,
            X, y,
            cv=5,
            scoring='f1_weighted'
        )
        return {
            "mean_score": cv_results.mean(),
            "std_score": cv_results.std(),
            "scores": cv_results.tolist()
        }

    def validate_predictions(self, predictions: List[Dict]) -> bool:
        return all(
            isinstance(p["cluster"], int) and
            isinstance(p["confidence"], float) and
            0 <= p["confidence"] <= 1
            for p in predictions
        )
```

## Observações

1. Modelos otimizados
2. Cache eficiente
3. Batch processing
4. Validação rigorosa
5. Métricas claras
6. Monitoramento
7. Retreinamento
8. Versionamento
9. Documentação
10. Testes automatizados 