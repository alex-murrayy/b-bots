"""
Food Delivery System for RC Car
Manages orders and optimizes delivery routes
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathfinding import Pathfinder
from map import CampusMap


class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Order:
    """Represents a food delivery order"""
    order_id: str
    customer_name: str
    pickup_location: str
    delivery_location: str
    items: List[str]
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    priority: int = 0  # Higher number = higher priority


class DeliverySystem:
    """Manages food delivery orders and routing"""
    
    def __init__(self, campus_map: CampusMap, pathfinder: Pathfinder):
        self.map = campus_map
        self.pathfinder = pathfinder
        self.orders: Dict[str, Order] = {}
        self.current_route: List[str] = []
        self.current_location: str = ""
        self.order_counter = 0
    
    def create_order(self, customer_name: str, pickup_location: str, 
                    delivery_location: str, items: List[str], 
                    priority: int = 0) -> str:
        """Create a new delivery order"""
        self.order_counter += 1
        order_id = f"ORD-{self.order_counter:04d}"
        
        # Validate locations
        if pickup_location not in self.map.locations:
            raise ValueError(f"Invalid pickup location: {pickup_location}")
        if delivery_location not in self.map.locations:
            raise ValueError(f"Invalid delivery location: {delivery_location}")
        
        order = Order(
            order_id=order_id,
            customer_name=customer_name,
            pickup_location=pickup_location,
            delivery_location=delivery_location,
            items=items,
            priority=priority
        )
        
        self.orders[order_id] = order
        return order_id
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by ID"""
        return self.orders.get(order_id)
    
    def get_pending_orders(self) -> List[Order]:
        """Get all pending orders, sorted by priority"""
        pending = [order for order in self.orders.values() 
                  if order.status == OrderStatus.PENDING]
        return sorted(pending, key=lambda x: (x.priority, x.created_at), reverse=True)
    
    def optimize_route(self, start_location: str, orders: List[Order]) -> Tuple[List[str], float]:
        """
        Optimize delivery route for multiple orders.
        Uses a greedy approach ensuring pickups happen before deliveries.
        """
        if not orders:
            return [start_location], 0.0
        
        # Track which orders have been picked up
        picked_up_orders = set()
        path = [start_location]
        total_distance = 0.0
        current = start_location
        remaining_order_ids = {order.order_id for order in orders}
        order_dict = {order.order_id: order for order in orders}
        
        # Build route ensuring pickups before deliveries
        while remaining_order_ids:
            best_next = None
            best_distance = float('inf')
            best_path = []
            action_type = None  # 'pickup' or 'deliver'
            best_order_id = None
            
            # Consider all possible next actions
            for order_id in remaining_order_ids:
                order = order_dict[order_id]
                
                # If not picked up, consider going to pickup location
                if order_id not in picked_up_orders:
                    pickup_path, pickup_dist = self.pathfinder.find_shortest_path(
                        current, order.pickup_location
                    )
                    if pickup_dist < best_distance:
                        best_next = order.pickup_location
                        best_distance = pickup_dist
                        best_path = pickup_path
                        action_type = 'pickup'
                        best_order_id = order_id
                
                # If already picked up, consider going to delivery location
                elif order_id in picked_up_orders:
                    delivery_path, delivery_dist = self.pathfinder.find_shortest_path(
                        current, order.delivery_location
                    )
                    if delivery_dist < best_distance:
                        best_next = order.delivery_location
                        best_distance = delivery_dist
                        best_path = delivery_path
                        action_type = 'deliver'
                        best_order_id = order_id
            
            if best_next is None:
                break
            
            # Add path to route (skip first node as it's already in path)
            if len(best_path) > 1:
                path.extend(best_path[1:])
            elif best_path:
                # If direct connection, just add the destination
                if best_path[0] != current:
                    path.append(best_path[0])
            
            total_distance += best_distance
            current = best_next
            
            # Update order status
            if action_type == 'pickup':
                picked_up_orders.add(best_order_id)
            elif action_type == 'deliver':
                remaining_order_ids.remove(best_order_id)
        
        return path, total_distance
    
    def plan_delivery_route(self, start_location: str, 
                           order_ids: Optional[List[str]] = None) -> Tuple[List[str], float, Dict]:
        """
        Plan a delivery route for specified orders or all pending orders.
        
        Returns:
            Tuple of (route path, total distance, route details)
        """
        if order_ids is None:
            # Get all pending orders
            orders_to_deliver = self.get_pending_orders()
        else:
            orders_to_deliver = [self.orders[oid] for oid in order_ids 
                               if oid in self.orders and 
                               self.orders[oid].status == OrderStatus.PENDING]
        
        if not orders_to_deliver:
            return [start_location], 0.0, {}
        
        # Optimize route
        route, distance = self.optimize_route(start_location, orders_to_deliver)
        
        # Build route details
        # Build detailed route information
        route_info = self._build_route_info(route, orders_to_deliver)
        
        route_details = {
            'orders': [order.order_id for order in orders_to_deliver],
            'total_orders': len(orders_to_deliver),
            'estimated_distance': distance,
            'estimated_time_minutes': distance / 60.0,  # Assuming 1 m/s average speed (more realistic for RC car)
            'route_info': route_info  # Location actions mapping
        }
        
        return route, distance, route_details
    
    def start_delivery(self, start_location: str, order_ids: Optional[List[str]] = None):
        """Start a delivery route"""
        route, distance, details = self.plan_delivery_route(start_location, order_ids)
        self.current_route = route
        self.current_location = start_location
        
        # Update order statuses
        if order_ids is None:
            order_ids = [order.order_id for order in self.get_pending_orders()]
        
        for order_id in order_ids:
            if order_id in self.orders:
                self.orders[order_id].status = OrderStatus.IN_PROGRESS
        
        return route, distance, details
    
    def complete_order(self, order_id: str):
        """Mark an order as completed"""
        if order_id in self.orders:
            order = self.orders[order_id]
            order.status = OrderStatus.COMPLETED
            order.completed_at = datetime.now()
    
    def cancel_order(self, order_id: str):
        """Cancel an order"""
        if order_id in self.orders:
            self.orders[order_id].status = OrderStatus.CANCELLED
    
    def get_route_instructions(self, route: List[str]) -> List[Dict]:
        """Get detailed navigation instructions for a route"""
        return self.pathfinder.get_path_instructions(route)
    
    def update_current_location(self, location: str):
        """Update the RC car's current location"""
        self.current_location = location
        
        # Check if we've reached any delivery points
        # This is a simplified version - in reality, you'd have more sophisticated tracking
        for order in self.orders.values():
            if order.status == OrderStatus.IN_PROGRESS:
                if location == order.pickup_location:
                    # At pickup location
                    pass
                elif location == order.delivery_location:
                    # At delivery location - could auto-complete
                    pass
    
    def _build_route_info(self, route: List[str], orders: List[Order]) -> Dict[str, List[str]]:
        """Build mapping of locations to actions (pickup/deliver orders)"""
        route_info = {}
        picked_up = set()
        delivered = set()
        order_dict = {order.order_id: order for order in orders}
        
        # Simulate the route to track which orders are picked up and delivered at each location
        for location in route:
            actions = []
            
            # First, check for pickups
            for order in orders:
                if location == order.pickup_location and order.order_id not in picked_up:
                    actions.append(f"PICKUP: {order.order_id}")
                    picked_up.add(order.order_id)
            
            # Then, check for deliveries (only if order was picked up and not yet delivered)
            for order in orders:
                if (location == order.delivery_location and 
                    order.order_id in picked_up and 
                    order.order_id not in delivered):
                    actions.append(f"DELIVER: {order.order_id}")
                    delivered.add(order.order_id)
            
            if actions:
                route_info[location] = actions
        
        return route_info
    
    def get_statistics(self) -> Dict:
        """Get delivery system statistics"""
        total_orders = len(self.orders)
        completed = sum(1 for o in self.orders.values() 
                       if o.status == OrderStatus.COMPLETED)
        pending = sum(1 for o in self.orders.values() 
                     if o.status == OrderStatus.PENDING)
        in_progress = sum(1 for o in self.orders.values() 
                         if o.status == OrderStatus.IN_PROGRESS)
        
        return {
            'total_orders': total_orders,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'completion_rate': completed / total_orders if total_orders > 0 else 0.0
        }

                    