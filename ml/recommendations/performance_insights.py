# Performance Insights
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, timedelta

class PerformanceInsights:
    def __init__(self):
        self.performance_data = {}
        self.benchmarks = {}
        self.insights_history = []
        
    def add_performance_data(self, keyword: str, data: List[Dict[str, Any]]) -> None:
        """Add performance data for analysis"""
        self.performance_data[keyword] = data
        
    def generate_insights(self, keyword: str) -> Dict[str, Any]:
        """Generate comprehensive performance insights"""
        if keyword not in self.performance_data:
            return {}
        
        data = self.performance_data[keyword]
        if len(data) < 7:  # Need at least a week of data
            return {}
        
        insights = {
            'keyword': keyword,
            'overall_performance': self._analyze_overall_performance(data),
            'trend_analysis': self._analyze_trends(data),
            'competitive_analysis': self._analyze_competition(data),
            'opportunity_analysis': self._analyze_opportunities(data),
            'recommendations': self._generate_recommendations(data),
            'risk_assessment': self._assess_risks(data)
        }
        
        # Store insights for historical analysis
        self.insights_history.append({
            'keyword': keyword,
            'timestamp': datetime.now(),
            'insights': insights
        })
        
        return insights
    
    def _analyze_overall_performance(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall performance metrics"""
        search_volumes = [entry.get('search_volume', 0) for entry in data]
        rankings = [entry.get('rank', 0) for entry in data]
        click_through_rates = [entry.get('ctr', 0) for entry in data]
        
        return {
            'average_search_volume': np.mean(search_volumes),
            'search_volume_trend': self._calculate_trend(search_volumes),
            'average_ranking': np.mean(rankings),
            'ranking_trend': self._calculate_trend(rankings),
            'average_ctr': np.mean(click_through_rates),
            'ctr_trend': self._calculate_trend(click_through_rates),
            'performance_score': self._calculate_performance_score(data)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "stable"
        
        # Calculate linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_performance_score(self, data: List[Dict[str, Any]]) -> float:
        """Calculate overall performance score"""
        if not data:
            return 0.0
        
        # Normalize metrics
        avg_volume = np.mean([entry.get('search_volume', 0) for entry in data])
        avg_rank = np.mean([entry.get('rank', 0) for entry in data])
        avg_ctr = np.mean([entry.get('ctr', 0) for entry in data])
        
        # Score components (0-100 scale)
        volume_score = min(100, avg_volume / 1000 * 100)  # Normalize to 1000 searches
        rank_score = max(0, 100 - avg_rank * 2)  # Better rank = higher score
        ctr_score = min(100, avg_ctr * 100)  # CTR as percentage
        
        # Weighted average
        performance_score = (volume_score * 0.4 + rank_score * 0.4 + ctr_score * 0.2)
        
        return max(0.0, min(100.0, performance_score))
    
    def _analyze_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends"""
        # Weekly trends
        weekly_trends = self._calculate_weekly_trends(data)
        
        # Seasonal patterns
        seasonal_patterns = self._analyze_seasonal_patterns(data)
        
        # Volatility analysis
        volatility = self._calculate_volatility(data)
        
        return {
            'weekly_trends': weekly_trends,
            'seasonal_patterns': seasonal_patterns,
            'volatility': volatility,
            'trend_stability': self._assess_trend_stability(data)
        }
    
    def _calculate_weekly_trends(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate weekly performance trends"""
        # Group by day of week
        daily_data = {}
        for entry in data:
            day = entry.get('day_of_week', 0)
            volume = entry.get('search_volume', 0)
            
            if day not in daily_data:
                daily_data[day] = []
            daily_data[day].append(volume)
        
        # Calculate average for each day
        weekly_trends = {}
        for day, volumes in daily_data.items():
            weekly_trends[f'day_{day}'] = np.mean(volumes)
        
        return weekly_trends
    
    def _analyze_seasonal_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze seasonal performance patterns"""
        # Group by month
        monthly_data = {}
        for entry in data:
            month = entry.get('month', 0)
            volume = entry.get('search_volume', 0)
            
            if month not in monthly_data:
                monthly_data[month] = []
            monthly_data[month].append(volume)
        
        # Calculate monthly averages
        monthly_averages = {}
        for month, volumes in monthly_data.items():
            monthly_averages[f'month_{month}'] = np.mean(volumes)
        
        return {
            'monthly_patterns': monthly_averages,
            'peak_month': max(monthly_averages, key=monthly_averages.get) if monthly_averages else None,
            'low_month': min(monthly_averages, key=monthly_averages.get) if monthly_averages else None
        }
    
    def _calculate_volatility(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate performance volatility"""
        volumes = [entry.get('search_volume', 0) for entry in data]
        rankings = [entry.get('rank', 0) for entry in data]
        
        return {
            'volume_volatility': np.std(volumes) / np.mean(volumes) if np.mean(volumes) > 0 else 0,
            'ranking_volatility': np.std(rankings) / np.mean(rankings) if np.mean(rankings) > 0 else 0
        }
    
    def _assess_trend_stability(self, data: List[Dict[str, Any]]) -> str:
        """Assess the stability of performance trends"""
        volumes = [entry.get('search_volume', 0) for entry in data]
        
        if len(volumes) < 2:
            return "insufficient_data"
        
        # Calculate coefficient of variation
        cv = np.std(volumes) / np.mean(volumes) if np.mean(volumes) > 0 else 0
        
        if cv < 0.2:
            return "very_stable"
        elif cv < 0.5:
            return "stable"
        elif cv < 1.0:
            return "moderate"
        else:
            return "volatile"
    
    def _analyze_competition(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        competition_levels = [entry.get('competition', 0) for entry in data]
        
        return {
            'average_competition': np.mean(competition_levels),
            'competition_trend': self._calculate_trend(competition_levels),
            'competitive_intensity': self._assess_competitive_intensity(competition_levels),
            'market_share_opportunity': self._calculate_market_share_opportunity(data)
        }
    
    def _assess_competitive_intensity(self, competition_levels: List[float]) -> str:
        """Assess competitive intensity"""
        avg_competition = np.mean(competition_levels)
        
        if avg_competition < 0.3:
            return "low"
        elif avg_competition < 0.7:
            return "medium"
        else:
            return "high"
    
    def _calculate_market_share_opportunity(self, data: List[Dict[str, Any]]) -> float:
        """Calculate market share opportunity"""
        volumes = [entry.get('search_volume', 0) for entry in data]
        rankings = [entry.get('rank', 0) for entry in data]
        
        if not volumes or not rankings:
            return 0.0
        
        avg_volume = np.mean(volumes)
        avg_rank = np.mean(rankings)
        
        # Opportunity based on current rank and volume
        if avg_rank <= 3:
            opportunity = 0.1  # Limited opportunity at top
        elif avg_rank <= 10:
            opportunity = 0.3  # Moderate opportunity
        else:
            opportunity = 0.8  # High opportunity
        
        # Adjust for volume
        if avg_volume > 10000:
            opportunity *= 1.5  # High volume = higher opportunity
        
        return min(1.0, opportunity)
    
    def _analyze_opportunities(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze growth opportunities"""
        return {
            'quick_wins': self._identify_quick_wins(data),
            'long_term_opportunities': self._identify_long_term_opportunities(data),
            'untapped_potential': self._calculate_untapped_potential(data),
            'optimization_priority': self._determine_optimization_priority(data)
        }
    
    def _identify_quick_wins(self, data: List[Dict[str, Any]]) -> List[str]:
        """Identify quick win opportunities"""
        quick_wins = []
        
        # Check for low-hanging fruit
        avg_rank = np.mean([entry.get('rank', 0) for entry in data])
        avg_volume = np.mean([entry.get('search_volume', 0) for entry in data])
        
        if avg_rank > 10 and avg_volume > 1000:
            quick_wins.append("Improve on-page SEO for better rankings")
        
        if avg_volume < 500:
            quick_wins.append("Target long-tail keyword variations")
        
        return quick_wins
    
    def _identify_long_term_opportunities(self, data: List[Dict[str, Any]]) -> List[str]:
        """Identify long-term growth opportunities"""
        opportunities = []
        
        # Analyze trends for opportunities
        volume_trend = self._calculate_trend([entry.get('search_volume', 0) for entry in data])
        
        if volume_trend == "increasing":
            opportunities.append("Expand content around trending topics")
        
        opportunities.append("Build authority through comprehensive content")
        opportunities.append("Develop link building strategy")
        
        return opportunities
    
    def _calculate_untapped_potential(self, data: List[Dict[str, Any]]) -> float:
        """Calculate untapped potential"""
        current_performance = self._calculate_performance_score(data)
        
        # Estimate potential based on current performance
        if current_performance < 30:
            potential = 0.8  # High potential for improvement
        elif current_performance < 60:
            potential = 0.5  # Moderate potential
        else:
            potential = 0.2  # Limited potential
        
        return potential
    
    def _determine_optimization_priority(self, data: List[Dict[str, Any]]) -> str:
        """Determine optimization priority"""
        performance_score = self._calculate_performance_score(data)
        competition = np.mean([entry.get('competition', 0) for entry in data])
        
        if performance_score < 30:
            return "high"
        elif performance_score < 60 or competition > 0.7:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Performance-based recommendations
        performance_score = self._calculate_performance_score(data)
        
        if performance_score < 50:
            recommendations.append({
                'type': 'immediate',
                'action': 'Focus on basic SEO optimization',
                'priority': 'high',
                'expected_impact': 'medium',
                'timeline': '2-4 weeks'
            })
        
        # Trend-based recommendations
        volume_trend = self._calculate_trend([entry.get('search_volume', 0) for entry in data])
        
        if volume_trend == "decreasing":
            recommendations.append({
                'type': 'strategic',
                'action': 'Investigate declining search volume and adjust strategy',
                'priority': 'high',
                'expected_impact': 'high',
                'timeline': '1-2 months'
            })
        
        return recommendations
    
    def _assess_risks(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess performance risks"""
        risks = []
        risk_level = "low"
        
        # Check for declining trends
        volume_trend = self._calculate_trend([entry.get('search_volume', 0) for entry in data])
        if volume_trend == "decreasing":
            risks.append("Declining search volume")
            risk_level = "medium"
        
        # Check for high volatility
        volatility = self._calculate_volatility(data)
        if volatility['volume_volatility'] > 0.5:
            risks.append("High performance volatility")
            risk_level = "medium"
        
        # Check for competitive threats
        competition_trend = self._calculate_trend([entry.get('competition', 0) for entry in data])
        if competition_trend == "increasing":
            risks.append("Increasing competition")
            risk_level = "high"
        
        return {
            'risk_level': risk_level,
            'identified_risks': risks,
            'mitigation_strategies': self._generate_mitigation_strategies(risks)
        }
    
    def _generate_mitigation_strategies(self, risks: List[str]) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = []
        
        for risk in risks:
            if "declining" in risk.lower():
                strategies.append("Monitor search trends and adapt content strategy")
            elif "volatility" in risk.lower():
                strategies.append("Implement more consistent content publishing schedule")
            elif "competition" in risk.lower():
                strategies.append("Strengthen unique value proposition and content quality")
        
        return strategies

# Example usage
performance_insights = PerformanceInsights()

# Add sample performance data
sample_data = [
    {'date': '2024-01-01', 'search_volume': 1000, 'rank': 5, 'ctr': 0.05, 'competition': 0.3, 'day_of_week': 0, 'month': 1},
    {'date': '2024-01-02', 'search_volume': 1100, 'rank': 4, 'ctr': 0.06, 'competition': 0.3, 'day_of_week': 1, 'month': 1},
    # ... more data points
]

performance_insights.add_performance_data("python programming", sample_data) 