"""
Core Typology Classification Engine
Main engine for classifying ad copy into persuasion typologies with multi-label support.
"""

from typing import Dict, List, Any, Optional, Union
import json
from datetime import datetime

from .patterns import PatternMatcher
from ..utils.text_processor import TextProcessor


class Typologist:
    """Core engine for ad copy typology classification."""
    
    def __init__(self, rules_path: str = None, config: Dict[str, Any] = None):
        """
        Initialize the typology classifier.
        
        Args:
            rules_path: Path to custom YAML rules file
            config: Override configuration settings
        """
        self.pattern_matcher = PatternMatcher(rules_path)
        self.text_processor = TextProcessor()
        
        # Merge custom config with defaults
        self.config = {
            'min_confidence': 0.5,
            'include_features': True,
            'include_patterns': True,
            'normalize_scores': True
        }
        if config:
            self.config.update(config)
    
    def classify_single(self, 
                       text: str, 
                       ad_id: str = None,
                       include_metadata: bool = True) -> Dict[str, Any]:
        """
        Classify a single piece of ad copy.
        
        Args:
            text: Ad copy text to classify
            ad_id: Optional identifier for the ad
            include_metadata: Whether to include detailed metadata
            
        Returns:
            Classification result dictionary
        """
        if not text or not text.strip():
            return self._empty_result(ad_id)
        
        # Clean and process text
        clean_text = self.text_processor.clean_text(text)
        
        # Get pattern matching results
        pattern_results = self.pattern_matcher.classify_text(clean_text)
        
        # Build result
        result = {
            'ad_id': ad_id,
            'original_text': text,
            'clean_text': clean_text if include_metadata else None,
            'typology_labels': pattern_results['labels'],
            'typology_count': len(pattern_results['labels']),
            'confidence_scores': pattern_results['confidence_scores'],
            'classified_at': datetime.utcnow().isoformat()
        }
        
        # Add detailed typology information
        if include_metadata:
            result['typologies'] = pattern_results['typologies']
            
            if self.config['include_patterns']:
                result['matched_patterns'] = pattern_results['matched_patterns']
            
            if self.config['include_features']:
                result['text_features'] = self.text_processor.extract_features(clean_text)
                result['buzzwords'] = self.text_processor.extract_buzzwords(clean_text)
                result['cta_phrases'] = self.text_processor.extract_cta_text(clean_text)
                result['sentiment_indicators'] = self.text_processor.analyze_sentiment_indicators(clean_text)
        
        # Normalize scores if requested
        if self.config['normalize_scores'] and result['confidence_scores']:
            max_score = max(result['confidence_scores'].values())
            if max_score > 0:
                result['normalized_scores'] = {
                    k: v / max_score for k, v in result['confidence_scores'].items()
                }
        
        return result
    
    def classify_batch(self, 
                      ads: List[Union[str, Dict[str, str]]], 
                      include_metadata: bool = True) -> List[Dict[str, Any]]:
        """
        Classify multiple ad copies in batch.
        
        Args:
            ads: List of ad copy texts or dictionaries with 'text' and optional 'ad_id'
            include_metadata: Whether to include detailed metadata
            
        Returns:
            List of classification results
        """
        results = []
        
        for i, ad in enumerate(ads):
            if isinstance(ad, str):
                text = ad
                ad_id = f"ad_{i}"
            elif isinstance(ad, dict):
                text = ad.get('text', '')
                ad_id = ad.get('ad_id', f"ad_{i}")
            else:
                results.append(self._empty_result(f"ad_{i}"))
                continue
            
            result = self.classify_single(text, ad_id, include_metadata)
            results.append(result)
        
        return results
    
    def analyze_typology_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze typology distribution across a set of classification results.
        
        Args:
            results: List of classification results from classify_batch
            
        Returns:
            Distribution analysis
        """
        if not results:
            return {}
        
        total_ads = len(results)
        typology_counts = {}
        confidence_totals = {}
        co_occurrence = {}
        
        # Count typologies and co-occurrences
        for result in results:
            labels = result.get('typology_labels', [])
            scores = result.get('confidence_scores', {})
            
            # Count individual typologies
            for label in labels:
                typology_counts[label] = typology_counts.get(label, 0) + 1
            
            # Sum confidence scores
            for typology, score in scores.items():
                confidence_totals[typology] = confidence_totals.get(typology, 0) + score
            
            # Count co-occurrences
            for i, label1 in enumerate(labels):
                for label2 in labels[i+1:]:
                    pair = tuple(sorted([label1, label2]))
                    co_occurrence[pair] = co_occurrence.get(pair, 0) + 1
        
        # Calculate statistics
        distribution = {
            'total_ads': total_ads,
            'typologies_found': len(typology_counts),
            'distribution': {},
            'co_occurrence': {},
            'summary': {}
        }
        
        # Typology distribution
        for typology, count in typology_counts.items():
            percentage = (count / total_ads) * 100
            avg_confidence = confidence_totals.get(typology, 0) / count if count > 0 else 0
            
            distribution['distribution'][typology] = {
                'count': count,
                'percentage': round(percentage, 2),
                'average_confidence': round(avg_confidence, 3)
            }
        
        # Co-occurrence analysis
        for (type1, type2), count in co_occurrence.items():
            percentage = (count / total_ads) * 100
            distribution['co_occurrence'][f"{type1} + {type2}"] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        # Summary statistics
        label_counts = [len(result.get('typology_labels', [])) for result in results]
        distribution['summary'] = {
            'avg_labels_per_ad': round(sum(label_counts) / len(label_counts), 2),
            'max_labels_per_ad': max(label_counts) if label_counts else 0,
            'ads_with_no_labels': sum(1 for count in label_counts if count == 0),
            'most_common_typology': max(typology_counts.items(), key=lambda x: x[1])[0] if typology_counts else None
        }
        
        return distribution
    
    def export_results(self, 
                      results: List[Dict[str, Any]], 
                      output_path: str,
                      format: str = 'json') -> None:
        """
        Export classification results to file.
        
        Args:
            results: Classification results to export
            output_path: Path to output file
            format: Export format ('json', 'csv')
        """
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            import csv
            
            if not results:
                return
            
            # Flatten results for CSV
            fieldnames = [
                'ad_id', 'original_text', 'typology_labels', 'typology_count',
                'word_count', 'exclamation_count', 'question_count'
            ]
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    row = {
                        'ad_id': result.get('ad_id', ''),
                        'original_text': result.get('original_text', ''),
                        'typology_labels': '; '.join(result.get('typology_labels', [])),
                        'typology_count': result.get('typology_count', 0)
                    }
                    
                    # Add text features if available
                    features = result.get('text_features', {})
                    row.update({
                        'word_count': features.get('word_count', 0),
                        'exclamation_count': features.get('exclamation_count', 0),
                        'question_count': features.get('question_count', 0)
                    })
                    
                    writer.writerow(row)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _empty_result(self, ad_id: str) -> Dict[str, Any]:
        """Generate empty result for invalid input."""
        return {
            'ad_id': ad_id,
            'original_text': '',
            'typology_labels': [],
            'typology_count': 0,
            'confidence_scores': {},
            'classified_at': datetime.utcnow().isoformat(),
            'error': 'Empty or invalid text input'
        }
    
    def get_available_typologies(self) -> Dict[str, Any]:
        """Get information about available typologies."""
        return self.pattern_matcher.get_typology_info()
    
    def validate_configuration(self) -> List[str]:
        """Validate the current configuration and rules."""
        return self.pattern_matcher.validate_rules()