#!/bin/bash
# Quick start script for the Order App

echo "🚗 UB Food Delivery Order App"
echo "=============================="
echo ""

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install flask flask-cors requests pyserial
else
    source venv/bin/activate
fi

echo ""
echo "Starting servers..."
echo ""

# Check if Pi server is already running
if curl -s http://127.0.0.1:5000/api/health > /dev/null 2>&1; then
    echo "✓ Pi Server already running on port 5000"
else
    echo "Starting Pi Server (simulation mode)..."
    python3 app/pi_server.py --simulate --host 127.0.0.1 --port 5000 &
    PI_PID=$!
    echo "Pi Server started (PID: $PI_PID)"
    sleep 2
fi

# Check if Order App is already running
if curl -s http://127.0.0.1:5001/ > /dev/null 2>&1; then
    echo "✓ Order App already running on port 5001"
else
    echo "Starting Order App..."
    python3 app/order_app.py --host 127.0.0.1 --port 5001 --pi-url http://127.0.0.1:5000 &
    APP_PID=$!
    echo "Order App started (PID: $APP_PID)"
    sleep 2
fi

echo ""
echo "=============================="
echo "✅ Servers are running!"
echo ""
echo "📱 Order App: http://localhost:5001"
echo "🔧 Pi Server: http://localhost:5000"
echo ""
echo "Open http://localhost:5001 in your browser to start placing orders!"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user interrupt
trap "kill $PI_PID $APP_PID 2>/dev/null; exit" INT
wait

