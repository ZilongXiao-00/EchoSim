# custom_tools/market_scanner.py

import requests
import xml.etree.ElementTree as ET
import re
import json
import time
from html import unescape
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def clean_html(text):
    if not text: return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    return re.sub(r'\s+', ' ', text).strip()

def safe_request(url, params=None):
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        return response if response.status_code == 200 else None
    except:
        return None

def fetch_google_news(query, count=3):
    encoded = requests.utils.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    resp = safe_request(url)
    if not resp: return []
    root = ET.fromstring(resp.content)
    return [{"source": "Google News", "title": i.findtext("title"), "snippet": clean_html(i.findtext("description"))[:200]} for i in root.findall(".//item")[:count]]

def fetch_reddit(query, count=3):
    encoded = requests.utils.quote(query)
    url = f"https://www.reddit.com/search.rss?q={encoded}&sort=relevance&t=year"
    resp = safe_request(url)
    if not resp: return []
    root = ET.fromstring(resp.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    return [{"source": "Reddit", "title": e.findtext("atom:title", "", ns), "snippet": clean_html(e.findtext("atom:content", "", ns))[:200]} for e in root.findall("atom:entry", ns)[:count]]

def fetch_hackernews(query, count=3):
    url = "https://hn.algolia.com/api/v1/search"
    resp = safe_request(url, params={"query": query, "tags": "story", "hitsPerPage": count})
    if not resp: return []
    return [{"source": "HN", "title": h.get("title"), "snippet": f"Points: {h.get('points')}"} for h in resp.json().get("hits", [])]

# === 核心入口函数 ===
def get_market_intel(query: str) -> str:
    """
    Scans Google News, Reddit, and Hacker News for a topic.
    Returns a JSON string summary.
    """
    print(f"DEBUG: Agent is scanning for '{query}'...")
    results = []
    results.extend(fetch_google_news(query))
    results.extend(fetch_reddit(query))
    results.extend(fetch_hackernews(query))
    
    if not results:
        return json.dumps({"error": "No data found", "topic": query})
        
    return json.dumps({"topic": query, "intelligence": results}, indent=2)