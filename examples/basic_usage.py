"""
Basic Usage Examples for Ad Copy Analyzer
Demonstrates how to use the analyzer for common tasks.
"""

from adcopy import AdCopyAnalyzer

def basic_classification():
    """Example of basic ad copy classification."""
    print("=== Basic Classification Example ===")
    
    # Initialize analyzer
    analyzer = AdCopyAnalyzer()
    
    # Classify a single ad
    ad_text = "Last chance! Save 50% on premium software. Join thousands of satisfied customers!"
    result = analyzer.classify(ad_text)
    
    print(f"Ad Text: {ad_text}")
    print(f"Typologies Found: {result['typology_labels']}")
    print(f"Number of Typologies: {result['typology_count']}")
    print()

def detailed_analysis():
    """Example of detailed analysis with metadata."""
    print("=== Detailed Analysis Example ===")
    
    analyzer = AdCopyAnalyzer()
    
    ad_text = "Tired of juggling receipts? Try our simple expense tracking solution today!"
    result = analyzer.classify(ad_text, detailed=True)
    
    print(f"Ad Text: {ad_text}")
    print(f"Typologies: {result['typology_labels']}")
    print(f"Buzzwords: {result['buzzwords']}")
    print(f"CTA Phrases: {result['cta_phrases']}")
    print(f"Word Count: {result['text_features']['word_count']}")
    print()

def batch_processing():
    """Example of processing multiple ads in batch."""
    print("=== Batch Processing Example ===")
    
    analyzer = AdCopyAnalyzer()
    
    # Sample ads from different brands/campaigns
    ads = [
        "Save 40% on luxury skincare - limited time offer!",
        {"text": "Join over 10,000 happy customers using our fitness app", "ad_id": "fitness_001"},
        "Learn the 5 secrets successful entrepreneurs don't want you to know",
        "Effortless meal planning for busy professionals",
        "Stop wasting time on complex tools. Try our simple solution!"
    ]
    
    results = analyzer.classify_batch(ads)
    
    print("Batch Classification Results:")
    for i, result in enumerate(results):
        print(f"Ad {i+1}: {result['typology_labels']}")
    print()

def campaign_analysis():
    """Example of comprehensive campaign analysis."""
    print("=== Campaign Analysis Example ===")
    
    analyzer = AdCopyAnalyzer()
    
    # Sample campaign ads
    summer_sale_ads = [
        "Last 3 days! Save up to 70% on summer favorites",
        "Join thousands who've already upgraded their wardrobe", 
        "Tired of boring outfits? Discover your perfect style",
        "Premium quality fabrics at unbeatable prices",
        "Transform your look with our styling experts' tips",
        "Free shipping on orders over $50 - today only!",
        "See why fashion bloggers are obsessed with our new collection"
    ]
    
    analysis = analyzer.analyze_campaign(summer_sale_ads, "Summer Sale 2025")
    
    print(f"Campaign: {analysis['campaign_name']}")
    print(f"Total Ads: {analysis['total_ads']}")
    print(f"Typologies Found: {analysis['typology_distribution']['typologies_found']}")
    print(f"Dominant Strategy: {analysis['insights']['dominant_strategy']['typology']}")
    print(f"Diversity Score: {analysis['insights']['diversity_score']}")
    
    print("\\nRecommendations:")
    for rec in analysis['recommendations']:
        print(f"- {rec}")
    print()

def typology_guide():
    """Example of getting typology information."""
    print("=== Available Typologies Guide ===")
    
    analyzer = AdCopyAnalyzer()
    guide = analyzer.get_typology_guide()
    
    print(f"Total Typologies Available: {guide['total_typologies']}")
    print("\\nTypologies:")
    
    for key, info in guide['typologies'].items():
        print(f"• {info['name']}")
        print(f"  Description: {info['description']}")
        print(f"  Patterns: {info['pattern_count']}")
        print()

def validation_check():
    """Example of validating analyzer setup."""
    print("=== Validation Check Example ===")
    
    analyzer = AdCopyAnalyzer()
    validation = analyzer.validate_setup()
    
    print(f"Setup Valid: {validation['valid']}")
    print(f"Typologies Loaded: {validation['typologies_loaded']}")
    print(f"Version: {validation['version']}")
    
    if validation['errors']:
        print("Errors found:")
        for error in validation['errors']:
            print(f"- {error}")
    else:
        print("No configuration errors found!")
    print()

if __name__ == "__main__":
    # Run all examples
    basic_classification()
    detailed_analysis()
    batch_processing()
    campaign_analysis()
    typology_guide()
    validation_check()
    
    print("=== Export Example ===")
    # Example of exporting results
    analyzer = AdCopyAnalyzer()
    ads = ["Sample ad 1", "Sample ad 2", "Sample ad 3"]
    results = analyzer.classify_batch(ads, detailed=True)
    
    # Export to JSON
    analyzer.export_results(results, "sample_results.json", format="json")
    print("Results exported to sample_results.json")
    
    # Export to CSV  
    analyzer.export_results(results, "sample_results.csv", format="csv")
    print("Results exported to sample_results.csv")