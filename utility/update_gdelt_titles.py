"""
Script to update GDELT events with scraped article titles from source URLs.
This will enhance the GDELT data with actual article titles instead of generic ones.
"""

import sqlite3
import time
import random
from news_scraper import scrape_gdelt_article_title

def update_gdelt_titles():
    """Update GDELT events with scraped article titles."""
    conn = sqlite3.connect('gdelt_events.db')
    c = conn.cursor()
    
    # Get all GDELT events that have source URLs but no scraped titles
    c.execute('''
        SELECT event_id, source_url, translated_title 
        FROM gdelt_events 
        WHERE source_url IS NOT NULL 
        AND source_url != '' 
        AND scraped_title IS NULL
        LIMIT 50
    ''')
    
    events = c.fetchall()
    print(f"Found {len(events)} events to update with scraped titles")
    
    updated_count = 0
    failed_count = 0
    
    for i, (event_id, source_url, translated_title) in enumerate(events):
        print(f"Processing {i+1}/{len(events)}: Event {event_id}")
        print(f"  URL: {source_url}")
        
        try:
            # Scrape the title from the source URL
            scraped_title = scrape_gdelt_article_title(source_url)
            
            if scraped_title:
                # Update the database with the scraped title
                c.execute('''
                    UPDATE gdelt_events 
                    SET scraped_title = ?, title_updated_at = datetime('now')
                    WHERE event_id = ?
                ''', (scraped_title, event_id))
                
                print(f"  ✅ Scraped title: {scraped_title[:80]}...")
                updated_count += 1
            else:
                print(f"  ⚠️  Could not scrape title")
                failed_count += 1
            
            # Add a delay to be respectful to servers
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            print(f"  ❌ Error scraping title: {e}")
            failed_count += 1
            continue
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"\n✅ Update complete!")
    print(f"  Updated: {updated_count} events")
    print(f"  Failed: {failed_count} events")

def add_scraped_title_column():
    """Add scraped_title column to the database if it doesn't exist."""
    conn = sqlite3.connect('gdelt_events.db')
    c = conn.cursor()
    
    # Check if column exists
    c.execute("PRAGMA table_info(gdelt_events)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'scraped_title' not in columns:
        print("Adding scraped_title column to database...")
        c.execute('''
            ALTER TABLE gdelt_events 
            ADD COLUMN scraped_title TEXT
        ''')
        
        c.execute('''
            ALTER TABLE gdelt_events 
            ADD COLUMN title_updated_at DATETIME
        ''')
        
        conn.commit()
        print("✅ Added scraped_title and title_updated_at columns")
    else:
        print("✅ scraped_title column already exists")
    
    conn.close()

def show_title_stats():
    """Show statistics about title sources in the database."""
    conn = sqlite3.connect('gdelt_events.db')
    c = conn.cursor()
    
    # Count different title types
    c.execute('''
        SELECT 
            COUNT(*) as total_events,
            COUNT(CASE WHEN scraped_title IS NOT NULL THEN 1 END) as with_scraped_title,
            COUNT(CASE WHEN translated_title IS NOT NULL THEN 1 END) as with_translated_title,
            COUNT(CASE WHEN scraped_title IS NULL AND translated_title IS NULL THEN 1 END) as no_title
        FROM gdelt_events
    ''')
    
    stats = c.fetchone()
    total, scraped, translated, none = stats
    
    print(f"\n📊 GDELT Title Statistics:")
    print(f"  Total events: {total}")
    print(f"  With scraped titles: {scraped} ({scraped/total*100:.1f}%)")
    print(f"  With translated titles: {translated} ({translated/total*100:.1f}%)")
    print(f"  No title: {none} ({none/total*100:.1f}%)")
    
    # Show some example scraped titles
    c.execute('''
        SELECT event_id, scraped_title, translated_title 
        FROM gdelt_events 
        WHERE scraped_title IS NOT NULL 
        LIMIT 5
    ''')
    
    examples = c.fetchall()
    if examples:
        print(f"\n📝 Example scraped titles:")
        for event_id, scraped, translated in examples:
            print(f"  Event {event_id}:")
            print(f"    Scraped: {scraped}")
            if translated:
                print(f"    Translated: {translated}")
            print()
    
    conn.close()

if __name__ == "__main__":
    print("🔄 GDELT Title Scraper")
    print("=" * 50)
    
    # Add column if needed
    add_scraped_title_column()
    
    # Show current stats
    show_title_stats()
    
    # Ask user if they want to proceed
    response = input("\nDo you want to scrape titles for GDELT events? (y/n): ")
    if response.lower() in ['y', 'yes']:
        update_gdelt_titles()
        show_title_stats()
    else:
        print("Skipping title scraping.") 