"""
Ad Copy Analyzer - Comprehensive Demo
Showcases all capabilities with real-world ad examples and professional reporting.
"""

import sys
import os
import json
import random
from datetime import datetime

# Add the package to path for demo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from adcopy import AdCopyAnalyzer

def load_demo_ads(file_path):
    """Load ad copies from input file."""
    ads = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    ads.append({
                        'text': line,
                        'ad_id': f'demo_ad_{i+1:02d}',
                        # Simulate performance data for demo
                        'ctr': round(random.uniform(0.5, 4.5), 3),
                        'cpa': round(random.uniform(8.50, 45.00), 2),
                        'spend': round(random.uniform(100, 5000), 2),
                        'industry': random.choice(['E-commerce', 'SaaS', 'Fitness', 'Beauty', 'Finance', 'Education'])
                    })
    except FileNotFoundError:
        print(f"Error: Could not find input file {file_path}")
        return []
    
    return ads

def generate_performance_insights(ads, results):
    """Generate performance insights by correlating typologies with mock performance data."""
    typology_performance = {}
    
    for ad, result in zip(ads, results):
        for typology in result['typology_labels']:
            if typology not in typology_performance:
                typology_performance[typology] = {'ctr': [], 'cpa': [], 'spend': []}
            
            typology_performance[typology]['ctr'].append(ad['ctr'])
            typology_performance[typology]['cpa'].append(ad['cpa'])
            typology_performance[typology]['spend'].append(ad['spend'])
    
    # Calculate averages
    performance_analysis = {}
    for typology, metrics in typology_performance.items():
        if metrics['ctr']:  # Only if we have data
            performance_analysis[typology] = {
                'avg_ctr': round(sum(metrics['ctr']) / len(metrics['ctr']), 3),
                'avg_cpa': round(sum(metrics['cpa']) / len(metrics['cpa']), 2),
                'total_spend': round(sum(metrics['spend']), 2),
                'ad_count': len(metrics['ctr'])
            }
    
    return performance_analysis

def create_demo_report(ads, results, campaign_analysis, performance_analysis, output_file):
    """Generate comprehensive demo report."""
    
    report_lines = []
    
    # Header
    report_lines.extend([
        "=" * 80,
        "AD COPY ANALYZER - COMPREHENSIVE DEMO REPORT",
        "=" * 80,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total Ads Analyzed: {len(ads)}",
        f"Analysis Duration: <1 second",
        "",
        ""
    ])
    
    # Section 1: Individual Ad Analysis
    report_lines.extend([
        "SECTION 1: INDIVIDUAL AD ANALYSIS",
        "-" * 40,
        ""
    ])
    
    for i, (ad, result) in enumerate(zip(ads, results), 1):
        report_lines.extend([
            f"AD #{i:02d} - {result['ad_id']}",
            f"Text: {ad['text']}",
            f"Industry: {ad['industry']}",
            f"Typologies: {', '.join(result['typology_labels'])} ({result['typology_count']} total)",
            f"Top Confidence Scores: {dict(sorted(result['confidence_scores'].items(), key=lambda x: x[1], reverse=True)[:3])}",
            f"Text Features: {result['text_features']['word_count']} words, {result['text_features']['exclamation_count']} exclamations",
            f"Performance: {ad['ctr']}% CTR, ${ad['cpa']} CPA, ${ad['spend']} spend",
            ""
        ])
    
    # Section 2: Campaign-Level Insights
    report_lines.extend([
        "",
        "SECTION 2: CAMPAIGN-LEVEL INSIGHTS",
        "-" * 40,
        ""
    ])
    
    distribution = campaign_analysis['typology_distribution']
    insights = campaign_analysis['insights']
    
    report_lines.extend([
        f"Campaign Overview:",
        f"  • Total Typologies Found: {distribution['typologies_found']}",
        f"  • Diversity Score: {insights['diversity_score']} (higher = more varied strategies)",
        f"  • Average Labels per Ad: {distribution['summary']['avg_labels_per_ad']}",
        f"  • Ads with No Classification: {distribution['summary']['ads_with_no_labels']}",
        "",
        "Typology Distribution:"
    ])
    
    for typology, data in sorted(distribution['distribution'].items(), key=lambda x: x[1]['count'], reverse=True):
        report_lines.append(f"  • {typology}: {data['count']} ads ({data['percentage']}%) - Avg Confidence: {data['average_confidence']}")
    
    report_lines.extend(["", "Co-occurrence Patterns:"])
    co_occur = distribution.get('co_occurrence', {})
    if co_occur:
        for pair, data in sorted(co_occur.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            report_lines.append(f"  • {pair}: {data['count']} ads ({data['percentage']}%)")
    else:
        report_lines.append("  • No significant co-occurrence patterns found")
    
    # Section 3: Performance Correlation
    report_lines.extend([
        "",
        "",
        "SECTION 3: PERFORMANCE CORRELATION ANALYSIS",
        "-" * 40,
        "(Based on simulated performance data for demo purposes)",
        ""
    ])
    
    # Sort by CTR performance
    sorted_performance = sorted(performance_analysis.items(), key=lambda x: x[1]['avg_ctr'], reverse=True)
    
    report_lines.extend([
        "Typology Performance Ranking (by CTR):",
        ""
    ])
    
    for i, (typology, metrics) in enumerate(sorted_performance, 1):
        report_lines.extend([
            f"{i}. {typology}",
            f"   Average CTR: {metrics['avg_ctr']}%",
            f"   Average CPA: ${metrics['avg_cpa']}",
            f"   Total Spend: ${metrics['total_spend']:,.2f}",
            f"   Sample Size: {metrics['ad_count']} ads",
            ""
        ])
    
    # Section 4: Strategic Recommendations
    report_lines.extend([
        "",
        "SECTION 4: STRATEGIC RECOMMENDATIONS",
        "-" * 40,
        ""
    ])
    
    recommendations = campaign_analysis['recommendations']
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"{i}. {rec}")
    
    # Add custom insights based on analysis
    custom_insights = []
    
    # Best performing typology
    if sorted_performance:
        best_typology = sorted_performance[0]
        custom_insights.append(f"Focus on '{best_typology[0]}' - highest CTR at {best_typology[1]['avg_ctr']}%")
    
    # Diversity insight
    if insights['diversity_score'] < 0.4:
        custom_insights.append("Low diversity detected - consider testing more varied persuasion strategies")
    elif insights['diversity_score'] > 0.8:
        custom_insights.append("High diversity detected - consider focusing on top-performing strategies")
    
    # Multi-label insight
    avg_labels = distribution['summary']['avg_labels_per_ad']
    if avg_labels > 2:
        custom_insights.append("Strong multi-strategy approach - good persuasion layering")
    
    if custom_insights:
        report_lines.extend(["", "Additional Insights:"])
        for i, insight in enumerate(custom_insights, len(recommendations) + 1):
            report_lines.append(f"{i}. {insight}")
    
    # Section 5: Technical Details
    report_lines.extend([
        "",
        "",
        "SECTION 5: TECHNICAL ANALYSIS",
        "-" * 40,
        ""
    ])
    
    # Calculate technical stats
    all_scores = []
    for result in results:
        all_scores.extend(result['confidence_scores'].values())
    
    word_counts = [result['text_features']['word_count'] for result in results]
    
    report_lines.extend([
        "Processing Statistics:",
        f"  • Total Confidence Scores Generated: {len(all_scores)}",
        f"  • Average Confidence Score: {sum(all_scores)/len(all_scores):.3f}" if all_scores else "  • No confidence scores available",
        f"  • Classification Success Rate: {(len(ads) - distribution['summary']['ads_with_no_labels'])/len(ads)*100:.1f}%",
        "",
        "Text Analysis:",
        f"  • Average Words per Ad: {sum(word_counts)/len(word_counts):.1f}",
        f"  • Shortest Ad: {min(word_counts)} words",
        f"  • Longest Ad: {max(word_counts)} words",
        "",
        "Pattern Matching:",
        f"  • Total Typologies Available: 8",
        f"  • Typologies Detected: {distribution['typologies_found']}",
        f"  • Multi-label Classification: {sum(1 for r in results if r['typology_count'] > 1)} ads"
    ])
    
    # Footer
    report_lines.extend([
        "",
        "",
        "=" * 80,
        "END OF DEMO REPORT",
        "",
        "This demo showcases the Ad Copy Analyzer's ability to:",
        "✓ Classify ads into 8 persuasion typologies",
        "✓ Handle multi-label classification",
        "✓ Provide campaign-level insights", 
        "✓ Generate performance correlations",
        "✓ Offer strategic recommendations",
        "✓ Process diverse ad copy formats",
        "",
        "For integration into your projects:",
        "from adcopy import AdCopyAnalyzer",
        "analyzer = AdCopyAnalyzer()",
        "result = analyzer.classify('Your ad copy here')",
        "",
        "=" * 80
    ])
    
    # Write report to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\\n'.join(report_lines))

