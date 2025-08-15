"""
Exemplo de Uso do Sistema ML Adaptativo - Omni Keywords Finder
Tracing ID: ML_EXAMPLE_20241219_001
Data: 2024-12-19
Versão: 1.0

Demonstra como usar o sistema ML adaptativo para:
- Clustering adaptativo de keywords
- Otimização automática de parâmetros
- Feedback loop para aprendizado contínuo
- Sugestões inteligentes
"""

import sys
import os
import time
from typing import List, Dict, Any
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar sistema ML adaptativo
from infrastructure.ml.adaptativo.modelo_adaptativo import (
    AdaptiveModel, ModelConfig, ModelType, get_adaptive_model
)
from infrastructure.ml.adaptativo.otimizador import (
    AutoOptimizer, OptimizationConfig, OptimizationAlgorithm, get_auto_optimizer
)
from infrastructure.ml.adaptativo.feedback_loop import (
    FeedbackLoop, FeedbackLoopConfig, FeedbackData, FeedbackType, get_feedback_loop
)


def create_sample_keywords_data() -> List[Dict[str, Any]]:
    """Cria dados de exemplo para demonstração."""
    keywords = [
        "marketing digital",
        "seo otimização",
        "google ads",
        "facebook ads",
        "instagram marketing",
        "linkedin ads",
        "email marketing",
        "content marketing",
        "inbound marketing",
        "social media marketing",
        "ppc campaigns",
        "google analytics",
        "conversion optimization",
        "landing page design",
        "copywriting",
        "brand strategy",
        "market research",
        "customer journey",
        "lead generation",
        "sales funnel",
        "crm software",
        "automation tools",
        "web design",
        "mobile marketing",
        "video marketing",
        "podcast marketing",
        "influencer marketing",
        "affiliate marketing",
        "retargeting ads",
        "display advertising"
    ]
    
    # Criar dados estruturados com métricas
    keywords_data = []
    for index, keyword in enumerate(keywords):
        keywords_data.append({
            "keyword": keyword,
            "score": 70 + (index % 30),  # Score variado
            "volume_busca": 1000 + (index * 100),
            "cpc": 1.5 + (index * 0.1),
            "concorrencia": 0.3 + (index * 0.02),
            "categoria": "marketing" if "marketing" in keyword else "tecnologia",
            "intencao": "comercial" if "ads" in keyword else "informacional"
        })
    
    return keywords_data


def demonstrate_adaptive_clustering():
    """Demonstra clustering adaptativo."""
    print("🔍 **DEMONSTRAÇÃO: CLUSTERING ADAPTATIVO**")
    print("=" * 50)
    
    # Criar dados de exemplo
    keywords_data = create_sample_keywords_data()
    print(f"📊 Keywords para clustering: {len(keywords_data)}")
    
    # Configurar modelo adaptativo
    config = ModelConfig(
        model_type=ModelType.KMEANS,
        optimization_strategy="bayesian_optimization",
        n_trials=20,  # Poucos trials para demonstração rápida
        min_clusters=3,
        max_clusters=8,
        auto_feature_selection=True
    )
    
    # Inicializar modelo
    model = AdaptiveModel(config)
    
    # Executar clustering
    print("🔄 Executando clustering adaptativo...")
    start_time = time.time()
    
    keywords_text = [item["keyword"] for item in keywords_data]
    optimization_result = model.fit(keywords_text)
    
    clustering_time = time.time() - start_time
    
    # Obter clusters
    cluster_labels = model.predict(keywords_text)
    
    # Organizar resultados
    clusters = {}
    for index, (keyword_data, label) in enumerate(zip(keywords_data, cluster_labels)):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(keyword_data["keyword"])
    
    # Exibir resultados
    print(f"✅ Clustering concluído em {clustering_time:.2f}string_data")
    print(f"🎯 Performance score: {optimization_result.best_score:.4f}")
    print(f"📈 Número de clusters: {len(clusters)}")
    print(f"🔧 Melhores parâmetros: {optimization_result.best_params}")
    
    print("\n📋 **CLUSTERS GERADOS:**")
    for cluster_id, keywords in clusters.items():
        print(f"\n🔸 Cluster {cluster_id} ({len(keywords)} keywords):")
        for keyword in keywords[:5]:  # Mostrar apenas os primeiros 5
            print(f"   • {keyword}")
        if len(keywords) > 5:
            print(f"   ... e mais {len(keywords) - 5} keywords")
    
    return model, clusters


