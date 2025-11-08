#!/usr/bin/env python3
"""
Pi Server - Runs on Raspberry Pi to receive and execute delivery orders
"""

import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
from typing import Dict, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add navigation directory to path
nav_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'navigation')
if nav_path not in sys.path:
    sys.path.insert(0, nav_path)

from map import CampusMap
from pathfinding import Pathfinder

# Import delivery system
app_path = os.path.dirname(os.path.abspath(__file__))
if app_path not in sys.path:
    sys.path.insert(0, app_path)

from delivery import DeliverySystem, OrderStatus

# Try to import route executor for actual delivery execution
try:
    from route_executor import RouteExecutor
    HAS_ROUTE_EXECUTOR = True
except ImportError:
    HAS_ROUTE_EXECUTOR = False
    RouteExecutor = None

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Initialize delivery system
campus_map = CampusMap()
pathfinder = Pathfinder(campus_map)
delivery_system = DeliverySystem(campus_map, pathfinder)

# Route executor (will be initialized when needed)
route_executor = None
arduino_port = os.environ.get('ARDUINO_PORT', '/dev/ttyACM0')
simulate_mode = os.environ.get('SIMULATE', 'false').lower() == 'true'

# Order execution queue
execution_queue = []
execution_lock = threading.Lock()
is_executing = False


def initialize_route_executor():
    """Initialize route executor for actual delivery"""
    global route_executor
    if HAS_ROUTE_EXECUTOR and not simulate_mode:
        try:
            route_executor = RouteExecutor(arduino_port=arduino_port, simulate=False)
            print(f"Route executor initialized on {arduino_port}")
        except Exception as e:
            print(f"Warning: Could not initialize route executor: {e}")
            print("Running in simulation mode")
            route_executor = RouteExecutor(arduino_port=arduino_port, simulate=True)
    elif HAS_ROUTE_EXECUTOR:
        route_executor = RouteExecutor(arduino_port=arduino_port, simulate=True)
        print("Route executor running in simulation mode")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    stats = delivery_system.get_statistics()
    return jsonify({
        'status': 'healthy',
        'total_orders': stats['total_orders'],
        'pending_orders': stats['pending'],
        'in_progress_orders': stats['in_progress'],
        'completed_orders': stats['completed'],
        'simulate_mode': simulate_mode,
        'has_route_executor': HAS_ROUTE_EXECUTOR
    }), 200


@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    orders = []
    for order in delivery_system.orders.values():
        orders.append({
            'order_id': order.order_id,
            'customer_name': order.customer_name,
            'pickup_location': order.pickup_location,
            'delivery_location': order.delivery_location,
            'items': order.items,
            'status': order.status.value,
            'priority': order.priority,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'completed_at': order.completed_at.isoformat() if order.completed_at else None
        })
    
    return jsonify({
        'orders': orders,
        'count': len(orders)
    }), 200


@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order"""
    order = delivery_system.get_order(order_id)
    if order:
        return jsonify({
            'order_id': order.order_id,
            'customer_name': order.customer_name,
            'pickup_location': order.pickup_location,
            'delivery_location': order.delivery_location,
            'items': order.items,
            'status': order.status.value,
            'priority': order.priority,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'completed_at': order.completed_at.isoformat() if order.completed_at else None
        }), 200
    else:
        return jsonify({'error': 'Order not found'}), 404


@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['customer_name', 'pickup_location', 'delivery_location', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create order
        order_id = delivery_system.create_order(
            customer_name=data['customer_name'],
            pickup_location=data['pickup_location'],
            delivery_location=data['delivery_location'],
            items=data['items'] if isinstance(data['items'], list) else [data['items']],
            priority=data.get('priority', 0)
        )
        
        # Get created order
        order = delivery_system.get_order(order_id)
        
        return jsonify({
            'order_id': order_id,
            'message': 'Order created successfully',
            'order': {
                'order_id': order.order_id,
                'customer_name': order.customer_name,
                'pickup_location': order.pickup_location,
                'delivery_location': order.delivery_location,
                'items': order.items,
                'status': order.status.value,
                'priority': order.priority,
                'created_at': order.created_at.isoformat() if order.created_at else None
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/orders/<order_id>/execute', methods=['POST'])
def execute_order(order_id):
    """Execute a specific order"""
    global is_executing
    
    order = delivery_system.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if order.status != OrderStatus.PENDING:
        return jsonify({'error': f'Order is already {order.status.value}'}), 400
    
    # Add to execution queue
    with execution_lock:
        if order_id not in execution_queue:
            execution_queue.append(order_id)
    
    # Start execution thread if not already running
    if not is_executing:
        thread = threading.Thread(target=execute_orders_thread, daemon=True)
        thread.start()
    
    return jsonify({
        'message': 'Order added to execution queue',
        'order_id': order_id,
        'queue_position': execution_queue.index(order_id) + 1
    }), 200


@app.route('/api/orders/execute-all', methods=['POST'])
def execute_all_orders():
    """Execute all pending orders"""
    global is_executing
    
    pending_orders = delivery_system.get_pending_orders()
    if not pending_orders:
        return jsonify({'message': 'No pending orders'}), 200
    
    # Add all pending orders to queue
    with execution_lock:
        for order in pending_orders:
            if order.order_id not in execution_queue:
                execution_queue.append(order.order_id)
    
    # Start execution thread if not already running
    if not is_executing:
        thread = threading.Thread(target=execute_orders_thread, daemon=True)
        thread.start()
    
    return jsonify({
        'message': f'{len(pending_orders)} orders added to execution queue',
        'orders': [order.order_id for order in pending_orders]
    }), 200


@app.route('/api/orders/<order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """Cancel an order"""
    order = delivery_system.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    delivery_system.cancel_order(order_id)
    
    # Remove from queue if present
    with execution_lock:
        if order_id in execution_queue:
            execution_queue.remove(order_id)
    
    return jsonify({
        'message': 'Order cancelled',
        'order_id': order_id
    }), 200


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get delivery statistics"""
    stats = delivery_system.get_statistics()
    return jsonify(stats), 200


