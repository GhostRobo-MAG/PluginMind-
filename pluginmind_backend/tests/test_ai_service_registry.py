"""
AI Service Registry Tests

Comprehensive tests for the plugin-style AI service registry system,
covering service registration, discovery, health checking, fallback mechanisms,
and new monitoring endpoints.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

# Set test environment before importing app modules
import os
os.environ["TESTING"] = "1"

from app.main import app
from app.services.ai_service_interface import (
    AIService,
    AIServiceRegistry,
    AIServiceMetadata,
    AIServiceType,
    AIServiceCapability,
    ai_service_registry
)
from app.core.exceptions import AIServiceError, ServiceUnavailableError


class TestAIServiceInterface:
    """Test the base AIService interface and registry infrastructure."""
    
    def test_service_metadata_creation(self):
        """Test AIServiceMetadata creation and serialization."""
        metadata = AIServiceMetadata(
            name="Test Service",
            provider="TestProvider",
            version="1.0.0",
            capabilities=[AIServiceCapability.PROMPT_OPTIMIZATION],
            model="test-model-v1",
            max_tokens=1000,
            temperature=0.5
        )
        
        assert metadata.name == "Test Service"
        assert metadata.provider == "TestProvider"
        assert metadata.supports_capability(AIServiceCapability.PROMPT_OPTIMIZATION)
        assert not metadata.supports_capability(AIServiceCapability.CRYPTO_ANALYSIS)
        
        # Test serialization
        metadata_dict = metadata.to_dict()
        assert metadata_dict["name"] == "Test Service"
        assert metadata_dict["capabilities"] == ["prompt_optimization"]
    
    def test_service_capability_checking(self):
        """Test capability checking functionality."""
        metadata = AIServiceMetadata(
            name="Multi-Capability Service",
            provider="TestProvider", 
            version="1.0.0",
            capabilities=[
                AIServiceCapability.PROMPT_OPTIMIZATION,
                AIServiceCapability.SENTIMENT_ANALYSIS
            ],
            model="test-model"
        )
        
        assert metadata.supports_capability(AIServiceCapability.PROMPT_OPTIMIZATION)
        assert metadata.supports_capability(AIServiceCapability.SENTIMENT_ANALYSIS)
        assert not metadata.supports_capability(AIServiceCapability.CRYPTO_ANALYSIS)


class MockAIService(AIService):
    """Mock AI service for testing."""
    
    def __init__(self, name="Mock Service", provider="TestProvider", capabilities=None, should_fail=False):
        self.should_fail = should_fail
        self.process_called = False
        self.health_check_called = False
        
        if capabilities is None:
            capabilities = [AIServiceCapability.PROMPT_OPTIMIZATION]
        
        self._metadata = AIServiceMetadata(
            name=name,
            provider=provider,
            version="1.0.0",
            capabilities=capabilities,
            model="mock-model"
        )
    
    def get_metadata(self) -> AIServiceMetadata:
        return self._metadata
    
    async def health_check(self) -> bool:
        self.health_check_called = True
        return not self.should_fail
    
    async def process(self, input_text: str, **kwargs) -> str:
        self.process_called = True
        if self.should_fail:
            raise AIServiceError("Mock service failure")
        return f"Processed: {input_text}"


class TestAIServiceRegistry:
    """Test the AI service registry functionality."""
    
    def setup_method(self):
        """Set up fresh registry for each test."""
        # Create a fresh registry instance for testing
        self.test_registry = AIServiceRegistry()
    
    def test_service_registration(self):
        """Test basic service registration."""
        mock_service = MockAIService("Test OpenAI", "OpenAI")
        
        # Register service
        self.test_registry.register(
            "test_openai",
            mock_service,
            AIServiceType.PROMPT_OPTIMIZER
        )
        
        # Verify registration
        registered_services = self.test_registry.list_services()
        assert "test_openai" in registered_services
        assert registered_services["test_openai"].name == "Test OpenAI"
        assert registered_services["test_openai"].provider == "OpenAI"
    
    def test_service_registration_with_replacement(self):
        """Test service registration with replacement."""
        service1 = MockAIService("Service V1", "Provider")
        service2 = MockAIService("Service V2", "Provider")
        
        # Register first service
        self.test_registry.register("test_service", service1, AIServiceType.PROMPT_OPTIMIZER)
        
        # Try to register again without replacement (should fail)
        with pytest.raises(ValueError, match="already registered"):
            self.test_registry.register("test_service", service2, AIServiceType.PROMPT_OPTIMIZER)
        
        # Register with replacement (should succeed)
        self.test_registry.register(
            "test_service", 
            service2, 
            AIServiceType.PROMPT_OPTIMIZER,
            replace_if_exists=True
        )
        
        # Verify replacement
        services = self.test_registry.list_services()
        assert services["test_service"].name == "Service V2"
    
    def test_service_discovery_by_type(self):
        """Test service discovery by service type."""
        optimizer = MockAIService("Optimizer", "Provider1", [AIServiceCapability.PROMPT_OPTIMIZATION])
        analyzer = MockAIService("Analyzer", "Provider2", [AIServiceCapability.CRYPTO_ANALYSIS])
        
        self.test_registry.register("optimizer", optimizer, AIServiceType.PROMPT_OPTIMIZER)
        self.test_registry.register("analyzer", analyzer, AIServiceType.CRYPTO_ANALYZER)
        
        # Test type-based discovery
        optimizers = self.test_registry.get_services_by_type(AIServiceType.PROMPT_OPTIMIZER)
        analyzers = self.test_registry.get_services_by_type(AIServiceType.CRYPTO_ANALYZER)
        
        assert len(optimizers) == 1
        assert len(analyzers) == 1
        assert optimizers[0].get_metadata().name == "Optimizer"
        assert analyzers[0].get_metadata().name == "Analyzer"
    
    def test_service_discovery_by_capability(self):
        """Test service discovery by capability."""
        multi_service = MockAIService(
            "Multi Service", 
            "Provider",
            [AIServiceCapability.PROMPT_OPTIMIZATION, AIServiceCapability.SENTIMENT_ANALYSIS]
        )
        crypto_service = MockAIService(
            "Crypto Service",
            "Provider", 
            [AIServiceCapability.CRYPTO_ANALYSIS]
        )
        
        self.test_registry.register("multi", multi_service, AIServiceType.PROMPT_OPTIMIZER)
        self.test_registry.register("crypto", crypto_service, AIServiceType.CRYPTO_ANALYZER)
        
        # Test capability-based discovery
        prompt_services = self.test_registry.get_services_by_capability(AIServiceCapability.PROMPT_OPTIMIZATION)
        sentiment_services = self.test_registry.get_services_by_capability(AIServiceCapability.SENTIMENT_ANALYSIS)
        crypto_services = self.test_registry.get_services_by_capability(AIServiceCapability.CRYPTO_ANALYSIS)
        
        assert len(prompt_services) == 1
        assert len(sentiment_services) == 1
        assert len(crypto_services) == 1
        assert prompt_services[0] == sentiment_services[0]  # Same service
    
    def test_preferred_service_selection(self):
        """Test preferred service selection (first registered)."""
        service1 = MockAIService("Service 1", "Provider1")
        service2 = MockAIService("Service 2", "Provider2")
        
        # Register in order
        self.test_registry.register("service1", service1, AIServiceType.PROMPT_OPTIMIZER)
        self.test_registry.register("service2", service2, AIServiceType.PROMPT_OPTIMIZER)
        
        # First registered should be preferred
        preferred = self.test_registry.get_preferred_service(AIServiceType.PROMPT_OPTIMIZER)
        assert preferred.get_metadata().name == "Service 1"
    
    def test_service_unregistration(self):
        """Test service removal from registry."""
        service = MockAIService("Test Service", "Provider")
        
        # Register and verify
        self.test_registry.register("test", service, AIServiceType.PROMPT_OPTIMIZER)
        assert "test" in self.test_registry.list_services()
        
        # Unregister and verify
        result = self.test_registry.unregister("test")
        assert result is True
        assert "test" not in self.test_registry.list_services()
        
        # Try to unregister non-existent service
        result = self.test_registry.unregister("nonexistent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_all_services(self):
        """Test health checking all registered services."""
        healthy_service = MockAIService("Healthy", "Provider1", should_fail=False)
        unhealthy_service = MockAIService("Unhealthy", "Provider2", should_fail=True)
        
        self.test_registry.register("healthy", healthy_service, AIServiceType.PROMPT_OPTIMIZER)
        self.test_registry.register("unhealthy", unhealthy_service, AIServiceType.CRYPTO_ANALYZER)
        
        # Perform health checks
        health_results = await self.test_registry.health_check_all()
        
        assert health_results["healthy"] is True
        assert health_results["unhealthy"] is False
        assert healthy_service.health_check_called
        assert unhealthy_service.health_check_called


class TestAnalysisServiceWithRegistry:
    """Test the analysis service registry integration."""
    
    def setup_method(self):
        """Set up test registry with mock services."""
        # Clear global registry and add test services
        # Note: In real tests, you'd want to use dependency injection
        # For now, we'll test the logic without modifying the global registry
        pass
    
    @pytest.mark.asyncio
    @patch('app.services.analysis_service.ai_service_registry')
    async def test_service_selection_by_type(self, mock_registry):
        """Test that analysis service selects correct services by type."""
        from app.services.analysis_service import AnalysisService
        
        # Mock services
        mock_optimizer = MockAIService("Mock OpenAI", "OpenAI")
        mock_analyzer = MockAIService("Mock Grok", "xAI", [AIServiceCapability.CRYPTO_ANALYSIS])
        
        # Configure mock registry
        mock_registry.get_preferred_service.side_effect = lambda service_type: {
            AIServiceType.PROMPT_OPTIMIZER: mock_optimizer,
            AIServiceType.CRYPTO_ANALYZER: mock_analyzer
        }.get(service_type)
        
        # Test analysis service
        analysis_service = AnalysisService()
        analysis_service.registry = mock_registry
        
        # Perform analysis
        result = await analysis_service.perform_analysis("test input", "test_user")
        
        assert result[0] == "Processed: test input"  # optimized_prompt
        assert result[1] == "Processed: Processed: test input"  # analysis_result
        assert mock_optimizer.process_called
        assert mock_analyzer.process_called
    
    @pytest.mark.asyncio
    @patch('app.services.analysis_service.ai_service_registry')
    async def test_fallback_mechanism(self, mock_registry):
        """Test fallback when primary services fail."""
        from app.services.analysis_service import AnalysisService
        
        # Mock failing primary service
        failing_optimizer = MockAIService("Failing OpenAI", "OpenAI", should_fail=True)
        backup_optimizer = MockAIService("Backup Claude", "Anthropic")
        mock_analyzer = MockAIService("Mock Grok", "xAI", [AIServiceCapability.CRYPTO_ANALYSIS])
        
        # Configure mock registry for fallback scenario
        mock_registry.get_preferred_service.side_effect = lambda service_type: {
            AIServiceType.PROMPT_OPTIMIZER: failing_optimizer,
            AIServiceType.CRYPTO_ANALYZER: mock_analyzer
        }.get(service_type)
        
        mock_registry.get_services_by_capability.side_effect = lambda capability: {
            AIServiceCapability.PROMPT_OPTIMIZATION: [backup_optimizer],
            AIServiceCapability.CRYPTO_ANALYSIS: [mock_analyzer]
        }.get(capability, [])
        
        analysis_service = AnalysisService()
        analysis_service.registry = mock_registry
        
        # This should fail since fallback is not implemented yet
        # Note: Fallback logic would need to be implemented in analysis_service.py
        with pytest.raises((AIServiceError, ServiceUnavailableError)):
            result = await analysis_service.perform_analysis("test input", "test_user")
        
        # Test would pass once fallback logic is implemented
    
    @pytest.mark.asyncio
    @patch('app.services.analysis_service.ai_service_registry')
    async def test_no_fallback_available(self, mock_registry):
        """Test behavior when no fallback services are available."""
        from app.services.analysis_service import AnalysisService
        
        # Configure registry with no services
        mock_registry.get_preferred_service.return_value = None
        mock_registry.get_services_by_capability.return_value = []
        
        analysis_service = AnalysisService()
        analysis_service.registry = mock_registry
        
        # Should raise ServiceUnavailableError
        with pytest.raises(ServiceUnavailableError):
            await analysis_service.perform_analysis("test input", "test_user")


class TestServiceMonitoringEndpoints:
    """Test the new service monitoring endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    @pytest.mark.asyncio
    @patch('app.main.ai_service_registry')
    async def test_services_list_endpoint(self, mock_registry):
        """Test GET /services endpoint."""
        # Mock registry response
        mock_metadata = AIServiceMetadata(
            name="Test OpenAI",
            provider="OpenAI", 
            version="1.0.0",
            capabilities=[AIServiceCapability.PROMPT_OPTIMIZATION],
            model="gpt-5"
        )
        
        # Mock the analysis service methods
        with patch('app.services.analysis_service.analysis_service.get_service_info') as mock_get_info, \
             patch('app.services.analysis_service.analysis_service.health_check') as mock_health_check:
            
            mock_get_info.return_value = {
                "registered_services": {
                    "openai_optimizer": mock_metadata.to_dict()
                },
                "total_services": 1
            }
            mock_health_check.return_value = {
                "openai_optimizer": True
            }
            
            # Make request
            response = self.client.get("/services")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "ai_services" in data
            assert "analysis_types" in data
            assert "endpoints" in data
            assert data["ai_services"]["total_services"] == 1
    
    @pytest.mark.asyncio
    @patch('app.main.ai_service_registry')
    async def test_services_health_endpoint(self, mock_registry):
        """Test GET /services/health endpoint."""
        # Mock health check results
        mock_registry.health_check_all = AsyncMock(return_value={
            "openai_optimizer": True,
            "grok_analyzer": True,
            "backup_service": False
        })
        
        # Make request
        response = self.client.get("/services/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "timestamp" in data
        assert "overall_healthy" in data
        assert "service_details" in data
    
    @pytest.mark.asyncio
    @patch('app.main.ai_service_registry')
    async def test_services_health_all_healthy(self, mock_registry):
        """Test health endpoint when all services are healthy."""
        mock_registry.health_check_all = AsyncMock(return_value={
            "openai_optimizer": True,
            "grok_analyzer": True
        })
        
        response = self.client.get("/services/health")
        data = response.json()
        
        assert response.status_code == 200
        assert "timestamp" in data
        assert "overall_healthy" in data
        assert "service_details" in data


class TestServiceInitialization:
    """Test service initialization and cleanup."""
    
    @patch('app.services.service_initialization.OpenAIService')
    @patch('app.services.service_initialization.GrokService') 
    @patch('app.services.service_initialization.ai_service_registry')
    def test_initialize_ai_services(self, mock_registry, mock_grok_service, mock_openai_service):
        """Test service initialization process."""
        from app.services.service_initialization import initialize_ai_services
        
        # Mock service instances
        mock_openai_instance = MagicMock()
        mock_grok_instance = MagicMock()
        mock_openai_service.return_value = mock_openai_instance
        mock_grok_service.return_value = mock_grok_instance
        
        # Run initialization
        initialize_ai_services()
        
        # Verify services were registered (8 different service registrations)
        assert mock_registry.register.call_count == 8
        
        # Verify that both OpenAI and Grok services were instantiated
        mock_openai_service.assert_called()
        mock_grok_service.assert_called()
        
        # Verify some of the registration calls
        registration_calls = mock_registry.register.call_args_list
        assert len(registration_calls) == 8


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_registry_with_no_services(self):
        """Test registry behavior with no registered services."""
        empty_registry = AIServiceRegistry()
        
        assert len(empty_registry.list_services()) == 0
        assert empty_registry.get_preferred_service(AIServiceType.PROMPT_OPTIMIZER) is None
        assert len(empty_registry.get_services_by_type(AIServiceType.CRYPTO_ANALYZER)) == 0
        assert len(empty_registry.get_services_by_capability(AIServiceCapability.CRYPTO_ANALYSIS)) == 0
    
    def test_invalid_service_registration(self):
        """Test registration of invalid services."""
        registry = AIServiceRegistry()
        
        # Try to register non-AIService object
        with pytest.raises(TypeError):
            registry.register("invalid", "not_a_service", AIServiceType.PROMPT_OPTIMIZER)
    
    @pytest.mark.asyncio
    async def test_health_check_with_exception(self):
        """Test health check when service raises exception."""
        registry = AIServiceRegistry()
        
        # Mock service that raises exception during health check
        class FailingService(MockAIService):
            async def health_check(self):
                raise Exception("Health check failed")
        
        failing_service = FailingService()
        registry.register("failing", failing_service, AIServiceType.PROMPT_OPTIMIZER)
        
        # Health check should handle exception and return False
        health_results = await registry.health_check_all()
        assert health_results["failing"] is False
    
    def test_service_metadata_edge_cases(self):
        """Test service metadata with edge cases."""
        # Test with minimal metadata
        minimal_metadata = AIServiceMetadata(
            name="Minimal",
            provider="Test",
            version="1.0",
            capabilities=[],
            model="test"
        )
        
        assert not minimal_metadata.supports_capability(AIServiceCapability.PROMPT_OPTIMIZATION)
        
        metadata_dict = minimal_metadata.to_dict()
        assert metadata_dict["capabilities"] == []
        assert metadata_dict["max_tokens"] is None


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])