"""
Hybrid Ad Copy Classifier
Combines rule-based classification with optional OpenAI LLM enhancements.
"""

import json
import openai
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from ..api.classifier import AdCopyAnalyzer
from ..utils.cost_tracker import OpenAICostTracker


class HybridAdCopyAnalyzer:
    """
    Hybrid analyzer combining rule-based classification with OpenAI enhancements.
    
    Provides cost-effective LLM integration with budget controls and fallback safety.
    """
    
    def __init__(self, 
                 openai_api_key: str = None,
                 enable_llm: bool = True,
                 budget_limit: float = 5.00,
                 default_model: str = "gpt-4o-mini",
                 timeout: int = 10):
        """
        Initialize hybrid analyzer.
        
        Args:
            openai_api_key: OpenAI API key
            enable_llm: Whether to enable LLM features
            budget_limit: Maximum spend limit in USD
            default_model: Default OpenAI model to use
            timeout: API call timeout in seconds
        """
        # Initialize rule-based analyzer (always available)
        self.rule_analyzer = AdCopyAnalyzer()
        
        # LLM configuration
        self.enable_llm = enable_llm
        self.default_model = default_model
        self.timeout = timeout
        
        # Cost tracking
        self.cost_tracker = OpenAICostTracker(budget_limit)
        
        # OpenAI client setup
        if enable_llm and openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                self.llm_available = True
            except Exception as e:
                print(f"Warning: OpenAI setup failed: {e}")
                self.llm_available = False
        else:
            self.openai_client = None
            self.llm_available = False
    
    def classify(self, 
                text: str, 
                ad_id: str = None,
                detailed: bool = False,
                enhanced: bool = False,
                industry: str = None) -> Dict[str, Any]:
        """
        Classify ad copy with optional LLM enhancement.
        
        Args:
            text: Ad copy text to analyze
            ad_id: Optional ad identifier
            detailed: Whether to include detailed analysis
            enhanced: Whether to use LLM enhancement (costs money)
            industry: Industry context for LLM analysis
            
        Returns:
            Classification result with optional LLM insights
        """
        # Always run rule-based classification first (free & fast)
        result = self.rule_analyzer.classify(text, ad_id, detailed)
        
        # Add LLM enhancement if requested and available
        if enhanced and self.llm_available and self.enable_llm:
            llm_insights = self._get_llm_insights(text, industry)
            if llm_insights:
                result['llm_insights'] = llm_insights
                result['enhanced'] = True
            else:
                result['llm_error'] = "LLM enhancement failed"
                result['enhanced'] = False
        else:
            result['enhanced'] = False
        
        # Add cost information
        budget_status = self.cost_tracker.get_budget_status()
        result['cost_info'] = {
            'session_spent': budget_status['spent'],
            'budget_remaining': budget_status['remaining'],
            'llm_calls_made': len(self.cost_tracker.call_log)
        }
        
        return result
    
    def classify_batch_enhanced(self, 
                               ads: List[Union[str, Dict[str, str]]],
                               industry: str = None,
                               enhanced_percentage: float = 1.0,
                               max_batch_cost: float = None) -> List[Dict[str, Any]]:
        """
        Classify multiple ads with smart LLM enhancement.
        
        Args:
            ads: List of ad texts or dictionaries
            industry: Industry context for all ads
            enhanced_percentage: Percentage of ads to enhance (0.0-1.0)
            max_batch_cost: Maximum cost for this batch
            
        Returns:
            List of classification results
        """
        results = []
        enhanced_count = 0
        max_enhanced = int(len(ads) * enhanced_percentage)
        
        # Set temporary budget limit for this batch if specified
        original_limit = self.cost_tracker.budget_limit
        if max_batch_cost:
            remaining = self.cost_tracker.budget_limit - self.cost_tracker.total_spent
            batch_limit = min(max_batch_cost, remaining)
            self.cost_tracker.budget_limit = self.cost_tracker.total_spent + batch_limit
        
        try:
            for i, ad in enumerate(ads):
                if isinstance(ad, str):
                    text = ad
                    ad_id = f"batch_ad_{i+1}"
                elif isinstance(ad, dict):
                    text = ad.get('text', '')
                    ad_id = ad.get('ad_id', f"batch_ad_{i+1}")
                    industry = ad.get('industry', industry)  # Per-ad industry override
                else:
                    continue
                
                # Decide whether to enhance this ad
                should_enhance = (
                    enhanced_count < max_enhanced and 
                    self.llm_available and 
                    not self.cost_tracker.is_budget_exceeded()
                )
                
                result = self.classify(
                    text, 
                    ad_id, 
                    detailed=True, 
                    enhanced=should_enhance,
                    industry=industry
                )
                
                if result.get('enhanced'):
                    enhanced_count += 1
                
                results.append(result)
                
                # Stop enhancing if budget is exceeded
                if self.cost_tracker.is_budget_exceeded():
                    print(f"Budget limit reached. Enhanced {enhanced_count}/{len(ads)} ads.")
                    break
        
        finally:
            # Restore original budget limit
            if max_batch_cost:
                self.cost_tracker.budget_limit = original_limit
        
        return results
    
    def _get_llm_insights(self, text: str, industry: str = None) -> Optional[Dict[str, Any]]:
        """
        Get LLM-powered insights for ad copy.
        
        Args:
            text: Ad copy text
            industry: Industry context
            
        Returns:
            LLM insights or None if failed
        """
        if not self.llm_available or self.cost_tracker.is_budget_exceeded():
            return None
        
        # Estimate token usage
        estimated_input_tokens = len(text.split()) * 1.3  # Rough estimate
        estimated_output_tokens = 50  # Small JSON response
        
        # Check if we can afford this call
        if not self.cost_tracker.can_afford(self.default_model, estimated_input_tokens, estimated_output_tokens):
            return None
        
        try:
            # Prepare prompt
            industry_context = f" for a {industry} business" if industry else ""
            
            prompt = f"""Analyze this ad copy{industry_context} and return emotional insights in JSON format:

"{text}"

Return exactly this JSON structure:
{{
    "emotional_tone": "[confident/playful/urgent/trustworthy/serious/friendly]",
    "target_audience": "[young_professionals/families/entrepreneurs/students/seniors/etc]",
    "emotional_intensity": [1-10 scale],
    "brand_personality": "[premium/budget/authoritative/casual/innovative/traditional]",
    "persuasion_approach": "[logical/emotional/social/urgency-based]"
}}"""

            # Make API call
            start_time = time.time()
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1,
                timeout=self.timeout
            )
            call_duration = time.time() - start_time
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                insights = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback: extract key insights even if JSON is malformed
                insights = {
                    "raw_response": response_text,
                    "parsing_error": "Invalid JSON format"
                }
            
            # Log the cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost_entry = self.cost_tracker.log_call(
                self.default_model, 
                input_tokens, 
                output_tokens
            )
            
            # Add metadata
            insights['_metadata'] = {
                'model': self.default_model,
                'cost': cost_entry['cost'],
                'tokens_used': input_tokens + output_tokens,
                'call_duration': round(call_duration, 3),
                'timestamp': datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            print(f"LLM enhancement failed: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_embedding_insights(self, text: str, industry: str = None) -> Optional[Dict[str, Any]]:
        """
        Get insights using text embeddings (ultra cheap option).
        
        Args:
            text: Ad copy text
            industry: Industry context
            
        Returns:
            Embedding-based insights or None if failed
        """
        if not self.llm_available or self.cost_tracker.is_budget_exceeded():
            return None
        
        # Estimate token usage for embeddings
        estimated_tokens = len(text.split()) * 1.2
        
        if not self.cost_tracker.can_afford("text-embedding-3-small", estimated_tokens):
            return None
        
        try:
            # Get embedding
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            embedding = response.data[0].embedding
            
            # Log the cost
            cost_entry = self.cost_tracker.log_call(
                "text-embedding-3-small",
                response.usage.total_tokens,
                0
            )
            
            # Simple analysis based on embedding patterns
            # (This is a simplified example - you could do more sophisticated analysis)
            insights = {
                'embedding_analysis': 'Basic pattern analysis',
                'text_similarity_ready': True,
                'clustering_ready': True,
                '_metadata': {
                    'model': 'text-embedding-3-small',
                    'cost': cost_entry['cost'],
                    'embedding_dimensions': len(embedding),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            return insights
            
        except Exception as e:
            print(f"Embedding analysis failed: {e}")
            return None
    
    def get_cost_report(self) -> Dict[str, Any]:
        """Get detailed cost and usage report."""
        return self.cost_tracker.get_usage_report()
    
    def export_cost_log(self, file_path: str) -> None:
        """Export cost log to file."""
        self.cost_tracker.export_log(file_path)
    
    def reset_budget(self, new_limit: float = None) -> None:
        """Reset cost tracking for new session."""
        self.cost_tracker.reset_session(new_limit)