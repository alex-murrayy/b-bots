#!/usr/bin/env python3
"""
Simple Delivery System with Hardcoded Routes
Uses hardcoded routes instead of complex pathfinding
Perfect for demos and reliable deliveries
"""

from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from hardcoded_routes import RouteLibrary, get_route_for_delivery, HardcodedRoute
from route_executor import RouteExecutor


@dataclass
class SimpleOrder:
    """Simple order for delivery"""
    order_id: str
    customer_name: str
    pickup_location: str
    delivery_location: str
    items: List[str]
    status: str = "pending"  # pending, in_progress, completed


class SimpleDeliverySystem:
    """Simple delivery system using hardcoded routes"""
    
    def __init__(self, arduino_port: str = '/dev/ttyACM0', simulate: bool = False):
        self.route_library = RouteLibrary()
        self.executor = RouteExecutor(arduino_port=arduino_port, simulate=simulate)
        self.orders: Dict[str, SimpleOrder] = {}
        self.order_counter = 0
    
    def create_order(self, customer_name: str, pickup_location: str,
                    delivery_location: str, items: List[str]) -> str:
        """Create a new order"""
        self.order_counter += 1
        order_id = f"ORD-{self.order_counter:04d}"
        
        order = SimpleOrder(
            order_id=order_id,
            customer_name=customer_name,
            pickup_location=pickup_location,
            delivery_location=delivery_location,
            items=items
        )
        
        self.orders[order_id] = order
        return order_id
    
    def get_available_routes(self) -> List[str]:
        """Get list of available delivery routes"""
        # Check which pickup/delivery pairs have routes
        available = []
        for order in self.orders.values():
            route = get_route_for_delivery(order.pickup_location, order.delivery_location)
            if route:
                available.append(order.order_id)
        return available
    
    def deliver_order(self, order_id: str) -> bool:
        """Execute delivery for an order"""
        if order_id not in self.orders:
            print(f"Order not found: {order_id}")
            return False
        
        order = self.orders[order_id]
        
        # Check if route exists
        route = get_route_for_delivery(order.pickup_location, order.delivery_location)
        if not route:
            print(f"No route available: {order.pickup_location} → {order.delivery_location}")
            print("Available routes:")
            for name in self.route_library.list_routes():
                print(f"  • {name}")
            return False
        
        # Update order status
        order.status = "in_progress"
        print(f"\nStarting delivery for order {order_id}")
        print(f"Customer: {order.customer_name}")
        print(f"Route: {order.pickup_location} → {order.delivery_location}")
        print(f"Items: {', '.join(order.items)}")
        
        # Execute route
        success = self.executor.execute_route(route, verbose=True)
        
        if success:
            order.status = "completed"
            print(f"✓ Order {order_id} delivered successfully!")
            return True
        else:
            order.status = "pending"  # Reset on failure
            print(f"✗ Delivery failed for order {order_id}")
            return False
    
    def list_orders(self):
        """List all orders"""
        print("\nOrders:")
        print("-" * 60)
        for order in self.orders.values():
            print(f"{order.order_id}: {order.customer_name}")
            print(f"  {order.pickup_location} → {order.delivery_location}")
            print(f"  Status: {order.status}")
            print(f"  Items: {', '.join(order.items)}")
            print()


def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Delivery System')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0',
                       help='Arduino port')
    parser.add_argument('--simulate', '-s', action='store_true',
                       help='Simulation mode')
    
    args = parser.parse_args()
    
    # Create delivery system
    delivery = SimpleDeliverySystem(arduino_port=args.port, simulate=args.simulate)
    
    # Create some orders
    print("Creating delivery orders...")
    order1 = delivery.create_order(
        "Alice",
        "Student Union",
        "Norton Hall",
        ["Pizza", "Soda"]
    )
    print(f"Created order: {order1}")
    
    order2 = delivery.create_order(
        "Bob",
        "C3 Dining Center",
        "Ellicott Complex",
        ["Burrito", "Chips"]
    )
    print(f"Created order: {order2}")
    
    # List orders
    delivery.list_orders()
    
    # Deliver orders
    print("\n" + "="*60)
    print("Starting Deliveries")
    print("="*60)
    
    delivery.deliver_order(order1)
    time.sleep(2)
    delivery.deliver_order(order2)
    
    # Final status
    delivery.list_orders()


if __name__ == '__main__':
    import time
    main()

