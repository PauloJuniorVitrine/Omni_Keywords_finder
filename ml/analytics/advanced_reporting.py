# Advanced Reporting using Machine Learning
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

class AdvancedReporter:
    def __init__(self):
        self.report_templates = {}
        self.report_configurations = {}
        self.data_sources = {}
        self.report_history = {}
        
    def generate_advanced_report(self, data: List[Dict[str, Any]], 
                               report_type: str, 
                               report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advanced report based on type and configuration"""
        report = {
            'report_id': self._generate_report_id(),
            'report_type': report_type,
            'generated_at': datetime.now().isoformat(),
            'data_summary': {},
            'insights': [],
            'recommendations': [],
            'visualizations': [],
            'metrics': {},
            'executive_summary': ''
        }
        
        # Prepare data
        df = self._prepare_data(data)
        
        # Generate report based on type
        if report_type == 'performance_report':
            report.update(self._generate_performance_report(df, report_config))
        elif report_type == 'competitive_report':
            report.update(self._generate_competitive_report(df, report_config))
        elif report_type == 'trend_report':
            report.update(self._generate_trend_report(df, report_config))
        elif report_type == 'roi_report':
            report.update(self._generate_roi_report(df, report_config))
        elif report_type == 'custom_report':
            report.update(self._generate_custom_report(df, report_config))
        
        # Add data summary
        report['data_summary'] = self._generate_data_summary(df)
        
        # Generate executive summary
        report['executive_summary'] = self._generate_executive_summary(report)
        
        # Store report
        self._store_report(report)
        
        return report
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"report_{timestamp}_{np.random.randint(1000, 9999)}"
    
    def _prepare_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare data for reporting"""
        df = pd.DataFrame(data)
        
        # Convert date columns
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col])
        
        # Sort by date if available
        if date_columns:
            df = df.sort_values(date_columns[0])
        
        return df
    
    def _generate_performance_report(self, df: pd.DataFrame, 
                                   config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance report"""
        report_sections = {
            'metrics': {},
            'insights': [],
            'recommendations': [],
            'visualizations': []
        }
        
        # Calculate key metrics
        if 'rank' in df.columns:
            report_sections['metrics']['ranking'] = {
                'average_rank': df['rank'].mean(),
                'best_rank': df['rank'].min(),
                'worst_rank': df['rank'].max(),
                'ranking_distribution': self._calculate_ranking_distribution(df['rank'])
            }
        
        if 'traffic' in df.columns:
            report_sections['metrics']['traffic'] = {
                'total_traffic': df['traffic'].sum(),
                'average_traffic': df['traffic'].mean(),
                'traffic_growth': self._calculate_growth_rate(df['traffic']),
                'top_traffic_sources': self._get_top_performers(df, 'traffic', 5)
            }
        
        if 'conversions' in df.columns:
            report_sections['metrics']['conversions'] = {
                'total_conversions': df['conversions'].sum(),
                'conversion_rate': df['conversions'].sum() / df['traffic'].sum() if 'traffic' in df.columns else 0,
                'conversion_growth': self._calculate_growth_rate(df['conversions'])
            }
        
        # Generate insights
        report_sections['insights'] = self._generate_performance_insights(df, report_sections['metrics'])
        
        # Generate recommendations
        report_sections['recommendations'] = self._generate_performance_recommendations(
            df, report_sections['metrics']
        )
        
        # Generate visualizations
        report_sections['visualizations'] = self._generate_performance_visualizations(df)
        
        return report_sections
    
    def _generate_competitive_report(self, df: pd.DataFrame, 
                                   config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate competitive analysis report"""
        report_sections = {
            'metrics': {},
            'insights': [],
            'recommendations': [],
            'visualizations': []
        }
        
        # Competitive metrics
        if 'competitor_rank' in df.columns and 'rank' in df.columns:
            report_sections['metrics']['competitive_position'] = {
                'market_share': self._calculate_market_share(df),
                'competitive_gap': self._calculate_competitive_gap(df),
                'win_rate': self._calculate_win_rate(df),
                'competitive_threats': self._identify_competitive_threats(df)
            }
        
        # Generate competitive insights
        report_sections['insights'] = self._generate_competitive_insights(df)
        
        # Generate competitive recommendations
        report_sections['recommendations'] = self._generate_competitive_recommendations(df)
        
        # Generate competitive visualizations
        report_sections['visualizations'] = self._generate_competitive_visualizations(df)
        
        return report_sections
    
    def _generate_trend_report(self, df: pd.DataFrame, 
                             config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trend analysis report"""
        report_sections = {
            'metrics': {},
            'insights': [],
            'recommendations': [],
            'visualizations': []
        }
        
        # Trend metrics
        if 'date' in df.columns:
            report_sections['metrics']['trends'] = {
                'ranking_trends': self._analyze_ranking_trends(df),
                'traffic_trends': self._analyze_traffic_trends(df),
                'conversion_trends': self._analyze_conversion_trends(df),
                'seasonal_patterns': self._analyze_seasonal_patterns(df)
            }
        
        # Generate trend insights
        report_sections['insights'] = self._generate_trend_insights(df)
        
        # Generate trend recommendations
        report_sections['recommendations'] = self._generate_trend_recommendations(df)
        
        # Generate trend visualizations
        report_sections['visualizations'] = self._generate_trend_visualizations(df)
        
        return report_sections
    
    def _generate_roi_report(self, df: pd.DataFrame, 
                           config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ROI analysis report"""
        report_sections = {
            'metrics': {},
            'insights': [],
            'recommendations': [],
            'visualizations': []
        }
        
        # ROI metrics
        report_sections['metrics']['roi'] = {
            'total_investment': config.get('total_investment', 0),
            'total_revenue': self._calculate_total_revenue(df),
            'roi_percentage': self._calculate_roi_percentage(df, config),
            'cost_per_conversion': self._calculate_cost_per_conversion(df, config),
            'roi_by_keyword': self._calculate_roi_by_keyword(df, config)
        }
        
        # Generate ROI insights
        report_sections['insights'] = self._generate_roi_insights(df, config)
        
        # Generate ROI recommendations
        report_sections['recommendations'] = self._generate_roi_recommendations(df, config)
        
        # Generate ROI visualizations
        report_sections['visualizations'] = self._generate_roi_visualizations(df)
        
        return report_sections
    
    def _generate_custom_report(self, df: pd.DataFrame, 
                              config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom report based on configuration"""
        report_sections = {
            'metrics': {},
            'insights': [],
            'recommendations': [],
            'visualizations': []
        }
        
        # Custom metrics based on configuration
        custom_metrics = config.get('metrics', [])
        for metric in custom_metrics:
            if metric in df.columns:
                report_sections['metrics'][metric] = {
                    'total': df[metric].sum(),
                    'average': df[metric].mean(),
                    'growth': self._calculate_growth_rate(df[metric])
                }
        
        # Custom insights
        report_sections['insights'] = self._generate_custom_insights(df, config)
        
        # Custom recommendations
        report_sections['recommendations'] = self._generate_custom_recommendations(df, config)
        
        # Custom visualizations
        report_sections['visualizations'] = self._generate_custom_visualizations(df, config)
        
        return report_sections
    
    def _calculate_ranking_distribution(self, ranks: pd.Series) -> Dict[str, int]:
        """Calculate ranking distribution"""
        distribution = {
            'top_3': len(ranks[ranks <= 3]),
            'top_10': len(ranks[ranks <= 10]),
            'top_20': len(ranks[ranks <= 20]),
            'beyond_20': len(ranks[ranks > 20])
        }
        return distribution
    
    def _calculate_growth_rate(self, values: pd.Series) -> float:
        """Calculate growth rate"""
        if len(values) < 2:
            return 0.0
        
        first_value = values.iloc[0]
        last_value = values.iloc[-1]
        
        if first_value == 0:
            return 0.0
        
        return ((last_value - first_value) / first_value) * 100
    
    def _get_top_performers(self, df: pd.DataFrame, column: str, top_n: int) -> List[Dict[str, Any]]:
        """Get top performers for a specific column"""
        if column not in df.columns:
            return []
        
        top_performers = df.nlargest(top_n, column)
        return [
            {
                'keyword': row.get('keyword', ''),
                'value': row[column],
                'rank': row.get('rank', 0)
            }
            for _, row in top_performers.iterrows()
        ]
    
    def _generate_performance_insights(self, df: pd.DataFrame, 
                                     metrics: Dict[str, Any]) -> List[str]:
        """Generate performance insights"""
        insights = []
        
        # Ranking insights
        if 'ranking' in metrics:
            ranking_metrics = metrics['ranking']
            avg_rank = ranking_metrics['average_rank']
            
            if avg_rank <= 5:
                insights.append("Excellent ranking performance with average position in top 5")
            elif avg_rank <= 10:
                insights.append("Good ranking performance with average position in top 10")
            elif avg_rank <= 20:
                insights.append("Moderate ranking performance, room for improvement")
            else:
                insights.append("Poor ranking performance, significant improvement needed")
        
        # Traffic insights
        if 'traffic' in metrics:
            traffic_metrics = metrics['traffic']
            traffic_growth = traffic_metrics['traffic_growth']
            
            if traffic_growth > 20:
                insights.append(f"Strong traffic growth of {traffic_growth:.1f}%")
            elif traffic_growth > 0:
                insights.append(f"Moderate traffic growth of {traffic_growth:.1f}%")
            else:
                insights.append(f"Traffic decline of {abs(traffic_growth):.1f}%")
        
        # Conversion insights
        if 'conversions' in metrics:
            conversion_metrics = metrics['conversions']
            conversion_rate = conversion_metrics['conversion_rate']
            
            if conversion_rate > 0.05:
                insights.append("Strong conversion rate above 5%")
            elif conversion_rate > 0.02:
                insights.append("Moderate conversion rate between 2-5%")
            else:
                insights.append("Low conversion rate, optimization needed")
        
        return insights
    
    def _generate_performance_recommendations(self, df: pd.DataFrame,
                                            metrics: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Ranking recommendations
        if 'ranking' in metrics:
            ranking_metrics = metrics['ranking']
            avg_rank = ranking_metrics['average_rank']
            
            if avg_rank > 10:
                recommendations.append("Focus on improving rankings through content optimization and link building")
            
            distribution = ranking_metrics['ranking_distribution']
            if distribution['beyond_20'] > len(df) * 0.3:
                recommendations.append("Address poor-performing keywords with targeted optimization")
        
        # Traffic recommendations
        if 'traffic' in metrics:
            traffic_metrics = metrics['traffic']
            traffic_growth = traffic_metrics['traffic_growth']
            
            if traffic_growth < 0:
                recommendations.append("Investigate traffic decline and implement recovery strategies")
            
            if traffic_metrics['total_traffic'] < 1000:
                recommendations.append("Focus on traffic generation through content marketing and keyword expansion")
        
        # Conversion recommendations
        if 'conversions' in metrics:
            conversion_metrics = metrics['conversions']
            conversion_rate = conversion_metrics['conversion_rate']
            
            if conversion_rate < 0.02:
                recommendations.append("Optimize landing pages and user experience to improve conversion rates")
        
        return recommendations
    
    def _generate_performance_visualizations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate performance visualizations"""
        visualizations = []
        
        # Ranking distribution chart
        if 'rank' in df.columns:
            visualizations.append({
                'type': 'ranking_distribution',
                'title': 'Ranking Distribution',
                'data': self._calculate_ranking_distribution(df['rank'])
            })
        
        # Traffic trend chart
        if 'traffic' in df.columns and 'date' in df.columns:
            visualizations.append({
                'type': 'traffic_trend',
                'title': 'Traffic Over Time',
                'data': self._prepare_trend_data(df, 'traffic')
            })
        
        # Performance scatter plot
        if 'rank' in df.columns and 'traffic' in df.columns:
            visualizations.append({
                'type': 'performance_scatter',
                'title': 'Rank vs Traffic',
                'data': self._prepare_scatter_data(df, 'rank', 'traffic')
            })
        
        return visualizations
    
    def _calculate_market_share(self, df: pd.DataFrame) -> float:
        """Calculate market share"""
        # Simplified market share calculation
        if 'competitor_rank' in df.columns and 'rank' in df.columns:
            wins = len(df[df['rank'] < df['competitor_rank']])
            total = len(df)
            return wins / total if total > 0 else 0
        return 0.0
    
    def _calculate_competitive_gap(self, df: pd.DataFrame) -> float:
        """Calculate competitive gap"""
        if 'competitor_rank' in df.columns and 'rank' in df.columns:
            gap = df['competitor_rank'] - df['rank']
            return gap.mean()
        return 0.0
    
    def _calculate_win_rate(self, df: pd.DataFrame) -> float:
        """Calculate win rate against competitors"""
        return self._calculate_market_share(df)
    
    def _identify_competitive_threats(self, df: pd.DataFrame) -> List[str]:
        """Identify competitive threats"""
        threats = []
        
        if 'competitor_rank' in df.columns and 'rank' in df.columns:
            # Keywords where competitor is significantly better
            significant_losses = df[df['competitor_rank'] < df['rank'] - 5]
            if len(significant_losses) > 0:
                threats.append(f"{len(significant_losses)} keywords where competitors have significant advantage")
        
        return threats
    
    def _generate_competitive_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate competitive insights"""
        insights = []
        
        market_share = self._calculate_market_share(df)
        if market_share > 0.7:
            insights.append("Strong competitive position with high market share")
        elif market_share > 0.5:
            insights.append("Competitive position with room for improvement")
        else:
            insights.append("Weak competitive position, significant improvement needed")
        
        return insights
    
    def _generate_competitive_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate competitive recommendations"""
        recommendations = []
        
        market_share = self._calculate_market_share(df)
        if market_share < 0.5:
            recommendations.append("Develop competitive advantages to improve market position")
        
        competitive_gap = self._calculate_competitive_gap(df)
        if competitive_gap < 0:
            recommendations.append("Focus on outperforming competitors in key areas")
        
        return recommendations
    
    def _generate_competitive_visualizations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate competitive visualizations"""
        visualizations = []
        
        if 'competitor_rank' in df.columns and 'rank' in df.columns:
            visualizations.append({
                'type': 'competitive_comparison',
                'title': 'Rank vs Competitor Rank',
                'data': self._prepare_comparison_data(df, 'rank', 'competitor_rank')
            })
        
        return visualizations
    
    def _analyze_ranking_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze ranking trends"""
        if 'rank' not in df.columns or 'date' not in df.columns:
            return {}
        
        # Calculate trend over time
        df_sorted = df.sort_values('date')
        trend = np.polyfit(range(len(df_sorted)), df_sorted['rank'], 1)[0]
        
        return {
            'trend_direction': 'improving' if trend < 0 else 'declining',
            'trend_strength': abs(trend),
            'trend_data': self._prepare_trend_data(df_sorted, 'rank')
        }
    
    def _analyze_traffic_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze traffic trends"""
        if 'traffic' not in df.columns or 'date' not in df.columns:
            return {}
        
        df_sorted = df.sort_values('date')
        trend = np.polyfit(range(len(df_sorted)), df_sorted['traffic'], 1)[0]
        
        return {
            'trend_direction': 'increasing' if trend > 0 else 'decreasing',
            'trend_strength': abs(trend),
            'trend_data': self._prepare_trend_data(df_sorted, 'traffic')
        }
    
    def _analyze_conversion_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze conversion trends"""
        if 'conversions' not in df.columns or 'date' not in df.columns:
            return {}
        
        df_sorted = df.sort_values('date')
        trend = np.polyfit(range(len(df_sorted)), df_sorted['conversions'], 1)[0]
        
        return {
            'trend_direction': 'increasing' if trend > 0 else 'decreasing',
            'trend_strength': abs(trend),
            'trend_data': self._prepare_trend_data(df_sorted, 'conversions')
        }
    
    def _analyze_seasonal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze seasonal patterns"""
        if 'date' not in df.columns:
            return {}
        
        df['month'] = df['date'].dt.month
        monthly_avg = df.groupby('month').mean()
        
        return {
            'peak_months': monthly_avg.idxmax().to_dict(),
            'low_months': monthly_avg.idxmin().to_dict(),
            'seasonal_data': monthly_avg.to_dict()
        }
    
    def _generate_trend_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate trend insights"""
        insights = []
        
        ranking_trends = self._analyze_ranking_trends(df)
        if ranking_trends:
            direction = ranking_trends['trend_direction']
            insights.append(f"Rankings are {direction} over time")
        
        traffic_trends = self._analyze_traffic_trends(df)
        if traffic_trends:
            direction = traffic_trends['trend_direction']
            insights.append(f"Traffic is {direction} over time")
        
        return insights
    
    def _generate_trend_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate trend recommendations"""
        recommendations = []
        
        ranking_trends = self._analyze_ranking_trends(df)
        if ranking_trends and ranking_trends['trend_direction'] == 'declining':
            recommendations.append("Address declining rankings with immediate optimization")
        
        traffic_trends = self._analyze_traffic_trends(df)
        if traffic_trends and traffic_trends['trend_direction'] == 'decreasing':
            recommendations.append("Investigate traffic decline and implement recovery strategies")
        
        return recommendations
    
    def _generate_trend_visualizations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate trend visualizations"""
        visualizations = []
        
        if 'date' in df.columns:
            for column in ['rank', 'traffic', 'conversions']:
                if column in df.columns:
                    visualizations.append({
                        'type': 'trend_line',
                        'title': f'{column.title()} Trend',
                        'data': self._prepare_trend_data(df, column)
                    })
        
        return visualizations
    
    def _calculate_total_revenue(self, df: pd.DataFrame) -> float:
        """Calculate total revenue"""
        if 'revenue' in df.columns:
            return df['revenue'].sum()
        elif 'conversions' in df.columns:
            # Estimate revenue based on conversions
            avg_conversion_value = 100  # Default value
            return df['conversions'].sum() * avg_conversion_value
        return 0.0
    
    def _calculate_roi_percentage(self, df: pd.DataFrame, config: Dict[str, Any]) -> float:
        """Calculate ROI percentage"""
        total_investment = config.get('total_investment', 0)
        total_revenue = self._calculate_total_revenue(df)
        
        if total_investment > 0:
            return ((total_revenue - total_investment) / total_investment) * 100
        return 0.0
    
    def _calculate_cost_per_conversion(self, df: pd.DataFrame, config: Dict[str, Any]) -> float:
        """Calculate cost per conversion"""
        total_investment = config.get('total_investment', 0)
        total_conversions = df['conversions'].sum() if 'conversions' in df.columns else 0
        
        if total_conversions > 0:
            return total_investment / total_conversions
        return 0.0
    
    def _calculate_roi_by_keyword(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate ROI by keyword"""
        roi_by_keyword = []
        
        if 'keyword' in df.columns and 'conversions' in df.columns:
            total_investment = config.get('total_investment', 0)
            total_conversions = df['conversions'].sum()
            
            for _, row in df.iterrows():
                keyword_roi = {
                    'keyword': row['keyword'],
                    'conversions': row['conversions'],
                    'roi': (row['conversions'] / total_conversions) * 100 if total_conversions > 0 else 0
                }
                roi_by_keyword.append(keyword_roi)
        
        return roi_by_keyword
    
    def _generate_roi_insights(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[str]:
        """Generate ROI insights"""
        insights = []
        
        roi_percentage = self._calculate_roi_percentage(df, config)
        if roi_percentage > 100:
            insights.append(f"Excellent ROI of {roi_percentage:.1f}%")
        elif roi_percentage > 0:
            insights.append(f"Positive ROI of {roi_percentage:.1f}%")
        else:
            insights.append(f"Negative ROI of {roi_percentage:.1f}%")
        
        cost_per_conversion = self._calculate_cost_per_conversion(df, config)
        if cost_per_conversion < 50:
            insights.append(f"Low cost per conversion of ${cost_per_conversion:.2f}")
        else:
            insights.append(f"High cost per conversion of ${cost_per_conversion:.2f}")
        
        return insights
    
    def _generate_roi_recommendations(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[str]:
        """Generate ROI recommendations"""
        recommendations = []
        
        roi_percentage = self._calculate_roi_percentage(df, config)
        if roi_percentage < 0:
            recommendations.append("Focus on improving ROI through better targeting and optimization")
        
        cost_per_conversion = self._calculate_cost_per_conversion(df, config)
        if cost_per_conversion > 100:
            recommendations.append("Optimize campaigns to reduce cost per conversion")
        
        return recommendations
    
    def _generate_roi_visualizations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate ROI visualizations"""
        visualizations = []
        
        if 'conversions' in df.columns and 'keyword' in df.columns:
            visualizations.append({
                'type': 'roi_by_keyword',
                'title': 'ROI by Keyword',
                'data': self._prepare_roi_data(df)
            })
        
        return visualizations
    
    def _generate_custom_insights(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[str]:
        """Generate custom insights"""
        insights = []
        
        # Add custom insights based on configuration
        custom_insights = config.get('insights', [])
        insights.extend(custom_insights)
        
        return insights
    
    def _generate_custom_recommendations(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[str]:
        """Generate custom recommendations"""
        recommendations = []
        
        # Add custom recommendations based on configuration
        custom_recommendations = config.get('recommendations', [])
        recommendations.extend(custom_recommendations)
        
        return recommendations
    
    def _generate_custom_visualizations(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate custom visualizations"""
        visualizations = []
        
        # Add custom visualizations based on configuration
        custom_visualizations = config.get('visualizations', [])
        visualizations.extend(custom_visualizations)
        
        return visualizations
    
    def _generate_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data summary"""
        return {
            'total_records': len(df),
            'date_range': {
                'start': df['date'].min().isoformat() if 'date' in df.columns else None,
                'end': df['date'].max().isoformat() if 'date' in df.columns else None
            },
            'columns': list(df.columns),
            'missing_data': df.isnull().sum().to_dict()
        }
    
    def _generate_executive_summary(self, report: Dict[str, Any]) -> str:
        """Generate executive summary"""
        summary_parts = []
        
        # Add key metrics
        if 'metrics' in report:
            metrics = report['metrics']
            if 'ranking' in metrics:
                avg_rank = metrics['ranking']['average_rank']
                summary_parts.append(f"Average ranking: {avg_rank:.1f}")
            
            if 'traffic' in metrics:
                total_traffic = metrics['traffic']['total_traffic']
                summary_parts.append(f"Total traffic: {total_traffic:,.0f}")
        
        # Add key insights
        if report['insights']:
            summary_parts.append(f"Key insights: {len(report['insights'])} identified")
        
        # Add recommendations
        if report['recommendations']:
            summary_parts.append(f"Recommendations: {len(report['recommendations'])} provided")
        
        return ". ".join(summary_parts) if summary_parts else "No summary available"
    
    def _prepare_trend_data(self, df: pd.DataFrame, column: str) -> List[Dict[str, Any]]:
        """Prepare trend data for visualization"""
        return [
            {
                'date': row['date'].isoformat() if 'date' in df.columns else str(i),
                'value': row[column]
            }
            for i, (_, row) in enumerate(df.iterrows())
        ]
    
    def _prepare_scatter_data(self, df: pd.DataFrame, x_col: str, y_col: str) -> List[Dict[str, Any]]:
        """Prepare scatter plot data"""
        return [
            {
                'x': row[x_col],
                'y': row[y_col],
                'keyword': row.get('keyword', '')
            }
            for _, row in df.iterrows()
        ]
    
    def _prepare_comparison_data(self, df: pd.DataFrame, col1: str, col2: str) -> List[Dict[str, Any]]:
        """Prepare comparison data"""
        return [
            {
                'keyword': row.get('keyword', ''),
                'our_rank': row[col1],
                'competitor_rank': row[col2]
            }
            for _, row in df.iterrows()
        ]
    
    def _prepare_roi_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prepare ROI data"""
        return [
            {
                'keyword': row.get('keyword', ''),
                'conversions': row.get('conversions', 0),
                'roi': row.get('roi', 0)
            }
            for _, row in df.iterrows()
        ]
    
    def _store_report(self, report: Dict[str, Any]) -> None:
        """Store report in history"""
        self.report_history[report['report_id']] = report

# Example usage
advanced_reporter = AdvancedReporter()

# Sample data
sample_data = [
    {
        'keyword': 'python programming',
        'rank': 8,
        'traffic': 1500,
        'conversions': 25,
        'date': '2024-01-01'
    },
    {
        'keyword': 'machine learning',
        'rank': 15,
        'traffic': 800,
        'conversions': 12,
        'date': '2024-01-01'
    }
]

# Generate performance report
report_config = {
    'total_investment': 5000,
    'metrics': ['rank', 'traffic', 'conversions']
}

performance_report = advanced_reporter.generate_advanced_report(
    sample_data, 
    'performance_report', 
    report_config
) 