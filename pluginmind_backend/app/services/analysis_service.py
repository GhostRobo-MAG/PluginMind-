"""
Analysis service orchestration with plugin-style AI service registry.

Coordinates generic AI processing workflows by orchestrating AI services 
through the registry system to deliver comprehensive analysis for multiple use cases.
"""

import time
from typing import Tuple, Optional, Dict, Any
from sqlmodel import Session
from app.core.logging import get_logger
from app.models.database import QueryLog, AnalysisResult, AnalysisResultStatus
from app.core.exceptions import AIServiceError, ServiceUnavailableError
from app.services.ai_service_interface import (
    AIServiceType,
    AIServiceCapability,
    ai_service_registry
)
from app.ash_prompt import AnalysisType, prompt_engine

logger = get_logger(__name__)


class AnalysisService:
    """
    Main analysis orchestration service using plugin registry.
    
    Coordinates generic AI processing workflows:
    1. Prompt optimization for specific analysis types
    2. AI processing via registered analyzers (document, chat, SEO, crypto)
    3. Result aggregation and structured storage
    4. Support for multiple analysis types and use cases
    """
    
    def __init__(self):
        """Initialize the analysis service."""
        self.registry = ai_service_registry
        self.prompt_engine = prompt_engine
        logger.info("Analysis service initialized with AI service registry and prompt engine")
    
    def _get_prompt_optimizer(self):
        """
        Get the prompt optimization service from registry.
        
        Returns:
            AIService instance for prompt optimization
            
        Raises:
            ServiceUnavailableError: If no optimizer is available
        """
        # Try to get by specific service type
        optimizer = self.registry.get_preferred_service(AIServiceType.PROMPT_OPTIMIZER)
        
        if not optimizer:
            # Fallback to capability-based lookup
            services = self.registry.get_services_by_capability(
                AIServiceCapability.PROMPT_OPTIMIZATION
            )
            if services:
                optimizer = services[0]
        
        if not optimizer:
            logger.error("No prompt optimization service available in registry")
            raise ServiceUnavailableError("Prompt optimization service unavailable")
        
        return optimizer
    
    def _get_analyzer_for_type(self, analysis_type: AnalysisType):
        """
        Get the appropriate analyzer service for the analysis type.
        
        Args:
            analysis_type: Type of analysis to perform
            
        Returns:
            AIService instance for the requested analysis type
            
        Raises:
            ServiceUnavailableError: If no suitable analyzer is available
        """
        # Map analysis types to service types
        service_mapping = {
            AnalysisType.DOCUMENT: AIServiceType.DOCUMENT_PROCESSOR,
            AnalysisType.CHAT: AIServiceType.CHAT_PROCESSOR,
            AnalysisType.SEO: AIServiceType.SEO_GENERATOR,
            AnalysisType.CRYPTO: AIServiceType.CRYPTO_ANALYZER,
            AnalysisType.CUSTOM: AIServiceType.GENERIC_ANALYZER
        }
        
        service_type = service_mapping.get(analysis_type, AIServiceType.GENERIC_ANALYZER)
        analyzer = self.registry.get_preferred_service(service_type)
        
        if not analyzer:
            # Fallback to generic analyzer for any type
            analyzer = self.registry.get_preferred_service(AIServiceType.GENERIC_ANALYZER)
            
        if not analyzer:
            # Last resort: try crypto analyzer (for backward compatibility)
            analyzer = self.registry.get_preferred_service(AIServiceType.CRYPTO_ANALYZER)
        
        if not analyzer:
            logger.error(f"No suitable analyzer found for {analysis_type}")
            raise ServiceUnavailableError(f"Analysis service for {analysis_type} unavailable")
        
        return analyzer
    
    async def analyze_generic(
        self,
        user_input: str,
        analysis_type: AnalysisType = AnalysisType.CUSTOM,
        user_id: Optional[str] = None,
        analysis_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_fallback: bool = True,
        session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Perform generic AI analysis workflow using the enhanced registry system.
        
        Coordinates the complete workflow:
        1. Generate optimized prompt for the analysis type
        2. Process content using appropriate AI service
        3. Store results in AnalysisResult model
        
        Args:
            user_input: Raw user query or content
            analysis_type: Type of analysis to perform
            user_id: User identifier for tracking
            analysis_id: Unique identifier for this analysis
            metadata: Additional metadata for the analysis
            use_fallback: Whether to try fallback services on failure
            
        Returns:
            Dictionary containing analysis results and metadata
            
        Raises:
            AIServiceError: If any step in the analysis fails
            ServiceUnavailableError: If required services are unavailable
        """
        try:
            logger.info(f"Starting {analysis_type} analysis workflow for user: {user_id}")
            
            # Step 1: Generate optimized prompt for the analysis type
            system_prompt = self.prompt_engine.get_system_prompt(analysis_type)
            
            # Step 2: Get prompt optimizer from registry
            prompt_optimizer = self._get_prompt_optimizer()
            optimizer_metadata = prompt_optimizer.get_metadata()
            logger.info(
                f"Using prompt optimizer: {optimizer_metadata.name} "
                f"(provider: {optimizer_metadata.provider})"
            )
            
            # Step 3: Optimize prompt using selected service
            optimized_prompt = await prompt_optimizer.process(user_input)
            
            # Step 4: Get appropriate analyzer for the analysis type
            analyzer = self._get_analyzer_for_type(analysis_type)
            analyzer_metadata = analyzer.get_metadata()
            logger.info(
                f"Using analyzer: {analyzer_metadata.name} "
                f"(provider: {analyzer_metadata.provider}, type: {analysis_type})"
            )
            
            # Step 5: Process with the analyzer
            analysis_result = await analyzer.process(optimized_prompt)
            
            # Step 6: Store result using AnalysisResult model if session provided
            result_data = {
                "analysis_type": analysis_type,
                "optimized_prompt": optimized_prompt,
                "analysis_result": analysis_result,
                "system_prompt": system_prompt,
                "services_used": {
                    "prompt_optimizer": {
                        "name": optimizer_metadata.name,
                        "provider": optimizer_metadata.provider,
                        "model": optimizer_metadata.model
                    },
                    "analyzer": {
                        "name": analyzer_metadata.name,
                        "provider": analyzer_metadata.provider,
                        "model": analyzer_metadata.model
                    }
                },
                "metadata": metadata or {}
            }
            
            # Store in database if session provided
            if session and analysis_id:
                try:
                    analysis_record = AnalysisResult(
                        analysis_id=analysis_id,
                        user_id=user_id,
                        analysis_type=analysis_type,
                        user_input=user_input,
                        result_data=result_data,
                        status=AnalysisResultStatus.COMPLETED
                    )
                    session.add(analysis_record)
                    session.commit()
                    logger.info(f"Stored analysis result in database (id: {analysis_id})")
                except Exception as db_error:
                    logger.warning(f"Failed to store analysis result: {str(db_error)}")
                    # Don't fail the analysis if database storage fails
            
            logger.info(
                f"Generic analysis workflow completed successfully "
                f"(type: {analysis_type}, optimizer: {optimizer_metadata.provider}, "
                f"analyzer: {analyzer_metadata.provider})"
            )
            
            return result_data
            
        except Exception as e:
            logger.error(f"Generic analysis workflow failed: {str(e)}")
            if use_fallback and analysis_type != AnalysisType.CUSTOM:
                logger.info("Attempting fallback to custom analysis")
                return await self.analyze_generic(
                    user_input, AnalysisType.CUSTOM, user_id, analysis_id, metadata, False
                )
            raise AIServiceError(f"Analysis failed: {str(e)}")
    
    def _get_crypto_analyzer(self):
        """
        Get the crypto analysis service from registry.
        
        Returns:
            AIService instance for crypto analysis
            
        Raises:
            ServiceUnavailableError: If no analyzer is available
        """
        # Try to get by specific service type
        analyzer = self.registry.get_preferred_service(AIServiceType.CRYPTO_ANALYZER)
        
        if not analyzer:
            # Fallback to capability-based lookup
            services = self.registry.get_services_by_capability(
                AIServiceCapability.CRYPTO_ANALYSIS
            )
            if services:
                analyzer = services[0]
        
        if not analyzer:
            logger.error("No crypto analysis service available in registry")
            raise ServiceUnavailableError("Crypto analysis service unavailable")
        
        return analyzer
    
    async def perform_analysis(
        self, 
        user_input: str, 
        user_id: str = "test_user",
        use_fallback: bool = True
    ) -> Tuple[str, str]:
        """
        Perform complete crypto analysis workflow using registered services.
        
        Orchestrates the 4-D Prompt Engine to transform user input
        into comprehensive crypto analysis.
        
        Args:
            user_input: Raw user query
            user_id: User identifier for tracking
            use_fallback: Whether to try fallback services on failure
            
        Returns:
            Tuple of (optimized_prompt, analysis_result)
            
        Raises:
            AIServiceError: If any step in the analysis fails
            ServiceUnavailableError: If required services are unavailable
        """
        try:
            logger.info(f"Starting analysis workflow for user: {user_id}")
            
            # Step 1: Get prompt optimizer from registry
            prompt_optimizer = self._get_prompt_optimizer()
            optimizer_metadata = prompt_optimizer.get_metadata()
            logger.info(
                f"Using prompt optimizer: {optimizer_metadata.name} "
                f"(provider: {optimizer_metadata.provider})"
            )
            
            # Step 2: Optimize prompt using selected service
            optimized_prompt = await prompt_optimizer.process(user_input)
            
            # Step 3: Get crypto analyzer from registry
            crypto_analyzer = self._get_crypto_analyzer()
            analyzer_metadata = crypto_analyzer.get_metadata()
            logger.info(
                f"Using crypto analyzer: {analyzer_metadata.name} "
                f"(provider: {analyzer_metadata.provider})"
            )
            
            # Step 4: Get analysis from selected service
            analysis_result = await crypto_analyzer.process(optimized_prompt)
            
            logger.info(
                f"Analysis workflow completed successfully "
                f"(optimizer: {optimizer_metadata.provider}, "
                f"analyzer: {analyzer_metadata.provider})"
            )
            
            return optimized_prompt, analysis_result
            
        except ServiceUnavailableError as e:
            # Service not available, try fallback if enabled
            if use_fallback:
                logger.warning(f"Primary service failed, attempting fallback: {str(e)}")
                return await self._perform_fallback_analysis(user_input, user_id)
            raise
            
        except Exception as e:
            logger.error(f"Analysis workflow failed: {str(e)}")
            raise
    
    async def _perform_fallback_analysis(
        self, 
        user_input: str, 
        user_id: str
    ) -> Tuple[str, str]:
        """
        Perform analysis using fallback services.
        
        This method can be extended to use alternative services
        or simplified analysis when primary services fail.
        
        Args:
            user_input: Raw user query
            user_id: User identifier
            
        Returns:
            Tuple of (optimized_prompt, analysis_result)
            
        Raises:
            ServiceUnavailableError: If fallback also fails
        """
        logger.info("Attempting fallback analysis workflow")
        
        # Try to use any available services with required capabilities
        prompt_services = self.registry.get_services_by_capability(
            AIServiceCapability.PROMPT_OPTIMIZATION
        )
        analysis_services = self.registry.get_services_by_capability(
            AIServiceCapability.CRYPTO_ANALYSIS
        )
        
        if not prompt_services or not analysis_services:
            raise ServiceUnavailableError(
                "No fallback services available for analysis"
            )
        
        # Use the first available service of each type
        # In production, this could be more sophisticated
        # (e.g., round-robin, least-recently-used, etc.)
        try:
            optimized_prompt = await prompt_services[0].process(user_input)
            analysis_result = await analysis_services[0].process(optimized_prompt)
            
            logger.info("Fallback analysis completed successfully")
            return optimized_prompt, analysis_result
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {str(e)}")
            raise ServiceUnavailableError("All analysis services unavailable")
    
    async def perform_analysis_with_logging(
        self,
        user_input: str,
        session: Session,
        user_id: str = "test_user"
    ) -> Tuple[str, str]:
        """
        Perform analysis with complete query logging.
        
        Executes the full analysis workflow while logging all details
        to the database for usage tracking and performance monitoring.
        
        Args:
            user_input: Raw user query
            session: Database session for logging
            user_id: User identifier for tracking
            
        Returns:
            Tuple of (optimized_prompt, analysis_result)
            
        Raises:
            AIServiceError: If analysis fails
        """
        start_time = time.time()
        
        # Initialize query log
        query_log = QueryLog(
            user_id=user_id,
            user_input=user_input
        )
        
        try:
            # Perform analysis using registry-based services
            optimized_prompt, analysis_result = await self.perform_analysis(
                user_input, user_id
            )
            
            # Calculate response time and log success
            response_time_ms = int((time.time() - start_time) * 1000)
            query_log.optimized_prompt = optimized_prompt
            query_log.ai_result = analysis_result
            query_log.response_time_ms = response_time_ms
            query_log.success = True
            
            # Save successful query log
            session.add(query_log)
            session.commit()
            
            logger.info(f"Analysis completed in {response_time_ms}ms")
            return optimized_prompt, analysis_result
            
        except Exception as e:
            # Log failed query
            response_time_ms = int((time.time() - start_time) * 1000)
            query_log.response_time_ms = response_time_ms
            query_log.success = False
            query_log.error_message = str(e)
            
            # Save failed query log
            session.add(query_log)
            session.commit()
            
            logger.error(f"Analysis failed after {response_time_ms}ms: {str(e)}")
            raise
    
    async def health_check(self) -> dict:
        """
        Perform health checks on all registered AI services.
        
        Returns:
            Dictionary with health status of all services
        """
        logger.info("Performing health check on all AI services")
        
        health_status = {
            "services_available": len(self.registry.list_services()),
            "service_health": await self.registry.health_check_all(),
            "prompt_optimizer_available": False,
            "crypto_analyzer_available": False
        }
        
        # Check for required service types
        try:
            self._get_prompt_optimizer()
            health_status["prompt_optimizer_available"] = True
        except ServiceUnavailableError:
            pass
        
        try:
            self._get_crypto_analyzer()
            health_status["crypto_analyzer_available"] = True
        except ServiceUnavailableError:
            pass
        
        # Overall health
        health_status["healthy"] = (
            health_status["prompt_optimizer_available"] and 
            health_status["crypto_analyzer_available"]
        )
        
        return health_status
    
    def get_service_info(self) -> dict:
        """
        Get information about registered AI services.
        
        Returns:
            Dictionary with service metadata
        """
        services_info = {}
        
        for service_id, metadata in self.registry.list_services().items():
            services_info[service_id] = metadata.to_dict()
        
        return {
            "registered_services": services_info,
            "total_services": len(services_info)
        }


# Global service instance
analysis_service = AnalysisService()