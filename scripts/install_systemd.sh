#!/bin/bash
set -e

echo "=== Axon Core - Systemd Installation ==="

if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: Please run as root or with sudo"
    exit 1
fi

INSTALL_DIR="/opt/axon-core"
SERVICE_NAME="axon-core"
USER="${SUDO_USER:-axon88}"

echo "Installation directory: $INSTALL_DIR"
echo "Service name: $SERVICE_NAME"
echo "Run as user: $USER"
echo ""

read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
cp -r . "$INSTALL_DIR/"
chown -R "$USER:$USER" "$INSTALL_DIR"

echo "Installing Python dependencies..."
cd "$INSTALL_DIR"
pip3 install -r requirements.txt

echo "Creating systemd service file..."
cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=Axon Core Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=/usr/bin/python3 -m uvicorn app.main:sio_app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd..."
systemctl daemon-reload

echo "Enabling service..."
systemctl enable "$SERVICE_NAME"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Start the service:"
echo "  sudo systemctl start $SERVICE_NAME"
echo ""
echo "Check status:"
echo "  sudo systemctl status $SERVICE_NAME"
echo ""
echo "View logs:"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo ""
