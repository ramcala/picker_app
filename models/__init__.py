"""
Database models and CRUD operations
"""
from .database import Base, SessionLocal, engine, get_db
from .product import Product, create_product, get_product, get_product_by_external_id, get_all_products, delete_product
from .inventory import Inventory, create_or_update_inventory, get_inventory, update_inventory_stock
from .customer import Customer, create_customer, get_customer, get_customer_by_external_id, get_all_customers, delete_customer
from .order import (
    Order, OrderItem, create_order, get_order, get_order_by_external_id, 
    get_order_by_reference, get_all_orders, get_orders_by_status, 
    update_order_status, update_order_picking_status, pack_order,
    create_order_item, get_order_items, get_order_item, update_order_item_picked_quantity
)
from .picking import (
    PickingActivity, CrateLabel, create_picking_activity, get_picking_activities,
    create_crate_label, get_crate_labels, get_crate_label_by_label
)
from .agent import Agent, create_agent, get_agent, get_agent_by_username, get_all_agents, update_agent_status, update_agent_password

__all__ = [
    # Database
    "Base", "SessionLocal", "engine", "get_db",
    # Product
    "Product", "create_product", "get_product", "get_product_by_external_id", "get_all_products", "delete_product",
    # Inventory
    "Inventory", "create_or_update_inventory", "get_inventory", "update_inventory_stock",
    # Customer
    "Customer", "create_customer", "get_customer", "get_customer_by_external_id", "get_all_customers", "delete_customer",
    # Order
    "Order", "OrderItem", "create_order", "get_order", "get_order_by_external_id", 
    "get_order_by_reference", "get_all_orders", "get_orders_by_status", 
    "update_order_status", "update_order_picking_status", "pack_order",
    "create_order_item", "get_order_items", "get_order_item", "update_order_item_picked_quantity",
    # Picking
    "PickingActivity", "CrateLabel", "create_picking_activity", "get_picking_activities",
    "create_crate_label", "get_crate_labels", "get_crate_label_by_label",
    # Agent
    "Agent", "create_agent", "get_agent", "get_agent_by_username", "get_all_agents", "update_agent_status", "update_agent_password",
]

