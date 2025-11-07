#!/bin/bash
# Setup script for Raspberry Pi
# Run this on your Raspberry Pi to set up the RC car control system

set -e

echo "RC Car Control Setup for Raspberry Pi"
echo "======================================"

# Create directory for scripts
INSTALL_DIR="$HOME/rc_car_control"
mkdir -p "$INSTALL_DIR"

echo "Installing directory: $INSTALL_DIR"

# Check if pyserial is installed
if ! python3 -c "import serial" 2>/dev/null; then
    echo "Installing pyserial..."
    pip3 install pyserial
else
    echo "pyserial already installed"
fi

# Copy controller script
echo "Copying controller script..."
# Note: You'll need to copy arduino_wasd_controller.py to the Pi manually
# or use scp from your laptop

# Create systemd service file
echo "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/rc-car.service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=RC Car Control Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/rc_car_service.py --mode file
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created at $SERVICE_FILE"
echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy arduino_wasd_controller.py and rc_car_service.py to $INSTALL_DIR"
echo "2. Test connection: python3 $INSTALL_DIR/arduino_wasd_controller.py --list-ports"
echo "3. Test manual control: python3 $INSTALL_DIR/arduino_wasd_controller.py -i"
echo "4. Enable service: sudo systemctl enable rc-car.service"
echo "5. Start service: sudo systemctl start rc-car.service"
echo "6. Check status: sudo systemctl status rc-car.service"

