# OpenAgents AWS Lightsail Deployment

Deploy OpenAgents to AWS Lightsail in minutes with one-click setup.

## Cost

| Plan | Monthly | Specs |
|------|---------|-------|
| Nano | $3.50 | 512MB RAM, 1 vCPU, 20GB SSD |
| **Micro** | **$5** | **1GB RAM, 1 vCPU, 40GB SSD** (recommended) |
| Small | $10 | 2GB RAM, 1 vCPU, 60GB SSD |

Static IP and reasonable data transfer included free.

---

## Deployment Steps

### 1. Create Lightsail Instance

1. Go to **AWS Lightsail Console**: https://lightsail.aws.amazon.com
2. Click **"Create instance"**
3. Choose your **region** (closest to your users)
4. Select **Linux/Unix** → **Ubuntu 22.04 LTS**
5. Select plan: **$5/month Micro** (recommended)

### 2. Add Launch Script

1. Expand the **"Launch script"** section
2. Copy the entire contents of [`cloud-init.sh`](./cloud-init.sh) and paste it
3. *(Optional)* For HTTPS, edit the `DOMAIN=` line before pasting:
   ```bash
   DOMAIN="your-domain.com"
   ```

### 3. Create Instance

1. Name your instance (e.g., `openagents`)
2. Click **"Create instance"**
3. Wait for instance to start (~1 minute)

### 4. Configure Firewall

1. Click on your instance → **Networking** tab
2. Under **IPv4 Firewall**, click **"Add rule"**:
   - Application: Custom
   - Protocol: TCP
   - Port: **8700**
3. *(Optional)* Add port **8600** for gRPC
4. *(Optional)* Create and attach a **Static IP** for a permanent address

### 5. Access OpenAgents

Wait 2-3 minutes for setup to complete, then visit:

```
http://<your-instance-ip>:8700/studio
```

---

## Management Commands

SSH into your instance and use:

```bash
/opt/openagents/manage.sh status   # Check status
/opt/openagents/manage.sh logs     # View logs
/opt/openagents/manage.sh restart  # Restart OpenAgents
/opt/openagents/manage.sh update   # Update to latest version
/opt/openagents/manage.sh backup   # Create backup
```

---

## HTTPS Setup (Optional)

To enable HTTPS with automatic SSL certificates:

1. **Before deploying**: Edit `DOMAIN=` in the cloud-init script
2. **Point DNS**: Create an A record pointing your domain to the server IP
3. **Open ports**: Add firewall rules for ports 80 and 443

---

## Troubleshooting

### Check Setup Progress

```bash
ssh ubuntu@<your-ip>
tail -f /var/log/openagents-setup.log
```

### Can't Access Studio

1. Verify port 8700 is open in Lightsail firewall
2. Check container status:
   ```bash
   /opt/openagents/manage.sh status
   ```
3. View logs:
   ```bash
   /opt/openagents/manage.sh logs
   ```

### Update OpenAgents

```bash
/opt/openagents/manage.sh update
```

---

## Support

- Documentation: https://openagents.org/docs
- Issues: https://github.com/openagents-org/openagents/issues
