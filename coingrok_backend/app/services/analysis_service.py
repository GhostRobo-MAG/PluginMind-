"""
Analysis service orchestration.

Coordinates the complete 4-D Prompt Engine workflow by orchestrating
OpenAI and Grok services to deliver comprehensive crypto analysis.
"""

import time
from typing import Tuple
from sqlmodel import Session
from app.core.logging import get_logger
from app.models.database import QueryLog
from app.services.openai_service import openai_service
from app.services.grok_service import grok_service
from app.core.exceptions import AIServiceError

logger = get_logger(__name__)


class AnalysisService:
    """
    Main analysis orchestration service.
    
    Coordinates the complete analysis workflow:
    1. Prompt optimization via OpenAI
    2. Crypto analysis via Grok  
    3. Result aggregation and logging
    """
    
    async def perform_analysis(
        self, 
        user_input: str, 
        user_id: str = "test_user"
    ) -> Tuple[str, str]:
        """
        Perform complete crypto analysis workflow.
        
        Orchestrates the 4-D Prompt Engine to transform user input
        into comprehensive crypto analysis.
        
        Args:
            user_input: Raw user query
            user_id: User identifier for tracking
            
        Returns:
            Tuple of (optimized_prompt, analysis_result)
            
        Raises:
            AIServiceError: If any step in the analysis fails
        """
        try:
            logger.info(f"Starting analysis workflow for user: {user_id}")
            
            # Step 1: Optimize prompt using OpenAI (4-D Engine)
            optimized_prompt = await openai_service.optimize_prompt(user_input)
            
            # Step 2: Get analysis from Grok
            analysis_result = await grok_service.analyze(optimized_prompt)
            
            logger.info("Analysis workflow completed successfully")
            return optimized_prompt, analysis_result
            
        except Exception as e:
            logger.error(f"Analysis workflow failed: {str(e)}")
            raise
    
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
            # Perform analysis
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


# Global service instance
analysis_service = AnalysisService()