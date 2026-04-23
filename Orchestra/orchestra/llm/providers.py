import asyncio
import json
import time
from typing import Any, Dict, List, Optional
from .base import BaseLLMProvider, LLMConfig, LLMResponse, LLMProvider
import urllib.request
import urllib.error


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_base = config.api_base or "https://api.openai.com/v1"
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return await self.generate_chat(messages, **kwargs)
    
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        start_time = time.time()
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
        }
        
        if self.config.stop_sequences:
            payload["stop"] = self.config.stop_sequences
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        try:
            response_data = await self._make_request(
                f"{self.api_base}/chat/completions",
                payload,
                headers
            )
            
            latency = time.time() - start_time
            
            choice = response_data["choices"][0]
            usage = response_data.get("usage", {})
            
            return LLMResponse(
                content=choice["message"]["content"],
                provider="openai",
                model=self.config.model,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                latency=latency,
                finish_reason=choice.get("finish_reason"),
                raw_response=response_data
            )
        
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    async def _make_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_request,
            url,
            payload,
            headers
        )
    
    def _sync_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"HTTP {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"URL Error: {str(e)}")


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_base = config.api_base or "https://api.anthropic.com/v1"
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return await self.generate_chat(messages, system_prompt=system_prompt, **kwargs)
    
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        start_time = time.time()
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens or 4096),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if self.config.stop_sequences:
            payload["stop_sequences"] = self.config.stop_sequences
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        try:
            response_data = await self._make_request(
                f"{self.api_base}/messages",
                payload,
                headers
            )
            
            latency = time.time() - start_time
            
            content = response_data["content"][0]["text"]
            usage = response_data.get("usage", {})
            
            return LLMResponse(
                content=content,
                provider="anthropic",
                model=self.config.model,
                prompt_tokens=usage.get("input_tokens", 0),
                completion_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                latency=latency,
                finish_reason=response_data.get("stop_reason"),
                raw_response=response_data
            )
        
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    async def _make_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_request,
            url,
            payload,
            headers
        )
    
    def _sync_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"HTTP {e.code}: {error_body}")


class OllamaProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_base = config.api_base or "http://localhost:11434"
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        start_time = time.time()
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.config.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
            }
        }
        
        if self.config.stop_sequences:
            payload["options"]["stop"] = self.config.stop_sequences
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response_data = await self._make_request(
                f"{self.api_base}/api/generate",
                payload,
                headers
            )
            
            latency = time.time() - start_time
            
            return LLMResponse(
                content=response_data.get("response", ""),
                provider="ollama",
                model=self.config.model,
                prompt_tokens=response_data.get("prompt_eval_count", 0),
                completion_tokens=response_data.get("eval_count", 0),
                total_tokens=response_data.get("prompt_eval_count", 0) + response_data.get("eval_count", 0),
                latency=latency,
                finish_reason="stop",
                raw_response=response_data
            )
        
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        start_time = time.time()
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response_data = await self._make_request(
                f"{self.api_base}/api/chat",
                payload,
                headers
            )
            
            latency = time.time() - start_time
            
            return LLMResponse(
                content=response_data["message"]["content"],
                provider="ollama",
                model=self.config.model,
                prompt_tokens=response_data.get("prompt_eval_count", 0),
                completion_tokens=response_data.get("eval_count", 0),
                total_tokens=response_data.get("prompt_eval_count", 0) + response_data.get("eval_count", 0),
                latency=latency,
                finish_reason="stop",
                raw_response=response_data
            )
        
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    async def _make_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_request,
            url,
            payload,
            headers
        )
    
    def _sync_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"HTTP {e.code}: {error_body}")


class HuggingFaceProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_base = config.api_base or "https://api-inference.huggingface.co/models"
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        start_time = time.time()
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_new_tokens": kwargs.get("max_tokens", self.config.max_tokens or 512),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "return_full_text": False
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        try:
            response_data = await self._make_request(
                f"{self.api_base}/{self.config.model}",
                payload,
                headers
            )
            
            latency = time.time() - start_time
            
            if isinstance(response_data, list) and len(response_data) > 0:
                content = response_data[0].get("generated_text", "")
            else:
                content = response_data.get("generated_text", "")
            
            return LLMResponse(
                content=content,
                provider="huggingface",
                model=self.config.model,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency=latency,
                finish_reason="stop",
                raw_response=response_data
            )
        
        except Exception as e:
            raise RuntimeError(f"HuggingFace API error: {str(e)}")
    
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        return await self.generate(prompt, **kwargs)
    
    async def _make_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_request,
            url,
            payload,
            headers
        )
    
    def _sync_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"HTTP {e.code}: {error_body}")
