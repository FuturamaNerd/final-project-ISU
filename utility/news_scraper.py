from newspaper import Article
import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None

def scrape_article_metadata(url, timeout=10):
    """
    Scrape article title and metadata from a URL.
    Returns a dictionary with title, description, and other metadata.
    """
    try:
        # Add a small delay to be respectful to servers
        time.sleep(random.uniform(0.5, 1.5))
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to extract title from various common selectors
        title = None
        title_selectors = [
            'title',
            'h1',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            'meta[name="title"]',
            '.headline',
            '.title',
            '.article-title',
            '[class*="title"]',
            '[class*="headline"]'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                if selector.startswith('meta'):
                    content = element.get('content')
                    title = str(content).strip() if content else ''
                else:
                    title = element.get_text().strip()
                if title and len(title) > 10:  # Ensure it's a meaningful title
                    break
        
        # Try to extract description
        description = None
        desc_selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]',
            'meta[name="twitter:description"]',
            '.description',
            '.summary',
            '.excerpt',
            '[class*="description"]',
            '[class*="summary"]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                if selector.startswith('meta'):
                    content = element.get('content')
                    description = str(content).strip() if content else ''
                else:
                    description = element.get_text().strip()
                if description and len(description) > 20:
                    break
        
        # If no description found, try to get first paragraph
        if not description:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 50 and len(text) < 500:  # Reasonable length for description
                    description = text
                    break
        
        return {
            'title': title,
            'description': description,
            'url': url,
            'scraped_successfully': True
        }
        
    except Exception as e:
        print(f"Failed to scrape metadata from {url}: {e}")
        return {
            'title': None,
            'description': None,
            'url': url,
            'scraped_successfully': False,
            'error': str(e)
        }

def scrape_gdelt_article_title(url):
    """
    Simplified function to just get the title from a GDELT article URL.
    Returns the title string or None if failed.
    """
    metadata = scrape_article_metadata(url)
    return metadata.get('title') if metadata.get('scraped_successfully') else None 