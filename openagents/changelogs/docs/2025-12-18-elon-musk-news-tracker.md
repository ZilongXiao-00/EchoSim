# Elon Musk News Tracker: Complete Setup Guide

This guide walks you through setting up an OpenAgents network as an information hub that continuously collects news about Elon Musk, then connecting Claude (or any MCP-compatible AI) to query the collected news.

## Overview

The Elon Musk News Tracker demonstrates:

1. **Network with Feed Mod** - Immutable post storage with full-text search
2. **Worker Agent** - Python-based agent that collects news from RSS/APIs
3. **MCP Transport** - External access for AI assistants like Claude Desktop

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Git (for cloning the repository)

## Installation

### Step 1: Clone and Install OpenAgents

```bash
# Clone the repository
git clone https://github.com/acenta-ai/openagents.git
cd openagents

# Install OpenAgents
pip install -e .

# Verify installation
openagents --version
```

### Step 2: Verify Demo Files

```bash
ls demos/06_elon_musk_tracker/
```

Expected structure:

```
demos/06_elon_musk_tracker/
├── network.yaml           # Network configuration
├── run.sh                 # One-command runner
├── README.md              # Demo documentation
├── agents/
│   ├── __init__.py
│   └── elon_fan_agent.py  # News collection agent
└── tools/
    ├── __init__.py
    └── rss_fetcher.py     # RSS/API utilities
```

## Running the Demo

### Option A: Single Command

```bash
cd demos/06_elon_musk_tracker
./run.sh
```

This starts both the network and the collector agent.

### Option B: Manual Start (Two Terminals)

**Terminal 1 - Start Network:**

```bash
cd demos/06_elon_musk_tracker
openagents network start network.yaml
```

Expected output:

```
INFO:openagents:Starting network: ElonMuskTracker
INFO:openagents:HTTP transport listening on 0.0.0.0:8700
INFO:openagents:gRPC transport listening on 0.0.0.0:8600
INFO:openagents:MCP endpoint available at http://localhost:8700/mcp
INFO:openagents:Loaded mod: openagents.mods.workspace.feed
```

**Terminal 2 - Start Agent:**

```bash
cd demos/06_elon_musk_tracker
python agents/news_collector.py
```

Expected output:

```
[NewsCollector] Connected! Starting news collection loop (interval: 300s)
[NewsCollector] Fetching news at 2025-12-18 10:30:00...
[NewsCollector] Found 12 new items to post.
[NewsCollector] Posted: Elon Musk's net worth soars...
```

## Network Configuration

### network.yaml Reference

```yaml
network:
  name: "ElonMuskTracker"
  mode: "centralized"
  node_id: "elon-tracker-1"

  transports:
    - type: "http"
      config:
        port: 8700
        serve_studio: true   # Web UI at http://localhost:8700
        serve_mcp: true      # MCP at http://localhost:8700/mcp
    - type: "grpc"
      config:
        port: 8600

  mods:
    - name: "openagents.mods.workspace.feed"
      enabled: true
      config:
        max_title_length: 200
        max_content_length: 50000
        enable_search: true
        categories:
          - "news"
          - "elon-musk"
          - "tesla"
          - "spacex"
          - "x-twitter"
          - "neuralink"
```

### Key Configuration Options

| Option | Description |
|--------|-------------|
| `serve_mcp: true` | Enables MCP endpoint for external agents |
| `serve_studio: true` | Enables web UI for monitoring |
| `enable_search: true` | Enables full-text search in feed mod |

## Agent Configuration

### NewsCollectorAgent

The agent is implemented as a `WorkerAgent` with a continuous collection loop:

```python
class NewsCollectorAgent(WorkerAgent):
    default_agent_id = "elon-news-collector"

    def __init__(self, fetch_interval: int = 300, **kwargs):
        super().__init__(**kwargs)
        self.fetch_interval = fetch_interval
        self.posted_hashes = set()  # Deduplication

    async def on_startup(self):
        self._collection_task = asyncio.create_task(self._collection_loop())

    async def _collection_loop(self):
        while True:
            await self._fetch_and_broadcast_news()
            await asyncio.sleep(self.fetch_interval)
```

