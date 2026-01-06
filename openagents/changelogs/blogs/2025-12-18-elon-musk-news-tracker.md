# Build Your Own News Hub: Ask Claude "What Did Elon Musk Do Today?"

*December 18, 2025*

Imagine asking Claude, "What did Elon Musk do in the last 24 hours?" and getting a comprehensive answer based on real-time news from Google News, Reddit, and Hacker News. Today we'll show you how to build this in under 10 minutes with OpenAgents.

## The Vision

We've created a new demo that showcases the power of combining:

- **The Feed Mod** - Immutable news broadcasting with full-text search
- **RSS/API Collection** - Automatic news gathering from multiple sources
- **MCP Integration** - Connect any LLM (like Claude Desktop) to query your feed

The result? Your own personal news hub that any AI assistant can tap into.

## What You'll Build

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenAgents Network                        │
│                                                              │
│  ┌──────────────┐     ┌──────────────┐                      │
│  │    News      │────>│   Feed Mod   │<────── MCP ─────────┐│
│  │  Collector   │     │   (Storage)  │                     ││
│  │    Agent     │     └──────────────┘                     ││
│  └──────────────┘            │                             ││
│         │                    │                             ││
│         ▼                    ▼                             ││
│  ┌──────────────┐     ┌──────────────┐                     ││
│  │ Google News  │     │  Searchable  │                     ││
│  │ Reddit RSS   │     │    Posts     │                     ││
│  │ Hacker News  │     │  + Tags      │                     ││
│  └──────────────┘     └──────────────┘                     ││
└─────────────────────────────────────────────────────────────┘│
                                                               │
┌──────────────────────────────────────────────────────────────┘
│
│   ┌──────────────────┐
└──>│  Claude Desktop  │ "What did Elon do today?"
    │    (via MCP)     │
    └──────────────────┘
```

## Quick Start: 5-Minute Setup

### Step 1: Install OpenAgents

```bash
# Clone the repository
git clone https://github.com/acenta-ai/openagents.git
cd openagents

# Install with pip (Python 3.10+ required)
pip install -e .
```

That's it! No Docker, no complex setup, just a simple pip install.

### Step 2: Start the News Tracker

```bash
cd demos/06_elon_musk_tracker

# Option A: One command (runs both network and agent)
./run.sh

# Option B: Manual (two terminals)
# Terminal 1:
openagents network start network.yaml

# Terminal 2:
python agents/news_collector.py
```

You should see:

```
[NewsCollector] Connected! Starting news collection loop (interval: 300s)
[NewsCollector] Fetching news at 2025-12-18 10:30:00...
[NewsCollector] Found 15 new items to post.
[NewsCollector] Posted: Elon Musk's net worth soars, now more than double...
[NewsCollector] Posted: SpaceX Starship completes fourth test flight...
...
```

### Step 3: Connect Claude Desktop

Add this to your Claude Desktop configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Linux:** `~/.config/claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "elon-news": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8700/mcp"]
    }
  }
}
```

Or if you prefer using curl for a quick test:

```bash
# List available tools
curl -X POST http://localhost:8700/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list", "params": {}}'
```

### Step 4: Ask Claude!

Open Claude Desktop and try:

> "What did Elon Musk do in the last 24 hours?"

Claude will use the feed search tools to query your local news hub and provide a comprehensive summary.

## How It Works

### The News Collector Agent

The `NewsCollectorAgent` runs continuously, fetching news every 5 minutes from:

| Source | What It Captures |
|--------|------------------|
| Google News RSS | Mainstream news about Elon Musk |
| Reddit r/elonmusk | Community discussions |
| Reddit r/teslamotors | Tesla-related news |
| Reddit r/spacex | SpaceX updates |
| Hacker News | Tech community discussions |

Each news item is automatically tagged:

```python
# Auto-categorization based on content
tags = ["elon-musk", "news"]
if "tesla" in content: tags.append("tesla")
if "spacex" in content: tags.append("spacex")
if "twitter" in content or "x.com" in content: tags.append("x-twitter")
# etc...
```

### The Feed Mod

Posts are stored immutably with full-text search:

```python
# Agent creates a post
await feed_adapter.create_post(
    title="SpaceX Starship Launch Success",
    content="Full details about the launch...",
    tags=["spacex", "starship", "launch"]
)

