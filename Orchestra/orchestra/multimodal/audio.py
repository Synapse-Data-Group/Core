import asyncio
import base64
import json
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import urllib.request
import urllib.error


@dataclass
class AudioInput:
    source: bytes
    format: str
    language: Optional[str] = None
    
    @classmethod
    def from_file(cls, path: str, language: Optional[str] = None) -> 'AudioInput':
        file_path = Path(path)
        with open(file_path, 'rb') as f:
            audio_bytes = f.read()
        
        format_ext = file_path.suffix.lstrip('.')
        return cls(source=audio_bytes, format=format_ext, language=language)
    
    @classmethod
    def from_bytes(cls, audio_bytes: bytes, format: str, language: Optional[str] = None) -> 'AudioInput':
        return cls(source=audio_bytes, format=format, language=language)


@dataclass
class AudioResponse:
    text: str
    model: str
    language: Optional[str] = None
    duration: Optional[float] = None
    latency: float = 0.0
    raw_response: Optional[Dict[str, Any]] = None


class AudioProvider:
    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        api_base: Optional[str] = None
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
    
    async def transcribe(
        self,
        audio: AudioInput,
        **kwargs
    ) -> AudioResponse:
        if self.provider == "openai":
            return await self._openai_transcribe(audio, **kwargs)
        else:
            raise ValueError(f"Unsupported audio provider: {self.provider}")
    
    async def _openai_transcribe(
        self,
        audio: AudioInput,
        **kwargs
    ) -> AudioResponse:
        start_time = time.time()
        
        api_base = self.api_base or "https://api.openai.com/v1"
        
        boundary = "----WebKitFormBoundary" + base64.b64encode(str(time.time()).encode()).decode()[:16]
        
        body_parts = []
        
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(b'Content-Disposition: form-data; name="file"; filename="audio.' + audio.format.encode() + b'"')
        body_parts.append(b'Content-Type: audio/' + audio.format.encode())
        body_parts.append(b'')
        body_parts.append(audio.source)
        
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(b'Content-Disposition: form-data; name="model"')
        body_parts.append(b'')
        body_parts.append(self.model.encode())
        
        if audio.language:
            body_parts.append(f'--{boundary}'.encode())
            body_parts.append(b'Content-Disposition: form-data; name="language"')
            body_parts.append(b'')
            body_parts.append(audio.language.encode())
        
        body_parts.append(f'--{boundary}--'.encode())
        body_parts.append(b'')
        
        body = b'\r\n'.join(body_parts)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }
        
        try:
            response_data = await self._make_request(
                f"{api_base}/audio/transcriptions",
                body,
                headers
            )
            
            latency = time.time() - start_time
            
            return AudioResponse(
                text=response_data.get("text", ""),
                model=self.model,
                language=response_data.get("language"),
                duration=response_data.get("duration"),
                latency=latency,
                raw_response=response_data
            )
        
        except Exception as e:
            raise RuntimeError(f"OpenAI Audio API error: {str(e)}")
    
    async def _make_request(
        self,
        url: str,
        body: bytes,
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_request,
            url,
            body,
            headers
        )
    
    def _sync_request(
        self,
        url: str,
        body: bytes,
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        req = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"HTTP {e.code}: {error_body}")


class TTSProvider:
    def __init__(
        self,
        provider: str,
        model: str,
        voice: str,
        api_key: str,
        api_base: Optional[str] = None
    ):
        self.provider = provider
        self.model = model
        self.voice = voice
        self.api_key = api_key
        self.api_base = api_base
    
    async def synthesize(
        self,
        text: str,
        **kwargs
    ) -> bytes:
        if self.provider == "openai":
            return await self._openai_tts(text, **kwargs)
        else:
            raise ValueError(f"Unsupported TTS provider: {self.provider}")
    
    async def _openai_tts(
        self,
        text: str,
        **kwargs
    ) -> bytes:
        api_base = self.api_base or "https://api.openai.com/v1"
        
        payload = {
            "model": self.model,
            "input": text,
            "voice": kwargs.get("voice", self.voice),
            "response_format": kwargs.get("response_format", "mp3"),
            "speed": kwargs.get("speed", 1.0)
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            audio_bytes = await self._make_request(
                f"{api_base}/audio/speech",
                payload,
                headers
            )
            
            return audio_bytes
        
        except Exception as e:
            raise RuntimeError(f"OpenAI TTS API error: {str(e)}")
    
    async def _make_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> bytes:
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
    ) -> bytes:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"HTTP {e.code}: {error_body}")
