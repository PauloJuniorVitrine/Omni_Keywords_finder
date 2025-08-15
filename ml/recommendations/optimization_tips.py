# Optimization Tips
from typing import List, Dict, Any, Optional
import numpy as np

class OptimizationTips:
    def __init__(self):
        self.tip_categories = {
            'content': [],
            'technical': [],
            'on_page': [],
            'off_page': [],
            'user_experience': []
        }
        self.user_profile = {}
        
    def generate_tips(self, keyword: str, current_rank: int, target_rank: int) -> List[Dict[str, Any]]:
        """Generate optimization tips based on current performance"""
        tips = []
        
        # Analyze current situation
        rank_gap = current_rank - target_rank
        difficulty = self._assess_optimization_difficulty(keyword, current_rank)
        
        # Generate content tips
        content_tips = self._generate_content_tips(keyword, rank_gap)
        tips.extend(content_tips)
        
        # Generate technical tips
        technical_tips = self._generate_technical_tips(keyword, difficulty)
        tips.extend(technical_tips)
        
        # Generate on-page tips
        on_page_tips = self._generate_on_page_tips(keyword, current_rank)
        tips.extend(on_page_tips)
        
        # Generate off-page tips
        off_page_tips = self._generate_off_page_tips(keyword, difficulty)
        tips.extend(off_page_tips)
        
        # Generate UX tips
        ux_tips = self._generate_ux_tips(keyword)
        tips.extend(ux_tips)
        
        # Prioritize tips
        prioritized_tips = self._prioritize_tips(tips, rank_gap, difficulty)
        
        return prioritized_tips
    
    def _assess_optimization_difficulty(self, keyword: str, current_rank: int) -> str:
        """Assess the difficulty of optimization"""
        if current_rank <= 3:
            return "hard"
        elif current_rank <= 10:
            return "medium"
        else:
            return "easy"
    
    def _generate_content_tips(self, keyword: str, rank_gap: int) -> List[Dict[str, Any]]:
        """Generate content optimization tips"""
        tips = []
        
        # Content length tip
        if rank_gap > 5:
            tips.append({
                'category': 'content',
                'tip': f"Create comprehensive content about '{keyword}' (aim for 2000+ words)",
                'priority': 'high',
                'effort': 'medium',
                'impact': 'high',
                'reasoning': 'Longer content tends to rank better for competitive keywords'
            })
        
        # Content freshness tip
        tips.append({
            'category': 'content',
            'tip': f"Update content about '{keyword}' regularly with fresh information",
            'priority': 'medium',
            'effort': 'low',
            'impact': 'medium',
            'reasoning': 'Fresh content signals relevance to search engines'
        })
        
        # Content structure tip
        tips.append({
            'category': 'content',
            'tip': f"Use proper heading structure (H1, H2, H3) for '{keyword}' content",
            'priority': 'high',
            'effort': 'low',
            'impact': 'high',
            'reasoning': 'Proper heading structure helps search engines understand content hierarchy'
        })
        
        return tips
    
    def _generate_technical_tips(self, keyword: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate technical optimization tips"""
        tips = []
        
        # Page speed tip
        tips.append({
            'category': 'technical',
            'tip': 'Optimize page loading speed (aim for under 3 seconds)',
            'priority': 'high',
            'effort': 'medium',
            'impact': 'high',
            'reasoning': 'Page speed is a direct ranking factor'
        })
        
        # Mobile optimization tip
        tips.append({
            'category': 'technical',
            'tip': 'Ensure mobile-friendly design and responsive layout',
            'priority': 'high',
            'effort': 'medium',
            'impact': 'high',
            'reasoning': 'Mobile-first indexing prioritizes mobile experience'
        })
        
        # Schema markup tip
        if difficulty == 'hard':
            tips.append({
                'category': 'technical',
                'tip': f"Implement structured data markup for '{keyword}' content",
                'priority': 'medium',
                'effort': 'low',
                'impact': 'medium',
                'reasoning': 'Schema markup can improve rich snippet opportunities'
            })
        
        return tips
    
    def _generate_on_page_tips(self, keyword: str, current_rank: int) -> List[Dict[str, Any]]:
        """Generate on-page optimization tips"""
        tips = []
        
        # Title optimization tip
        tips.append({
            'category': 'on_page',
            'tip': f"Optimize page title to include '{keyword}' naturally",
            'priority': 'high',
            'effort': 'low',
            'impact': 'high',
            'reasoning': 'Title tags are crucial for SEO ranking'
        })
        
        # Meta description tip
        tips.append({
            'category': 'on_page',
            'tip': f"Write compelling meta description with '{keyword}'",
            'priority': 'medium',
            'effort': 'low',
            'impact': 'medium',
            'reasoning': 'Meta descriptions influence click-through rates'
        })
        
        # URL optimization tip
        tips.append({
            'category': 'on_page',
            'tip': f"Use clean, keyword-rich URLs for '{keyword}' pages",
            'priority': 'medium',
            'effort': 'low',
            'impact': 'medium',
            'reasoning': 'URL structure affects both ranking and user experience'
        })
        
        return tips
    
    def _generate_off_page_tips(self, keyword: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate off-page optimization tips"""
        tips = []
        
        # Link building tip
        if difficulty in ['medium', 'hard']:
            tips.append({
                'category': 'off_page',
                'tip': f"Build high-quality backlinks related to '{keyword}'",
                'priority': 'high',
                'effort': 'high',
                'impact': 'high',
                'reasoning': 'Backlinks are a major ranking factor for competitive keywords'
            })
        
        # Social signals tip
        tips.append({
            'category': 'off_page',
            'tip': f"Promote '{keyword}' content on social media platforms',
            'priority': 'medium',
            'effort': 'low',
            'impact': 'medium',
            'reasoning': 'Social signals can indirectly impact search rankings'
        })
        
        # Brand mentions tip
        tips.append({
            'category': 'off_page',
            'tip': 'Encourage brand mentions and citations',
            'priority': 'medium',
            'effort': 'medium',
            'impact': 'medium',
            'reasoning': 'Brand mentions contribute to domain authority'
        })
        
        return tips
    
    def _generate_ux_tips(self, keyword: str) -> List[Dict[str, Any]]:
        """Generate user experience optimization tips"""
        tips = []
        
        # Internal linking tip
        tips.append({
            'category': 'user_experience',
            'tip': f"Create internal links to related '{keyword}' content",
            'priority': 'medium',
            'effort': 'low',
            'impact': 'medium',
            'reasoning': 'Internal linking improves site structure and user navigation'
        })
        
        # User engagement tip
        tips.append({
            'category': 'user_experience',
            'tip': 'Add interactive elements to increase user engagement',
            'priority': 'medium',
            'effort': 'medium',
            'impact': 'medium',
            'reasoning': 'Higher engagement signals content quality to search engines'
        })
        
        # Readability tip
        tips.append({
            'category': 'user_experience',
            'tip': 'Improve content readability with clear formatting',
            'priority': 'high',
            'effort': 'low',
            'impact': 'high',
            'reasoning': 'Readable content keeps users on page longer'
        })
        
        return tips
    
    def _prioritize_tips(self, tips: List[Dict[str, Any]], rank_gap: int, difficulty: str) -> List[Dict[str, Any]]:
        """Prioritize tips based on impact and effort"""
        for tip in tips:
            # Calculate priority score
            impact_scores = {'low': 1, 'medium': 2, 'high': 3}
            effort_scores = {'low': 3, 'medium': 2, 'high': 1}
            
            impact_score = impact_scores.get(tip['impact'], 2)
            effort_score = effort_scores.get(tip['effort'], 2)
            
            # Adjust for rank gap and difficulty
            if rank_gap > 10:
                impact_score *= 1.2  # Higher impact for bigger gaps
            if difficulty == 'easy':
                effort_score *= 1.1  # Slightly higher effort score for easy wins
            
            tip['priority_score'] = impact_score * effort_score
        
        # Sort by priority score
        tips.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return tips
    
    def get_personalized_tips(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get personalized optimization tips based on user profile"""
        self.user_profile = user_profile
        
        tips = []
        
        # Analyze user's current situation
        experience_level = user_profile.get('experience_level', 'beginner')
        available_time = user_profile.get('available_time', 'medium')
        budget = user_profile.get('budget', 'low')
        
        # Generate personalized tips
        if experience_level == 'beginner':
            tips.extend(self._get_beginner_tips())
        elif experience_level == 'intermediate':
            tips.extend(self._get_intermediate_tips())
        else:
            tips.extend(self._get_advanced_tips())
        
        # Adjust based on available time
        if available_time == 'low':
            tips = [tip for tip in tips if tip['effort'] == 'low']
        elif available_time == 'high':
            # Include all tips for high time availability
            pass
        
        # Adjust based on budget
        if budget == 'low':
            tips = [tip for tip in tips if 'free' in tip.get('cost', 'free')]
        
        return tips[:10]  # Return top 10 tips
    
    def _get_beginner_tips(self) -> List[Dict[str, Any]]:
        """Get tips for beginners"""
        return [
            {
                'category': 'content',
                'tip': 'Start with basic on-page SEO optimization',
                'priority': 'high',
                'effort': 'low',
                'impact': 'high',
                'cost': 'free',
                'reasoning': 'On-page SEO provides the best ROI for beginners'
            },
            {
                'category': 'technical',
                'tip': 'Focus on page speed and mobile optimization',
                'priority': 'high',
                'effort': 'medium',
                'impact': 'high',
                'cost': 'free',
                'reasoning': 'Technical SEO fundamentals are essential'
            }
        ]
    
    def _get_intermediate_tips(self) -> List[Dict[str, Any]]:
        """Get tips for intermediate users"""
        return [
            {
                'category': 'content',
                'tip': 'Implement advanced content strategies',
                'priority': 'high',
                'effort': 'medium',
                'impact': 'high',
                'cost': 'free',
                'reasoning': 'Advanced content strategies can significantly improve rankings'
            },
            {
                'category': 'off_page',
                'tip': 'Start building quality backlinks',
                'priority': 'high',
                'effort': 'high',
                'impact': 'high',
                'cost': 'low',
                'reasoning': 'Backlinks are crucial for competitive keywords'
            }
        ]
    
    def _get_advanced_tips(self) -> List[Dict[str, Any]]:
        """Get tips for advanced users"""
        return [
            {
                'category': 'technical',
                'tip': 'Implement advanced schema markup and structured data',
                'priority': 'medium',
                'effort': 'high',
                'impact': 'medium',
                'cost': 'free',
                'reasoning': 'Advanced technical SEO can provide competitive advantages'
            },
            {
                'category': 'off_page',
                'tip': 'Develop comprehensive link building and PR strategies',
                'priority': 'high',
                'effort': 'high',
                'impact': 'high',
                'cost': 'high',
                'reasoning': 'Advanced link building is essential for top rankings'
            }
        ]

# Example usage
optimization_tips = OptimizationTips()

# Generate tips for a keyword
tips = optimization_tips.generate_tips("python programming", current_rank=15, target_rank=5) 