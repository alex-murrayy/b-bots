#!/usr/bin/env python3
"""
Order App - Web interface for placing delivery orders
Run this on your laptop/computer to place orders
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
import os
import requests
import json
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from navigation.map import CampusMap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Default Pi server URL (can be overridden)
PI_SERVER_URL = os.environ.get('PI_SERVER_URL', 'http://raspberrypi.local:5000')

# Initialize campus map
campus_map = CampusMap()


@app.route('/')
def index():
    """Main page - order form"""
    locations = sorted(campus_map.get_all_locations())
    return render_template('order_form.html', locations=locations, 
                         pi_server_url=PI_SERVER_URL)


@app.route('/api/places', methods=['GET'])
def get_locations():
    """API endpoint to get all available locations"""
    locations = sorted(campus_map.get_all_locations())
    return jsonify({
        'locations': locations,
        'count': len(locations)
    })


@app.route('/api/order', methods=['POST'])
def create_order():
    """Create a new order and send it to the Pi"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['customer_name', 'pickup_location', 'delivery_location', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate locations
        if data['pickup_location'] not in campus_map.locations:
            return jsonify({'error': f'Invalid pickup location: {data["pickup_location"]}'}), 400
        if data['delivery_location'] not in campus_map.locations:
            return jsonify({'error': f'Invalid delivery location: {data["delivery_location"]}'}), 400
        
        # Prepare order data
        order_data = {
            'customer_name': data['customer_name'],
            'pickup_location': data['pickup_location'],
            'delivery_location': data['delivery_location'],
            'items': data['items'] if isinstance(data['items'], list) else [data['items']],
            'priority': data.get('priority', 0)
        }
        
        # Send order to Pi server
        try:
            response = requests.post(
                f'{PI_SERVER_URL}/api/orders',
                json=order_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return jsonify({
                    'success': True,
                    'order_id': result.get('order_id'),
                    'message': f'Order {result.get("order_id")} created successfully!',
                    'pi_response': result
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': f'Pi server error: {response.text}',
                    'status_code': response.status_code
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({
                'success': False,
                'error': f'Could not connect to Pi server at {PI_SERVER_URL}',
                'hint': 'Make sure the Pi server is running and accessible'
            }), 503
        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'error': 'Request to Pi server timed out'
            }), 504
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error communicating with Pi: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders from Pi server"""
    try:
        response = requests.get(f'{PI_SERVER_URL}/api/orders', timeout=10)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': 'Failed to fetch orders'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/order/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order from Pi server"""
    try:
        response = requests.get(f'{PI_SERVER_URL}/api/orders/{order_id}', timeout=10)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/orders')
def orders_page():
    """Page showing all orders"""
    return render_template('orders.html', pi_server_url=PI_SERVER_URL)


@app.route('/status')
def status_page():
    """Status page showing Pi server connection status"""
    try:
        response = requests.get(f'{PI_SERVER_URL}/api/health', timeout=5)
        if response.status_code == 200:
            health = response.json()
            return render_template('status.html', 
                                 connected=True, 
                                 health=health,
                                 pi_server_url=PI_SERVER_URL)
        else:
            return render_template('status.html', 
                                 connected=False,
                                 error='Server returned error',
                                 pi_server_url=PI_SERVER_URL)
    except Exception as e:
        return render_template('status.html', 
                             connected=False,
                             error=str(e),
                             pi_server_url=PI_SERVER_URL)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Order App - Place delivery orders')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind to')
    parser.add_argument('--pi-url', default=None, help='Pi server URL')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.pi_url:
        PI_SERVER_URL = args.pi_url
        os.environ['PI_SERVER_URL'] = args.pi_url
    
    print(f"Starting Order App on http://{args.host}:{args.port}")
    print(f"Pi Server URL: {PI_SERVER_URL}")
    print(f"Open http://localhost:{args.port} in your browser")
    
    app.run(host=args.host, port=args.port, debug=args.debug)