### Command Line Options

```bash
python agents/news_collector.py --help

Options:
  --host TEXT      Network host (default: localhost)
  --port INTEGER   Network port (default: 8700)
  --interval INT   Fetch interval in seconds (default: 300)
```

## News Sources

The `rss_fetcher.py` module fetches from:

| Source | Function | Description |
|--------|----------|-------------|
| Google News | `fetch_google_news_rss()` | Mainstream news RSS |
| Reddit | `fetch_reddit_rss()` | Subreddit feeds (r/elonmusk, r/teslamotors, r/spacex) |
| Hacker News | `fetch_hackernews_search()` | Algolia API search |

### Adding Custom Sources

```python
# tools/rss_fetcher.py

def fetch_custom_rss(url: str, count: int = 10) -> List[Dict]:
    """Fetch from any RSS feed."""
    response = requests.get(url, timeout=15)
    root = ET.fromstring(response.content)

    items = []
    for item in root.findall(".//item")[:count]:
        items.append({
            "title": item.findtext("title", ""),
            "link": item.findtext("link", ""),
            "description": item.findtext("description", ""),
            "published_date": item.findtext("pubDate", ""),
            "feed_source": "custom"
        })
    return items
```

## Connecting Claude Desktop

### Claude Desktop Configuration

#### macOS

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

#### Linux

Edit `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "elon-news-tracker": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8700/mcp"
      ]
    }
  }
}
```

#### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "elon-news-tracker": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8700/mcp"
      ]
    }
  }
}
```

### Restart Claude Desktop

After saving the config, restart Claude Desktop. You should see "elon-news-tracker" in the MCP servers list.

### Example Queries

Once connected, try these prompts:

| Query | What Claude Does |
|-------|------------------|
| "What did Elon Musk do today?" | Calls `get_recent_feed_posts` then summarizes |
| "Search for SpaceX news" | Calls `search_feed_posts` with query "SpaceX" |
| "Show me Tesla-related news" | Calls `list_feed_posts` with tag filter "tesla" |
| "Get the latest 5 posts" | Calls `list_feed_posts` with limit 5 |

## MCP Tools Reference

### Tools Exposed via MCP

| Tool | Parameters | Description |
|------|------------|-------------|
| `list_feed_posts` | `limit`, `offset`, `tags`, `sort_by` | List posts with filters |
| `search_feed_posts` | `query`, `limit` | Full-text search |
| `get_recent_feed_posts` | `since_timestamp`, `limit` | Get posts since timestamp |
| `get_feed_post` | `post_id` | Get specific post |

### Example Tool Calls

```python
# Via MCP protocol
{
    "method": "tools/call",
    "params": {
        "name": "search_feed_posts",
        "arguments": {
            "query": "SpaceX launch",
            "limit": 10
        }
    }
}
```

## Adding Authentication

### Configure Auth Token

Edit `network.yaml`:

```yaml
external_access:
  # Option 1: Direct token
  auth_token: "your-secret-token-here"

  # Option 2: From environment variable
  auth_token_env: "ELON_NEWS_AUTH_TOKEN"
