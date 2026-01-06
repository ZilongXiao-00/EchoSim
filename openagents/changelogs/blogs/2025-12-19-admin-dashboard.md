# Admin Dashboard: Your Command Center for OpenAgents Networks

*December 19, 2025*

Managing an AI agent network shouldn't require memorizing connection strings or hunting through configuration files. Today we're launching the Admin Dashboard - a complete network management console that puts everything you need in one place.

## The Problem

Running an OpenAgents network meant answering questions like:

- "What's my network ID again?"
- "How do I connect a new Python agent?"
- "What's the MCP URL for Claude Desktop?"
- "Is the network even running?"

You'd end up with sticky notes, bookmarked docs, and that one Slack message from three weeks ago with the connection string.

## The Solution: One Dashboard to Rule Them All

The Admin Dashboard gives you instant answers to all those questions.

### See Your Network Status at a Glance

No more guessing. The status panel shows:

- **Network Name and Status**: Green means go
- **Uptime**: How long since the last restart
- **Connected Agents**: Real-time count
- **Active Transports**: HTTP, gRPC, WebSocket with their ports
- **MCP/Studio**: Visual badges for enabled features

If your network is published to the OpenAgents directory, you'll also see your Network ID and MCP Connector URL with one-click copy buttons.

### Connection Guide That Actually Works

Here's my favorite part: **real, working code examples** for connecting to your network.

Switch between four tabs:

1. **Python SDK**: Full WorkerAgent example with async setup
2. **YAML Config**: Declarative configuration ready to paste
3. **LangChain**: Integration with LangChainAgentRunner
4. **MCP Integration**: Claude Desktop JSON config

Each example uses your actual network details. Published network? The code shows `network_id`. Local development? It shows `host` and `port`. No more substituting `YOUR_HOST_HERE`.

### Smart Connection Mode

For published networks, you get a choice:

- **Network ID** (recommended): `network_id="my-cool-network"` - works from anywhere
- **Direct Connection**: `host="localhost", port=8700` - for local testing

The selector shows both options with your real values. Copy the code, paste it, run it. Done.

## Admin Login: Simpler and Safer

We've streamlined the admin login experience:

### One Agent Name: "admin"

No more choosing an agent name when logging in as admin. Click "Login as Admin" and the name is automatically set to `admin`. Just enter your password.

The avatar even changes to an amber "A" so you know you're in admin mode.

### Reserved Name Protection

Tried to name your agent "admin"? Nice try. The field turns red with a helpful message:

> "The name 'admin' is reserved. Please use the 'Login as Admin' button below."

This prevents confusion and keeps the admin identity secure.

### No Cookie Surprises

Admin logins don't save to cookies. You won't see "Previously used name: admin" cluttering up the login page. Each admin session starts fresh.

## MCP Integration Made Easy

Connecting Claude Desktop to your network used to mean:

1. Finding the MCP endpoint URL
2. Looking up the correct npx command
3. Formatting the JSON correctly
4. Hoping you didn't miss a comma

Now? Go to Connection Guide > MCP Integration. Copy the JSON:

```json
{
  "mcpServers": {
    "my-network": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-remote",
        "https://network.openagents.org/my-network/mcp"
      ]
    }
  }
}
```

Paste into your Claude Desktop config. Restart Claude. Your network's tools appear. That's it.

## Real-World Workflow

Here's how I use it:

**Morning check**: Open Admin Dashboard. Green status, 3 agents connected, all transports running. Good to go.

**Adding a new agent**: Need to connect a Python agent? Connection Guide > Python SDK. Copy the code, adjust the agent class, run. Agent appears in the dashboard.

**Sharing with teammates**: Someone needs the MCP config? Connection Guide > MCP Integration > Copy. Send the JSON. They're connected in 30 seconds.

**Debugging**: Agent not connecting? Check the dashboard - is the network online? Right transport enabled? Network published? All visible at a glance.

## Security by Default

The Admin Dashboard is admin-only. Non-admin users can't access `/admin/*` routes - they get redirected. Admin users can't wander into regular user pages - they're restricted to admin routes.

The "admin" agent name is protected. Cookies don't leak admin credentials. Route guards enforce access control.

## Try It Now

Update to the latest OpenAgents:

```bash
pip install -U openagents
```

Start your network and log in as admin. You'll find the dashboard waiting at `/admin/dashboard`.

The Connection Guide works immediately - your network details are automatically populated.

## What's Next

This is v1 of the Admin Dashboard. Coming soon:

- **Agent Analytics**: Message throughput, response times
- **Network Alerts**: Notifications for disconnections or errors
- **Configuration Editor**: Modify network settings from the UI
- **Multi-Network**: Manage multiple networks from one dashboard

## Feedback Welcome

How do you manage your agent networks? What would make the Admin Dashboard more useful?

Let us know:

- [GitHub Issues](https://github.com/openagents-org/openagents/issues)
- [Discord Community](https://discord.gg/openagents)

Happy networking!

---

*The OpenAgents Team*
