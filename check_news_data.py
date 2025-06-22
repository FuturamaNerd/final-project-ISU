from helper.database import NewsDatabase

db = NewsDatabase()

print("=== Checking News Data ===")
all_news = db.get_all_news()
print(f"Total news articles: {len(all_news)}")

if all_news:
    print("\nFirst 3 news articles:")
    for i, news in enumerate(all_news[:3]):
        print(f"{i+1}. Country: {news['country']}, Continent: {news['continent']}")
        print(f"   Title: {news['title']}")
        print(f"   URL: {news['url']}")
        print()

print("=== Checking Recent News ===")
recent_news = db.get_most_recent_news(3)
print(f"Recent news articles: {len(recent_news)}")

if recent_news:
    print("\nRecent news details:")
    for i, news in enumerate(recent_news):
        print(f"{i+1}. Country: {news['country']}, Continent: {news['continent']}")
        print(f"   Title: {news['title']}")
        print()
else:
    print("No recent news found!") 