"""
Generate Hybrid Results JSON
Creates hybrid analysis results with OpenAI insights for comparison with rule-based results.
"""

import sys
import os
import json
from datetime import datetime

# Add package to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from adcopy import HybridAdCopyAnalyzer

def load_demo_ads():
    """Load the same ads used in the original demo."""
    ads = []
    try:
        with open('demo_input_ads.txt', 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                line = line.strip()
                if line and not line.startswith('#'):
                    ads.append({
                        'text': line,
                        'ad_id': f'ad_{i}',
                        'index': i
                    })
    except FileNotFoundError:
        print("Error: demo_input_ads.txt not found")
        return []
    
    return ads

def generate_hybrid_results():
    """Generate hybrid results with OpenAI insights."""
    print("🤖 GENERATING HYBRID RESULTS WITH OPENAI INSIGHTS")
    print("=" * 60)
    
    # Initialize hybrid analyzer
    analyzer = HybridAdCopyAnalyzer(
        openai_api_key="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",
        enable_llm=True,
        budget_limit=2.00  # $2 budget for full demo
    )
    
    # Load demo ads
    ads = load_demo_ads()
    if not ads:
        return
    
    print(f"Processing {len(ads)} ads with hybrid analysis...")
    print(f"Budget: ${analyzer.cost_tracker.budget_limit}")
    print()
    
    results = []
    enhanced_count = 0
    
    for i, ad in enumerate(ads):
        print(f"Processing ad {i+1}/{len(ads)}: {ad['text'][:50]}...")
        
        # Get hybrid analysis
        result = analyzer.classify(
            ad['text'],
            ad_id=ad['ad_id'],
            detailed=True,
            enhanced=True,  # Request LLM enhancement
            industry="Mixed"  # General industry context
        )
        
        # Structure the result for JSON output
        hybrid_result = {
            "ad_id": ad['ad_id'],
            "original_text": ad['text'],
            "clean_text": result.get('clean_text', ad['text']),
            "typology_labels": result['typology_labels'],
            "typology_count": result['typology_count'],
            "confidence_scores": result.get('confidence_scores', {}),
            "text_features": result.get('text_features', {}),
            "enhanced": result.get('enhanced', False),
            "cost_info": result.get('cost_info', {})
        }
        
        # Add LLM insights if available
        if result.get('enhanced') and 'llm_insights' in result:
            insights = result['llm_insights']
            hybrid_result['llm_insights'] = {
                "emotional_tone": insights.get('emotional_tone', 'unknown'),
                "target_audience": insights.get('target_audience', 'unknown'),
                "emotional_intensity": insights.get('emotional_intensity', 0),
                "brand_personality": insights.get('brand_personality', 'unknown'),
                "persuasion_approach": insights.get('persuasion_approach', 'unknown'),
                "metadata": insights.get('_metadata', {})
            }
            enhanced_count += 1
        else:
            hybrid_result['llm_insights'] = None
            hybrid_result['llm_error'] = result.get('llm_error', 'Enhancement not available')
        
        results.append(hybrid_result)
        
        # Show progress
        current_cost = analyzer.cost_tracker.total_spent
        print(f"  Enhanced: {result.get('enhanced', False)}")
        print(f"  Cost so far: ${current_cost:.6f}")
        
        # Check budget
        if analyzer.cost_tracker.is_budget_exceeded():
            print("Budget limit reached!")
            break
        
        print()
    
    # Add summary metadata
    cost_report = analyzer.get_cost_report()
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "total_ads": len(results),
        "enhanced_ads": enhanced_count,
        "analysis_type": "hybrid_with_openai",
        "cost_summary": {
            "total_spent": cost_report['total_spent'],
            "budget_limit": cost_report['budget_limit'],
            "budget_remaining": cost_report['budget_remaining'],
            "calls_made": cost_report['calls_made'],
            "average_cost_per_call": cost_report.get('average_cost_per_call', 0)
        },
        "models_used": list(cost_report.get('models_used', {}).keys())
    }
    
    # Create final output
    output = {
        "metadata": metadata,
        "results": results
    }
    
    # Save to JSON file
    output_file = "hybrid_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("=" * 60)
    print("✅ HYBRID RESULTS GENERATED")
    print("=" * 60)
    print(f"File saved: {output_file}")
    print(f"Total ads processed: {len(results)}")
    print(f"Enhanced with LLM: {enhanced_count}")
    print(f"Total cost: ${cost_report['total_spent']:.6f}")
    print(f"Average cost per ad: ${cost_report['total_spent']/len(results):.6f}")
    
    # Export detailed cost log
    cost_log_file = f"hybrid_cost_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    analyzer.export_cost_log(cost_log_file)
    print(f"Cost log exported: {cost_log_file}")

if __name__ == "__main__":
    generate_hybrid_results()