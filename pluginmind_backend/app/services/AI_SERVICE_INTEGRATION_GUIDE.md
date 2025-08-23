# Adding New AI Services to PluginMind

> **Complete Developer Guide for Extending the AI Service Registry**

## Table of Contents
1. [Overview](#overview)
2. [Architecture Understanding](#architecture-understanding)
3. [Step-by-Step Integration Process](#step-by-step-integration-process)
4. [Practical Examples](#practical-examples)
5. [Advanced Configuration](#advanced-configuration)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Best Practices](#best-practices)

---

## Overview

### What is the PluginMind AI Service Registry?

PluginMind uses a **plugin architecture** that allows you to seamlessly integrate multiple AI services into your application. This design pattern provides:

- **🔌 Hot-swappable AI services** - Add or remove services without changing core logic
- **🔄 Automatic fallback mechanisms** - Seamlessly switch between services on failure
- **🏥 Built-in health monitoring** - Real-time service availability tracking
- **🎯 Type-safe integration** - Pydantic models ensure data consistency
- **📊 Service discovery** - Automatic routing based on capabilities

### Current Services

PluginMind comes with 8 pre-configured AI services:

| Provider | Service Types | Use Cases |
|----------|--------------|-----------|
| **OpenAI** | Document, Chat, SEO, Crypto | GPT-4/GPT-3.5 for general AI tasks |
| **Grok xAI** | Document, Chat, SEO, Crypto | Advanced analysis with Grok models |

### Benefits of the Plugin Architecture

1. **Vendor Independence** - Not locked into a single AI provider
2. **Cost Optimization** - Route requests to most cost-effective service
3. **Reliability** - Automatic failover when services are down
4. **Scalability** - Add new services as they become available
5. **Testing** - Easy mock service injection for testing

---

## Architecture Understanding

### Core Components

```
┌─────────────────────────────────────────────────────┐
│                   API Request                       │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│              Analysis Service                       │
│         (Orchestration & Routing)                   │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│           AI Service Registry                       │
│      (Service Discovery & Selection)                │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│     Individual AI Service Implementations            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │ OpenAI   │ │   Grok   │ │  Claude  │  ...         │
│  └──────────┘ └──────────┘ └──────────┘              │
└─────────────────────────────────────────────────────-┘
```

### Key Interfaces

#### AIServiceInterface (Abstract Base)
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIServiceInterface(ABC):
    """Base interface that all AI services must implement"""
    
    @abstractmethod
    async def analyze(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Perform AI analysis"""
        pass
    
    @abstractmethod
    async def get_health(self) -> bool:
        """Check if service is healthy"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of supported analysis types"""
        pass
```

---

## Step-by-Step Integration Process

### 1. Create New AI Service Class

Let's create a new AI service for **Anthropic Claude**:

#### File: `app/services/claude_service.py`

```python
"""
Anthropic Claude AI Service Implementation
Provides advanced reasoning and analysis capabilities
"""

import os
import httpx
from typing import Dict, Any, List, Optional
from app.services.ai_service_interface import AIServiceInterface, AIServiceMetadata
from app.core.logging import get_logger
from app.core.exceptions import ServiceUnavailableError, RateLimitError

logger = get_logger(__name__)

class ClaudeService(AIServiceInterface):
    """Anthropic Claude implementation of the AI service interface"""
    
    def __init__(self):
        """Initialize Claude service with API configuration"""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
        self.timeout = httpx.Timeout(
            connect=10.0,
            read=60.0,
            write=10.0,
            pool=5.0
        )
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not configured")
    
    async def analyze(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Perform analysis using Claude AI
        
        Args:
            prompt: The prompt to send to Claude
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Dict containing the analysis results
        """
        if not self.api_key:
            raise ServiceUnavailableError("Claude service not configured")
        
        # Prepare the request
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Build the message
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        # Add system prompt if provided
        if "system_prompt" in kwargs:
            data["system"] = kwargs["system_prompt"]
        
        try:
            # Make the API call
            response = await self.client.post(
                self.api_url,
                headers=headers,
                json=data
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get("retry-after", 60)
                raise RateLimitError(
                    f"Claude API rate limit exceeded",
                    retry_after=int(retry_after)
                )
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            return {
                "content": result["content"][0]["text"],
                "model": result["model"],
                "usage": result.get("usage", {}),
                "service": "claude"
            }
            
        except httpx.TimeoutException:
            logger.error("Claude API timeout")
            raise ServiceUnavailableError("Claude API timeout")
        except httpx.HTTPError as e:
            logger.error(f"Claude API error: {str(e)}")
            raise ServiceUnavailableError(f"Claude API error: {str(e)}")
    
    async def get_health(self) -> bool:
        """
        Check Claude service health
        
        Returns:
            True if service is healthy, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            # Simple health check - verify API key is valid
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Use a minimal request to check connectivity
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 1
            }
            
            response = await self.client.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=5.0  # Quick timeout for health check
            )
            
            return response.status_code in [200, 429]  # 429 means working but rate limited
            
        except Exception as e:
            logger.debug(f"Claude health check failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """
        Return Claude's capabilities
        
        Returns:
            List of supported analysis types
        """
        return [
            "document",     # Document analysis
            "chat",        # Conversational AI
            "code",        # Code generation and analysis
            "reasoning",   # Complex reasoning tasks
            "creative"     # Creative writing
        ]
    
    def get_metadata(self) -> AIServiceMetadata:
        """
        Return service metadata
        
        Returns:
            Metadata about this AI service
        """
        return AIServiceMetadata(
            service_id="claude",
            name="Anthropic Claude",
            provider="Anthropic",
            model=self.model,
            capabilities=self.get_capabilities(),
            is_available=bool(self.api_key)
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context manager exit"""
        await self.client.aclose()


# Service factory functions for different analysis types
def create_claude_document_service() -> ClaudeService:
    """Factory for document analysis service"""
    return ClaudeService()

def create_claude_chat_service() -> ClaudeService:
    """Factory for chat service"""
    return ClaudeService()

def create_claude_code_service() -> ClaudeService:
    """Factory for code analysis service"""
    return ClaudeService()
```

### 2. Service Registration

Register your new service in the initialization system:

#### File: `app/services/service_initialization.py`

Add the following to the `initialize_ai_services()` function:

```python
from app.services.claude_service import (
    create_claude_document_service,
    create_claude_chat_service,
    create_claude_code_service
)

def initialize_ai_services():
    """Initialize and register all AI services"""
    
    # ... existing services ...
    
    # Register Claude services
    if os.getenv("ANTHROPIC_API_KEY"):
        # Document processing with Claude
        ai_service_registry.register_service(
            service_id="claude_document",
            service=create_claude_document_service(),
            service_type="document",
            priority=2  # Higher priority than Grok, lower than OpenAI
        )
        
        # Chat with Claude
        ai_service_registry.register_service(
            service_id="claude_chat",
            service=create_claude_chat_service(),
            service_type="chat",
            priority=2
        )
        
        # Code analysis with Claude (new capability!)
        ai_service_registry.register_service(
            service_id="claude_code",
            service=create_claude_code_service(),
            service_type="code",
            priority=1  # Claude is excellent at code
        )
        
        logger.info("Claude AI services registered successfully")
```

### 3. Configuration Setup

Add configuration support for your new service:

#### File: `app/core/config.py`

```python
class Settings(BaseModel):
    # ... existing configuration ...
    
    # Anthropic Claude Configuration
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    claude_model: str = Field("claude-3-opus-20240229", env="CLAUDE_MODEL")
    claude_max_tokens: int = Field(4096, env="CLAUDE_MAX_TOKENS")
    claude_temperature: float = Field(0.7, env="CLAUDE_TEMPERATURE")
    claude_timeout_seconds: int = Field(60, env="CLAUDE_TIMEOUT_SECONDS")
    
    def _validate_configuration(self):
        """Enhanced validation including Claude"""
        errors = []
        warnings = []
        
        # ... existing validation ...
        
        # Claude configuration validation
        if self.anthropic_api_key:
            if len(self.anthropic_api_key) < 10:
                errors.append("ANTHROPIC_API_KEY appears invalid (too short)")
            else:
                logger.info("✓ Claude AI service configured")
        else:
            warnings.append("ANTHROPIC_API_KEY not set - Claude service disabled")
```

### 4. Health Monitoring Integration

The health monitoring is automatically integrated through the registry. Your service's `get_health()` method will be called by:

```python
# Endpoint: GET /services/health
@app.get("/services/health")
async def services_health():
    """Check health status of all AI services"""
    health_results = await ai_service_registry.health_check_all()
    
    # Your Claude service health will be included here
    return {
        "overall_health": "healthy" if all(health_results.values()) else "degraded",
        "services": health_results
    }
```

### 5. Testing Implementation

Create comprehensive tests for your new service:

#### File: `tests/test_claude_service.py`

```python
"""
Test suite for Claude AI service integration
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.claude_service import ClaudeService
from app.core.exceptions import ServiceUnavailableError, RateLimitError

class TestClaudeService:
    """Test Claude AI service implementation"""
    
    @pytest.fixture
    def claude_service(self, monkeypatch):
        """Create Claude service with test configuration"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("CLAUDE_MODEL", "claude-3-opus-20240229")
        return ClaudeService()
    
    @pytest.mark.asyncio
    async def test_analyze_success(self, claude_service):
        """Test successful analysis call"""
        # Mock the HTTP client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "Analysis result"}],
            "model": "claude-3-opus-20240229",
            "usage": {"input_tokens": 10, "output_tokens": 20}
        }
        
        with patch.object(claude_service.client, 'post', 
                         return_value=mock_response) as mock_post:
            result = await claude_service.analyze("Test prompt")
            
            assert result["content"] == "Analysis result"
            assert result["service"] == "claude"
            assert "usage" in result
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_rate_limit(self, claude_service):
        """Test rate limit handling"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"retry-after": "30"}
        
        with patch.object(claude_service.client, 'post',
                         return_value=mock_response):
            with pytest.raises(RateLimitError) as exc_info:
                await claude_service.analyze("Test prompt")
            
            assert exc_info.value.retry_after == 30
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, claude_service):
        """Test health check when service is healthy"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        with patch.object(claude_service.client, 'post',
                         return_value=mock_response):
            health = await claude_service.get_health()
            assert health is True
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, claude_service):
        """Test health check when service is down"""
        with patch.object(claude_service.client, 'post',
                         side_effect=Exception("Connection error")):
            health = await claude_service.get_health()
            assert health is False
    
    def test_capabilities(self, claude_service):
        """Test service capabilities"""
        capabilities = claude_service.get_capabilities()
        assert "document" in capabilities
        assert "chat" in capabilities
        assert "code" in capabilities
    
    def test_metadata(self, claude_service):
        """Test service metadata"""
        metadata = claude_service.get_metadata()
        assert metadata.service_id == "claude"
        assert metadata.provider == "Anthropic"
        assert metadata.is_available is True


class TestClaudeIntegration:
    """Integration tests with AI service registry"""
    
    @pytest.mark.asyncio
    async def test_claude_registration(self):
        """Test Claude service registration in registry"""
        from app.services.ai_service_interface import ai_service_registry
        from app.services.service_initialization import initialize_ai_services
        
        # Initialize services with Claude API key set
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            initialize_ai_services()
            
            # Check Claude services are registered
            services = ai_service_registry.list_services()
            assert "claude_document" in services
            assert "claude_chat" in services
            assert "claude_code" in services
```

---

## Practical Examples

### Example 1: Complete Anthropic Claude Integration

Here's the complete process for adding Claude to your PluginMind instance:

#### Step 1: Environment Configuration

Add to your `.env` file:

```bash
# Anthropic Claude Configuration
ANTHROPIC_API_KEY=sk-ant-api03-...
CLAUDE_MODEL=claude-3-opus-20240229  # or claude-3-sonnet-20240229 for faster/cheaper
CLAUDE_MAX_TOKENS=4096
CLAUDE_TEMPERATURE=0.7
CLAUDE_TIMEOUT_SECONDS=60
```

#### Step 2: Install Dependencies

```bash
# No additional dependencies needed - httpx is already included!
```

#### Step 3: Verify Integration

```python
# Quick test script
import asyncio
from app.services.claude_service import ClaudeService

async def test_claude():
    service = ClaudeService()
    
    # Test health
    is_healthy = await service.get_health()
    print(f"Claude health: {is_healthy}")
    
    # Test analysis
    if is_healthy:
        result = await service.analyze("What is the meaning of life?")
        print(f"Claude says: {result['content']}")

asyncio.run(test_claude())
```

### Example 2: Google Gemini Integration

Integration for Google's Gemini AI:

#### File: `app/services/gemini_service.py`

```python
"""
Google Gemini AI Service Implementation
Provides multimodal AI capabilities
"""

import os
import google.generativeai as genai
from typing import Dict, Any, List
from app.services.ai_service_interface import AIServiceInterface

class GeminiService(AIServiceInterface):
    """Google Gemini implementation"""
    
    def __init__(self):
        """Initialize Gemini with API key"""
        self.api_key = os.getenv("GOOGLE_AI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
    
    async def analyze(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Perform analysis using Gemini"""
        if not self.api_key:
            raise ServiceUnavailableError("Gemini not configured")
        
        # Gemini uses synchronous API, wrap in async
        import asyncio
        
        def _generate():
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get("temperature", 0.7),
                    max_output_tokens=kwargs.get("max_tokens", 2048),
                )
            )
            return response.text
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, _generate)
        
        return {
            "content": content,
            "service": "gemini",
            "model": "gemini-pro"
        }
    
    async def get_health(self) -> bool:
        """Check Gemini health"""
        if not self.api_key:
            return False
        
        try:
            # Quick generation to test connectivity
            self.model.generate_content("Hi", 
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1
                ))
            return True
        except:
            return False
    
    def get_capabilities(self) -> List[str]:
        """Gemini supports multimodal inputs"""
        return ["document", "chat", "image", "video", "audio"]
```

### Example 3: Hugging Face Integration

For open-source models via Hugging Face:

#### File: `app/services/huggingface_service.py`

```python
"""
Hugging Face AI Service Implementation
Provides access to open-source models
"""

import os
import httpx
from typing import Dict, Any, List
from app.services.ai_service_interface import AIServiceInterface

class HuggingFaceService(AIServiceInterface):
    """Hugging Face API implementation"""
    
    def __init__(self, model_id: str = "meta-llama/Llama-2-70b-chat-hf"):
        """Initialize with specific model"""
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.model_id = model_id
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def analyze(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Perform analysis using Hugging Face model"""
        if not self.api_key:
            raise ServiceUnavailableError("Hugging Face not configured")
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Different models have different input formats
        if "llama" in self.model_id.lower():
            # Llama format
            formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        else:
            formatted_prompt = prompt
        
        data = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": kwargs.get("max_tokens", 512),
                "temperature": kwargs.get("temperature", 0.7),
                "do_sample": True
            }
        }
        
        response = await self.client.post(
            self.api_url,
            headers=headers,
            json=data
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Handle different response formats
        if isinstance(result, list) and len(result) > 0:
            content = result[0].get("generated_text", "")
        else:
            content = result.get("generated_text", "")
        
        # Remove the prompt from response if included
        if content.startswith(formatted_prompt):
            content = content[len(formatted_prompt):].strip()
        
        return {
            "content": content,
            "service": "huggingface",
            "model": self.model_id
        }
```

---

## Advanced Configuration

### Service Capabilities and Routing

Define custom routing logic based on capabilities:

```python
# app/services/analysis_service.py

async def select_service_for_request(
    analysis_type: str,
    request_metadata: Dict[str, Any]
) -> AIServiceInterface:
    """
    Custom service selection logic
    
    Args:
        analysis_type: Type of analysis requested
        request_metadata: Additional context (user tier, priority, etc.)
    
    Returns:
        Selected AI service
    """
    # Premium users get Claude for code analysis
    if analysis_type == "code" and request_metadata.get("user_tier") == "premium":
        return ai_service_registry.get_service("claude_code")
    
    # Use Gemini for multimodal requests
    if request_metadata.get("has_images"):
        return ai_service_registry.get_service("gemini_multimodal")
    
    # Cost optimization: Use cheaper models for simple tasks
    if request_metadata.get("complexity") == "simple":
        return ai_service_registry.get_service("gpt35_turbo")
    
    # Default to standard service discovery
    return ai_service_registry.get_preferred_service(analysis_type)
```

### Custom Processing Types

Add new analysis types beyond the defaults:

```python
# app/models/schemas.py

class AnalysisType(str, Enum):
    """Extended analysis types"""
    DOCUMENT = "document"
    CHAT = "chat"
    SEO = "seo"
    CRYPTO = "crypto"
    CODE = "code"          # New: Code analysis
    LEGAL = "legal"        # New: Legal document review
    MEDICAL = "medical"    # New: Medical text analysis
    CREATIVE = "creative"  # New: Creative writing
    TRANSLATE = "translate" # New: Translation

# app/ash_prompt.py - Add prompt templates

PROMPT_TEMPLATES = {
    "code": {
        "system": "You are an expert code reviewer and developer assistant.",
        "template": "Analyze this code:\n\n{code}\n\nProvide: 1) Issues, 2) Improvements, 3) Security concerns"
    },
    "legal": {
        "system": "You are a legal document analyst. Provide analysis but not legal advice.",
        "template": "Review this legal text:\n\n{document}\n\nIdentify: key terms, obligations, risks"
    }
}
```

### Performance Optimization

Implement caching for expensive AI calls:

```python
# app/services/cache_layer.py

import hashlib
import json
from typing import Optional, Dict, Any
from redis import asyncio as aioredis

class AIResponseCache:
    """Cache layer for AI responses"""
    
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
        self.ttl = 3600  # 1 hour default TTL
    
    def _generate_cache_key(self, 
                           service_id: str, 
                           prompt: str, 
                           params: Dict) -> str:
        """Generate deterministic cache key"""
        cache_data = {
            "service": service_id,
            "prompt": prompt,
            "params": params
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return f"ai_cache:{hashlib.sha256(cache_str.encode()).hexdigest()}"
    
    async def get(self, service_id: str, prompt: str, params: Dict) -> Optional[Dict]:
        """Get cached response if available"""
        key = self._generate_cache_key(service_id, prompt, params)
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set(self, service_id: str, prompt: str, params: Dict, 
                  response: Dict, ttl: Optional[int] = None):
        """Cache the response"""
        key = self._generate_cache_key(service_id, prompt, params)
        await self.redis.setex(
            key, 
            ttl or self.ttl,
            json.dumps(response)
        )

# Integration in analysis service
cache = AIResponseCache(settings.redis_url)

async def analyze_with_cache(service_id: str, prompt: str, **kwargs):
    """Analyze with caching layer"""
    # Check cache first
    cached = await cache.get(service_id, prompt, kwargs)
    if cached:
        logger.info(f"Cache hit for {service_id}")
        return cached
    
    # Perform actual analysis
    service = ai_service_registry.get_service(service_id)
    result = await service.analyze(prompt, **kwargs)
    
    # Cache the result
    await cache.set(service_id, prompt, kwargs, result)
    
    return result
```

---

## Troubleshooting Guide

### Common Integration Issues

#### 1. Authentication Failures

**Problem:** API key not working
```
ServiceUnavailableError: Claude service not configured
```

**Solutions:**
- Verify API key is correct in `.env`
- Check API key has proper permissions
- Ensure billing is active on AI provider account
- Test with provider's official client first

#### 2. Rate Limiting

**Problem:** Getting rate limit errors
```
RateLimitError: API rate limit exceeded, retry after 60
```

**Solutions:**
```python
# Implement exponential backoff
import asyncio
from typing import TypeVar, Callable

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    base_delay: float = 1.0
) -> T:
    """Retry with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            
            delay = min(base_delay * (2 ** attempt), 60)
            if hasattr(e, 'retry_after'):
                delay = e.retry_after
            
            logger.info(f"Rate limited, retrying in {delay}s")
            await asyncio.sleep(delay)
```

#### 3. Service Unavailable

**Problem:** Service health checks failing

**Debugging steps:**
```python
# Debug script
import asyncio
from app.services.claude_service import ClaudeService

async def debug_service():
    service = ClaudeService()
    
    # Check configuration
    print(f"API Key present: {bool(service.api_key)}")
    print(f"API URL: {service.api_url}")
    print(f"Model: {service.model}")
    
    # Test raw HTTP call
    import httpx
    client = httpx.AsyncClient()
    try:
        response = await client.post(
            service.api_url,
            headers={"x-api-key": service.api_key},
            json={"test": "connection"},
            timeout=5.0
        )
        print(f"HTTP Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Connection error: {e}")

asyncio.run(debug_service())
```

#### 4. Configuration Validation Errors

**Problem:** Service not loading at startup

**Check configuration validation:**
```python
# app/core/config.py
def _validate_configuration(self):
    """Debug configuration issues"""
    
    # Add detailed logging
    if self.anthropic_api_key:
        # Test format
        if not self.anthropic_api_key.startswith("sk-ant-"):
            logger.warning("ANTHROPIC_API_KEY may have incorrect format")
        
        # Test length
        if len(self.anthropic_api_key) < 40:
            logger.warning("ANTHROPIC_API_KEY seems too short")
```

### Debugging Tools

#### 1. Enable Debug Logging

```python
# Set in .env
LOG_LEVEL=DEBUG

# Or programmatically
import logging
logging.getLogger("app.services.claude_service").setLevel(logging.DEBUG)
```

#### 2. Service Introspection Endpoint

Add a debug endpoint:

```python
@app.get("/services/debug/{service_id}")
async def debug_service(service_id: str):
    """Debug endpoint for service introspection"""
    service = ai_service_registry.get_service(service_id)
    if not service:
        raise HTTPException(404, f"Service {service_id} not found")
    
    return {
        "service_id": service_id,
        "metadata": service.get_metadata().dict(),
        "health": await service.get_health(),
        "capabilities": service.get_capabilities(),
        "configuration": {
            "has_api_key": bool(getattr(service, 'api_key', None)),
            "model": getattr(service, 'model', None),
            "timeout": getattr(service, 'timeout', None)
        }
    }
```

#### 3. Performance Monitoring

```python
# Add timing decorator
import time
from functools import wraps

def measure_performance(func):
    """Decorator to measure AI service performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"{func.__name__} took {duration:.2f}s")
            
            # Add to result metadata
            if isinstance(result, dict):
                result['performance_ms'] = int(duration * 1000)
            
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    
    return wrapper

# Apply to analyze method
@measure_performance
async def analyze(self, prompt: str, **kwargs) -> Dict[str, Any]:
    # ... existing implementation
```

---

## Best Practices

### Security Considerations

#### 1. API Key Management

**Never commit API keys!** Use environment variables:

```python
# ❌ BAD
api_key = "sk-ant-api03-abcd1234..."

# ✅ GOOD
api_key = os.getenv("ANTHROPIC_API_KEY")
```

**Implement key rotation:**

```python
class RotatingAPIKey:
    """Support for rotating API keys"""
    
    def __init__(self, primary_key: str, secondary_key: Optional[str] = None):
        self.primary = primary_key
        self.secondary = secondary_key
        self.use_primary = True
    
    def get_current(self) -> str:
        """Get current active key"""
        return self.primary if self.use_primary else self.secondary
    
    def rotate(self):
        """Switch to secondary key"""
        if self.secondary:
            self.use_primary = not self.use_primary
            logger.info(f"Rotated to {'primary' if self.use_primary else 'secondary'} key")
```

#### 2. Input Validation

Always validate and sanitize inputs:

```python
from pydantic import BaseModel, validator

class AIRequestValidator(BaseModel):
    """Validate AI service requests"""
    
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7
    
    @validator('prompt')
    def validate_prompt(cls, v):
        # Check length
        if len(v) > 10000:
            raise ValueError("Prompt too long (max 10000 chars)")
        
        # Check for injection attempts
        suspicious_patterns = ['<script', 'javascript:', 'onclick=']
        for pattern in suspicious_patterns:
            if pattern.lower() in v.lower():
                raise ValueError(f"Suspicious content detected: {pattern}")
        
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        return v
```

#### 3. Error Message Sanitization

Never expose internal details in errors:

```python
async def analyze_safe(self, prompt: str, **kwargs) -> Dict[str, Any]:
    """Analyze with sanitized error handling"""
    try:
        return await self.analyze(prompt, **kwargs)
    except Exception as e:
        # Log full error internally
        logger.error(f"AI service error: {str(e)}", exc_info=True)
        
        # Return sanitized error to user
        if isinstance(e, RateLimitError):
            raise HTTPException(429, "Service temporarily unavailable, please retry")
        elif isinstance(e, ServiceUnavailableError):
            raise HTTPException(503, "AI service currently unavailable")
        else:
            # Generic error for unexpected issues
            raise HTTPException(500, "An error occurred processing your request")
```

### Production Deployment

#### 1. Service Rollout Strategy

Implement gradual rollout:

```python
class ServiceRollout:
    """Gradual rollout for new AI services"""
    
    def __init__(self, service_id: str, rollout_percentage: int = 0):
        self.service_id = service_id
        self.rollout_percentage = rollout_percentage
    
    def should_use_new_service(self, user_id: str) -> bool:
        """Determine if user should get new service"""
        # Consistent hashing for stable assignment
        import hashlib
        
        hash_int = int(hashlib.md5(f"{user_id}:{self.service_id}".encode()).hexdigest(), 16)
        user_bucket = hash_int % 100
        
        return user_bucket < self.rollout_percentage
    
    def increase_rollout(self, increment: int = 10):
        """Gradually increase rollout"""
        self.rollout_percentage = min(100, self.rollout_percentage + increment)
        logger.info(f"Increased {self.service_id} rollout to {self.rollout_percentage}%")
```

#### 2. A/B Testing

Compare service performance:

```python
class ABTest:
    """A/B test different AI services"""
    
    def __init__(self, service_a: str, service_b: str):
        self.service_a = service_a
        self.service_b = service_b
        self.metrics = {"a": [], "b": []}
    
    async def run_test(self, prompt: str) -> Dict[str, Any]:
        """Run both services and compare"""
        import random
        
        # Random assignment
        use_a = random.random() < 0.5
        service_id = self.service_a if use_a else self.service_b
        
        # Get service and measure performance
        service = ai_service_registry.get_service(service_id)
        start = time.time()
        result = await service.analyze(prompt)
        duration = time.time() - start
        
        # Record metrics
        group = "a" if use_a else "b"
        self.metrics[group].append({
            "duration": duration,
            "tokens": result.get("usage", {}).get("total_tokens", 0)
        })
        
        # Add test metadata
        result["ab_test"] = {
            "group": group,
            "service": service_id,
            "duration_ms": int(duration * 1000)
        }
        
        return result
    
    def get_results(self) -> Dict:
        """Get A/B test results"""
        import statistics
        
        results = {}
        for group in ["a", "b"]:
            if self.metrics[group]:
                durations = [m["duration"] for m in self.metrics[group]]
                results[group] = {
                    "service": self.service_a if group == "a" else self.service_b,
                    "requests": len(self.metrics[group]),
                    "avg_duration": statistics.mean(durations),
                    "median_duration": statistics.median(durations)
                }
        
        return results
```

#### 3. Monitoring and Alerting

Set up comprehensive monitoring:

```python
# app/monitoring/ai_metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI service requests',
    ['service', 'status']
)

ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'AI service request duration',
    ['service']
)

ai_service_health = Gauge(
    'ai_service_health',
    'AI service health status',
    ['service']
)

# Decorator for automatic metrics
def track_ai_metrics(service_name: str):
    """Decorator to track AI service metrics"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                ai_requests_total.labels(service=service_name, status='success').inc()
                return result
            except Exception as e:
                ai_requests_total.labels(service=service_name, status='error').inc()
                raise
            finally:
                duration = time.time() - start
                ai_request_duration.labels(service=service_name).observe(duration)
        
        return wrapper
    return decorator

# Alert thresholds
ALERT_RULES = {
    "high_error_rate": {
        "condition": lambda metrics: metrics["error_rate"] > 0.05,
        "message": "AI service error rate above 5%"
    },
    "slow_response": {
        "condition": lambda metrics: metrics["p95_latency"] > 5.0,
        "message": "AI service P95 latency above 5 seconds"
    },
    "service_down": {
        "condition": lambda metrics: not metrics["is_healthy"],
        "message": "AI service health check failing"
    }
}
```

### Maintenance and Updates

#### 1. Service Version Management

Track AI model versions:

```python
class ServiceVersion:
    """Track AI service versions"""
    
    def __init__(self, service_id: str, version: str):
        self.service_id = service_id
        self.version = version
        self.deployed_at = datetime.utcnow()
        self.previous_version = None
    
    def update_version(self, new_version: str):
        """Update to new version"""
        self.previous_version = self.version
        self.version = new_version
        self.deployed_at = datetime.utcnow()
        
        logger.info(
            f"Updated {self.service_id} from {self.previous_version} to {new_version}"
        )
    
    def rollback(self):
        """Rollback to previous version"""
        if self.previous_version:
            current = self.version
            self.version = self.previous_version
            self.previous_version = current
            
            logger.info(f"Rolled back {self.service_id} to {self.version}")
```

#### 2. Backward Compatibility

Maintain compatibility during updates:

```python
class BackwardCompatibleService(AIServiceInterface):
    """Service with backward compatibility support"""
    
    def __init__(self, version: str = "v2"):
        self.version = version
        self.v1_client = LegacyAIClient()  # Old implementation
        self.v2_client = ModernAIClient()  # New implementation
    
    async def analyze(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Route to appropriate version"""
        # Check for version override
        requested_version = kwargs.pop("api_version", self.version)
        
        if requested_version == "v1":
            # Use legacy format
            result = await self.v1_client.process(prompt)
            # Convert to modern format
            return self._convert_v1_response(result)
        else:
            # Use modern implementation
            return await self.v2_client.analyze(prompt, **kwargs)
    
    def _convert_v1_response(self, v1_response: Dict) -> Dict:
        """Convert v1 response to v2 format"""
        return {
            "content": v1_response.get("text", ""),
            "service": "legacy",
            "metadata": v1_response.get("meta", {})
        }
```

#### 3. Update Procedures

Safe update process:

```bash
#!/bin/bash
# scripts/update_ai_service.sh

SERVICE_NAME=$1
NEW_VERSION=$2

echo "Updating $SERVICE_NAME to $NEW_VERSION"

# 1. Run health check
curl -f http://localhost:8000/services/health || exit 1

# 2. Create backup of current config
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 3. Update configuration
sed -i "s/${SERVICE_NAME}_VERSION=.*/${SERVICE_NAME}_VERSION=${NEW_VERSION}/" .env

# 4. Test new configuration
TESTING=1 python -m pytest tests/test_${SERVICE_NAME}_service.py || {
    echo "Tests failed, rolling back"
    cp .env.backup.* .env
    exit 1
}

# 5. Reload service
curl -X POST http://localhost:8000/services/reload

# 6. Verify health
sleep 5
curl -f http://localhost:8000/services/health || {
    echo "Health check failed, rolling back"
    cp .env.backup.* .env
    curl -X POST http://localhost:8000/services/reload
    exit 1
}

