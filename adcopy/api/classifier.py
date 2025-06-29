"""
Main API Interface for Ad Copy Analyzer
Provides simple, clean interface for ad copy typology classification.
"""

from typing import Dict, List, Any, Union, Optional
import json
from pathlib import Path

from ..core.typologist import Typologist


class AdCopyAnalyzer:
    """
    Main interface for analyzing ad copy typologies.
    
    This is the primary class users will interact with for classifying
    ad copy into persuasion typologies and extracting insights.
    """
    
    def __init__(self, 
                 rules_path: str = None, 
                 config: Dict[str, Any] = None):
        """
        Initialize the Ad Copy Analyzer.
        
        Args:
            rules_path: Path to custom YAML rules file
            config: Configuration overrides
            
        Example:
            analyzer = AdCopyAnalyzer()
            result = analyzer.classify("Last chance! Save 50% today only!")
        """
        self.typologist = Typologist(rules_path=rules_path, config=config)
        self._version = "1.0.0"
    
    def classify(self, 
                text: str, 
                ad_id: str = None,
                detailed: bool = False) -> Dict[str, Any]:
        """
        Classify a single ad copy text.
        
        Args:
            text: The ad copy text to analyze
            ad_id: Optional identifier for the ad
            detailed: Whether to include detailed analysis
            
        Returns:
            Classification result with typology labels and scores
            
        Example:
            result = analyzer.classify("Tired of complex software? Try our simple solution!")
            print(result['typology_labels'])  # ['Problem / Solution Framing']
        """
        return self.typologist.classify_single(
            text=text,
            ad_id=ad_id,
            include_metadata=detailed
        )
    
    def classify_batch(self, 
                      ads: List[Union[str, Dict[str, str]]],
                      detailed: bool = False) -> List[Dict[str, Any]]:
        """
        Classify multiple ad copies in batch.
        
        Args:
            ads: List of ad copy texts or dictionaries with 'text' and optional 'ad_id'
            detailed: Whether to include detailed analysis
            
        Returns:
            List of classification results
            
        Example:
            ads = [
                "Save 50% today only!",
                {"text": "Join thousands of happy customers", "ad_id": "ad_123"},
                "Learn the secret to success"
            ]
            results = analyzer.classify_batch(ads)
        """
        return self.typologist.classify_batch(ads, include_metadata=detailed)
    
    def analyze_campaign(self, 
                        ads: List[Union[str, Dict[str, str]]],
                        campaign_name: str = None) -> Dict[str, Any]:
        """
        Analyze a complete campaign's ad copy patterns.
        
        Args:
            ads: List of ad copies in the campaign
            campaign_name: Optional name for the campaign
            
        Returns:
            Comprehensive campaign analysis with patterns and recommendations
            
        Example:
            campaign_ads = ["Ad copy 1", "Ad copy 2", "Ad copy 3"]
            analysis = analyzer.analyze_campaign(campaign_ads, "Summer Sale")
        """
        # Classify all ads
        results = self.classify_batch(ads, detailed=True)
        
        # Get distribution analysis
        distribution = self.typologist.analyze_typology_distribution(results)
        
        # Generate campaign insights
        insights = self._generate_campaign_insights(results, distribution)
        
        campaign_analysis = {
            'campaign_name': campaign_name,
            'total_ads': len(ads),
            'classification_results': results,
            'typology_distribution': distribution,
            'insights': insights,
            'recommendations': self._generate_recommendations(distribution, results)
        }
        
        return campaign_analysis
    
    def get_typology_guide(self) -> Dict[str, Any]:
        """
        Get a guide to all available typologies.
        
        Returns:
            Dictionary with typology information and examples
        """
        typologies = self.typologist.get_available_typologies()
        
        guide = {
            'version': self._version,
            'total_typologies': len(typologies),
            'typologies': {}
        }
        
        for key, info in typologies.items():
            guide['typologies'][key] = {
                'name': info['name'],
                'description': info['description'],
                'threshold': info['threshold'],
                'pattern_count': info['pattern_count']
            }
        
        return guide
    
    def validate_setup(self) -> Dict[str, Any]:
        """
        Validate the analyzer configuration and rules.
        
        Returns:
            Validation results and any error messages
        """
        errors = self.typologist.validate_configuration()
        typologies = self.typologist.get_available_typologies()
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'typologies_loaded': len(typologies),
            'version': self._version
        }
    
    def export_results(self, 
                      results: List[Dict[str, Any]], 
                      output_path: str,
                      format: str = 'json') -> None:
        """
        Export classification results to file.
        
        Args:
            results: Results from classify_batch or analyze_campaign
            output_path: Path for output file
            format: Export format ('json' or 'csv')
        """
        self.typologist.export_results(results, output_path, format)
    
    def _generate_campaign_insights(self, 
                                   results: List[Dict[str, Any]], 
                                   distribution: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from campaign analysis."""
        insights = {
            'dominant_strategy': None,
            'diversity_score': 0,
            'avg_confidence': 0,
            'text_characteristics': {},
            'patterns': []
        }
        
        # Find dominant strategy
        dist_data = distribution.get('distribution', {})
        if dist_data:
            dominant = max(dist_data.items(), key=lambda x: x[1]['count'])
            insights['dominant_strategy'] = {
                'typology': dominant[0],
                'percentage': dominant[1]['percentage'],
                'count': dominant[1]['count']
            }
        
        # Calculate diversity (how many different typologies are used)
        typology_count = len(dist_data)
        total_ads = distribution.get('total_ads', 1)
        insights['diversity_score'] = round(typology_count / max(total_ads, 1), 2)
        
        # Average confidence across all classifications
        all_confidences = []
        word_counts = []
        
        for result in results:
            scores = result.get('confidence_scores', {})
            if scores:
                all_confidences.extend(scores.values())
            
            features = result.get('text_features', {})
            if features:
                word_counts.append(features.get('word_count', 0))
        
        if all_confidences:
            insights['avg_confidence'] = round(sum(all_confidences) / len(all_confidences), 3)
        
        # Text characteristics
        if word_counts:
            insights['text_characteristics'] = {
                'avg_word_count': round(sum(word_counts) / len(word_counts), 1),
                'max_word_count': max(word_counts),
                'min_word_count': min(word_counts)
            }
        
        return insights
    
    def _generate_recommendations(self, 
                                 distribution: Dict[str, Any],
                                 results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        summary = distribution.get('summary', {})
        dist_data = distribution.get('distribution', {})
        
        # Check for low diversity
        if len(dist_data) <= 2:
            recommendations.append(
                "Consider diversifying your ad copy strategies. Currently using only "
                f"{len(dist_data)} typology/typologies."
            )
        
        # Check for ads with no labels
        no_labels = summary.get('ads_with_no_labels', 0)
        total_ads = distribution.get('total_ads', 1)
        if no_labels > 0:
            percentage = (no_labels / total_ads) * 100
            recommendations.append(
                f"{no_labels} ads ({percentage:.1f}%) couldn't be classified. "
                "Consider strengthening persuasive elements in these ads."
            )
        
        # Check for overuse of single strategy
        if dist_data:
            max_usage = max(data['percentage'] for data in dist_data.values())
            if max_usage > 70:
                recommendations.append(
                    f"One typology dominates {max_usage:.1f}% of ads. "
                    "Consider A/B testing other persuasion strategies."
                )
        
        # Check average labels per ad
        avg_labels = summary.get('avg_labels_per_ad', 0)
        if avg_labels < 1.5:
            recommendations.append(
                "Average of only {:.1f} typologies per ad. Consider combining "
                "multiple persuasion strategies for stronger impact.".format(avg_labels)
            )
        
        return recommendations