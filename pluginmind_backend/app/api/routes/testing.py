"""
Testing endpoints for error handling and validation testing.

These endpoints are only enabled in testing mode and bypass authentication
to allow proper testing of validation error handling.
"""

from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.core.logging import get_logger
from app.models.schemas import AnalysisRequest

logger = get_logger(__name__)
router = APIRouter()


if settings.testing:
    @router.post("/test-validation-error")
    async def test_validation_error(req: AnalysisRequest):
        """
        Test endpoint for validation error testing (testing mode only).
        
        This endpoint accepts AnalysisRequest but bypasses authentication
        to allow testing of validation error handling.
        """
        # If we get here, validation passed
        return {"message": "Validation successful", "user_input": req.user_input}

    @router.get("/test-generic-exception")
    async def test_generic_exception():
        """
        Test endpoint that triggers a generic exception (testing mode only).
        """
        raise Exception("This is a test generic exception")

    @router.post("/test-malformed-json")
    async def test_malformed_json(req: dict):
        """
        Test endpoint for malformed JSON testing (testing mode only).
        
        Accepts generic dict to trigger JSON validation errors.
        """
        return {"message": "JSON parsing successful", "data": req}