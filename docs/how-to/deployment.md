# Deployment

This guide explains how to deploy UrsaProxy to a production server.

## Prerequisites

- A Linux server with Python 3.13+
- A domain name pointing to your server
- TLS certificates (see [TLS Certificates](tls-certificates.md))
- Root/sudo access

## Step 1: Create a System User

Create a dedicated user for UrsaProxy:

```bash
sudo useradd --system --shell /bin/false --home-dir /opt/ursaproxy ursaproxy
sudo mkdir -p /opt/ursaproxy
sudo chown ursaproxy:ursaproxy /opt/ursaproxy
```

## Step 2: Install UrsaProxy

Install using uv or pip in a virtual environment:

```bash
sudo -u ursaproxy bash -c '
cd /opt/ursaproxy
python3 -m venv .venv
.venv/bin/pip install ursaproxy
'
```

## Step 3: Configure Environment

Create an environment file:

```bash
sudo nano /opt/ursaproxy/.env
```

Add your configuration:

```bash
BEARBLOG_URL=https://example.bearblog.dev
BLOG_NAME=My Gemini Blog
CERT_FILE=/etc/letsencrypt/live/gemini.example.com/fullchain.pem
KEY_FILE=/etc/letsencrypt/live/gemini.example.com/privkey.pem
GEMINI_HOST=gemini.example.com
HOST=0.0.0.0
PORT=1965
PAGES={"about": "About", "now": "Now"}
CACHE_TTL_FEED=600
CACHE_TTL_POST=3600
```

Secure the file:

```bash
sudo chown ursaproxy:ursaproxy /opt/ursaproxy/.env
sudo chmod 600 /opt/ursaproxy/.env
```

## Step 4: Create systemd Service

Create a service file:

```bash
sudo nano /etc/systemd/system/ursaproxy.service
```

Add the following:

```ini
[Unit]
Description=UrsaProxy - Bearblog to Gemini Proxy
After=network.target

[Service]
Type=simple
User=ursaproxy
Group=ursaproxy
WorkingDirectory=/opt/ursaproxy
EnvironmentFile=/opt/ursaproxy/.env
ExecStart=/opt/ursaproxy/.venv/bin/ursaproxy
Restart=always
RestartSec=5

# Security hardening
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ReadOnlyPaths=/etc/letsencrypt

# Allow binding to port 1965
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
```

## Step 5: Start the Service

Enable and start UrsaProxy:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ursaproxy
sudo systemctl start ursaproxy
```

Check the status:

```bash
sudo systemctl status ursaproxy
```

View logs:

```bash
sudo journalctl -u ursaproxy -f
```

## Step 6: Configure Firewall

Allow Gemini traffic through your firewall:

=== "ufw"

    ```bash
    sudo ufw allow 1965/tcp
    ```

=== "firewalld"

    ```bash
    sudo firewall-cmd --permanent --add-port=1965/tcp
    sudo firewall-cmd --reload
    ```

=== "iptables"

    ```bash
    sudo iptables -A INPUT -p tcp --dport 1965 -j ACCEPT
    ```

## Step 7: Verify Deployment

From another machine, test the connection:

```bash
# Using a Gemini client
lagrange gemini://gemini.example.com/

# Using openssl
echo "gemini://gemini.example.com/" | openssl s_client -connect gemini.example.com:1965 -crlf
```

## Managing the Service

Common systemctl commands:

```bash
# Start
sudo systemctl start ursaproxy

# Stop
sudo systemctl stop ursaproxy

# Restart
sudo systemctl restart ursaproxy

# View status
sudo systemctl status ursaproxy

# View logs
sudo journalctl -u ursaproxy -f
```

## Updating UrsaProxy

To update to a new version:

```bash
sudo systemctl stop ursaproxy
sudo -u ursaproxy /opt/ursaproxy/.venv/bin/pip install --upgrade ursaproxy
sudo systemctl start ursaproxy
```

## Docker Deployment (Alternative)

If you prefer Docker:

```dockerfile
FROM python:3.13-slim

RUN pip install ursaproxy

EXPOSE 1965

CMD ["ursaproxy"]
```

Build and run:

```bash
docker build -t ursaproxy .
docker run -d \
    -p 1965:1965 \
    -e BEARBLOG_URL=https://example.bearblog.dev \
    -e BLOG_NAME="My Blog" \
    -e CERT_FILE=/certs/cert.pem \
    -e KEY_FILE=/certs/key.pem \
    -v /path/to/certs:/certs:ro \
    ursaproxy
```

## See Also

- [TLS Certificates](tls-certificates.md) - Certificate setup
- [Caching](caching.md) - Optimizing cache settings
- [Configuration](configuration.md) - All options
