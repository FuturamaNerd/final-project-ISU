from helper.database import NewsDatabase

# Create database instance
db = NewsDatabase()

# Add some test countries and news
test_news = {
    'articles': [
        {
            'title': 'Test News from United States',
            'url': 'https://example.com/us-news', 
            'seendate': '2025-06-21',
            'domain': 'example.com',
            'language': 'EN'
        },
        {
            'title': 'Test News from United Kingdom',
            'url': 'https://example.com/uk-news',
            'seendate': '2025-06-21',
            'domain': 'example.com',
            'language': 'EN'
        },
        {
            'title': 'Test News from China',
            'url': 'https://example.com/china-news',
            'seendate': '2025-06-21',
            'domain': 'example.com',
            'language': 'EN'
        }
    ]
}

# Add test data
db.add_news('United States', test_news)
db.add_news('United Kingdom', test_news)
db.add_news('China', test_news)

print("Test data added successfully!")
print("Now visit http://localhost:5000/ to see the cards.") 