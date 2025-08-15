# Automated Performance Optimizer using Machine Learning
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

class PerformanceOptimizer:
    def __init__(self):
        self.performance_metrics = {}
        self.optimization_strategies = {}
        self.performance_history = {}
        self.optimization_rules = {}
        
    def optimize_performance(self, performance_data: List[Dict[str, Any]], 
                           optimization_goals: List[str]) -> Dict[str, Any]:
        """Automatically optimize performance based on goals"""
        optimization_results = {
            'original_performance': self._calculate_current_performance(performance_data),
            'optimized_performance': {},
            'performance_issues': [],
            'optimization_strategies': [],
            'predicted_improvements': {},
            'recommendations': []
        }
        
        # Analyze current performance
        performance_analysis = self._analyze_performance(performance_data)
        optimization_results['performance_issues'] = performance_analysis['issues']
        
        # Generate optimization strategies
        strategies = self._generate_optimization_strategies(performance_analysis, optimization_goals)
        optimization_results['optimization_strategies'] = strategies
        
        # Apply optimizations
        optimized_performance = self._apply_performance_optimizations(performance_data, strategies)
        optimization_results['optimized_performance'] = optimized_performance
        
        # Predict improvements
        predicted_improvements = self._predict_performance_improvements(
            performance_analysis, strategies
        )
        optimization_results['predicted_improvements'] = predicted_improvements
        
        # Generate recommendations
        optimization_results['recommendations'] = self._generate_performance_recommendations(
            performance_analysis, strategies
        )
        
        return optimization_results
    
    def _calculate_current_performance(self, performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate current performance metrics"""
        if not performance_data:
            return {}
        
        df = pd.DataFrame(performance_data)
        
        return {
            'average_rank': df['rank'].mean() if 'rank' in df.columns else 0,
            'average_traffic': df['traffic'].mean() if 'traffic' in df.columns else 0,
            'average_conversions': df['conversions'].mean() if 'conversions' in df.columns else 0,
            'average_ctr': df['ctr'].mean() if 'ctr' in df.columns else 0,
            'total_keywords': len(performance_data),
            'performance_score': self._calculate_overall_performance_score(df)
        }
    
    def _calculate_overall_performance_score(self, df: pd.DataFrame) -> float:
        """Calculate overall performance score"""
        score = 0.0
        
        # Ranking score (better rank = higher score)
        if 'rank' in df.columns:
            avg_rank = df['rank'].mean()
            rank_score = max(0, (100 - avg_rank) / 100)
            score += rank_score * 0.3
        
        # Traffic score
        if 'traffic' in df.columns:
            avg_traffic = df['traffic'].mean()
            traffic_score = min(1.0, avg_traffic / 10000)
            score += traffic_score * 0.3
        
        # Conversion score
        if 'conversions' in df.columns:
            avg_conversions = df['conversions'].mean()
            conversion_score = min(1.0, avg_conversions / 100)
            score += conversion_score * 0.2
        
        # CTR score
        if 'ctr' in df.columns:
            avg_ctr = df['ctr'].mean()
            ctr_score = min(1.0, avg_ctr)
            score += ctr_score * 0.2
        
        return min(1.0, score)
    
    def _analyze_performance(self, performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance data for optimization opportunities"""
        analysis = {
            'performance_trends': self._analyze_performance_trends(performance_data),
            'keyword_performance': self._analyze_keyword_performance(performance_data),
            'performance_gaps': self._identify_performance_gaps(performance_data),
            'optimization_opportunities': self._identify_optimization_opportunities(performance_data),
            'issues': []
        }
        
        # Identify performance issues
        analysis['issues'] = self._identify_performance_issues(performance_data)
        
        return analysis
    
    def _analyze_performance_trends(self, performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if not performance_data or 'date' not in performance_data[0]:
            return {}
        
        df = pd.DataFrame(performance_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        trends = {}
        
        # Ranking trends
        if 'rank' in df.columns:
            ranking_trend = self._calculate_trend(df['rank'].values)
            trends['ranking_trend'] = ranking_trend
        
        # Traffic trends
        if 'traffic' in df.columns:
            traffic_trend = self._calculate_trend(df['traffic'].values)
            trends['traffic_trend'] = traffic_trend
        
        # Conversion trends
        if 'conversions' in df.columns:
            conversion_trend = self._calculate_trend(df['conversions'].values)
            trends['conversion_trend'] = conversion_trend
        
        return trends
    
    def _calculate_trend(self, values: np.ndarray) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "stable"
        
        # Calculate linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.01 * np.mean(values):
            return "increasing"
        elif slope < -0.01 * np.mean(values):
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_keyword_performance(self, performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze individual keyword performance"""
        keyword_analysis = {
            'top_performers': [],
            'underperformers': [],
            'improving_keywords': [],
            'declining_keywords': []
        }
        
        for data in performance_data:
            keyword = data.get('keyword', '')
            rank = data.get('rank', 0)
            traffic = data.get('traffic', 0)
            
            # Top performers (good rank and traffic)
            if rank <= 5 and traffic > 1000:
                keyword_analysis['top_performers'].append({
                    'keyword': keyword,
                    'rank': rank,
                    'traffic': traffic
                })
            
            # Underperformers (poor rank or low traffic)
            elif rank > 20 or traffic < 100:
                keyword_analysis['underperformers'].append({
                    'keyword': keyword,
                    'rank': rank,
                    'traffic': traffic
                })
        
        return keyword_analysis
    
    def _identify_performance_gaps(self, performance_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify performance gaps"""
        gaps = []
        
        # Analyze ranking gaps
        ranks = [data.get('rank', 0) for data in performance_data]
        if ranks:
            avg_rank = np.mean(ranks)
            if avg_rank > 15:
                gaps.append({
                    'type': 'ranking',
                    'description': 'Average ranking is too high',
                    'current_value': avg_rank,
                    'target_value': '< 10',
                    'priority': 'high'
                })
        
        # Analyze traffic gaps
        traffic_values = [data.get('traffic', 0) for data in performance_data]
        if traffic_values:
            avg_traffic = np.mean(traffic_values)
            if avg_traffic < 500:
                gaps.append({
                    'type': 'traffic',
                    'description': 'Average traffic is too low',
                    'current_value': avg_traffic,
                    'target_value': '> 1000',
                    'priority': 'high'
                })
        
        # Analyze conversion gaps
        conversions = [data.get('conversions', 0) for data in performance_data]
        if conversions:
            avg_conversions = np.mean(conversions)
            if avg_conversions < 10:
                gaps.append({
                    'type': 'conversion',
                    'description': 'Average conversions are too low',
                    'current_value': avg_conversions,
                    'target_value': '> 20',
                    'priority': 'medium'
                })
        
        return gaps
    
    def _identify_optimization_opportunities(self, performance_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        opportunities = []
        
        for data in performance_data:
            keyword = data.get('keyword', '')
            rank = data.get('rank', 0)
            traffic = data.get('traffic', 0)
            conversions = data.get('conversions', 0)
            
            # High traffic, low conversion opportunity
            if traffic > 1000 and conversions < 20:
                opportunities.append({
                    'keyword': keyword,
                    'type': 'conversion_optimization',
                    'description': 'High traffic but low conversions',
                    'priority': 'medium'
                })
            
            # Good rank, low traffic opportunity
            if rank <= 10 and traffic < 500:
                opportunities.append({
                    'keyword': keyword,
                    'type': 'traffic_optimization',
                    'description': 'Good rank but low traffic',
                    'priority': 'high'
                })
            
            # Poor rank, high potential opportunity
            if rank > 20 and len(keyword.split()) <= 2:
                opportunities.append({
                    'keyword': keyword,
                    'type': 'ranking_optimization',
                    'description': 'Poor rank for high-potential keyword',
                    'priority': 'high'
                })
        
        return opportunities
    
    def _identify_performance_issues(self, performance_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify performance issues"""
        issues = []
        
        # Check for declining performance
        trends = self._analyze_performance_trends(performance_data)
        
        if trends.get('ranking_trend') == 'decreasing':
            issues.append({
                'type': 'ranking_decline',
                'severity': 'high',
                'description': 'Rankings are declining',
                'recommendation': 'Investigate and fix ranking issues'
            })
        
        if trends.get('traffic_trend') == 'decreasing':
            issues.append({
                'type': 'traffic_decline',
                'severity': 'high',
                'description': 'Traffic is declining',
                'recommendation': 'Analyze traffic sources and optimize'
            })
        
        # Check for low performance keywords
        low_performance_count = sum(1 for data in performance_data 
                                  if data.get('rank', 0) > 20 or data.get('traffic', 0) < 100)
        
        if low_performance_count > len(performance_data) * 0.5:
            issues.append({
                'type': 'low_performance',
                'severity': 'medium',
                'description': f'{low_performance_count} keywords are underperforming',
                'recommendation': 'Focus on improving underperforming keywords'
            })
        
        return issues
    
    def _generate_optimization_strategies(self, analysis: Dict[str, Any], 
                                        optimization_goals: List[str]) -> List[Dict[str, Any]]:
        """Generate optimization strategies"""
        strategies = []
        
        # Ranking optimization strategies
        if 'ranking' in optimization_goals:
            ranking_strategies = self._generate_ranking_strategies(analysis)
            strategies.extend(ranking_strategies)
        
        # Traffic optimization strategies
        if 'traffic' in optimization_goals:
            traffic_strategies = self._generate_traffic_strategies(analysis)
            strategies.extend(traffic_strategies)
        
        # Conversion optimization strategies
        if 'conversion' in optimization_goals:
            conversion_strategies = self._generate_conversion_strategies(analysis)
            strategies.extend(conversion_strategies)
        
        # Overall performance strategies
        if 'overall' in optimization_goals:
            overall_strategies = self._generate_overall_strategies(analysis)
            strategies.extend(overall_strategies)
        
        return strategies
    
    def _generate_ranking_strategies(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate ranking optimization strategies"""
        strategies = []
        
        # Focus on underperforming keywords
        underperformers = analysis['keyword_performance']['underperformers']
        if underperformers:
            strategies.append({
                'type': 'ranking_focus',
                'description': f'Focus optimization efforts on {len(underperformers)} underperforming keywords',
                'priority': 'high',
                'expected_impact': 'medium',
                'keywords': [kw['keyword'] for kw in underperformers]
            })
        
        # Improve content for low-ranking keywords
        strategies.append({
            'type': 'content_improvement',
            'description': 'Improve content quality for better rankings',
            'priority': 'medium',
            'expected_impact': 'high'
        })
        
        # Build backlinks for authority
        strategies.append({
            'type': 'backlink_building',
            'description': 'Build quality backlinks to improve domain authority',
            'priority': 'medium',
            'expected_impact': 'high'
        })
        
        return strategies
    
    def _generate_traffic_strategies(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate traffic optimization strategies"""
        strategies = []
        
        # Optimize for high-traffic keywords
        strategies.append({
            'type': 'traffic_keywords',
            'description': 'Target high-traffic, low-competition keywords',
            'priority': 'high',
            'expected_impact': 'high'
        })
        
        # Improve click-through rates
        strategies.append({
            'type': 'ctr_optimization',
            'description': 'Optimize meta titles and descriptions for better CTR',
            'priority': 'medium',
            'expected_impact': 'medium'
        })
        
        # Expand keyword portfolio
        strategies.append({
            'type': 'keyword_expansion',
            'description': 'Add long-tail keywords to capture more traffic',
            'priority': 'low',
            'expected_impact': 'medium'
        })
        
        return strategies
    
    def _generate_conversion_strategies(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate conversion optimization strategies"""
        strategies = []
        
        # Optimize landing pages
        strategies.append({
            'type': 'landing_page_optimization',
            'description': 'Optimize landing pages for better conversions',
            'priority': 'high',
            'expected_impact': 'high'
        })
        
        # Improve user experience
        strategies.append({
            'type': 'ux_improvement',
            'description': 'Improve user experience to increase conversions',
            'priority': 'medium',
            'expected_impact': 'medium'
        })
        
        # Add call-to-action elements
        strategies.append({
            'type': 'cta_optimization',
            'description': 'Add and optimize call-to-action elements',
            'priority': 'medium',
            'expected_impact': 'medium'
        })
        
        return strategies
    
    def _generate_overall_strategies(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate overall performance strategies"""
        strategies = []
        
        # Comprehensive SEO audit
        strategies.append({
            'type': 'seo_audit',
            'description': 'Conduct comprehensive SEO audit',
            'priority': 'high',
            'expected_impact': 'high'
        })
        
        # Performance monitoring
        strategies.append({
            'type': 'performance_monitoring',
            'description': 'Implement continuous performance monitoring',
            'priority': 'medium',
            'expected_impact': 'medium'
        })
        
        # Competitor analysis
        strategies.append({
            'type': 'competitor_analysis',
            'description': 'Analyze and learn from competitors',
            'priority': 'medium',
            'expected_impact': 'medium'
        })
        
        return strategies
    
    def _apply_performance_optimizations(self, performance_data: List[Dict[str, Any]],
                                       strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply performance optimizations"""
        optimized_data = performance_data.copy()
        
        for strategy in strategies:
            if strategy['type'] == 'ranking_focus':
                optimized_data = self._apply_ranking_focus(optimized_data, strategy)
            elif strategy['type'] == 'content_improvement':
                optimized_data = self._apply_content_improvement(optimized_data)
            elif strategy['type'] == 'traffic_keywords':
                optimized_data = self._apply_traffic_optimization(optimized_data)
            elif strategy['type'] == 'ctr_optimization':
                optimized_data = self._apply_ctr_optimization(optimized_data)
        
        return self._calculate_current_performance(optimized_data)
    
    def _apply_ranking_focus(self, performance_data: List[Dict[str, Any]], 
                           strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply ranking focus optimization"""
        target_keywords = strategy.get('keywords', [])
        
        for data in performance_data:
            if data.get('keyword') in target_keywords:
                # Simulate ranking improvement
                current_rank = data.get('rank', 0)
                if current_rank > 10:
                    data['rank'] = max(1, current_rank - 3)  # Improve by 3 positions
        
        return performance_data
    
    def _apply_content_improvement(self, performance_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply content improvement optimization"""
        for data in performance_data:
            # Simulate content improvement effects
            current_rank = data.get('rank', 0)
            if current_rank > 5:
                data['rank'] = max(1, current_rank - 2)  # Improve by 2 positions
            
            # Increase traffic slightly
            current_traffic = data.get('traffic', 0)
            data['traffic'] = int(current_traffic * 1.1)  # 10% increase
        
        return performance_data
    
    def _apply_traffic_optimization(self, performance_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply traffic optimization"""
        for data in performance_data:
            # Simulate traffic improvement
            current_traffic = data.get('traffic', 0)
            data['traffic'] = int(current_traffic * 1.2)  # 20% increase
        
        return performance_data
    
    def _apply_ctr_optimization(self, performance_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply CTR optimization"""
        for data in performance_data:
            # Simulate CTR improvement
            current_ctr = data.get('ctr', 0)
            data['ctr'] = min(1.0, current_ctr * 1.15)  # 15% increase
        
        return performance_data
    
    def _predict_performance_improvements(self, analysis: Dict[str, Any],
                                        strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict performance improvements"""
        improvements = {
            'ranking_improvement': 0.0,
            'traffic_improvement': 0.0,
            'conversion_improvement': 0.0,
            'overall_improvement': 0.0
        }
        
        for strategy in strategies:
            strategy_type = strategy['type']
            expected_impact = strategy.get('expected_impact', 'medium')
            
            # Convert impact to numerical value
            impact_value = {'low': 0.05, 'medium': 0.15, 'high': 0.25}[expected_impact]
            
            if 'ranking' in strategy_type:
                improvements['ranking_improvement'] += impact_value
            elif 'traffic' in strategy_type:
                improvements['traffic_improvement'] += impact_value
            elif 'conversion' in strategy_type:
                improvements['conversion_improvement'] += impact_value
        
        # Cap improvements
        for key in improvements:
            improvements[key] = min(1.0, improvements[key])
        
        # Calculate overall improvement
        improvements['overall_improvement'] = (
            improvements['ranking_improvement'] * 0.4 +
            improvements['traffic_improvement'] * 0.4 +
            improvements['conversion_improvement'] * 0.2
        )
        
        return improvements
    
    def _generate_performance_recommendations(self, analysis: Dict[str, Any],
                                            strategies: List[Dict[str, Any]]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Issue-based recommendations
        for issue in analysis['issues']:
            recommendations.append(issue['recommendation'])
        
        # Strategy-based recommendations
        for strategy in strategies:
            if strategy['priority'] == 'high':
                recommendations.append(f"Prioritize: {strategy['description']}")
        
        # General recommendations
        if len(analysis['keyword_performance']['underperformers']) > 5:
            recommendations.append("Focus on improving underperforming keywords")
        
        if analysis['performance_trends'].get('ranking_trend') == 'decreasing':
            recommendations.append("Investigate and address ranking decline")
        
        recommendations.append("Monitor performance metrics regularly")
        recommendations.append("Implement A/B testing for optimization")
        
        return recommendations

# Example usage
performance_optimizer = PerformanceOptimizer()

# Sample performance data
sample_data = [
    {
        'keyword': 'python programming',
        'rank': 8,
        'traffic': 1500,
        'conversions': 25,
        'ctr': 0.08,
        'date': '2024-01-01'
    },
    {
        'keyword': 'machine learning',
        'rank': 15,
        'traffic': 800,
        'conversions': 12,
        'ctr': 0.06,
        'date': '2024-01-01'
    }
]

# Optimize performance
optimization_result = performance_optimizer.optimize_performance(
    sample_data, 
    optimization_goals=['ranking', 'traffic', 'conversion']
) 