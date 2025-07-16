#!/usr/bin/env python3
"""
Test script for smart news fetching with country coordinates.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from fetch_news_smart import fetch_single_country_news, get_country_coordinates

def test_country_coordinates():
    """Test country coordinate loading."""
    print("🧪 Testing country coordinates...")
    
    test_countries = ['US', 'CA', 'BR', 'MX', 'GB', 'DE', 'FR', 'CN', 'JP', 'IN', 'AU', 'ZA', 'EG']
    
    for country in test_countries:
        coords = get_country_coordinates(country)
        print(f"  {country}: {coords}")
    
    print("✅ Country coordinates test completed\n")

def test_single_country_fetch():
    """Test fetching a single article from a country."""
    print("🧪 Testing single country fetch...")
    
    # Test with a few countries
    test_cases = [
        ('US', 'Americas'),
        ('GB', 'Europe'),
        ('JP', 'Asia')
    ]
    
    for country, continent in test_cases:
        print(f"  Testing {country} ({continent})...")
        article = fetch_single_country_news(country, continent)
        
        if article:
            print(f"    ✅ Success: {article.get('title', 'No title')[:50]}...")
            print(f"    📍 Coordinates: {article.get('coordinates', 'None')}")
            print(f"    🎯 Precision: {article.get('location_precision', 'None')}")
            print(f"    🌍 Source: {article.get('source_country', 'None')}")
        else:
            print(f"    ❌ Failed to fetch article")
        print()

def main():
    """Main test function."""
    print("🚀 SMART NEWS FETCH TEST")
    print("=" * 50)
    
    # Test country coordinates
    test_country_coordinates()
    
    # Test single country fetch
    test_single_country_fetch()
    
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main() 