"""
Customer Service Client for communicating with customer service
"""
import httpx
import json
import logging
from config import ORDER_SERVICE_HOST, ORGANIZATION_ID
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CustomerServiceClient:
    """Client for communicating with customer service API"""
    
    def __init__(self, host: str = ORDER_SERVICE_HOST):
        self.host = host
        self.org_id = ORGANIZATION_ID
    
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get customer details from customer service
        
        Args:
            customer_id: Customer ID
        
        Returns:
            Customer data if found, None otherwise
        """
        try:
            url = f"{self.host}/customer-service/customer/{customer_id}"
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Customer {customer_id} not found: {response.status_code}")
                    return None
                    
        except httpx.RequestError as e:
            logger.error(f"Network error fetching customer {customer_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching customer {customer_id}: {str(e)}")
            return None
    
    def update_customer(
        self,
        customer_id: str,
        customer_data: Dict[str, Any]
    ) -> bool:
        """
        Update customer information
        
        Args:
            customer_id: Customer ID
            customer_data: Customer data to update
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.host}/customer-service/customer/{customer_id}"
            
            payload = {
                "organizationId": self.org_id,
                **customer_data
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.patch(url, json=payload)
                
                if response.status_code in [200, 201]:
                    logger.info(f"Successfully updated customer {customer_id}")
                    return True
                else:
                    logger.error(f"Failed to update customer {customer_id}: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.RequestError as e:
            logger.error(f"Network error updating customer {customer_id}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error updating customer {customer_id}: {str(e)}")
            return False
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new customer
        
        Args:
            customer_data: Customer data
        
        Returns:
            Created customer data if successful, None otherwise
        """
        try:
            url = f"{self.host}/customer-service/customer"
            
            payload = {
                "organizationId": self.org_id,
                **customer_data
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                
                if response.status_code in [200, 201]:
                    logger.info(f"Successfully created customer")
                    return response.json()
                else:
                    logger.error(f"Failed to create customer: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.RequestError as e:
            logger.error(f"Network error creating customer: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return None
