"""
Market Scanner Module
Integrates multiple intelligence sources (Google News, Reddit, Hacker News)
to provide comprehensive market research data for AI Agents.
"""

import requests
import xml.etree.ElementTree as ET
import re
import json
import time
from html import unescape
from datetime import datetime

# === Configuration ===
# Headers are crucial for Reddit to avoid 429/403 errors
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# === Helper Functions ===

def clean_html(text):
    """Removes HTML tags and entities from descriptions."""
    if not text: 
        return ""
    # Remove standard HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode entities like &amp; -> &
    text = unescape(text)
    # Collapse whitespace
    return re.sub(r'\s+', ' ', text).strip()

def safe_request(url, params=None, retries=2):
    """Robust request wrapper with retries."""
    for i in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                time.sleep(2) # Wait if rate limited
        except Exception as e:
            print(f"Request error ({url}): {e}")
    return None

# === Source 1: Google News RSS (General Trends) ===
def fetch_google_news(query, count=5):
    print(f"  -> Scanning Google News for '{query}'...")
    try:
        encoded_query = requests.utils.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        response = safe_request(url)
        if not response: return []

        root = ET.fromstring(response.content)
        items = []
        
        for item in root.findall(".//item")[:count]:
            items.append({
                "source": "Google News",
                "title": item.findtext("title", "N/A"),
                "date": item.findtext("pubDate", "N/A"),
                "link": item.findtext("link", ""),
                "snippet": clean_html(item.findtext("description", ""))[:300]
            })
        return items
    except Exception as e:
        print(f"Error parsing Google RSS: {e}")
        return []

# === Source 2: Reddit RSS (Real User Complaints/Feedback) ===
def fetch_reddit(query, count=5):
    print(f"  -> Scanning Reddit for '{query}'...")
    try:
        # Use general search RSS to find discussions across all subreddits
        encoded_query = requests.utils.quote(query)
        url = f"https://www.reddit.com/search.rss?q={encoded_query}&sort=relevance&t=year"
        
        response = safe_request(url)
        if not response: return []

        root = ET.fromstring(response.content)
        # Reddit RSS uses Atom namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        items = []
        
        for entry in root.findall("atom:entry", ns)[:count]:
            content_html = entry.findtext("atom:content", "", ns)
            items.append({
                "source": "Reddit",
                "title": entry.findtext("atom:title", "N/A", ns),
                "link": entry.find("atom:link", ns).attrib.get("href", ""),
                "date": entry.findtext("atom:updated", "N/A", ns),
                "snippet": clean_html(content_html)[:300] # Get real user comments
            })
        return items
    except Exception as e:
        print(f"Error parsing Reddit RSS: {e}")
        return []

# === Source 3: Hacker News API (Technical/Innovation Perspectives) ===
def fetch_hackernews(query, count=5):
    print(f"  -> Scanning Hacker News for '{query}'...")
    try:
        url = "https://hn.algolia.com/api/v1/search"
        params = {"query": query, "tags": "story", "hitsPerPage": count}
        
        response = safe_request(url, params=params)
        if not response: return []

        data = response.json()
        items = []
        
        for hit in data.get("hits", []):
            items.append({
                "source": "Hacker News",
                "title": hit.get("title", "N/A"),
                "link": hit.get("url", ""),
                "date": hit.get("created_at", "N/A"),
                "snippet": f"Points: {hit.get('points')} | Comments: {hit.get('num_comments')} | Author: {hit.get('author')}"
            })
        return items
    except Exception as e:
        print(f"Error parsing HN API: {e}")
        return []

# === Main Aggregator Function ===
def get_market_intel(topic):
    """
    Main entry point. Fetches data from all sources and returns JSON string.
    """
    print(f"--- Starting Market Scanner for: {topic} ---")
    
    # 1. Fetch from all sources
    google_data = fetch_google_news(topic, count=4)
    reddit_data = fetch_reddit(topic, count=3)
    hn_data = fetch_hackernews(topic, count=3)
    
    # 2. Combine
    combined_data = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "summary_counts": {
            "google_news": len(google_data),
            "reddit": len(reddit_data),
            "hacker_news": len(hn_data)
        },
        "intelligence": google_data + reddit_data + hn_data
    }
    
    # 3. Return JSON string (for easy printing in Agent)
    return json.dumps(combined_data, indent=2)

# Allow local testing
if __name__ == "__main__":
    # Test run
    print(get_market_intel("AI Pin"))