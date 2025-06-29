# Ad Copy Analyzer 🎯

A powerful standalone tool for analyzing advertising copy typologies and persuasion patterns. Built for marketers, researchers, and developers who want to understand what makes ad copy effective.

🌐 **[VIEW LIVE DEMO →](https://your-username.github.io/ad-copy-analyzer/enhanced_comparison_app.html)**

## Features ✨

### 🔧 Rule-Based Analysis (Free)
- **8 Core Typologies**: Classify ads into proven persuasion strategies
- **Multi-Label Classification**: Ads can have multiple typology labels
- **Batch Processing**: Analyze hundreds of ads at once
- **Campaign Analysis**: Get insights across entire campaigns
- **Pattern Matching**: Rule-based classification with YAML configuration
- **Export Options**: JSON and CSV export formats
- **Zero Cost**: Completely free analysis

### 🤖 Hybrid Analysis (OpenAI Enhanced)
- **All rule-based features** PLUS:
- **Emotional Tone Analysis**: confident, urgent, playful, trustworthy
- **Target Audience Insights**: young professionals, families, entrepreneurs
- **Emotional Intensity**: 1-10 scale emotional impact rating
- **Brand Personality**: premium, budget, authoritative, casual
- **Cost**: ~$0.000059 per ad (less than 6¢ per 1000 ads)

## Quick Start 🚀

### Installation

```bash
# Clone the repository
git clone https://github.com/adanalytics/ad-copy-analyzer.git
cd ad-copy-analyzer

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### Basic Usage

```python
from adcopy import AdCopyAnalyzer, HybridAdCopyAnalyzer

# Rule-based analysis (Free)
analyzer = AdCopyAnalyzer()
result = analyzer.classify("Last chance! Save 50% today only!")
print(result['typology_labels'])
# Output: ['Urgency / Scarcity', 'Value Proposition / Deal']

# Hybrid analysis with OpenAI enhancement
hybrid_analyzer = HybridAdCopyAnalyzer(
    openai_api_key="your-api-key",
    budget_limit=5.00
)

# Enhanced analysis with emotional insights
enhanced_result = hybrid_analyzer.classify(
    "Feel confident and beautiful with our premium skincare routine!",
    enhanced=True,
    industry="Beauty"
)

print(enhanced_result['typology_labels'])
# Output: ['Emotional Appeal', 'Aspirational / Lifestyle']

print(enhanced_result['llm_insights'])
# Output: {
#   'emotional_tone': 'confident',
#   'target_audience': 'young_professionals', 
#   'emotional_intensity': 7,
#   'brand_personality': 'premium'
# }
```

## Typologies 📋

The analyzer recognizes 8 core persuasion typologies:

1. **Urgency / Scarcity** - "Last chance!", "Limited time"
2. **Social Proof** - "Join thousands", "5-star rated"  
3. **Emotional Appeal** - "Feel beautiful", "Transform your life"
4. **Value Proposition** - "Save 50%", "Best price"
5. **Problem / Solution** - "Tired of X? Try Y", "Finally, a solution"
6. **Aspirational / Lifestyle** - "Effortless elegance", "Live your best life"
7. **Instructional / How-To** - "Learn how", "3 steps to success"
8. **Brand Voice / Meta** - "We get it", "Not your average product"

## API Reference 📖

### AdCopyAnalyzer

Main interface for ad copy analysis.

#### Methods

- `classify(text, ad_id=None, detailed=False)` - Classify single ad copy
- `classify_batch(ads, detailed=False)` - Process multiple ads
- `analyze_campaign(ads, campaign_name=None)` - Full campaign analysis
- `get_typology_guide()` - Get information about typologies
- `validate_setup()` - Check configuration validity
- `export_results(results, output_path, format='json')` - Export results

#### Example Response

```python
{
    'ad_id': 'ad_001',
    'original_text': 'Last chance! Save 50% today only!',
    'typology_labels': ['Urgency / Scarcity', 'Value Proposition / Deal'],
    'typology_count': 2,
    'confidence_scores': {
        'urgency_scarcity': 1.8,
        'value_proposition': 1.0
    },
    'text_features': {
        'word_count': 6,
        'exclamation_count': 1,
        'caps_ratio': 0.12
    }
}
```

## Configuration ⚙️

### Custom Rules

Create custom typology rules in YAML format:

```yaml
typologies:
  custom_typology:
    name: "Custom Persuasion Type"
    description: "Description of the typology"
    patterns:
      - regex: "(?i)\\b(custom pattern)\\b"
        weight: 1.0
    threshold: 0.8
```

### Analyzer Configuration

```python
config = {
    'min_confidence': 0.5,
    'include_features': True,
    'normalize_scores': True
}

analyzer = AdCopyAnalyzer(config=config)
```

## Integration Examples 🔧

### With Pandas DataFrames

```python
import pandas as pd
from adcopy import AdCopyAnalyzer

# Load ad data
df = pd.read_csv('ad_campaigns.csv')
analyzer = AdCopyAnalyzer()

# Classify all ads
results = analyzer.classify_batch(df['ad_text'].tolist())

# Add results to DataFrame
df['typologies'] = [r['typology_labels'] for r in results]
df['typology_count'] = [r['typology_count'] for r in results]
```

### With Flask API

```python
from flask import Flask, request, jsonify
from adcopy import AdCopyAnalyzer

app = Flask(__name__)
analyzer = AdCopyAnalyzer()

@app.route('/classify', methods=['POST'])
def classify_ad():
    data = request.json
    result = analyzer.classify(data['text'])
    return jsonify(result)

@app.route('/analyze-campaign', methods=['POST'])
def analyze_campaign():
    data = request.json
    analysis = analyzer.analyze_campaign(data['ads'])
    return jsonify(analysis)
```

### With Existing Facebook Ads Scraper

```python
# In your existing Facebook scraper project
from adcopy import AdCopyAnalyzer

# Initialize analyzer
analyzer = AdCopyAnalyzer()

# After scraping ad data
for ad in scraped_ads:
    # Classify the ad copy
    classification = analyzer.classify(ad['primary_text'])
    
    # Add typology data to your ad record
    ad['typologies'] = classification['typology_labels']
    ad['persuasion_score'] = classification['typology_count']
```

## Performance Analysis 📊

Combine with performance data for insights:

```python
# Assuming you have CTR data
ads_with_performance = [
    {"text": "Save 50% today!", "ctr": 0.045, "cpa": 12.50},
    {"text": "Join thousands of users", "ctr": 0.032, "cpa": 15.20}
]

# Classify and correlate
for ad in ads_with_performance:
    result = analyzer.classify(ad['text'])
    ad['typologies'] = result['typology_labels']

# Analyze performance by typology
typology_performance = {}
for ad in ads_with_performance:
    for typology in ad['typologies']:
        if typology not in typology_performance:
            typology_performance[typology] = {'ctr': [], 'cpa': []}
        typology_performance[typology]['ctr'].append(ad['ctr'])
        typology_performance[typology]['cpa'].append(ad['cpa'])
```

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

- 📧 Email: support@adanalytics.com
- 🐛 Issues: [GitHub Issues](https://github.com/adanalytics/ad-copy-analyzer/issues)
- 📖 Documentation: [Full Docs](https://ad-copy-analyzer.readthedocs.io/)

---

**Made for marketers who want to understand what makes copy convert** 🎯