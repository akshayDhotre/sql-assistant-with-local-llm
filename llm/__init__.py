"""
LLM module for SQL Assistant

This module handles loading and inference with local LLM models.
"""

from .loader import get_llm_model
from .inference import get_response_from_llm_model

__all__ = ["get_llm_model", "get_response_from_llm_model"]
