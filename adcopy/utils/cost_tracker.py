"""
OpenAI Cost Tracking Utilities
Monitors and controls LLM usage costs with budget limits and detailed logging.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class OpenAICostTracker:
    """Track OpenAI API costs with budget controls."""
    
    # OpenAI pricing as of 2024 (per 1K tokens)
    PRICING = {
        "text-embedding-3-small": 0.00002,
        "text-embedding-3-large": 0.00013,
        "gpt-4o-mini": {
            "input": 0.000150,
            "output": 0.000600
        },
        "gpt-4o": {
            "input": 0.0050,
            "output": 0.0150
        },
        "gpt-3.5-turbo": {
            "input": 0.0005,
            "output": 0.0015
        }
    }
    
    def __init__(self, budget_limit: float = 5.00, session_name: str = None):
        """
        Initialize cost tracker.
        
        Args:
            budget_limit: Maximum spend limit in USD
            session_name: Optional name for this session
        """
        self.budget_limit = budget_limit
        self.session_name = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.total_spent = 0.0
        self.call_log = []
        self.started_at = datetime.now()
        
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int = 0) -> float:
        """
        Estimate cost for a potential API call.
        
        Args:
            model: OpenAI model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens (for completion models)
            
        Returns:
            Estimated cost in USD
        """
        if model in ["text-embedding-3-small", "text-embedding-3-large"]:
            return (input_tokens / 1000) * self.PRICING[model]
        
        elif model in self.PRICING and isinstance(self.PRICING[model], dict):
            pricing = self.PRICING[model]
            input_cost = (input_tokens / 1000) * pricing["input"]
            output_cost = (output_tokens / 1000) * pricing["output"]
            return input_cost + output_cost
        
        else:
            # Default estimate for unknown models
            return (input_tokens / 1000) * 0.001
    
    def can_afford(self, model: str, estimated_input_tokens: int, estimated_output_tokens: int = 50) -> bool:
        """
        Check if we can afford a potential API call.
        
        Args:
            model: OpenAI model name
            estimated_input_tokens: Estimated input tokens
            estimated_output_tokens: Estimated output tokens
            
        Returns:
            True if within budget, False otherwise
        """
        estimated_cost = self.estimate_cost(model, estimated_input_tokens, estimated_output_tokens)
        return (self.total_spent + estimated_cost) <= self.budget_limit
    
    def log_call(self, 
                 model: str, 
                 input_tokens: int, 
                 output_tokens: int = 0,
                 actual_cost: float = None) -> Dict[str, Any]:
        """
        Log an API call and its cost.
        
        Args:
            model: OpenAI model used
            input_tokens: Actual input tokens used
            output_tokens: Actual output tokens generated
            actual_cost: Actual cost if available from API
            
        Returns:
            Log entry dictionary
        """
        if actual_cost is None:
            actual_cost = self.estimate_cost(model, input_tokens, output_tokens)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': actual_cost,
            'cumulative_cost': self.total_spent + actual_cost
        }
        
        self.total_spent += actual_cost
        self.call_log.append(log_entry)
        
        return log_entry
    
    def get_usage_report(self) -> Dict[str, Any]:
        """
        Generate a detailed usage report.
        
        Returns:
            Usage statistics and cost breakdown
        """
        if not self.call_log:
            return {
                'session_name': self.session_name,
                'total_spent': 0.0,
                'budget_limit': self.budget_limit,
                'budget_remaining': self.budget_limit,
                'calls_made': 0,
                'session_duration': str(datetime.now() - self.started_at)
            }
        
        # Calculate statistics
        models_used = {}
        for call in self.call_log:
            model = call['model']
            if model not in models_used:
                models_used[model] = {'calls': 0, 'cost': 0.0, 'tokens': 0}
            models_used[model]['calls'] += 1
            models_used[model]['cost'] += call['cost']
            models_used[model]['tokens'] += call['input_tokens'] + call['output_tokens']
        
        return {
            'session_name': self.session_name,
            'started_at': self.started_at.isoformat(),
            'session_duration': str(datetime.now() - self.started_at),
            'total_spent': round(self.total_spent, 6),
            'budget_limit': self.budget_limit,
            'budget_remaining': round(self.budget_limit - self.total_spent, 6),
            'budget_used_percentage': round((self.total_spent / self.budget_limit) * 100, 2),
            'calls_made': len(self.call_log),
            'average_cost_per_call': round(self.total_spent / len(self.call_log), 6),
            'models_used': models_used,
            'cost_breakdown': self.call_log[-5:] if len(self.call_log) > 5 else self.call_log  # Last 5 calls
        }
    
    def is_budget_exceeded(self) -> bool:
        """Check if budget has been exceeded."""
        return self.total_spent >= self.budget_limit
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status."""
        remaining = self.budget_limit - self.total_spent
        percentage_used = (self.total_spent / self.budget_limit) * 100
        
        status = "OK"
        if percentage_used >= 90:
            status = "CRITICAL"
        elif percentage_used >= 75:
            status = "WARNING"
        elif percentage_used >= 50:
            status = "CAUTION"
        
        return {
            'status': status,
            'spent': round(self.total_spent, 6),
            'remaining': round(remaining, 6),
            'limit': self.budget_limit,
            'percentage_used': round(percentage_used, 2)
        }
    
    def export_log(self, file_path: str) -> None:
        """
        Export call log to JSON file.
        
        Args:
            file_path: Path to save the log file
        """
        report = self.get_usage_report()
        report['full_call_log'] = self.call_log
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    
    def reset_session(self, new_budget_limit: float = None) -> None:
        """
        Reset the tracker for a new session.
        
        Args:
            new_budget_limit: Optional new budget limit
        """
        if new_budget_limit is not None:
            self.budget_limit = new_budget_limit
            
        self.total_spent = 0.0
        self.call_log = []
        self.started_at = datetime.now()
        self.session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"