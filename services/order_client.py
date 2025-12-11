"""
Order Service Client for communicating with order service
"""
import httpx
import json
import logging
from config import ORDER_SERVICE_HOST, ORGANIZATION_ID, ORDER_SERVICE_USER_ID
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class OrderServiceClient:
    """Client for communicating with order service API"""
    
    def __init__(self, host: str = ORDER_SERVICE_HOST):
        self.host = host
        self.org_id = ORGANIZATION_ID
        self.user_id = ORDER_SERVICE_USER_ID
    
    def update_order_status(
        self,
        reference_number: str,
        status: str,
        crates: list = None,
        package_metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Update order status in order service
        
        Args:
            reference_number: Order reference number
            status: New status (e.g., "PACKED")
            crates: List of crate labels
            package_metadata: Package metadata with weight and items
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.host}/order-service/order/{reference_number}"
            
            # Build details JSON
            details = {
                "crates": crates or []
            }
            
            payload = {
                "organizationId": self.org_id,
                "user": json.dumps({"id": int(self.user_id)}),
                "status": status,
                "details": json.dumps(details),
                "packageMetaData": package_metadata or {}
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.patch(url, json=payload)
                
                if response.status_code in [200, 201]:
                    logger.info(f"Successfully updated order {reference_number} to {status}")
                    return True
                else:
                    logger.error(f"Failed to update order {reference_number}: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.RequestError as e:
            logger.error(f"Network error updating order {reference_number}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error updating order {reference_number}: {str(e)}")
            return False
    
    def get_order(self, reference_number: str) -> Optional[Dict[str, Any]]:
        """
        Get order details from order service
        
        Args:
            reference_number: Order reference number
        
        Returns:
            Order data if found, None otherwise
        """
        try:
            url = f"{self.host}/order-service/order/{reference_number}"
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Order {reference_number} not found: {response.status_code}")
                    return None
                    
        except httpx.RequestError as e:
            logger.error(f"Network error fetching order {reference_number}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching order {reference_number}: {str(e)}")
            return None
