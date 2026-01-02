"""
Module for connecting to Ollama LLM service

Author: Akshay Dhotre
"""

import requests
from typing import Dict, Any


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "phi"):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Base URL of Ollama service (default: http://localhost:11434)
            model: Model name to use (default: phi)
        """
        self.base_url = base_url
        self.model = model
        self.api_endpoint = f"{base_url}/api/generate"
    
    def is_available(self) -> bool:
        """
        Check if Ollama service is available.
        
        Returns:
            True if Ollama is running and accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False
    
    def __call__(self, prompt: str, temperature: float = 0.1, **kwargs) -> str:
        """
        Generate response from Ollama model.
        
        Args:
            prompt: Input prompt for the model
            temperature: Temperature for generation (default: 0.1)
            **kwargs: Additional parameters for the API
            
        Returns:
            Generated text response
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False,
                **kwargs
            }
            
            response = requests.post(self.api_endpoint, json=payload, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")


def get_llm_model(ollama_base_url: str = "http://localhost:11434", model_name: str = "phi") -> OllamaClient:
    """
    Initialize and return an Ollama client.
    
    Args:
        ollama_base_url: Base URL of the Ollama service
        model_name: Name of the model to use (must be pulled in Ollama)
        
    Returns:
        Initialized OllamaClient instance
    """
    client = OllamaClient(base_url=ollama_base_url, model=model_name)
    
    # Check if Ollama is available
    if not client.is_available():
        raise ConnectionError(
            f"Ollama service is not available at {ollama_base_url}. "
            "Please ensure Ollama is running: https://ollama.ai"
        )
    
    return client
