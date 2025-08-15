# Predictive Competition Analysis using Machine Learning
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class CompetitionAnalyzer:
    def __init__(self):
        self.models = {
            'ranking_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
            'threat_classifier': RandomForestClassifier(n_estimators=100, random_state=42),
            'movement_predictor': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        self.scaler = StandardScaler()
        self.trained_models = {}
        self.competitor_profiles = {}
        self.threat_levels = {}
        
    def analyze_competitor_movements(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitor movements and predict future actions"""
        if not competitor_data:
            return {}
        
        # Analyze historical movements
        movement_analysis = self._analyze_historical_movements(competitor_data)
        
        # Predict future movements
        future_predictions = self._predict_future_movements(competitor_data)
        
        # Assess threat levels
        threat_assessment = self._assess_threat_levels(competitor_data)
        
        # Generate competitive insights
        competitive_insights = self._generate_competitive_insights(
            movement_analysis, future_predictions, threat_assessment
        )
        
        return {
            'movement_analysis': movement_analysis,
            'future_predictions': future_predictions,
            'threat_assessment': threat_assessment,
            'competitive_insights': competitive_insights
        }
    
    def _analyze_historical_movements(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze historical competitor movements"""
        df = pd.DataFrame(competitor_data)
        
        if 'date' not in df.columns or 'competitor' not in df.columns:
            return {}
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['competitor', 'date'])
        
        movement_patterns = {}
        
        for competitor in df['competitor'].unique():
            comp_data = df[df['competitor'] == competitor]
            
            if len(comp_data) < 2:
                continue
            
            # Calculate ranking changes
            comp_data = comp_data.sort_values('date')
            comp_data['ranking_change'] = comp_data['rank'].diff()
            
            # Analyze movement patterns
            patterns = {
                'total_movements': len(comp_data),
                'positive_movements': len(comp_data[comp_data['ranking_change'] > 0]),
                'negative_movements': len(comp_data[comp_data['ranking_change'] < 0]),
                'stable_periods': len(comp_data[comp_data['ranking_change'] == 0]),
                'avg_movement': comp_data['ranking_change'].mean(),
                'movement_volatility': comp_data['ranking_change'].std(),
                'best_rank': comp_data['rank'].min(),
                'worst_rank': comp_data['rank'].max(),
                'current_rank': comp_data['rank'].iloc[-1],
                'trend': self._calculate_competitor_trend(comp_data)
            }
            
            movement_patterns[competitor] = patterns
        
        return movement_patterns
    
    def _calculate_competitor_trend(self, comp_data: pd.DataFrame) -> str:
        """Calculate trend for a competitor"""
        if len(comp_data) < 3:
            return 'insufficient_data'
        
        # Calculate trend using linear regression
        x = np.arange(len(comp_data))
        y = comp_data['rank'].values
        
        slope = np.polyfit(x, y, 1)[0]
        
        if slope < -0.5:
            return 'improving'
        elif slope > 0.5:
            return 'declining'
        else:
            return 'stable'
    
    def _predict_future_movements(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future competitor movements"""
        df = pd.DataFrame(competitor_data)
        
        if 'date' not in df.columns or 'competitor' not in df.columns:
            return {}
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['competitor', 'date'])
        
        future_predictions = {}
        
        for competitor in df['competitor'].unique():
            comp_data = df[df['competitor'] == competitor]
            
            if len(comp_data) < 7:  # Need at least a week of data
                continue
            
            # Prepare features for prediction
            features = self._prepare_competitor_features(comp_data)
            
            if features is not None:
                # Predict next ranking
                predicted_rank = self._predict_next_ranking(features)
                
                # Predict movement direction
                movement_direction = self._predict_movement_direction(features)
                
                # Calculate confidence
                confidence = self._calculate_prediction_confidence(features)
                
                future_predictions[competitor] = {
                    'predicted_rank': predicted_rank,
                    'movement_direction': movement_direction,
                    'confidence': confidence,
                    'prediction_date': (datetime.now() + timedelta(days=7)).isoformat()
                }
        
        return future_predictions
    
    def _prepare_competitor_features(self, comp_data: pd.DataFrame) -> Optional[List[float]]:
        """Prepare features for competitor prediction"""
        try:
            # Calculate various features
            current_rank = comp_data['rank'].iloc[-1]
            avg_rank = comp_data['rank'].mean()
            rank_std = comp_data['rank'].std()
            
            # Recent trend
            recent_data = comp_data.tail(7)
            recent_trend = np.polyfit(range(len(recent_data)), recent_data['rank'], 1)[0]
            
            # Movement frequency
            ranking_changes = comp_data['rank'].diff().dropna()
            movement_frequency = len(ranking_changes[ranking_changes != 0]) / len(ranking_changes)
            
            # Volatility
            volatility = ranking_changes.std()
            
            # Domain authority (if available)
            domain_authority = comp_data.get('domain_authority', 50).iloc[-1]
            
            # Content activity (if available)
            content_activity = comp_data.get('content_updates', 0).iloc[-1]
            
            features = [
                current_rank,
                avg_rank,
                rank_std,
                recent_trend,
                movement_frequency,
                volatility,
                domain_authority,
                content_activity,
                len(comp_data)  # Data points available
            ]
            
            return features
            
        except Exception as e:
            print(f"Error preparing competitor features: {e}")
            return None
    
    def _predict_next_ranking(self, features: List[float]) -> int:
        """Predict next ranking for competitor"""
        # Simplified prediction using feature-based logic
        current_rank, avg_rank, rank_std, recent_trend, movement_freq, volatility, domain_auth, content_activity, data_points = features
        
        # Base prediction on current rank and trend
        base_prediction = current_rank + recent_trend * 7  # 7 days ahead
        
        # Adjust based on domain authority
        authority_adjustment = (domain_auth - 50) / 100  # -0.5 to 0.5
        base_prediction -= authority_adjustment * 2
        
        # Adjust based on content activity
        activity_adjustment = content_activity / 10  # Normalize
        base_prediction -= activity_adjustment
        
        # Add some randomness based on volatility
        random_factor = np.random.normal(0, volatility)
        base_prediction += random_factor
        
        return max(1, int(base_prediction))
    
    def _predict_movement_direction(self, features: List[float]) -> str:
        """Predict movement direction"""
        current_rank, avg_rank, rank_std, recent_trend, movement_freq, volatility, domain_auth, content_activity, data_points = features
        
        # Determine direction based on trend and factors
        if recent_trend < -0.5:
            return 'improving'
        elif recent_trend > 0.5:
            return 'declining'
        elif domain_auth > 70 and content_activity > 5:
            return 'improving'
        elif domain_auth < 30:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_prediction_confidence(self, features: List[float]) -> float:
        """Calculate confidence in prediction"""
        current_rank, avg_rank, rank_std, recent_trend, movement_freq, volatility, domain_auth, content_activity, data_points = features
        
        # Base confidence
        confidence = 0.7
        
        # Adjust based on data quality
        if data_points >= 30:
            confidence += 0.1
        elif data_points < 7:
            confidence -= 0.2
        
        # Adjust based on volatility
        if volatility < 1:
            confidence += 0.1
        elif volatility > 5:
            confidence -= 0.1
        
        # Adjust based on domain authority
        if domain_auth > 80:
            confidence += 0.1
        elif domain_auth < 20:
            confidence -= 0.1
        
        return max(0.1, min(1.0, confidence))
    
    def _assess_threat_levels(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess threat levels for each competitor"""
        df = pd.DataFrame(competitor_data)
        
        if 'competitor' not in df.columns:
            return {}
        
        threat_assessment = {}
        
        for competitor in df['competitor'].unique():
            comp_data = df[df['competitor'] == competitor]
            
            # Calculate threat factors
            current_rank = comp_data['rank'].iloc[-1] if len(comp_data) > 0 else 100
            domain_authority = comp_data.get('domain_authority', 50).iloc[-1] if len(comp_data) > 0 else 50
            content_activity = comp_data.get('content_updates', 0).iloc[-1] if len(comp_data) > 0 else 0
            
            # Calculate threat score
            threat_score = self._calculate_threat_score(current_rank, domain_authority, content_activity)
            
            # Determine threat level
            if threat_score > 0.7:
                threat_level = 'high'
            elif threat_score > 0.4:
                threat_level = 'medium'
            else:
                threat_level = 'low'
            
            threat_assessment[competitor] = {
                'threat_score': threat_score,
                'threat_level': threat_level,
                'current_rank': current_rank,
                'domain_authority': domain_authority,
                'content_activity': content_activity,
                'risk_factors': self._identify_risk_factors(current_rank, domain_authority, content_activity)
            }
        
        return threat_assessment
    
    def _calculate_threat_score(self, current_rank: int, domain_authority: float, content_activity: int) -> float:
        """Calculate threat score for a competitor"""
        # Rank factor (lower rank = higher threat)
        rank_factor = max(0, (100 - current_rank) / 100)
        
        # Authority factor (higher authority = higher threat)
        authority_factor = domain_authority / 100
        
        # Activity factor (higher activity = higher threat)
        activity_factor = min(1.0, content_activity / 10)
        
        # Weighted combination
        threat_score = (rank_factor * 0.4 + authority_factor * 0.4 + activity_factor * 0.2)
        
        return min(1.0, threat_score)
    
    def _identify_risk_factors(self, current_rank: int, domain_authority: float, content_activity: int) -> List[str]:
        """Identify risk factors for a competitor"""
        risk_factors = []
        
        if current_rank <= 5:
            risk_factors.append("High ranking position")
        
        if domain_authority > 80:
            risk_factors.append("High domain authority")
        
        if content_activity > 5:
            risk_factors.append("High content activity")
        
        if current_rank <= 10 and domain_authority > 70:
            risk_factors.append("Strong competitive position")
        
        return risk_factors
    
    def _generate_competitive_insights(self, movement_analysis: Dict[str, Any],
                                    future_predictions: Dict[str, Any],
                                    threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate competitive insights"""
        insights = {
            'key_competitors': [],
            'emerging_threats': [],
            'declining_competitors': [],
            'strategic_recommendations': [],
            'market_dynamics': {}
        }
        
        # Identify key competitors
        for competitor, threat_data in threat_assessment.items():
            if threat_data['threat_level'] == 'high':
                insights['key_competitors'].append({
                    'competitor': competitor,
                    'threat_score': threat_data['threat_score'],
                    'current_rank': threat_data['current_rank']
                })
        
        # Identify emerging threats
        for competitor, prediction in future_predictions.items():
            if prediction['movement_direction'] == 'improving' and prediction['confidence'] > 0.6:
                insights['emerging_threats'].append({
                    'competitor': competitor,
                    'predicted_rank': prediction['predicted_rank'],
                    'confidence': prediction['confidence']
                })
        
        # Identify declining competitors
        for competitor, prediction in future_predictions.items():
            if prediction['movement_direction'] == 'declining' and prediction['confidence'] > 0.6:
                insights['declining_competitors'].append({
                    'competitor': competitor,
                    'predicted_rank': prediction['predicted_rank'],
                    'confidence': prediction['confidence']
                })
        
        # Generate strategic recommendations
        insights['strategic_recommendations'] = self._generate_strategic_recommendations(
            movement_analysis, future_predictions, threat_assessment
        )
        
        # Analyze market dynamics
        insights['market_dynamics'] = self._analyze_market_dynamics(
            movement_analysis, future_predictions, threat_assessment
        )
        
        return insights
    
    def _generate_strategic_recommendations(self, movement_analysis: Dict[str, Any],
                                         future_predictions: Dict[str, Any],
                                         threat_assessment: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        # Count high-threat competitors
        high_threat_count = sum(1 for data in threat_assessment.values() if data['threat_level'] == 'high')
        
        if high_threat_count > 3:
            recommendations.append("Focus on differentiation to stand out from strong competitors")
        
        # Check for emerging threats
        emerging_threats = [p for p in future_predictions.values() if p['movement_direction'] == 'improving']
        if emerging_threats:
            recommendations.append("Monitor and respond to emerging competitive threats")
        
        # Check for opportunities
        declining_competitors = [p for p in future_predictions.values() if p['movement_direction'] == 'declining']
        if declining_competitors:
            recommendations.append("Capitalize on declining competitors' weaknesses")
        
        recommendations.append("Continuously monitor competitor movements and adapt strategy")
        recommendations.append("Focus on unique value propositions and content quality")
        
        return recommendations
    
    def _analyze_market_dynamics(self, movement_analysis: Dict[str, Any],
                               future_predictions: Dict[str, Any],
                               threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall market dynamics"""
        # Calculate market concentration
        threat_scores = [data['threat_score'] for data in threat_assessment.values()]
        market_concentration = np.mean(threat_scores) if threat_scores else 0
        
        # Calculate competitive intensity
        improving_count = sum(1 for p in future_predictions.values() if p['movement_direction'] == 'improving')
        declining_count = sum(1 for p in future_predictions.values() if p['movement_direction'] == 'declining')
        
        competitive_intensity = 'high' if improving_count > len(future_predictions) / 2 else 'medium'
        
        # Determine market phase
        if improving_count > declining_count:
            market_phase = 'growth'
        elif declining_count > improving_count:
            market_phase = 'consolidation'
        else:
            market_phase = 'stable'
        
        return {
            'market_concentration': market_concentration,
            'competitive_intensity': competitive_intensity,
            'market_phase': market_phase,
            'improving_competitors': improving_count,
            'declining_competitors': declining_count,
            'total_competitors': len(threat_assessment)
        }

# Example usage
competition_analyzer = CompetitionAnalyzer()

# Sample competitor data
sample_data = [
    {
        'date': '2024-01-01',
        'competitor': 'competitor_a',
        'rank': 5,
        'domain_authority': 85,
        'content_updates': 3
    },
    # ... more data points
]

# Analyze competition
analysis_result = competition_analyzer.analyze_competitor_movements(sample_data) 