#!/usr/bin/env python3
"""
Installation script for spaCy and its English language model.
Run this script to set up NER functionality.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def download_spacy_model():
    """Download the spaCy English language model."""
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✅ Successfully downloaded spaCy English model")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download spaCy model: {e}")
        return False

def test_spacy():
    """Test if spaCy is working correctly."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        
        # Test with a sample text
        text = "Barack Obama lives in Washington D.C. and works at the White House."
        doc = nlp(text)
        
        locations = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC', 'FAC']]
        
        print("✅ spaCy test successful!")
        print(f"Sample text: {text}")
        print(f"Extracted locations: {locations}")
        return True
        
    except Exception as e:
        print(f"❌ spaCy test failed: {e}")
        return False

def main():
    """Main installation function."""
    print("🚀 INSTALLING SPACY FOR NER FUNCTIONALITY")
    print("=" * 50)
    
    # Install required packages
    packages = [
        "spacy==3.7.2",
        "flask-pymongo==2.3.0",
        "requests==2.31.0"
    ]
    
    print("\n📦 Installing required packages...")
    for package in packages:
        install_package(package)
    
    print("\n🌍 Downloading spaCy English language model...")
    download_spacy_model()
    
    print("\n🧪 Testing spaCy installation...")
    if test_spacy():
        print("\n🎉 Installation completed successfully!")
        print("\nYou can now:")
        print("1. Run 'python process_articles_with_ner.py' to process your articles")
        print("2. Start your Flask app with 'python app.py'")
        print("3. Visit '/locations' to see articles with extracted locations")
    else:
        print("\n❌ Installation failed. Please check the error messages above.")
        print("You may need to:")
        print("1. Update pip: python -m pip install --upgrade pip")
        print("2. Install Visual C++ build tools (on Windows)")
        print("3. Try installing spaCy manually: pip install spacy")

if __name__ == "__main__":
    main() 