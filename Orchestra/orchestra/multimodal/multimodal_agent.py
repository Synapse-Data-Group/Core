import asyncio
from typing import Any, Dict, List, Optional, Union
from .vision import VisionProvider, ImageInput, VisionResponse
from .audio import AudioProvider, AudioInput, AudioResponse, TTSProvider


class MultimodalAgent:
    def __init__(
        self,
        agent_id: str,
        vision_provider: Optional[VisionProvider] = None,
        audio_provider: Optional[AudioProvider] = None,
        tts_provider: Optional[TTSProvider] = None,
        text_executor: Optional[Any] = None
    ):
        self.agent_id = agent_id
        self.vision_provider = vision_provider
        self.audio_provider = audio_provider
        self.tts_provider = tts_provider
        self.text_executor = text_executor
        
        self.execution_count = 0
        self.modalities_used = {
            "text": 0,
            "vision": 0,
            "audio": 0,
            "tts": 0
        }
    
    async def execute(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self.execution_count += 1
        context = context or {}
        
        modality = task.get("modality", "text")
        
        if modality == "vision":
            return await self._execute_vision(task, context)
        elif modality == "audio":
            return await self._execute_audio(task, context)
        elif modality == "tts":
            return await self._execute_tts(task, context)
        elif modality == "multimodal":
            return await self._execute_multimodal(task, context)
        else:
            return await self._execute_text(task, context)
    
    async def _execute_vision(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.vision_provider:
            return {
                "error": "Vision provider not configured",
                "agent_id": self.agent_id
            }
        
        self.modalities_used["vision"] += 1
        
        prompt = task.get("prompt", "")
        images = task.get("images", [])
        
        image_inputs = []
        for img in images:
            if isinstance(img, str):
                if img.startswith("http"):
                    image_inputs.append(ImageInput.from_url(img))
                else:
                    image_inputs.append(ImageInput.from_path(img))
            elif isinstance(img, ImageInput):
                image_inputs.append(img)
        
        response = await self.vision_provider.analyze_image(prompt, image_inputs)
        
        return {
            "modality": "vision",
            "result": response.content,
            "images_processed": response.images_processed,
            "tokens": response.total_tokens,
            "latency": response.latency,
            "agent_id": self.agent_id
        }
    
    async def _execute_audio(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.audio_provider:
            return {
                "error": "Audio provider not configured",
                "agent_id": self.agent_id
            }
        
        self.modalities_used["audio"] += 1
        
        audio_file = task.get("audio_file")
        audio_bytes = task.get("audio_bytes")
        audio_format = task.get("audio_format", "mp3")
        language = task.get("language")
        
        if audio_file:
            audio_input = AudioInput.from_file(audio_file, language)
        elif audio_bytes:
            audio_input = AudioInput.from_bytes(audio_bytes, audio_format, language)
        else:
            return {
                "error": "No audio input provided",
                "agent_id": self.agent_id
            }
        
        response = await self.audio_provider.transcribe(audio_input)
        
        return {
            "modality": "audio",
            "result": response.text,
            "language": response.language,
            "duration": response.duration,
            "latency": response.latency,
            "agent_id": self.agent_id
        }
    
    async def _execute_tts(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.tts_provider:
            return {
                "error": "TTS provider not configured",
                "agent_id": self.agent_id
            }
        
        self.modalities_used["tts"] += 1
        
        text = task.get("text", "")
        
        audio_bytes = await self.tts_provider.synthesize(text)
        
        output_file = task.get("output_file")
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(audio_bytes)
        
        return {
            "modality": "tts",
            "result": "Audio synthesized successfully",
            "audio_bytes": audio_bytes if not output_file else None,
            "output_file": output_file,
            "agent_id": self.agent_id
        }
    
    async def _execute_multimodal(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        results = {}
        
        if task.get("vision_task"):
            vision_result = await self._execute_vision(task["vision_task"], context)
            results["vision"] = vision_result
        
        if task.get("audio_task"):
            audio_result = await self._execute_audio(task["audio_task"], context)
            results["audio"] = audio_result
        
        if task.get("text_task"):
            text_result = await self._execute_text(task["text_task"], context)
            results["text"] = text_result
        
        return {
            "modality": "multimodal",
            "results": results,
            "agent_id": self.agent_id
        }
    
    async def _execute_text(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.text_executor:
            return {
                "error": "Text executor not configured",
                "agent_id": self.agent_id
            }
        
        self.modalities_used["text"] += 1
        
        result = self.text_executor(context)
        if asyncio.iscoroutine(result):
            result = await result
        
        return {
            "modality": "text",
            "result": result,
            "agent_id": self.agent_id
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "execution_count": self.execution_count,
            "modalities_used": self.modalities_used,
            "capabilities": {
                "vision": self.vision_provider is not None,
                "audio": self.audio_provider is not None,
                "tts": self.tts_provider is not None,
                "text": self.text_executor is not None
            }
        }
