"""
Unified LLM Interface - Model-agnostic interface for GPT, Claude, Gemini, etc.
Supports multiple LLM providers with a consistent API
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CUSTOM = "custom"


class LLMInterface:
    """
    Unified interface for multiple LLM providers.
    Abstracts away provider-specific details.
    """
    
    def __init__(self, provider: LLMProvider, api_key: str, model: str = None):
        self.provider = provider
        self.api_key = api_key
        
        # Default models for each provider
        if model is None:
            model = self._get_default_model()
        self.model = model
        
    def _get_default_model(self) -> str:
        """Get default model for provider"""
        defaults = {
            LLMProvider.OPENAI: "gpt-4o-mini",
            LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
            LLMProvider.GOOGLE: "gemini-pro"
        }
        return defaults.get(self.provider, "gpt-4o-mini")
    
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7, 
                 max_tokens: int = 1000) -> str:
        """
        Generate text using the configured LLM provider.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        if self.provider == LLMProvider.OPENAI:
            return self._call_openai(messages, temperature, max_tokens)
        elif self.provider == LLMProvider.ANTHROPIC:
            return self._call_anthropic(messages, temperature, max_tokens)
        elif self.provider == LLMProvider.GOOGLE:
            return self._call_google(messages, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _call_openai(self, messages: List[Dict[str, str]], temperature: float, 
                     max_tokens: int) -> str:
        """Call OpenAI API"""
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content'].strip()
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return f"OpenAI API Error: {e.code} - {error_body}"
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"
    
    def _call_anthropic(self, messages: List[Dict[str, str]], temperature: float,
                       max_tokens: int) -> str:
        """Call Anthropic Claude API"""
        url = "https://api.anthropic.com/v1/messages"
        
        # Convert messages format (Claude uses different format)
        system_msg = None
        claude_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_msg = msg['content']
            else:
                claude_messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "messages": claude_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if system_msg:
            data["system"] = system_msg
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['content'][0]['text'].strip()
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return f"Anthropic API Error: {e.code} - {error_body}"
        except Exception as e:
            return f"Error calling Anthropic: {str(e)}"
    
    def _call_google(self, messages: List[Dict[str, str]], temperature: float,
                    max_tokens: int) -> str:
        """Call Google Gemini API"""
        url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={self.api_key}"
        
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg['role'] in ['user', 'system'] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg['content']}]
            })
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['candidates'][0]['content']['parts'][0]['text'].strip()
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return f"Google API Error: {e.code} - {error_body}"
        except Exception as e:
            return f"Error calling Google: {str(e)}"
    
    def generate_json(self, messages: List[Dict[str, str]], temperature: float = 0.7,
                     max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate JSON response from LLM.
        Attempts to parse response as JSON, returns dict or error.
        """
        response = self.generate(messages, temperature, max_tokens)
        
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, return structured error
            return {
                "error": "Failed to parse JSON",
                "raw_response": response
            }


def create_llm(provider_name: str, api_key: str, model: str = None) -> LLMInterface:
    """
    Factory function to create LLM interface.
    
    Args:
        provider_name: "openai", "anthropic", "google", or "custom"
        api_key: API key for the provider
        model: Optional model name (uses default if not specified)
        
    Returns:
        LLMInterface instance
    """
    provider_map = {
        "openai": LLMProvider.OPENAI,
        "anthropic": LLMProvider.ANTHROPIC,
        "claude": LLMProvider.ANTHROPIC,
        "google": LLMProvider.GOOGLE,
        "gemini": LLMProvider.GOOGLE,
        "custom": LLMProvider.CUSTOM
    }
    
    provider = provider_map.get(provider_name.lower())
    if provider is None:
        raise ValueError(f"Unknown provider: {provider_name}. Supported: {list(provider_map.keys())}")
    
    return LLMInterface(provider, api_key, model)