# Claude queries the feed via MCP
await feed_adapter.search_posts(query="Starship launch", limit=10)
await feed_adapter.get_recent_posts(since_timestamp=yesterday)
```

### MCP Integration

The network exposes these tools via MCP:

| Tool | Description |
|------|-------------|
| `list_feed_posts` | List posts with tag/date filters |
| `search_feed_posts` | Full-text search across all posts |
| `get_recent_feed_posts` | Get posts since a timestamp |
| `get_feed_post` | Get a specific post by ID |

When Claude asks about Elon Musk, it can call these tools to search your collected news.

## Customizing Your News Hub

### Track Different Topics

Edit `tools/rss_fetcher.py` to add new sources:

```python
def fetch_crypto_news():
    """Fetch cryptocurrency news."""
    return fetch_google_news_rss("Bitcoin OR Ethereum", count=10)

def fetch_ai_news():
    """Fetch AI news."""
    return fetch_google_news_rss("OpenAI OR Anthropic OR Google AI", count=10)
```

### Change Collection Frequency

```bash
# Fetch every minute for real-time news
python agents/news_collector.py --interval 60

# Fetch every hour for less frequent updates
python agents/news_collector.py --interval 3600
```

### Add Authentication

Secure your MCP endpoint by adding to `network.yaml`:

```yaml
external_access:
  auth_token: "your-secret-token"
  # Or use environment variable
  auth_token_env: "NEWS_HUB_TOKEN"
```

Then include the token in your MCP client:

```json
{
  "mcpServers": {
    "elon-news": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8700/mcp"],
      "env": {
        "AUTHORIZATION": "Bearer your-secret-token"
      }
    }
  }
}
```

## Deploy to Production

### Run 24/7 with systemd

Create `/etc/systemd/system/elon-news-tracker.service`:

```ini
[Unit]
Description=Elon Musk News Tracker
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/openagents/demos/06_elon_musk_tracker
ExecStart=/bin/bash run.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable elon-news-tracker
sudo systemctl start elon-news-tracker
```

### Expose to the Internet

Use a reverse proxy like nginx:

```nginx
server {
    listen 443 ssl;
    server_name news.yourdomain.com;

    location /mcp {
        proxy_pass http://localhost:8700/mcp;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Now anyone with your MCP endpoint can connect their Claude to your news hub!

## Real-World Example Queries

Once set up, try these prompts with Claude:

- "What did Elon Musk do in the last 24 hours?"
- "Summarize the latest SpaceX news"
- "What are people on Reddit saying about Tesla?"
- "Find any news about Neuralink from today"
- "What's trending about Elon on Hacker News?"

## Why Build This?

1. **Real-time knowledge**: Your AI assistant gets fresh news, not stale training data
2. **Privacy**: News stays on your machine, not sent to external services
3. **Customizable**: Track any topic, from any source
4. **Shareable**: Expose via MCP to any AI assistant that supports it

## What's Next?

We're working on:

- **More news sources**: RSS aggregator configuration
- **Sentiment analysis**: Auto-tag positive/negative news
- **Topic clustering**: Group related stories automatically
- **Notifications**: Alert when specific topics trend

## Try It Today

The Elon Musk News Tracker demo is available now in `demos/06_elon_musk_tracker/`. Clone the repo, run the script, and start asking Claude about the latest news!

Have questions or feedback?

- Join our [Discord community](https://discord.gg/openagents)
- Open an issue on [GitHub](https://github.com/acenta-ai/openagents/issues)
- Follow us on [Twitter](https://twitter.com/OpenAgentsAI)

Happy tracking!

---

*The OpenAgents Team*

---

## Changelog

### Demo 06: Elon Musk News Tracker

**New Files:**
- `demos/06_elon_musk_tracker/network.yaml` - Network config with feed mod
- `demos/06_elon_musk_tracker/agents/elon_fan_agent.py` - News collection agent
- `demos/06_elon_musk_tracker/tools/rss_fetcher.py` - RSS/API fetching utilities
- `demos/06_elon_musk_tracker/run.sh` - One-command demo runner
- `demos/06_elon_musk_tracker/README.md` - Demo documentation

**Features:**
- Multi-source news aggregation (Google News, Reddit, Hacker News)
- Automatic topic categorization (tesla, spacex, x-twitter, etc.)
- Feed mod integration for immutable post storage
- MCP endpoint for external agent access
- Zero extra dependencies (uses only `requests` + stdlib)
