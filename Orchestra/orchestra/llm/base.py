import asyncio
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


@dataclass
class LLMConfig:
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency: float = 0.0
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def cost_estimate(self) -> float:
        cost_per_1k = {
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
            "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
            "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
            "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
            "claude-3-haiku": {"prompt": 0.00025, "completion": 0.00125},
        }
        
        if self.model in cost_per_1k:
            rates = cost_per_1k[self.model]
            prompt_cost = (self.prompt_tokens / 1000) * rates["prompt"]
            completion_cost = (self.completion_tokens / 1000) * rates["completion"]
            return prompt_cost + completion_cost
        
        return 0.0


class BaseLLMProvider(ABC):
    def __init__(self, config: LLMConfig):
        self.config = config
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.request_history: List[Dict[str, Any]] = []
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        pass
    
    @abstractmethod
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        pass
    
    async def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                response = await self.generate(prompt, system_prompt, **kwargs)
                self._track_request(response)
                return response
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
        
        raise RuntimeError(f"Failed after {self.config.max_retries} retries: {last_error}")
    
    def _track_request(self, response: LLMResponse) -> None:
        self.total_requests += 1
        self.total_tokens += response.total_tokens
        self.total_cost += response.cost_estimate
        
        self.request_history.append({
            "timestamp": time.time(),
            "model": response.model,
            "tokens": response.total_tokens,
            "cost": response.cost_estimate,
            "latency": response.latency
        })
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "provider": self.config.provider.value,
            "model": self.config.model,
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "avg_tokens_per_request": self.total_tokens / self.total_requests if self.total_requests > 0 else 0,
            "avg_cost_per_request": self.total_cost / self.total_requests if self.total_requests > 0 else 0
        }
    
    def reset_statistics(self) -> None:
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.request_history.clear()


class LLMAgent:
    def __init__(
        self,
        agent_id: str,
        provider: BaseLLMProvider,
        system_prompt: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.provider = provider
        self.system_prompt = system_prompt
        self.metadata = metadata or {}
        self.conversation_history: List[Dict[str, str]] = []
    
    async def execute(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        use_history: bool = False,
        **kwargs
    ) -> LLMResponse:
        if use_history and self.conversation_history:
            messages = self.conversation_history.copy()
            messages.append({"role": "user", "content": prompt})
            response = await self.provider.generate_chat(messages, **kwargs)
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": response.content})
        else:
            response = await self.provider.generate_with_retry(
                prompt=prompt,
                system_prompt=self.system_prompt,
                **kwargs
            )
        
        return response
    
    async def execute_batch(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[LLMResponse]:
        tasks = [self.execute(prompt, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks)
    
    def clear_history(self) -> None:
        self.conversation_history.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        stats = self.provider.get_statistics()
        stats["agent_id"] = self.agent_id
        stats["conversation_length"] = len(self.conversation_history)
        return stats
