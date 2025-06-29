"""
Text Processing Utilities
Handles text cleaning, normalization, and preprocessing for ad copy analysis.
"""

import re
import string
from typing import List, Dict, Any


class TextProcessor:
    """Text processing and normalization utilities."""
    
    def __init__(self):
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", 
            flags=re.UNICODE
        )
        
    def clean_text(self, text: str, remove_emojis: bool = False) -> str:
        """
        Clean and normalize text for analysis.
        
        Args:
            text: Raw ad copy text
            remove_emojis: Whether to remove emoji characters
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove emojis if requested
        if remove_emojis:
            text = self.emoji_pattern.sub('', text)
            
        # Normalize whitespace
        text = re.sub(r'\\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """
        Extract linguistic features from ad copy.
        
        Args:
            text: Cleaned ad copy text
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Basic metrics
        features['word_count'] = len(text.split())
        features['char_count'] = len(text)
        features['sentence_count'] = len([s for s in text.split('.') if s.strip()])
        
        # Capitalization patterns
        features['all_caps_words'] = len(re.findall(r'\\b[A-Z]{3,}\\b', text))
        features['caps_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Punctuation analysis
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['emoji_count'] = len(self.emoji_pattern.findall(text))
        
        # Numeric content
        features['number_count'] = len(re.findall(r'\\d+', text))
        features['percentage_mentions'] = len(re.findall(r'\\d+%', text))
        features['price_mentions'] = len(re.findall(r'\\$\\d+', text))
        
        # Call-to-action indicators
        cta_patterns = [
            r'\\b(shop|buy|get|try|learn|discover|sign up|download)\\b',
            r'\\b(now|today|click|tap|visit)\\b'
        ]
        features['cta_signals'] = sum(len(re.findall(pattern, text, re.IGNORECASE)) 
                                    for pattern in cta_patterns)
        
        return features
    
    def extract_buzzwords(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract potential buzzwords from ad copy.
        
        Args:
            text: Ad copy text
            min_length: Minimum word length to consider
            
        Returns:
            List of potential buzzwords
        """
        # Clean text and convert to lowercase
        clean_text = self.clean_text(text, remove_emojis=True).lower()
        
        # Remove punctuation and split into words
        words = re.findall(r'\\b[a-z]+\\b', clean_text)
        
        # Filter by length and remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 
            'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 
            'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'
        }
        
        buzzwords = [word for word in words 
                    if len(word) >= min_length and word not in stop_words]
        
        return list(set(buzzwords))  # Remove duplicates
    
    def extract_cta_text(self, text: str) -> List[str]:
        """
        Extract call-to-action phrases from ad copy.
        
        Args:
            text: Ad copy text
            
        Returns:
            List of identified CTAs
        """
        cta_patterns = [
            r'\\b(shop now|buy now|get started|learn more|sign up|try free)\\b',
            r'\\b(download|subscribe|register|join|order|purchase)\\b',
            r'\\b(click here|tap here|visit|call now|book now)\\b'
        ]
        
        ctas = []
        for pattern in cta_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            ctas.extend(matches)
            
        return list(set(ctas))  # Remove duplicates
    
    def analyze_sentiment_indicators(self, text: str) -> Dict[str, int]:
        """
        Analyze basic sentiment indicators in text.
        
        Args:
            text: Ad copy text
            
        Returns:
            Dictionary with sentiment indicator counts
        """
        positive_words = [
            'amazing', 'awesome', 'beautiful', 'best', 'better', 'excellent', 
            'fantastic', 'great', 'incredible', 'love', 'perfect', 'wonderful'
        ]
        
        negative_words = [
            'bad', 'boring', 'difficult', 'hard', 'hate', 'horrible', 
            'never', 'no', 'problem', 'terrible', 'ugly', 'worst'
        ]
        
        urgency_words = [
            'fast', 'hurry', 'immediate', 'instant', 'now', 'quick', 
            'rapid', 'rush', 'soon', 'today', 'urgent'
        ]
        
        text_lower = text.lower()
        
        return {
            'positive_count': sum(1 for word in positive_words if word in text_lower),
            'negative_count': sum(1 for word in negative_words if word in text_lower),
            'urgency_count': sum(1 for word in urgency_words if word in text_lower)
        }