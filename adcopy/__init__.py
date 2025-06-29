"""
Ad Copy Typology Analyzer
A standalone tool for analyzing and classifying advertising copy based on persuasion patterns and strategies.
"""

from .api.classifier import AdCopyAnalyzer
from .api.hybrid_classifier import HybridAdCopyAnalyzer
from .core.typologist import Typologist
from .utils.text_processor import TextProcessor
from .utils.cost_tracker import OpenAICostTracker

__version__ = "1.1.0"
__author__ = "Ad Copy Intelligence Team"

__all__ = [
    "AdCopyAnalyzer",
    "HybridAdCopyAnalyzer",
    "Typologist", 
    "TextProcessor",
    "OpenAICostTracker"
]