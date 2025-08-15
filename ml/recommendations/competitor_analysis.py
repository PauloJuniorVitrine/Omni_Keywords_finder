# Competitor Analysis
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, timedelta

class CompetitorAnalysis:
    def __init__(self):
        self.competitors = {}
        self.analysis_data = {}
        
    def add_competitor(self, name: str, domain: str, keywords: List[str]) -> None:
        """Add a competitor to track"""
        self.competitors[name] = {
            'domain': domain,
            'keywords': keywords,
            'rankings': {},
            'traffic_estimates': {},
            'content_analysis': {},
            'last_updated': datetime.now()
        }
    
    def analyze_competitor_keywords(self, competitor_name: str) -> Dict[str, Any]:
        """Analyze competitor's keyword strategy"""
        if competitor_name not in self.competitors:
            return {}
        
        competitor = self.competitors[competitor_name]
        keywords = competitor['keywords']
        
        analysis = {
            'total_keywords': len(keywords),
            'keyword_categories': self._categorize_keywords(keywords),
            'keyword_difficulty_distribution': self._analyze_difficulty_distribution(keywords),
            'search_volume_analysis': self._analyze_search_volume(keywords),
            'ranking_opportunities': self._find_ranking_opportunities(keywords)
        }
        
        return analysis
    
    def _categorize_keywords(self, keywords: List[str]) -> Dict[str, int]:
        """Categorize keywords by type"""
        categories = {
            'informational': 0,
            'transactional': 0,
            'navigational': 0,
            'long_tail': 0
        }
        
        for keyword in keywords:
            if any(word in keyword.lower() for word in ['how', 'what', 'why', 'guide', 'tips']):
                categories['informational'] += 1
            elif any(word in keyword.lower() for word in ['buy', 'price', 'cost', 'purchase']):
                categories['transactional'] += 1
            elif any(word in keyword.lower() for word in ['brand', 'company', 'official']):
                categories['navigational'] += 1
            else:
                categories['long_tail'] += 1
        
        return categories
    
    def _analyze_difficulty_distribution(self, keywords: List[str]) -> Dict[str, int]:
        """Analyze keyword difficulty distribution"""
        difficulties = {
            'easy': 0,
            'medium': 0,
            'hard': 0
        }
        
        for keyword in keywords:
            difficulty = self._calculate_keyword_difficulty(keyword)
            if difficulty < 0.4:
                difficulties['easy'] += 1
            elif difficulty < 0.7:
                difficulties['medium'] += 1
            else:
                difficulties['hard'] += 1
        
        return difficulties
    
    def _calculate_keyword_difficulty(self, keyword: str) -> float:
        """Calculate keyword difficulty score"""
        # Simulated difficulty calculation
        base_difficulty = len(keyword.split()) * 0.2
        competition_factor = np.random.uniform(0.1, 0.8)
        return min(1.0, base_difficulty + competition_factor)
    
    def _analyze_search_volume(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyze search volume patterns"""
        volumes = [self._estimate_search_volume(keyword) for keyword in keywords]
        
        return {
            'total_volume': sum(volumes),
            'average_volume': np.mean(volumes),
            'high_volume_keywords': [kw for kw, vol in zip(keywords, volumes) if vol > 10000],
            'low_volume_keywords': [kw for kw, vol in zip(keywords, volumes) if vol < 1000]
        }
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume for a keyword"""
        # Simulated search volume
        base_volume = len(keyword) * 200
        random_factor = np.random.uniform(0.3, 3.0)
        return int(base_volume * random_factor)
    
    def _find_ranking_opportunities(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Find ranking opportunities"""
        opportunities = []
        
        for keyword in keywords:
            difficulty = self._calculate_keyword_difficulty(keyword)
            volume = self._estimate_search_volume(keyword)
            
            # Calculate opportunity score
            opportunity_score = volume * (1 - difficulty)
            
            if opportunity_score > 5000:  # Threshold for good opportunity
                opportunities.append({
                    'keyword': keyword,
                    'difficulty': difficulty,
                    'search_volume': volume,
                    'opportunity_score': opportunity_score
                })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        return opportunities
    
    def compare_competitors(self, competitors: List[str]) -> Dict[str, Any]:
        """Compare multiple competitors"""
        comparison = {
            'keyword_overlap': self._find_keyword_overlap(competitors),
            'strength_analysis': self._analyze_competitor_strengths(competitors),
            'weakness_analysis': self._analyze_competitor_weaknesses(competitors),
            'opportunity_gaps': self._find_opportunity_gaps(competitors)
        }
        
        return comparison
    
    def _find_keyword_overlap(self, competitors: List[str]) -> Dict[str, List[str]]:
        """Find overlapping keywords between competitors"""
        all_keywords = {}
        
        for competitor in competitors:
            if competitor in self.competitors:
                keywords = self.competitors[competitor]['keywords']
                for keyword in keywords:
                    if keyword not in all_keywords:
                        all_keywords[keyword] = []
                    all_keywords[keyword].append(competitor)
        
        # Find keywords used by multiple competitors
        overlap = {keyword: comps for keyword, comps in all_keywords.items() if len(comps) > 1}
        return overlap
    
    def _analyze_competitor_strengths(self, competitors: List[str]) -> Dict[str, List[str]]:
        """Analyze each competitor's strengths"""
        strengths = {}
        
        for competitor in competitors:
            if competitor in self.competitors:
                keywords = self.competitors[competitor]['keywords']
                strengths[competitor] = [
                    kw for kw in keywords 
                    if self._estimate_search_volume(kw) > 5000 and 
                    self._calculate_keyword_difficulty(kw) < 0.5
                ]
        
        return strengths
    
    def _analyze_competitor_weaknesses(self, competitors: List[str]) -> Dict[str, List[str]]:
        """Analyze each competitor's weaknesses"""
        weaknesses = {}
        
        for competitor in competitors:
            if competitor in self.competitors:
                keywords = self.competitors[competitor]['keywords']
                weaknesses[competitor] = [
                    kw for kw in keywords 
                    if self._estimate_search_volume(kw) < 1000 or 
                    self._calculate_keyword_difficulty(kw) > 0.8
                ]
        
        return weaknesses
    
    def _find_opportunity_gaps(self, competitors: List[str]) -> List[str]:
        """Find keyword opportunities that competitors are missing"""
        all_competitor_keywords = set()
        
        for competitor in competitors:
            if competitor in self.competitors:
                all_competitor_keywords.update(self.competitors[competitor]['keywords'])
        
        # This would typically compare against a broader keyword database
        # For now, return some sample opportunities
        potential_opportunities = [
            "emerging technology trends",
            "new programming languages",
            "future of AI",
            "blockchain development",
            "quantum computing basics"
        ]
        
        return [opp for opp in potential_opportunities if opp not in all_competitor_keywords]

# Example usage
competitor_analysis = CompetitorAnalysis()

# Add sample competitors
competitor_analysis.add_competitor(
    "TechCorp", 
    "techcorp.com", 
    ["python programming", "machine learning", "web development"]
)

competitor_analysis.add_competitor(
    "CodeMaster", 
    "codemaster.com", 
    ["javascript", "react", "node.js", "python programming"]
) 