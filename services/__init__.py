"""
Services package - contains all external service integrations
"""
from .order_client import OrderServiceClient
from .inventory_client import InventoryServiceClient
from .customer_client import CustomerServiceClient

__all__ = ["OrderServiceClient", "InventoryServiceClient", "CustomerServiceClient"]

