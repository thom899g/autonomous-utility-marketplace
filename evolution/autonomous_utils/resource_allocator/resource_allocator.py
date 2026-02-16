import logging
from typing import Dict, Optional, Any
from pydantic import BaseModel, validator
from evolution.core.agent_master import MasterAgentJudge

logger = logging.getLogger(__name__)

class ResourceRequest(BaseModel):
    """Pydantic model for resource allocation requests."""
    type: str
    quantity: float
    user_id: str
    
    @validator('quantity')
    def check_quantity(cls, v, field_info):
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v

class ResourceAllocator:
    """Handles resource allocation for businesses using AI utilities."""
    
    def __init__(self, available_resources: Dict[str, float]):
        self.available = available_resources
        self.requested = {}
        self.user_limitations = {}  # To track limitations per user
        
        logger.info("Resource Allocator initialized with resources: %s", str(available_resources))
        
    def allocate_resource(self, user_id: str, request: ResourceRequest) -> Dict[str, Any]:
        """Allocates resources based on user requests.
        
        Args:
            user_id: Unique identifier for the user making the request.
            request: Pydantic model containing resource details.
            
        Returns:
            Dict with allocation status and details.
            
        Raises:
            ValueError if resource allocation fails.
        """
        try:
            # Validate resource availability
            self._validate_resource_availability(request.type)
            
            # Calculate required quantity
            required = request.quantity
            
            # Check user limitations
            self._check_user_limitations(user_id, required)
            
            # Perform allocation
            allocated = self._perform_allocation(request.type, required, user_id)
            
            logger.info("Allocated %s units of %s to user %s", str(allocated), request.type, user_id)
            
            return {
                "status": "success",
                "allocated_quantity": allocated,
                "remaining_resources": self.available[request.type]
            }
            
        except Exception as e:
            logger.error("Resource allocation failed: %s", str(e))
            raise ValueError(f"Failed to allocate resources: {str(e)}")
    
    def _validate_resource_availability(self, resource_type: str) -> None:
        """Validates if the requested resource is available."""
        if resource_type not in self.available or self.available[resource_type] <= 0:
            raise ValueError("Resource unavailable or insufficient")
    
    def _check_user_limitations(self, user_id: str, quantity: float) -> None:
        """Implements limitations per user to prevent abuse."""
        if user_id in self.user_limitations:
            total_requested = self.user_limitations[user_id] + quantity
            if total_requested > 1000:  # Arbitrary limit for demonstration
                raise ValueError("User has exceeded allocation limits")
        else:
            self.user_limitations[user_id] = quantity
    
    def _perform_allocation(self, resource_type: str, quantity: float, user_id: str) -> float:
        """Performs the actual resource allocation."""
        if self.available[resource_type] >= quantity:
            self.available[resource_type] -= quantity
            return quantity
        else:
            raise ValueError("Insufficient resources available")
    
    def get_resource_status(self, resource_type: Optional[str] = None) -> Dict[str, Any]:
        """Returns status of all or specific resources."""
        if resource_type:
            return {resource_type: self.available.get(resource_type, 0)}
        else:
            return dict(self.available)