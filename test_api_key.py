#!/usr/bin/env python3
"""
Test script to check NewsAPI key status and usage.
"""

import requests
import json
from config import NEWS_API_KEY

def test_api_key():
    """Test the NewsAPI key with a simple request."""
    
    print(f"API Key: {NEWS_API_KEY[:10]}...{NEWS_API_KEY[-10:]}")
    
    # Test with a simple request to US (should work)
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': 'us',
        'apiKey': NEWS_API_KEY,
        'pageSize': 1
    }
    
    try:
        print("\nTesting API key with US news...")
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Key is working!")
            print(f"Status: {data.get('status')}")
            print(f"Total Results: {data.get('totalResults', 0)}")
            if data.get('articles'):
                print(f"First Article: {data['articles'][0].get('title', 'No title')[:50]}...")
        else:
            print("❌ API Key error!")
            print(f"Error Response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"Error Code: {error_data.get('code')}")
                print(f"Error Message: {error_data.get('message')}")
            except:
                print("Could not parse error response")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

def check_api_usage():
    """Check API usage limits."""
    print("\n" + "="*50)
    print("API USAGE INFORMATION:")
    print("="*50)
    print("Free tier limits:")
    print("- 100 requests per day")
    print("- Articles have 24-hour delay")
    print("- No extra requests available")
    print("\nTo check your usage:")
    print("1. Go to https://newsapi.org/account")
    print("2. Log in with your API key")
    print("3. Check your daily usage")

if __name__ == "__main__":
    test_api_key()
    check_api_usage() 