def demonstrate_auto_optimization():
    """Demonstra otimização automática."""
    print("\n⚡ **DEMONSTRAÇÃO: OTIMIZAÇÃO AUTOMÁTICA**")
    print("=" * 50)
    
    # Configurar otimizador
    config = OptimizationConfig(
        algorithm=OptimizationAlgorithm.TPE,
        n_trials=15,  # Poucos trials para demonstração
        timeout=300,  # 5 minutos
        early_stopping=True,
        patience=5
    )
    
    # Inicializar otimizador
    optimizer = AutoOptimizer(config)
    
    # Definir limites dos parâmetros
    from sklearn.cluster import KMeans
    parameter_bounds = {
        'n_clusters': ('int', 2, 10),
        'max_iter': ('int', 100, 500),
        'n_init': ('int', 5, 15)
    }
    
    optimizer.set_parameter_bounds(parameter_bounds)
    
    # Criar dados de exemplo
    import numpy as np
    X = np.random.rand(100, 5)  # 100 amostras, 5 features
    
    # Executar otimização
    print("🔄 Executando otimização automática...")
    start_time = time.time()
    
    result = optimizer.optimize(X, KMeans)
    
    optimization_time = time.time() - start_time
    
    # Exibir resultados
    print(f"✅ Otimização concluída em {optimization_time:.2f}string_data")
    print(f"🎯 Melhor score: {result.best_score:.4f}")
    print(f"🔧 Melhores parâmetros: {result.best_params}")
    print(f"📊 Número de tentativas: {result.n_trials}")
    
    return optimizer, result


def demonstrate_feedback_loop():
    """Demonstra feedback loop."""
    print("\n🔄 **DEMONSTRAÇÃO: FEEDBACK LOOP**")
    print("=" * 50)
    
    # Configurar feedback loop
    config = FeedbackLoopConfig(
        feedback_window_size=100,
        drift_detection_threshold=0.1,
        retraining_threshold=0.15,
        enable_automatic_retraining=True
    )
    
    # Inicializar feedback loop
    feedback_loop = FeedbackLoop(config)
    
    # Simular feedback de usuários
    print("📝 Simulando feedback de usuários...")
    
    feedback_types = [
        FeedbackType.USER_RATING,
        FeedbackType.CLICK_THROUGH_RATE,
        FeedbackType.CONVERSION_RATE,
        FeedbackType.DWELL_TIME
    ]
    
    for index in range(20):
        feedback_type = feedback_types[index % len(feedback_types)]
        value = 0.3 + (index * 0.03)  # Valores crescentes
        user_id = f"user_{index % 5}"
        
        feedback = FeedbackData(
            feedback_type=feedback_type,
            value=value,
            timestamp=time.time() - (index * 3600),  # Timestamps decrescentes
            user_id=user_id,
            metadata={"cluster_id": f"cluster_{index % 3}"}
        )
        
        feedback_loop.add_feedback(feedback)
    
    # Aguardar processamento
    time.sleep(2)
    
    # Obter resumo
    summary = feedback_loop.get_feedback_summary()
    
    print("✅ Feedback processado!")
    print(f"📊 Total de feedbacks: {summary.get('total_feedback', 0)}")
    print(f"📈 Performance média: {summary.get('average_performance', 0):.3f}")
    print(f"🔄 Drift detectado: {summary.get('drift_detected', False)}")
    
    if summary.get('drift_detected'):
        print(f"⚠️ Severidade do drift: {summary.get('drift_severity', 0):.3f}")
    
    return feedback_loop, summary


