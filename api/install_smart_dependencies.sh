#!/bin/bash

# Installation script for smart keyword extraction dependencies

echo "Installing smart keyword extraction dependencies..."

# Install Python packages
pip install spacy>=3.7.0
pip install yake>=0.4.8
pip install rake-nltk>=1.0.6
pip install scikit-learn>=1.3.0
pip install wordfreq>=3.0.3
pip install rapidfuzz>=3.0.0
pip install symspellpy>=6.7.7

# Download spaCy English model
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Download NLTK data for RAKE
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"

echo "Installation completed!"
echo "You can now test the smart keyword extraction with: python test_smart_keywords.py"