def main():
    """Run the comprehensive demo."""
    print("🎯 Starting Ad Copy Analyzer Comprehensive Demo...")
    
    # Initialize analyzer
    analyzer = AdCopyAnalyzer()
    
    # Load demo ads
    print("📖 Loading demo ads...")
    ads = load_demo_ads('demo_input_ads.txt')
    if not ads:
        print("❌ Failed to load demo ads. Please ensure demo_input_ads.txt exists.")
        return
    
    print(f"✅ Loaded {len(ads)} demo ads")
    
    # Run comprehensive analysis
    print("🔍 Running comprehensive analysis...")
    
    # Individual classification
    results = analyzer.classify_batch([ad['text'] for ad in ads], detailed=True)
    
    # Campaign analysis
    campaign_analysis = analyzer.analyze_campaign([ad['text'] for ad in ads], "Demo Campaign")
    
    # Performance correlation (simulated)
    performance_analysis = generate_performance_insights(ads, results)
    
    print("✅ Analysis complete!")
    
    # Generate report
    print("📊 Generating comprehensive report...")
    create_demo_report(ads, results, campaign_analysis, performance_analysis, 'demo_output_report.txt')
    
    # Export data
    print("💾 Exporting data...")
    analyzer.export_results(results, 'demo_results.json', 'json')
    analyzer.export_results(results, 'demo_results.csv', 'csv')
    
    print("🎉 Demo complete! Generated files:")
    print("  📄 demo_output_report.txt - Comprehensive analysis report")
    print("  📊 demo_results.json - Detailed JSON results")
    print("  📈 demo_results.csv - CSV export for spreadsheet analysis")
    
    # Quick preview
    print("\\n📋 Quick Preview:")
    total_typologies = len(campaign_analysis['typology_distribution']['distribution'])
    dominant = campaign_analysis['insights']['dominant_strategy']
    print(f"  • {len(ads)} ads analyzed across {total_typologies} typologies")
    print(f"  • Dominant strategy: {dominant['typology']} ({dominant['percentage']}%)")
    print(f"  • Diversity score: {campaign_analysis['insights']['diversity_score']}")

if __name__ == "__main__":
    main()