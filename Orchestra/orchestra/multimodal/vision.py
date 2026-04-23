import asyncio
import base64
import json
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import urllib.request
import urllib.error


@dataclass
class ImageInput:
    source: Union[str, bytes]
    source_type: str
    detail: str = "auto"
    
    @classmethod
    def from_url(cls, url: str, detail: str = "auto") -> 'ImageInput':
        return cls(source=url, source_type="url", detail=detail)
    
    @classmethod
    def from_path(cls, path: str, detail: str = "auto") -> 'ImageInput':
        with open(path, 'rb') as f:
            image_bytes = f.read()
        return cls(source=image_bytes, source_type="base64", detail=detail)
    
    @classmethod
    def from_bytes(cls, image_bytes: bytes, detail: str = "auto") -> 'ImageInput':
        return cls(source=image_bytes, source_type="base64", detail=detail)
    
    def to_base64(self) -> str:
        if self.source_type == "base64" and isinstance(self.source, bytes):
            return base64.b64encode(self.source).decode('utf-8')
        return ""


@dataclass
class VisionResponse:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency: float = 0.0
    images_processed: int = 0
    raw_response: Optional[Dict[str, Any]] = None


class VisionProvider:
    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        api_base: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    async def analyze_image(
        self,
        prompt: str,
        images: List[ImageInput],
        **kwargs
    ) -> VisionResponse:
        if self.provider == "openai":
            return await self._openai_vision(prompt, images, **kwargs)
        elif self.provider == "anthropic":
            return await self._anthropic_vision(prompt, images, **kwargs)
        else:
            raise ValueError(f"Unsupported vision provider: {self.provider}")
    
    async def _openai_vision(
        self,
        prompt: str,
        images: List[ImageInput],
        **kwargs
    ) -> VisionResponse:
        start_time = time.time()
        
        api_base = self.api_base or "https://api.openai.com/v1"
        
        content = [{"type": "text", "text": prompt}]
        
        for image in images:
            if image.source_type == "url":
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image.source,
                        "detail": image.detail
                    }
                })
            elif image.source_type == "base64":
                base64_image = image.to_base64()
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": image.detail
                    }
                })
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature)
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response_data = await self._make_request(
                f"{api_base}/chat/completions",
                payload,
                headers
            )
            
            latency = time.time() - start_time
            
            choice = response_data["choices"][0]
            usage = response_data.get("usage", {})
            
            return VisionResponse(
                content=choice["message"]["content"],
                model=self.model,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                latency=latency,
                images_processed=len(images),
                raw_response=response_data
            )
        
        except Exception as e:
            raise RuntimeError(f"OpenAI Vision API error: {str(e)}")
    
    async def _anthropic_vision(
        self,
        prompt: str,
        images: List[ImageInput],
        **kwargs
    ) -> VisionResponse:
        start_time = time.time()
        
        api_base = self.api_base or "https://api.anthropic.com/v1"
        
        content = []
        
        for image in images:
            if image.source_type == "base64":
                base64_image = image.to_base64()
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_image
                    }
                })
            elif image.source_type == "url":
                try:
                    with urllib.request.urlopen(image.source) as response:
                        image_bytes = response.read()
                        base64_image = base64.b64encode(image_bytes).decode('utf-8')
                        content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        })
                except Exception:
                    pass
        
        content.append({
            "type": "text",
            "text": prompt
        })
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature)
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        try:
            response_data = await self._make_request(
                f"{api_base}/messages",
                payload,
                headers
            )
            
            latency = time.time() - start_time
            
            content_blocks = response_data["content"]
            text_content = " ".join([
                block["text"] for block in content_blocks
                if block["type"] == "text"
            ])
            
            usage = response_data.get("usage", {})
            
            return VisionResponse(
                content=text_content,
                model=self.model,
                prompt_tokens=usage.get("input_tokens", 0),
                completion_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                latency=latency,
                images_processed=len(images),
                raw_response=response_data
            )
        
        except Exception as e:
            raise RuntimeError(f"Anthropic Vision API error: {str(e)}")
    
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
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"HTTP {e.code}: {error_body}")