def execute_orders_thread():
    """Background thread to execute orders from queue"""
    global is_executing, route_executor
    
    if not route_executor:
        initialize_route_executor()
    
    is_executing = True
    
    try:
        while True:
            order_id = None
            
            # Get next order from queue
            with execution_lock:
                if execution_queue:
                    order_id = execution_queue.pop(0)
                else:
                    break
            
            if not order_id:
                break
            
            # Execute order
            try:
                execute_single_order(order_id)
            except Exception as e:
                print(f"Error executing order {order_id}: {e}")
                # Mark order as failed or keep as pending
                order = delivery_system.get_order(order_id)
                if order:
                    order.status = OrderStatus.PENDING
            
            # Small delay between orders
            time.sleep(1)
    
    finally:
        is_executing = False


def execute_single_order(order_id: str):
    """Execute a single order"""
    order = delivery_system.get_order(order_id)
    if not order:
        return
    
    print(f"\n{'='*60}")
    print(f"Executing Order: {order_id}")
    print(f"Customer: {order.customer_name}")
    print(f"Route: {order.pickup_location} → {order.delivery_location}")
    print(f"Items: {', '.join(order.items)}")
    print(f"{'='*60}\n")
    
    # Mark order as in progress
    order.status = OrderStatus.IN_PROGRESS
    
    # Plan route
    # For now, we'll use a simple approach - in the future, this could use
    # the pathfinding system or hardcoded routes
    try:
        # Get current location (for now, assume starting from pickup)
        start_location = order.pickup_location
        
        # Plan route from pickup to delivery
        route, distance, details = delivery_system.plan_delivery_route(
            start_location,
            [order_id]
        )
        
        print(f"Route planned: {len(route)} locations")
        print(f"Estimated distance: {distance:.1f} meters")
        print(f"Route: {' → '.join(route)}\n")
        
        # For now, we'll simulate the delivery
        # In a real system, you would:
        # 1. Use route_executor to execute the route
        # 2. Or use hardcoded routes if available
        # 3. Track the car's actual position
        
        print("Simulating delivery...")
        time.sleep(2)  # Simulate delivery time
        
        # Mark order as completed
        delivery_system.complete_order(order_id)
        print(f"✓ Order {order_id} completed successfully!")
        
    except Exception as e:
        print(f"Error executing order: {e}")
        order.status = OrderStatus.PENDING
        raise


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Pi Server - Receive and execute delivery orders')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--arduino-port', default='/dev/ttyACM0', help='Arduino port')
    parser.add_argument('--simulate', action='store_true', help='Simulation mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    arduino_port = args.arduino_port
    simulate_mode = args.simulate
    
    print(f"Starting Pi Server on http://{args.host}:{args.port}")
    print(f"Arduino Port: {arduino_port}")
    print(f"Simulation Mode: {simulate_mode}")
    print(f"Route Executor Available: {HAS_ROUTE_EXECUTOR}")
    
    # Initialize route executor
    if HAS_ROUTE_EXECUTOR:
        initialize_route_executor()
    
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)

