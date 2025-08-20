"""
Enumeration definitions for PluginMind Backend.

Contains all enum classes used throughout the application
for type safety and consistency.
"""

from enum import Enum


class JobStatus(str, Enum):
    """
    Enumeration of possible analysis job states.
    
    Used to track async job progress through the AI pipeline.
    """
    QUEUED = "queued"                    # Job created, waiting to start
    PROCESSING_OPENAI = "processing_openai"  # Getting optimized prompt
    PROCESSING_GROK = "processing_grok"      # Getting final analysis
    COMPLETED = "completed"              # Successfully finished
    FAILED = "failed"                    # Error occurred