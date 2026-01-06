#!/bin/bash
# =============================================================================
# OpenAgents AWS Lightsail Cloud-Init Script
# =============================================================================
#
# USAGE: Paste this entire script into the "Launch script" field when creating
#        a new Lightsail instance, OR run it on a fresh Ubuntu instance.
#
# This script will:
#   1. Install Docker
#   2. Deploy OpenAgents with persistent storage
#   3. Set up automatic restarts
#   4. (Optional) Configure HTTPS with Caddy
#
# After running, access OpenAgents at: http://<your-ip>:8700/studio
# =============================================================================

set -e

# Configuration - modify these as needed
OPENAGENTS_VERSION="${OPENAGENTS_VERSION:-latest}"
DATA_DIR="${DATA_DIR:-/opt/openagents/data}"
DOMAIN="${DOMAIN:-}"  # Set this for HTTPS, e.g., "openagents.example.com"

# Logging
exec > >(tee /var/log/openagents-setup.log) 2>&1
echo "=== OpenAgents Setup Started at $(date) ==="

# Update system
echo ">>> Updating system packages..."
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# Install Docker
echo ">>> Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose plugin
echo ">>> Installing Docker Compose..."
apt-get install -y docker-compose-plugin

# Create OpenAgents directory structure
echo ">>> Creating directory structure..."
mkdir -p /opt/openagents
mkdir -p "$DATA_DIR"

# Create docker-compose.yml
echo ">>> Creating Docker Compose configuration..."
cat > /opt/openagents/docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  openagents:
    image: ghcr.io/openagents-org/openagents:${OPENAGENTS_VERSION:-latest}
    container_name: openagents
    ports:
      - "8700:8700"
      - "8600:8600"
    environment:
      - PYTHONUNBUFFERED=1
      - NODE_ENV=production
      # Add your API keys here if needed:
      # - OPENAI_API_KEY=${OPENAI_API_KEY}
      # - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ${DATA_DIR:-/opt/openagents/data}:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8700/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

COMPOSE_EOF

# Create environment file
echo ">>> Creating environment file..."
cat > /opt/openagents/.env << ENV_EOF
OPENAGENTS_VERSION=${OPENAGENTS_VERSION}
DATA_DIR=${DATA_DIR}
# Add your API keys below (uncomment and fill in):
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here
ENV_EOF

# Create management script
echo ">>> Creating management script..."
cat > /opt/openagents/manage.sh << 'MANAGE_EOF'
#!/bin/bash
# OpenAgents Management Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "$1" in
    start)
        echo "Starting OpenAgents..."
        docker compose up -d
        ;;
    stop)
        echo "Stopping OpenAgents..."
        docker compose down
        ;;
    restart)
        echo "Restarting OpenAgents..."
        docker compose restart
        ;;
    update)
        echo "Updating OpenAgents to latest version..."
        docker compose pull
        docker compose up -d
        ;;
    logs)
        docker compose logs -f
        ;;
    status)
        docker compose ps
        echo ""
        echo "Health check:"
        curl -s http://localhost:8700/api/health | head -c 200
        echo ""
        ;;
    backup)
        BACKUP_FILE="openagents-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
        echo "Creating backup: $BACKUP_FILE"
        tar -czvf "$BACKUP_FILE" -C /opt/openagents data
        echo "Backup created: $(pwd)/$BACKUP_FILE"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|update|logs|status|backup}"
        exit 1
        ;;
esac
MANAGE_EOF
chmod +x /opt/openagents/manage.sh

# Create systemd service for auto-start on boot
echo ">>> Creating systemd service..."
cat > /etc/systemd/system/openagents.service << 'SERVICE_EOF'
[Unit]
Description=OpenAgents Network
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/openagents
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl daemon-reload
systemctl enable openagents.service

# Pull and start OpenAgents
echo ">>> Pulling OpenAgents image..."
cd /opt/openagents
docker compose pull

echo ">>> Starting OpenAgents..."
docker compose up -d

# Wait for startup
echo ">>> Waiting for OpenAgents to start..."
sleep 15

# Check health
echo ">>> Checking health..."
for i in {1..10}; do
    if curl -sf http://localhost:8700/api/health > /dev/null 2>&1; then
        echo "OpenAgents is healthy!"
        break
    fi
    echo "Waiting for health check... ($i/10)"
    sleep 5
done

# Setup HTTPS if domain is provided
if [ -n "$DOMAIN" ]; then
    echo ">>> Setting up HTTPS for domain: $DOMAIN"

    # Install Caddy
    apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
    apt-get update
    apt-get install -y caddy

    # Configure Caddy
    cat > /etc/caddy/Caddyfile << CADDY_EOF
$DOMAIN {
    reverse_proxy localhost:8700
}
CADDY_EOF

    systemctl restart caddy
    echo "HTTPS configured! Access at: https://$DOMAIN"
fi

# Print summary
echo ""
echo "=============================================="
echo "  OpenAgents Installation Complete!"
echo "=============================================="
echo ""
echo "Access OpenAgents Studio at:"
if [ -n "$DOMAIN" ]; then
    echo "  https://$DOMAIN/studio"
else
    echo "  http://<your-server-ip>:8700/studio"
fi
echo ""
echo "Management commands:"
echo "  /opt/openagents/manage.sh start    - Start OpenAgents"
echo "  /opt/openagents/manage.sh stop     - Stop OpenAgents"
echo "  /opt/openagents/manage.sh restart  - Restart OpenAgents"
echo "  /opt/openagents/manage.sh update   - Update to latest version"
echo "  /opt/openagents/manage.sh logs     - View logs"
echo "  /opt/openagents/manage.sh status   - Check status"
echo "  /opt/openagents/manage.sh backup   - Create backup"
echo ""
echo "Data directory: $DATA_DIR"
echo "Logs: /var/log/openagents-setup.log"
echo ""
echo "=== Setup completed at $(date) ==="
