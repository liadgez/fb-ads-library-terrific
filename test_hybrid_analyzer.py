"""
Test Hybrid Ad Copy Analyzer with OpenAI Integration
Demonstrates cost-controlled LLM enhancement capabilities.
"""

import sys
import os
from datetime import datetime

# Add package to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from adcopy import HybridAdCopyAnalyzer
    print("✅ Successfully imported HybridAdCopyAnalyzer")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Installing dependencies...")
    os.system("pip install openai")
    from adcopy import HybridAdCopyAnalyzer

def test_basic_functionality():
    """Test basic hybrid analyzer functionality."""
    print("=" * 60)
    print("1. BASIC HYBRID ANALYZER TEST")
    print("=" * 60)
    
    # Initialize with your OpenAI key and small budget
    analyzer = HybridAdCopyAnalyzer(
        openai_api_key="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",
        enable_llm=True,
        budget_limit=1.00  # Start with $1 budget
    )
    
    print(f"LLM Available: {analyzer.llm_available}")
    print(f"Budget Limit: ${analyzer.cost_tracker.budget_limit}")
    print()
    
    # Test rule-based only (free)
    print("Testing rule-based classification (free):")
    result = analyzer.classify("Last chance! Save 70% today only!")
    print(f"  Typologies: {result['typology_labels']}")
    print(f"  Enhanced: {result['enhanced']}")
    print(f"  Cost: ${result['cost_info']['session_spent']}")
    print()

def test_llm_enhancement():
    """Test LLM enhancement with cost tracking."""
    print("=" * 60)
    print("2. LLM ENHANCEMENT TEST")
    print("=" * 60)
    
    analyzer = HybridAdCopyAnalyzer(
        openai_api_key="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",
        budget_limit=0.50  # $0.50 budget for testing
    )
    
    test_ads = [
        {
            'text': "Feel confident and beautiful with our premium skincare routine!",
            'industry': "Beauty"
        },
        {
            'text': "Join 50,000+ entrepreneurs who transformed their business",
            'industry': "SaaS"
        },
        {
            'text': "Limited time: Save 80% on professional tools",
            'industry': "E-commerce"
        }
    ]
    
    print(f"Testing {len(test_ads)} ads with LLM enhancement...")
    print(f"Budget: ${analyzer.cost_tracker.budget_limit}")
    print()
    
    for i, ad in enumerate(test_ads, 1):
        print(f"Ad {i}: {ad['text'][:50]}...")
        
        # Get enhanced analysis
        result = analyzer.classify(
            ad['text'],
            ad_id=f"test_ad_{i}",
            detailed=True,
            enhanced=True,  # This costs money!
            industry=ad['industry']
        )
        
        print(f"  Rule-based: {result['typology_labels']}")
        
        if result['enhanced'] and 'llm_insights' in result:
            insights = result['llm_insights']
            print(f"  LLM Tone: {insights.get('emotional_tone', 'N/A')}")
            print(f"  Target: {insights.get('target_audience', 'N/A')}")
            print(f"  Intensity: {insights.get('emotional_intensity', 'N/A')}/10")
            
            if '_metadata' in insights:
                meta = insights['_metadata']
                print(f"  Cost: ${meta['cost']:.6f}")
                print(f"  Tokens: {meta['tokens_used']}")
        else:
            print(f"  LLM: Failed or disabled")
        
        print(f"  Total Spent: ${result['cost_info']['session_spent']:.6f}")
        print()
        
        # Check budget status
        budget_status = analyzer.cost_tracker.get_budget_status()
        if budget_status['status'] in ['WARNING', 'CRITICAL']:
            print(f"⚠️  Budget Status: {budget_status['status']} ({budget_status['percentage_used']:.1f}% used)")
            
        if analyzer.cost_tracker.is_budget_exceeded():
            print("🛑 Budget limit reached!")
            break

