"""
Setup script for Ad Copy Analyzer
Standalone tool for analyzing advertising copy typologies and persuasion patterns.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Ad Copy Typology Analyzer - A tool for analyzing advertising copy patterns."

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name="ad-copy-analyzer",
    version="1.0.0",
    author="Ad Intelligence Team",
    author_email="contact@adanalytics.com",
    description="Standalone tool for analyzing advertising copy typologies and persuasion patterns",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/adanalytics/ad-copy-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Marketing Professionals",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Office/Business :: Marketing"
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    include_package_data=True,
    package_data={
        'adcopy': [
            'config/*.yml',
            'config/*.yaml'
        ]
    },
    entry_points={
        'console_scripts': [
            'adcopy-analyze=adcopy.cli:main',
        ],
    },
    keywords="advertising, marketing, nlp, text-analysis, typology, persuasion, copy-analysis",
    project_urls={
        "Bug Reports": "https://github.com/adanalytics/ad-copy-analyzer/issues",
        "Source": "https://github.com/adanalytics/ad-copy-analyzer",
        "Documentation": "https://ad-copy-analyzer.readthedocs.io/"
    }
)