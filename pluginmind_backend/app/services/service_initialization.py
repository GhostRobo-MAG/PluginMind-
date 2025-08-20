"""
Service initialization and registration module.

Handles the registration of AI services at application startup,
providing a centralized place to configure the plugin registry.
"""

from app.core.logging import get_logger
from app.core.config import settings
from app.services.ai_service_interface import (
    AIServiceType,
    ai_service_registry
)
from app.services.openai_service import OpenAIService
from app.services.grok_service import GrokService

logger = get_logger(__name__)


def initialize_ai_services() -> None:
    """
    Initialize and register all AI services at startup.
    
    This function should be called during application initialization
    to register all available AI service implementations with the registry.
    
    The registration order can determine preference when multiple
    services provide the same capability.
    """
    logger.info("Initializing AI services registry")
    
    try:
        # Register OpenAI service for prompt optimization
        openai_service = OpenAIService()
        ai_service_registry.register(
            service_id="openai_optimizer",
            service=openai_service,
            service_type=AIServiceType.PROMPT_OPTIMIZER,
            replace_if_exists=True
        )
        logger.info("Registered OpenAI service as prompt optimizer")
        
        # Register OpenAI service for document processing
        ai_service_registry.register(
            service_id="openai_document",
            service=openai_service,
            service_type=AIServiceType.DOCUMENT_PROCESSOR,
            replace_if_exists=True
        )
        logger.info("Registered OpenAI service as document processor")
        
        # Register OpenAI service for chat processing
        ai_service_registry.register(
            service_id="openai_chat",
            service=openai_service,
            service_type=AIServiceType.CHAT_PROCESSOR,
            replace_if_exists=True
        )
        logger.info("Registered OpenAI service as chat processor")
        
        # Register OpenAI service for SEO generation
        ai_service_registry.register(
            service_id="openai_seo",
            service=openai_service,
            service_type=AIServiceType.SEO_GENERATOR,
            replace_if_exists=True
        )
        logger.info("Registered OpenAI service as SEO generator")
        
        # Register OpenAI service as generic analyzer (fallback)
        ai_service_registry.register(
            service_id="openai_generic",
            service=openai_service,
            service_type=AIServiceType.GENERIC_ANALYZER,
            replace_if_exists=True
        )
        logger.info("Registered OpenAI service as generic analyzer")
        
        # Register Grok service for crypto analysis
        grok_service = GrokService()
        ai_service_registry.register(
            service_id="grok_analyzer",
            service=grok_service,
            service_type=AIServiceType.CRYPTO_ANALYZER,
            replace_if_exists=True
        )
        logger.info("Registered Grok service as crypto analyzer")
        
        # Register Grok service as document processor (alternative)
        ai_service_registry.register(
            service_id="grok_document",
            service=grok_service,
            service_type=AIServiceType.DOCUMENT_PROCESSOR,
            replace_if_exists=True
        )
        logger.info("Registered Grok service as document processor")
        
        # Register Grok service as generic analyzer (alternative)
        ai_service_registry.register(
            service_id="grok_generic",
            service=grok_service,
            service_type=AIServiceType.GENERIC_ANALYZER,
            replace_if_exists=True
        )
        
        # Future: Register additional services based on configuration
        # This could be extended to load services dynamically from config
        # or from a plugin directory
        
        # Example of conditional registration based on config
        if hasattr(settings, 'enable_alternative_services') and settings.enable_alternative_services:
            # Register alternative services if configured
            logger.info("Alternative services enabled but not yet implemented")
        
        # Log registry status
        services = ai_service_registry.list_services()
        logger.info(
            f"AI services initialization complete. "
            f"Registered {len(services)} services: {list(services.keys())}"
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize AI services: {str(e)}")
        raise


def register_custom_service(
    service_id: str,
    service_class_path: str,
    service_type: AIServiceType,
    **kwargs
) -> None:
    """
    Dynamically register a custom AI service.
    
    This function allows runtime registration of custom AI service
    implementations, useful for testing or dynamic service loading.
    
    Args:
        service_id: Unique identifier for the service
        service_class_path: Full path to the service class (e.g., "module.ClassName")
        service_type: Type of service being registered
        **kwargs: Additional arguments to pass to service constructor
    
    Raises:
        ImportError: If the service class cannot be imported
        ValueError: If registration fails
    """
    try:
        # Dynamic import of the service class
        module_path, class_name = service_class_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        service_class = getattr(module, class_name)
        
        # Instantiate the service
        service = service_class(**kwargs)
        
        # Register with the registry
        ai_service_registry.register(
            service_id=service_id,
            service=service,
            service_type=service_type,
            replace_if_exists=True
        )
        
        logger.info(
            f"Dynamically registered service '{service_id}' "
            f"from {service_class_path}"
        )
        
    except ImportError as e:
        logger.error(f"Failed to import service class {service_class_path}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to register custom service {service_id}: {str(e)}")
        raise


def cleanup_ai_services() -> None:
    """
    Cleanup and shutdown AI services.
    
    This function should be called during application shutdown
    to properly cleanup any resources held by AI services.
    """
    logger.info("Cleaning up AI services")
    
    try:
        # Perform health checks before shutdown
        health_status = ai_service_registry.health_check_all()
        logger.info(f"Final health check before shutdown: {health_status}")
        
        # Future: Add any service-specific cleanup logic here
        # For example, closing persistent connections, saving state, etc.
        
        logger.info("AI services cleanup complete")
        
    except Exception as e:
        logger.warning(f"Error during AI services cleanup: {str(e)}")


# Example usage for testing alternative implementations
def register_mock_services_for_testing() -> None:
    """
    Register mock services for testing purposes.
    
    This function can be called in test environments to replace
    real AI services with mock implementations.
    """
    logger.info("Registering mock AI services for testing")
    
    # This would import and register mock implementations
    # from app.tests.mocks import MockOpenAIService, MockGrokService
    # 
    # mock_openai = MockOpenAIService()
    # ai_service_registry.register(
    #     service_id="mock_openai",
    #     service=mock_openai,
    #     service_type=AIServiceType.PROMPT_OPTIMIZER,
    #     replace_if_exists=True
    # )
    
    logger.info("Mock services registered for testing")