def test_cost_monitoring():
    """Test detailed cost monitoring features."""
    print("=" * 60)
    print("3. COST MONITORING TEST")
    print("=" * 60)
    
    analyzer = HybridAdCopyAnalyzer(
        openai_api_key="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",
        budget_limit=0.25  # Small budget
    )
    
    # Test a few ads
    test_ads = [
        "Amazing results! Join thousands of satisfied customers",
        "Limited offer - don't miss out on this deal!",
        "Premium quality at unbeatable prices"
    ]
    
    print("Running enhanced analysis on sample ads...")
    
    for i, ad in enumerate(test_ads, 1):
        if not analyzer.cost_tracker.is_budget_exceeded():
            result = analyzer.classify(ad, enhanced=True, industry="E-commerce")
            print(f"Ad {i}: Enhanced = {result['enhanced']}")
    
    # Get detailed cost report
    print("\\nDetailed Cost Report:")
    report = analyzer.get_cost_report()
    
    print(f"  Session Duration: {report['session_duration']}")
    print(f"  Total Spent: ${report['total_spent']:.6f}")
    print(f"  Budget Remaining: ${report['budget_remaining']:.6f}")
    print(f"  Calls Made: {report['calls_made']}")
    
    if report['calls_made'] > 0:
        print(f"  Avg Cost/Call: ${report['average_cost_per_call']:.6f}")
        print(f"  Models Used: {list(report['models_used'].keys())}")
    
    # Export cost log
    log_file = f"cost_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    analyzer.export_cost_log(log_file)
    print(f"\\nCost log exported to: {log_file}")

def test_batch_processing():
    """Test cost-controlled batch processing."""
    print("=" * 60)
    print("4. BATCH PROCESSING TEST")
    print("=" * 60)
    
    analyzer = HybridAdCopyAnalyzer(
        openai_api_key="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",
        budget_limit=0.30
    )
    
    # Batch of ads
    batch_ads = [
        {"text": "Save 50% on premium software today!", "industry": "SaaS"},
        {"text": "Transform your skin with our proven routine", "industry": "Beauty"},
        {"text": "Join millions using our fitness app", "industry": "Fitness"},
        {"text": "Limited time: Free shipping on all orders", "industry": "E-commerce"},
        {"text": "Learn investing secrets from top pros", "industry": "Finance"}
    ]
    
    print(f"Processing {len(batch_ads)} ads with smart enhancement...")
    print(f"Budget: ${analyzer.cost_tracker.budget_limit}")
    
    # Process with cost controls
    results = analyzer.classify_batch_enhanced(
        batch_ads,
        enhanced_percentage=0.6,  # Enhance 60% of ads
        max_batch_cost=0.20      # Max $0.20 for this batch
    )
    
    enhanced_count = sum(1 for r in results if r.get('enhanced'))
    total_cost = analyzer.cost_tracker.total_spent
    
    print(f"\\nResults:")
    print(f"  Ads Processed: {len(results)}")
    print(f"  Enhanced: {enhanced_count}")
    print(f"  Total Cost: ${total_cost:.6f}")
    print(f"  Average Cost: ${total_cost/len(results):.6f} per ad")

def main():
    """Run all hybrid analyzer tests."""
    print("🤖 HYBRID AD COPY ANALYZER - OPENAI INTEGRATION TEST")
    print("Testing cost-controlled LLM enhancement capabilities")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        test_basic_functionality()
        test_llm_enhancement()
        test_cost_monitoring()
        test_batch_processing()
        
        print("=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("Key Features Demonstrated:")
        print("  ✓ Rule-based classification (free)")
        print("  ✓ Optional LLM enhancement (paid)")
        print("  ✓ Real-time cost tracking")
        print("  ✓ Budget limits and controls")
        print("  ✓ Graceful fallback on errors")
        print("  ✓ Batch processing with cost optimization")
        print()
        print("💡 Integration Example:")
        print("from adcopy import HybridAdCopyAnalyzer")
        print("analyzer = HybridAdCopyAnalyzer(openai_api_key='your-key', budget_limit=5.00)")
        print("result = analyzer.classify('Your ad copy', enhanced=True)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()