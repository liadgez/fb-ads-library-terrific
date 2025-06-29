"""
Test the Ad Copy Analyzer with real Walcott Radio data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adcopy import AdCopyAnalyzer

def test_walcott_radio():
    """Test analyzer with actual Walcott Radio ad copy."""
    
    # Initialize analyzer
    analyzer = AdCopyAnalyzer()
    
    # Real Walcott Radio ad copies from the scraped data
    walcott_ads = [
        {
            "text": "🌪️🇺🇸 Stay connected when it matters most. During extreme weather, a ham radio could be your lifeline. Get prepared now—don't wait until the next storm hits.",
            "ad_id": "walcott_001"
        },
        {
            "text": "We know things can feel a little uncertain right now. That's exactly why we've done the work to be ready. We've built up inventory, organized our warehouse, and streamlined our shipping - so we can get your orders out fast, and keep our prices as low as we can.",
            "ad_id": "walcott_002"
        },
        {
            "text": "Big on CB Radios? 📻🎙 Walcott's One Stop Radio Shop is your go-to place for all CB Radios & Gear. Check out our incredible prices below.",
            "ad_id": "walcott_003"
        },
        {
            "text": "Introducing the Powerhouse of Radios! 💪🏽 🚀 Ranger RCI99N4 - Unmatched at 400 Watts! 🚀 Get ready to experience radio like never before with the Ranger RCI99N4: ✅ 400 Watts of Raw Power ✅ Customize Your Style with a Colorful Faceplate ✅ Crystal-Clear Communication with Echo & Talkback Features",
            "ad_id": "walcott_004"
        },
        {
            "text": "There are a lot of people out there who have issues with or just aren't too sure exactly how to turn on the Stryker 655HPC and Stryker 955HPC radios. Today we take a look on how exactly to power the radio on and what to look for when trying to troubleshoot the issue.",
            "ad_id": "walcott_005"
        }
    ]
    
    print("=== Walcott Radio Ad Copy Analysis ===\\n")
    
    # Analyze each ad individually
    for ad in walcott_ads:
        result = analyzer.classify(ad['text'], ad['ad_id'], detailed=True)
        
        print(f"Ad ID: {result['ad_id']}")
        print(f"Text: {result['original_text'][:100]}...")
        print(f"Typologies: {result['typology_labels']}")
        print(f"Confidence Scores: {result['confidence_scores']}")
        print(f"Buzzwords: {result['buzzwords'][:10]}")  # First 10 buzzwords
        print(f"Word Count: {result['text_features']['word_count']}")
        print("-" * 80)
        print()
    
    # Campaign analysis
    print("=== Campaign-Level Analysis ===\\n")
    campaign_analysis = analyzer.analyze_campaign(walcott_ads, "Walcott Radio Campaign")
    
    print(f"Campaign: {campaign_analysis['campaign_name']}")
    print(f"Total Ads: {campaign_analysis['total_ads']}")
    print(f"Typologies Found: {campaign_analysis['typology_distribution']['typologies_found']}")
    
    # Distribution breakdown
    print("\\nTypology Distribution:")
    for typology, data in campaign_analysis['typology_distribution']['distribution'].items():
        print(f"  {typology}: {data['count']} ads ({data['percentage']}%)")
    
    # Insights
    insights = campaign_analysis['insights']
    print(f"\\nDominant Strategy: {insights['dominant_strategy']['typology']} ({insights['dominant_strategy']['percentage']}%)")
    print(f"Diversity Score: {insights['diversity_score']}")
    print(f"Average Confidence: {insights['avg_confidence']}")
    
    # Recommendations
    print("\\nRecommendations:")
    for rec in campaign_analysis['recommendations']:
        print(f"  • {rec}")
    
    # Export results
    print("\\n=== Exporting Results ===")
    analyzer.export_results(
        campaign_analysis['classification_results'], 
        "walcott_radio_analysis.json",
        format="json"
    )
    print("Results exported to walcott_radio_analysis.json")

if __name__ == "__main__":
    test_walcott_radio()