```

### Update Claude Desktop Config

```json
{
  "mcpServers": {
    "elon-news-tracker": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8700/mcp"
      ],
      "env": {
        "MCP_HEADERS": "Authorization:Bearer your-secret-token-here"
      }
    }
  }
}
```

## Publishing Your Network

### Local Network (Same Machine)

No additional configuration needed. Use `localhost:8700`.

### LAN Network (Same Local Network)

1. Find your machine's IP:
   ```bash
   ip addr  # Linux
   ifconfig # macOS
   ```

2. Configure Claude Desktop with your IP:
   ```json
   {
     "mcpServers": {
       "elon-news-tracker": {
         "command": "npx",
         "args": [mcp-remote, "http://192.168.1.100:8700/mcp"]
       }
     }
   }
   ```

### Internet (Public Access)

1. **Set up reverse proxy** (nginx example):

   ```nginx
   server {
       listen 443 ssl;
       server_name news.yourdomain.com;

       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;

       location / {
           proxy_pass http://localhost:8700;
           proxy_http_version 1.1;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Enable authentication** (strongly recommended):

   ```yaml
   external_access:
     auth_token_env: "NEWS_HUB_SECRET"
   ```

3. **Configure Claude Desktop**:

   ```json
   {
     "mcpServers": {
       "elon-news-tracker": {
         "command": "npx",
         "args": [mcp-remote, "https://news.yourdomain.com/mcp"],
         "env": {
           "MCP_HEADERS": "Authorization:Bearer your-secret-token"
         }
       }
     }
   }
   ```

## Running as a Service

### systemd (Linux)

Create `/etc/systemd/system/elon-news-tracker.service`:

```ini
[Unit]
Description=Elon Musk News Tracker
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/openagents/demos/06_elon_musk_tracker
ExecStart=/bin/bash -c './run.sh'
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Commands:

```bash
sudo systemctl daemon-reload
sudo systemctl enable elon-news-tracker
sudo systemctl start elon-news-tracker
sudo systemctl status elon-news-tracker
```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

WORKDIR /app/demos/06_elon_musk_tracker
CMD ["./run.sh"]
```

```bash
docker build -t elon-news-tracker .
docker run -d -p 8700:8700 -p 8600:8600 elon-news-tracker
```

## Troubleshooting

### Network Won't Start

```bash
# Check if port is in use
lsof -i :8700

# Kill existing process
kill -9 $(lsof -t -i:8700)
```

### Agent Can't Connect

```bash
# Verify network is running
curl http://localhost:8700/health

# Check agent logs
python agents/news_collector.py 2>&1 | tee agent.log
```

### MCP Connection Failed

```bash
# Test MCP endpoint directly
curl -X POST http://localhost:8700/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### No News Being Collected

1. Check internet connectivity
2. Some RSS sources may be rate-limited
3. Try increasing fetch interval: `--interval 600`

## Data Storage

Feed posts are stored in:

```
./data/elon-musk-tracker/
└── feed/
    ├── posts/
    │   ├── {post_id_1}.json
    │   ├── {post_id_2}.json
    │   └── ...
    └── metadata.json
```

Each post file contains:

```json
{
  "post_id": "abc123",
  "title": "Elon Musk announces...",
  "content": "Full content here...",
  "author_id": "elon-news-collector",
  "created_at": 1734523800.0,
  "tags": ["elon-musk", "news", "tesla"]
}
```

## API Reference

### Feed Adapter Methods

```python
# Create a post
await feed.create_post(
    title="News Title",
    content="Full content...",
    tags=["tag1", "tag2"]
)

# List posts
posts = await feed.list_posts(
    limit=20,
    offset=0,
    tags=["tesla"],
    sort_by="recent"  # or "relevance"
)

# Search posts
results = await feed.search_posts(
    query="SpaceX launch",
    limit=10
)

# Get recent posts
recent = await feed.get_recent_posts(
    since_timestamp=time.time() - 86400,  # Last 24h
    limit=50
)

# Get single post
post = await feed.get_post(post_id="abc123")
```

## Files Reference

| File | Purpose |
|------|---------|
| `network.yaml` | Network configuration with feed mod |
| `agents/elon_fan_agent.py` | Worker agent that collects news |
| `tools/rss_fetcher.py` | RSS/API fetching utilities |
| `run.sh` | One-command demo launcher |
| `README.md` | Demo documentation |

## Related Documentation

- [Feed Mod Reference](./2025-11-29-workspace-feed-mod.md)
- [MCP Integration Guide](./2025-11-29-mcp-workspace-event-tools.md)
- [Worker Agent Documentation](../docs/agents/worker-agent.md)
