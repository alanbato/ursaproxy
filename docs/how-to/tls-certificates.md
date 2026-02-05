# TLS Certificates

This guide explains how to set up TLS certificates for your UrsaProxy Gemini server.

## Why TLS is Required

The Gemini protocol mandates TLS for all connections. Unlike HTTP, there's no unencrypted option. This means you need a certificate and private key to run UrsaProxy.

## Certificate Options

### Self-Signed (Development)

For local development and testing:

```bash
openssl req -x509 -newkey rsa:4096 \
    -keyout key.pem \
    -out cert.pem \
    -days 365 \
    -nodes \
    -subj '/CN=localhost'
```

!!! warning

    Self-signed certificates will show warnings in Gemini clients. They're fine for development but not recommended for production.

### Let's Encrypt (Production)

For production, use Let's Encrypt with certbot:

```bash
# Install certbot
sudo apt install certbot

# Get a certificate (DNS validation)
sudo certbot certonly --manual --preferred-challenges dns \
    -d gemini.example.com

# Certificates are saved to:
# /etc/letsencrypt/live/gemini.example.com/fullchain.pem
# /etc/letsencrypt/live/gemini.example.com/privkey.pem
```

Configure UrsaProxy:

```bash
export CERT_FILE="/etc/letsencrypt/live/gemini.example.com/fullchain.pem"
export KEY_FILE="/etc/letsencrypt/live/gemini.example.com/privkey.pem"
```

### TOFU (Trust On First Use)

Many Gemini clients support TOFU, where they remember your certificate on first connection. This is the Gemini community's preferred approach for self-signed certificates.

For TOFU-friendly certificates:

1. Generate a long-lived self-signed certificate
2. Keep it consistent (don't regenerate frequently)
3. Document your certificate fingerprint for users

```bash
# Generate a 10-year certificate
openssl req -x509 -newkey rsa:4096 \
    -keyout key.pem \
    -out cert.pem \
    -days 3650 \
    -nodes \
    -subj '/CN=gemini.example.com'

# Get the fingerprint
openssl x509 -in cert.pem -noout -fingerprint -sha256
```

## Certificate Permissions

Ensure UrsaProxy can read the certificate files:

```bash
# If running as a dedicated user
sudo chown ursaproxy:ursaproxy /path/to/cert.pem /path/to/key.pem
chmod 600 /path/to/key.pem
chmod 644 /path/to/cert.pem
```

## Certificate Renewal

### Let's Encrypt Auto-Renewal

Certbot sets up automatic renewal. After renewal, restart UrsaProxy:

```bash
# Add to /etc/letsencrypt/renewal-hooks/post/ursaproxy.sh
#!/bin/bash
systemctl restart ursaproxy
```

Make it executable:

```bash
chmod +x /etc/letsencrypt/renewal-hooks/post/ursaproxy.sh
```

### Manual Renewal

For self-signed certificates, regenerate before expiry:

```bash
# Check expiry date
openssl x509 -in cert.pem -noout -dates

# Regenerate if needed
openssl req -x509 -newkey rsa:4096 \
    -keyout key.pem -out cert.pem \
    -days 365 -nodes -subj '/CN=gemini.example.com'
```

## Verification

Test your certificate setup:

```bash
# Start UrsaProxy
ursaproxy

# In another terminal, test with openssl
openssl s_client -connect localhost:1965 -servername localhost
```

You should see certificate information and be able to type a Gemini request.

## Troubleshooting

### Permission Denied

```
PermissionError: [Errno 13] Permission denied: '/path/to/key.pem'
```

Fix: Check file ownership and permissions.

### Certificate Mismatch

```
ssl.SSLError: [SSL: KEY_VALUES_MISMATCH]
```

Fix: Ensure the certificate and key match. Regenerate both together.

### Wrong Certificate Format

```
ssl.SSLError: [SSL: PEM_LIB]
```

Fix: Ensure files are PEM format (text starting with `-----BEGIN`).

## See Also

- [Deployment](deployment.md) - Production deployment guide
- [Configuration](configuration.md) - All configuration options
