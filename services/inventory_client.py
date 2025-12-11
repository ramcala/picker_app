"""
Inventory Service Client for communicating with inventory service
"""
import httpx
import json
import logging
from config import ORDER_SERVICE_HOST, ORGANIZATION_ID
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class InventoryServiceClient:
    """Client for communicating with inventory service API"""
    
    def __init__(self, host: str = ORDER_SERVICE_HOST):
        self.host = host
        self.org_id = ORGANIZATION_ID
    
    def update_inventory(
        self,
        product_id: int,
        store_id: int,
        stock: float
    ) -> bool:
        """
        Update inventory in inventory service
        
        Args:
            product_id: Product ID
            store_id: Store ID
            stock: New stock quantity
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.host}/inventory-service/item"
            
            payload = {
                "organizationId": self.org_id,
                "productId": product_id,
                "storeId": store_id,
                "stock": stock
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                
                if response.status_code in [200, 201]:
                    logger.info(f"Successfully updated inventory for product {product_id} at store {store_id}")
                    return True
                else:
                    logger.error(f"Failed to update inventory: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.RequestError as e:
            logger.error(f"Network error updating inventory: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error updating inventory: {str(e)}")
            return False
    
    def get_inventory(self, product_id: int, store_id: int) -> Optional[Dict[str, Any]]:
        """
        Get inventory details from inventory service
        
        Args:
            product_id: Product ID
            store_id: Store ID
        
        Returns:
            Inventory data if found, None otherwise
        """
        try:
            url = f"{self.host}/inventory-service/item/{product_id}/{store_id}"
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Inventory not found for product {product_id} at store {store_id}: {response.status_code}")
                    return None
                    
        except httpx.RequestError as e:
            logger.error(f"Network error fetching inventory: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching inventory: {str(e)}")
            return None
    
    def get_inventory_by_product(self, product_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get inventory for all stores for a product
        
        Args:
            product_id: Product ID
        
        Returns:
            List of inventory data if found, None otherwise
        """
        try:
            url = f"{self.host}/inventory-service/product/{product_id}"
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Inventory not found for product {product_id}: {response.status_code}")
                    return None
                    
        except httpx.RequestError as e:
            logger.error(f"Network error fetching inventory: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching inventory: {str(e)}")
            return None
