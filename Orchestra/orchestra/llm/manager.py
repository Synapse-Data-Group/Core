import asyncio
from typing import Any, Dict, List, Optional
from .base import LLMAgent, LLMConfig, LLMProvider, LLMResponse
from .providers import OpenAIProvider, AnthropicProvider, OllamaProvider, HuggingFaceProvider


class LLMManager:
    def __init__(self):
        self.agents: Dict[str, LLMAgent] = {}
        self.provider_registry: Dict[str, type] = {
            LLMProvider.OPENAI.value: OpenAIProvider,
            LLMProvider.ANTHROPIC.value: AnthropicProvider,
            LLMProvider.OLLAMA.value: OllamaProvider,
            LLMProvider.HUGGINGFACE.value: HuggingFaceProvider,
        }
    
    def create_agent(
        self,
        agent_id: str,
        config: LLMConfig,
        system_prompt: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMAgent:
        provider_class = self.provider_registry.get(config.provider.value)
        if not provider_class:
            raise ValueError(f"Unknown provider: {config.provider.value}")
        
        provider = provider_class(config)
        agent = LLMAgent(agent_id, provider, system_prompt, metadata)
        self.agents[agent_id] = agent
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[LLMAgent]:
        return self.agents.get(agent_id)
    
    def remove_agent(self, agent_id: str) -> None:
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    async def execute_parallel(
        self,
        agent_ids: List[str],
        prompt: str,
        **kwargs
    ) -> Dict[str, LLMResponse]:
        tasks = {}
        for agent_id in agent_ids:
            agent = self.agents.get(agent_id)
            if agent:
                tasks[agent_id] = agent.execute(prompt, **kwargs)
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        return {
            agent_id: result
            for agent_id, result in zip(tasks.keys(), results)
            if not isinstance(result, Exception)
        }
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        return {
            agent_id: agent.get_statistics()
            for agent_id, agent in self.agents.items()
        }
    
    def reset_all_statistics(self) -> None:
        for agent in self.agents.values():
            agent.provider.reset_statistics()
