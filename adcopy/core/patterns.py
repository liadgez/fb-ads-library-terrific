"""
Pattern Matching Engine
Handles regex-based pattern matching and scoring for typology classification.
"""

import re
import yaml
from typing import Dict, List, Tuple, Any
from pathlib import Path


class PatternMatcher:
    """Regex-based pattern matching for ad copy typologies."""
    
    def __init__(self, rules_path: str = None):
        """
        Initialize pattern matcher with typology rules.
        
        Args:
            rules_path: Path to YAML rules file
        """
        if rules_path is None:
            # Default to config file in package
            config_dir = Path(__file__).parent.parent / "config"
            rules_path = config_dir / "typology_rules.yml"
            
        self.rules = self._load_rules(rules_path)
        self.typologies = self.rules.get('typologies', {})
        self.settings = self.rules.get('settings', {})
        
    def _load_rules(self, rules_path: str) -> Dict[str, Any]:
        """Load typology rules from YAML file."""
        try:
            with open(rules_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise ValueError(f"Failed to load rules from {rules_path}: {e}")
    
    def match_patterns(self, text: str, typology_key: str) -> Tuple[float, List[str]]:
        """
        Match text against patterns for a specific typology.
        
        Args:
            text: Text to analyze
            typology_key: Key for typology in rules
            
        Returns:
            Tuple of (total_score, matched_patterns)
        """
        if typology_key not in self.typologies:
            return 0.0, []
            
        typology = self.typologies[typology_key]
        patterns = typology.get('patterns', [])
        threshold = typology.get('threshold', 0.5)
        
        total_score = 0.0
        matched_patterns = []
        
        for pattern_def in patterns:
            regex = pattern_def.get('regex', '')
            weight = pattern_def.get('weight', 1.0)
            
            try:
                matches = re.findall(regex, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # Score based on number of matches and weight
                    match_score = len(matches) * weight
                    total_score += match_score
                    matched_patterns.extend([str(match) for match in matches])
                    
            except re.error as e:
                print(f"Invalid regex pattern '{regex}': {e}")
                continue
                
        return total_score, matched_patterns
    
    def classify_text(self, text: str) -> Dict[str, Any]:
        """
        Classify text against all typologies.
        
        Args:
            text: Text to classify
            
        Returns:
            Classification results with scores and matched patterns
        """
        results = {
            'text': text,
            'typologies': {},
            'labels': [],
            'confidence_scores': {},
            'matched_patterns': {}
        }
        
        # Test against each typology
        for typology_key, typology_def in self.typologies.items():
            score, patterns = self.match_patterns(text, typology_key)
            threshold = typology_def.get('threshold', 0.5)
            typology_name = typology_def.get('name', typology_key)
            
            results['confidence_scores'][typology_key] = score
            results['matched_patterns'][typology_key] = patterns
            
            # Include if score meets threshold
            if score >= threshold:
                results['labels'].append(typology_name)
                results['typologies'][typology_key] = {
                    'name': typology_name,
                    'score': score,
                    'threshold': threshold,
                    'patterns_matched': patterns,
                    'description': typology_def.get('description', '')
                }
        
        # Limit number of labels if specified
        max_labels = self.settings.get('max_labels_per_ad', float('inf'))
        if len(results['labels']) > max_labels:
            # Sort by score and take top N
            sorted_typologies = sorted(
                results['typologies'].items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )[:max_labels]
            
            results['labels'] = [item[1]['name'] for item in sorted_typologies]
            results['typologies'] = dict(sorted_typologies)
        
        return results
    
    def get_typology_info(self, typology_key: str = None) -> Dict[str, Any]:
        """
        Get information about available typologies.
        
        Args:
            typology_key: Specific typology to get info for, or None for all
            
        Returns:
            Typology information
        """
        if typology_key:
            if typology_key in self.typologies:
                return self.typologies[typology_key]
            else:
                return {}
        
        # Return all typologies with basic info
        info = {}
        for key, typology in self.typologies.items():
            info[key] = {
                'name': typology.get('name', key),
                'description': typology.get('description', ''),
                'pattern_count': len(typology.get('patterns', [])),
                'threshold': typology.get('threshold', 0.5)
            }
        
        return info
    
    def validate_rules(self) -> List[str]:
        """
        Validate loaded rules for syntax errors.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        for typology_key, typology in self.typologies.items():
            patterns = typology.get('patterns', [])
            
            for i, pattern_def in enumerate(patterns):
                regex = pattern_def.get('regex', '')
                if not regex:
                    errors.append(f"{typology_key}: Pattern {i} has empty regex")
                    continue
                    
                try:
                    re.compile(regex)
                except re.error as e:
                    errors.append(f"{typology_key}: Pattern {i} invalid regex '{regex}': {e}")
                    
                weight = pattern_def.get('weight', 1.0)
                if not isinstance(weight, (int, float)) or weight < 0:
                    errors.append(f"{typology_key}: Pattern {i} invalid weight: {weight}")
        
        return errors