def demonstrate_integration():
    """Demonstra integração completa."""
    print("\n🚀 **DEMONSTRAÇÃO: INTEGRAÇÃO COMPLETA**")
    print("=" * 50)
    
    # Criar dados de exemplo
    keywords_data = create_sample_keywords_data()
    
    # 1. Clustering adaptativo
    print("1️⃣ Executando clustering adaptativo...")
    model, clusters = demonstrate_adaptive_clustering()
    
    # 2. Otimização automática
    print("\n2️⃣ Executando otimização automática...")
    optimizer, opt_result = demonstrate_auto_optimization()
    
    # 3. Feedback loop
    print("\n3️⃣ Executando feedback loop...")
    feedback_loop, feedback_summary = demonstrate_feedback_loop()
    
    # 4. Sugestões inteligentes
    print("\n4️⃣ Gerando sugestões inteligentes...")
    
    # Simular predições
    keywords_text = [item["keyword"] for item in keywords_data[:10]]
    cluster_labels = model.predict(keywords_text)
    
    suggestions = []
    for index, (keyword_data, label) in enumerate(zip(keywords_data[:10], cluster_labels)):
        cluster_score = 0.5 + (label * 0.1)
        final_score = keyword_data["score"] * 0.7 + cluster_score * 0.3
        
        suggestions.append({
            "keyword": keyword_data["keyword"],
            "original_score": keyword_data["score"],
            "cluster_score": cluster_score,
            "final_score": final_score,
            "cluster": label
        })
    
    # Ordenar por score final
    suggestions.sort(key=lambda value: value["final_score"], reverse=True)
    
    print("✅ Sugestões geradas!")
    print("\n🏆 **TOP 5 SUGESTÕES:**")
    for index, suggestion in enumerate(suggestions[:5]):
        print(f"{index+1}. {suggestion['keyword']}")
        print(f"   Score original: {suggestion['original_score']:.1f}")
        print(f"   Score cluster: {suggestion['cluster_score']:.3f}")
        print(f"   Score final: {suggestion['final_score']:.1f}")
        print(f"   Cluster: {suggestion['cluster']}")
        print()
    
    # 5. Resumo final
    print("📊 **RESUMO DA INTEGRAÇÃO:**")
    print(f"✅ Clustering: {len(clusters)} clusters gerados")
    print(f"✅ Otimização: Score {opt_result.best_score:.4f}")
    print(f"✅ Feedback: {feedback_summary.get('total_feedback', 0)} feedbacks processados")
    print(f"✅ Sugestões: {len(suggestions)} keywords analisadas")
    
    return {
        "model": model,
        "optimizer": optimizer,
        "feedback_loop": feedback_loop,
        "clusters": clusters,
        "suggestions": suggestions
    }


def main():
    """Função principal de demonstração."""
    print("🤖 **SISTEMA ML ADAPTATIVO - OMNİ KEYWORDS FINDER**")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}")
    print(f"🆔 Tracing ID: ML_EXAMPLE_20241219_001")
    print("=" * 60)
    
    try:
        # Executar demonstração completa
        results = demonstrate_integration()
        
        print("\n🎉 **DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!**")
        print("=" * 60)
        print("✅ Sistema ML adaptativo funcionando perfeitamente")
        print("✅ Clustering adaptativo implementado")
        print("✅ Otimização automática ativa")
        print("✅ Feedback loop operacional")
        print("✅ Sugestões inteligentes geradas")
        print("=" * 60)
        
        return results
        
    except Exception as e:
        print(f"\n❌ **ERRO NA DEMONSTRAÇÃO:** {str(e)}")
        print("🔧 Verifique se todas as dependências estão instaladas")
        return None


if __name__ == "__main__":
    main() 