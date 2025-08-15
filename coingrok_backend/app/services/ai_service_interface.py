"""
Abstract interface for AI services with plugin-style registry.

Provides a uniform interface for different AI providers (OpenAI, Grok, etc.)
and a registry system for dynamic service management.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Protocol
from enum import Enum
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIServiceType(str, Enum):
    """Enumeration of available AI service types."""
    PROMPT_OPTIMIZER = "prompt_optimizer"
    CRYPTO_ANALYZER = "crypto_analyzer"
    # Future service types can be added here
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    NEWS_SUMMARIZER = "news_summarizer"


class AIServiceCapability(str, Enum):
    """Capabilities that AI services can provide."""
    PROMPT_OPTIMIZATION = "prompt_optimization"
    CRYPTO_ANALYSIS = "crypto_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NEWS_SUMMARIZATION = "news_summarization"
    MARKET_PREDICTION = "market_prediction"


class AIServiceMetadata:
    """Metadata about an AI service implementation."""
    
    def __init__(
        self,
        name: str,
        provider: str,
        version: str,
        capabilities: list[AIServiceCapability],
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ):
        self.name = name
        self.provider = provider
        self.version = version
        self.capabilities = capabilities
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    def supports_capability(self, capability: AIServiceCapability) -> bool:
        """Check if this service supports a specific capability."""
        return capability in self.capabilities
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            "name": self.name,
            "provider": self.provider,
            "version": self.version,
            "capabilities": [cap.value for cap in self.capabilities],
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }


class AIService(ABC):
    """
    Abstract base class for AI service implementations.
    
    All AI services must implement this interface to be compatible
    with the plugin registry system.
    """
    
    @abstractmethod
    def __init__(self):
        """Initialize the AI service with necessary configuration."""
        pass
    
    @abstractmethod
    async def process(self, input_text: str, **kwargs) -> str:
        """
        Process input text and return the result.
        
        Args:
            input_text: The text to process
            **kwargs: Additional service-specific parameters
            
        Returns:
            Processed text result
            
        Raises:
            AIServiceError: If processing fails
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> AIServiceMetadata:
        """
        Get metadata about this AI service.
        
        Returns:
            AIServiceMetadata object describing the service
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the service is healthy and available.
        
        Returns:
            True if service is healthy, False otherwise
        """
        pass
    
    async def validate_input(self, input_text: str) -> bool:
        """
        Validate input before processing (optional override).
        
        Args:
            input_text: Input to validate
            
        Returns:
            True if input is valid, False otherwise
        """
        # Default implementation - can be overridden
        if not input_text or not input_text.strip():
            return False
        return True
    
    async def prepare_request(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare the request payload for the AI service (optional override).
        
        Args:
            input_text: Input text to process
            **kwargs: Additional parameters
            
        Returns:
            Prepared request payload
        """
        # Default implementation - can be overridden
        return {"input": input_text, **kwargs}


class AIServiceRegistry:
    """
    Registry for managing AI service implementations.
    
    Provides a centralized way to register, retrieve, and manage
    different AI service implementations.
    """
    
    def __init__(self):
        """Initialize the registry with empty service maps."""
        self._services: Dict[str, AIService] = {}
        self._service_types: Dict[AIServiceType, list[str]] = {}
        self._capabilities: Dict[AIServiceCapability, list[str]] = {}
        logger.info("AI Service Registry initialized")
    
    def register(
        self, 
        service_id: str, 
        service: AIService,
        service_type: AIServiceType,
        replace_if_exists: bool = False
    ) -> None:
        """
        Register an AI service implementation.
        
        Args:
            service_id: Unique identifier for the service
            service: AIService implementation
            service_type: Type of service being registered
            replace_if_exists: Whether to replace existing service
            
        Raises:
            ValueError: If service already exists and replace_if_exists is False
        """
        if service_id in self._services and not replace_if_exists:
            raise ValueError(f"Service '{service_id}' already registered")
        
        # Validate service implements the interface correctly
        if not isinstance(service, AIService):
            raise TypeError(f"Service must implement AIService interface")
        
        # Register the service
        self._services[service_id] = service
        
        # Track by service type
        if service_type not in self._service_types:
            self._service_types[service_type] = []
        if service_id not in self._service_types[service_type]:
            self._service_types[service_type].append(service_id)
        
        # Track by capabilities
        metadata = service.get_metadata()
        for capability in metadata.capabilities:
            if capability not in self._capabilities:
                self._capabilities[capability] = []
            if service_id not in self._capabilities[capability]:
                self._capabilities[capability].append(service_id)
        
        logger.info(
            f"Registered AI service '{service_id}' "
            f"(type: {service_type.value}, provider: {metadata.provider})"
        )
    
    def get_service(self, service_id: str) -> AIService:
        """
        Get a specific AI service by ID.
        
        Args:
            service_id: Unique identifier of the service
            
        Returns:
            AIService implementation
            
        Raises:
            KeyError: If service is not found
        """
        if service_id not in self._services:
            raise KeyError(f"Service '{service_id}' not found in registry")
        return self._services[service_id]
    
    def get_services_by_type(self, service_type: AIServiceType) -> list[AIService]:
        """
        Get all services of a specific type.
        
        Args:
            service_type: Type of services to retrieve
            
        Returns:
            List of AIService implementations
        """
        service_ids = self._service_types.get(service_type, [])
        return [self._services[sid] for sid in service_ids]
    
    def get_services_by_capability(
        self, 
        capability: AIServiceCapability
    ) -> list[AIService]:
        """
        Get all services that support a specific capability.
        
        Args:
            capability: Required capability
            
        Returns:
            List of AIService implementations supporting the capability
        """
        service_ids = self._capabilities.get(capability, [])
        return [self._services[sid] for sid in service_ids]
    
    def get_preferred_service(
        self, 
        service_type: AIServiceType
    ) -> Optional[AIService]:
        """
        Get the preferred (first registered) service of a type.
        
        Args:
            service_type: Type of service needed
            
        Returns:
            AIService implementation or None if no services registered
        """
        services = self.get_services_by_type(service_type)
        return services[0] if services else None
    
    def list_services(self) -> Dict[str, AIServiceMetadata]:
        """
        List all registered services with their metadata.
        
        Returns:
            Dictionary mapping service IDs to metadata
        """
        return {
            service_id: service.get_metadata()
            for service_id, service in self._services.items()
        }
    
    def unregister(self, service_id: str) -> bool:
        """
        Unregister a service from the registry.
        
        Args:
            service_id: ID of service to remove
            
        Returns:
            True if service was removed, False if not found
        """
        if service_id not in self._services:
            return False
        
        # Get service metadata before removing
        service = self._services[service_id]
        metadata = service.get_metadata()
        
        # Remove from main registry
        del self._services[service_id]
        
        # Remove from type tracking
        for service_type, service_ids in self._service_types.items():
            if service_id in service_ids:
                service_ids.remove(service_id)
        
        # Remove from capability tracking
        for capability in metadata.capabilities:
            if capability in self._capabilities and service_id in self._capabilities[capability]:
                self._capabilities[capability].remove(service_id)
        
        logger.info(f"Unregistered AI service '{service_id}'")
        return True
    
    async def health_check_all(self) -> Dict[str, bool]:
        """
        Perform health checks on all registered services.
        
        Returns:
            Dictionary mapping service IDs to health status
        """
        results = {}
        for service_id, service in self._services.items():
            try:
                results[service_id] = await service.health_check()
            except Exception as e:
                logger.warning(f"Health check failed for service '{service_id}': {str(e)}")
                results[service_id] = False
        return results


# Global registry instance
ai_service_registry = AIServiceRegistry()