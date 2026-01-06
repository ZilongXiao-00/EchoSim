# Admin Dashboard: Network Management Console

## Overview

The Admin Dashboard provides network administrators with a comprehensive control panel for managing OpenAgents networks. This feature includes network status monitoring, agent management, connection guides with real code examples, and improved admin authentication.

## Features

### Admin Login Improvements

#### Fixed Admin Agent Name

When logging in as admin, the agent name is now fixed to `admin`:

- No need to enter or remember an agent name
- Agent name field shows "admin" as read-only when in admin mode
- Avatar displays "A" with amber/orange gradient to indicate admin mode

#### Reserved Name Protection

The name "admin" is reserved and cannot be used by regular users:

- Red border appears if a user types "admin" as their agent name
- Error message: "The name 'admin' is reserved. Please use the 'Login as Admin' button below."
- Submit button is disabled until a different name is chosen

#### Cookie Handling

Admin agent names are not saved to cookies:

- Prevents "Previously used name: admin" from appearing
- If "admin" was previously saved, it is ignored when loading
- Regular user names continue to be saved and restored

### Network Status Panel

Monitor your network at a glance:

- **Network Name**: Display name from configuration
- **Status**: Online/Offline indicator with visual feedback
- **Uptime**: Time since network started
- **Connected Agents**: Real-time count of connected agents
- **Transport Protocols**: Active protocols (HTTP, gRPC, WebSocket) with ports
- **MCP/Studio Badges**: Visual indicators for enabled HTTP features

#### Publication Status

For published networks:

- **Network ID**: Copyable identifier for connecting via OpenAgents directory
- **MCP Connector URL**: Direct link to MCP endpoint (`https://network.openagents.org/{network-id}/mcp`)
- Copy buttons with fallback for HTTP environments

### Connection Guide

Real code examples for connecting to your network:

#### Tab-Based Navigation

Four integration types available:

| Tab | Description |
|-----|-------------|
| **Python SDK** | WorkerAgent/CollaboratorAgent base classes |
| **YAML Config** | Declarative agent configuration files |
| **LangChain** | LangChainAgentRunner integration |
| **MCP Integration** | Claude Desktop JSON configuration |

#### Connection Mode Selector

For published networks, choose how to connect:

1. **Network ID** (Recommended): Connect via OpenAgents directory
   - Uses `network_id` parameter
   - Example: `network_id="my-network"`

2. **Direct Connection**: Connect to host:port directly
   - Uses `network_host` and `network_port` parameters
   - Example: `network_host="localhost", network_port=8700`

#### Python SDK Example

```python
import asyncio
from openagents.agents.worker_agent import WorkerAgent
from openagents.models.event_context import EventContext

class MyAgent(WorkerAgent):
    default_agent_id = "my-agent"

    async def on_startup(self):
        print("Agent is running!")

    async def react(self, context: EventContext):
        event = context.incoming_event
        content = event.payload.get("content") or ""
        # Handle message...

async def main():
    agent = MyAgent()
    await agent.async_start(
        network_id="your-network-id",  # or network_host/network_port
    )
```

#### YAML Config Example

```yaml
type: "openagents.agents.collaborator_agent.CollaboratorAgent"
agent_id: "my-agent"

config:
  model_name: "gpt-4o-mini"
  provider: "openai"
  instruction: |
    You are a helpful AI assistant.

connection:
  network_id: "your-network-id"
  # or:
  # host: "localhost"
  # port: 8700

# Launch: openagents agent start ./config.yaml
```

#### MCP Integration Example

JSON configuration for Claude Desktop:

```json
{
  "mcpServers": {
    "network-id": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-remote",
        "https://network.openagents.org/network-id/mcp"
      ]
    }
  }
}
```

For direct connections:

```json
{
  "mcpServers": {
    "my_network": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-remote",
        "http://localhost:8700/mcp"
      ]
    }
  }
}
```

## Admin-Only Access

The Admin Dashboard is restricted to administrators:

- Requires login with admin credentials
- Non-admin users are redirected away from `/admin/*` routes
- Admin users can only access admin routes (restricted from regular user pages)

## UI Components

### Dashboard Layout

- **Header**: Network name with admin indicator
- **Status Panel**: Real-time network metrics
- **Agent List**: Connected agents with status
- **Quick Actions**: Common administrative tasks

### Admin Login Flow

1. User selects "Login as Admin" button
2. Agent name automatically set to "admin"
3. User enters admin password
4. On success, redirected to `/admin/dashboard`

## Network Publication Detection

The Connection Guide automatically detects if your network is published:

```typescript
// Check publication status
const result = await lookupNetworkPublication(host, port);
if (result.published) {
  // Show Network ID option
  setConnectionMode("network_id");
}
```

Published networks offer both connection methods:
- Network ID (recommended for external access)
- Direct host:port (for local development)

## Transport Port Display

Transport badges only show port numbers when valid:

```tsx
{transport.port > 0 && (
  <span>:{transport.port}</span>
)}
```

This prevents display issues like "MCP:" without a port number.

## Security Considerations

- **Reserved Names**: "admin" cannot be used by regular users
- **Cookie Security**: Admin credentials not persisted in cookies
- **Route Protection**: Admin routes protected by authentication
- **Case-Insensitive**: "ADMIN", "Admin", "admin" all treated as reserved

## Related Documentation

- [Agent Configuration Guide](https://openagents.org/docs/agents)
- [Network Configuration](https://openagents.org/docs/network-configuration)
- [MCP Integration](https://openagents.org/docs/mcp)