echo "Update successful!"
```

---

## Quick Reference

### Checklist for Adding New AI Service

- [ ] Create service class implementing `AIServiceInterface`
- [ ] Add configuration variables to `.env` and `config.py`
- [ ] Register service in `service_initialization.py`
- [ ] Create unit tests in `tests/test_<service>_service.py`
- [ ] Add integration tests with registry
- [ ] Update documentation with new service
- [ ] Test health monitoring endpoint
- [ ] Verify fallback behavior
- [ ] Add performance metrics
- [ ] Create rollout plan

### Common Commands

```bash
# Test new service
TESTING=1 python -m pytest tests/test_claude_service.py -v

# Check service health
curl http://localhost:8000/services/health | jq

# List registered services
curl http://localhost:8000/services | jq

# Test specific service
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"user_input": "Test", "analysis_type": "document", "service": "claude"}'

# Monitor service metrics
curl http://localhost:8000/metrics | grep ai_
```

### Environment Variables Reference

```bash
# Claude
ANTHROPIC_API_KEY=sk-ant-api03-...
CLAUDE_MODEL=claude-3-opus-20240229
CLAUDE_MAX_TOKENS=4096
CLAUDE_TEMPERATURE=0.7

# Gemini
GOOGLE_AI_API_KEY=AIza...
GEMINI_MODEL=gemini-pro

# Hugging Face
HUGGINGFACE_API_KEY=hf_...
HUGGINGFACE_MODEL=meta-llama/Llama-2-70b-chat-hf

# Service configuration
AI_SERVICE_TIMEOUT=60
AI_SERVICE_CACHE_TTL=3600
AI_SERVICE_MAX_RETRIES=3
```

---

## Conclusion

You now have everything needed to extend PluginMind with any AI service! The plugin architecture makes it simple to:

1. Add new AI providers without changing core code
2. Implement custom routing and selection logic
3. Monitor and optimize service performance
4. Maintain backward compatibility
5. Scale your AI capabilities as needed

Remember: The AI service registry is designed to grow with your needs. Start simple, add complexity as required, and always maintain good testing practices.

**Happy coding!** 🚀

---

*For more help, check the [PluginMind documentation](https://github.com/YourOrg/PluginMind) or open an issue.*