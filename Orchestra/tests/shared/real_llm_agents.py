#!/usr/bin/env python3
"""
Real LLM Agents for Orchestra v4.0 Benchmarking
Creates 10 real LLM agents with different configurations using OpenAI API
These agents make ACTUAL API calls to OpenAI for benchmarking against LangChain
"""

import os
from typing import Dict, Any, List
from orchestra.llm import (
    LLMAgent,
    LLMConfig,
    LLMProvider,
    LLMManager
)


class RealAgentFactory:
    """Factory for creating real LLM agents with OpenAI API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.manager = LLMManager()
        self.agents: List[LLMAgent] = []
    
    def create_all_agents(self) -> List[LLMAgent]:
        """Create all 10 real LLM agents with different specializations"""
        
        # Agent 1: GPT-4 Strategic Planner
        config1 = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key=self.api_key,
            temperature=0.7,
            max_tokens=500
        )
        agent1 = self.manager.create_agent(
            "gpt4_strategic_planner",
            config1,
            system_prompt="You are a strategic planner. Provide high-level strategic solutions focusing on long-term impact, scalability, and business value."
        )
        self.agents.append(agent1)
        
        # Agent 2: GPT-4 Turbo Fast Analyzer
        config2 = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4-turbo-preview",
            api_key=self.api_key,
            temperature=0.5,
            max_tokens=400
        )
        agent2 = self.manager.create_agent(
            "gpt4_turbo_analyzer",
            config2,
            system_prompt="You are a fast analytical thinker. Provide quick, data-driven analysis with clear reasoning."
        )
        self.agents.append(agent2)
        
        # Agent 3: GPT-3.5 Turbo Efficient Worker
        config3 = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            api_key=self.api_key,
            temperature=0.6,
            max_tokens=300
        )
        agent3 = self.manager.create_agent(
            "gpt35_efficient_worker",
            config3,
            system_prompt="You are an efficient problem solver. Provide practical, cost-effective solutions quickly."
        )
        self.agents.append(agent3)
        
        # Agent 4: GPT-4 Creative Innovator
        config4 = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key=self.api_key,
            temperature=0.9,
            max_tokens=600
        )
        agent4 = self.manager.create_agent(
            "gpt4_creative_innovator",
            config4,
            system_prompt="You are a creative innovator. Think outside the box and propose novel, unconventional solutions."
        )
        self.agents.append(agent4)
        
        # Agent 5: GPT-3.5 Turbo Precise Executor
        config5 = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            api_key=self.api_key,
            temperature=0.3,
            max_tokens=350
        )
        agent5 = self.manager.create_agent(
            "gpt35_precise_executor",
            config5,
            system_prompt="You are a precise executor. Provide detailed, step-by-step solutions with high accuracy."
        )
        self.agents.append(agent5)
        
        # Agent 6: GPT-4 Technical Expert
        config6 = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key=self.api_key,
            temperature=0.4,
            max_tokens=500
        )
        agent6 = self.manager.create_agent(
            "gpt4_technical_expert",
            config6,
            system_prompt="You are a technical expert. Provide deep technical insights with implementation details."
        )
        self.agents.append(agent6)
        
        # Agent 7: GPT-3.5 Turbo Rapid Responder
        config7 = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            api_key=self.api_key,
            temperature=0.7,
            max_tokens=250
        )
        agent7 = self.manager.create_agent(
            "gpt35_rapid_responder",
            config7,
            system_prompt="You are a rapid responder. Provide quick, concise answers. Get to the point fast."
        )
        self.agents.append(agent7)
        
        # Agent 8: GPT-4 Research Analyst
        config8 = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key=self.api_key,
            temperature=0.6,
            max_tokens=700
        )
        agent8 = self.manager.create_agent(
            "gpt4_research_analyst",
            config8,
            system_prompt="You are a research analyst. Provide comprehensive, well-researched answers with multiple perspectives."
        )
        self.agents.append(agent8)
        
        # Agent 9: GPT-3.5 Turbo Balanced Generalist
        config9 = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            api_key=self.api_key,
            temperature=0.7,
            max_tokens=400
        )
        agent9 = self.manager.create_agent(
            "gpt35_balanced_generalist",
            config9,
            system_prompt="You are a balanced generalist. Provide well-rounded solutions that balance speed, quality, and practicality."
        )
        self.agents.append(agent9)
        
        # Agent 10: GPT-4 Quality Reviewer
        config10 = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key=self.api_key,
            temperature=0.5,
            max_tokens=450
        )
        agent10 = self.manager.create_agent(
            "gpt4_quality_reviewer",
            config10,
            system_prompt="You are a quality reviewer. Evaluate solutions critically and identify potential issues or improvements."
        )
        self.agents.append(agent10)
        
        return self.agents
    
    def get_agent(self, agent_id: str) -> LLMAgent:
        """Get agent by ID"""
        return self.manager.get_agent(agent_id)
    
    def get_all_agents(self) -> List[LLMAgent]:
        """Get all agents"""
        return self.agents
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics for all agents"""
        return self.manager.get_all_statistics()
    
    def reset_stats(self):
        """Reset statistics for all agents"""
        self.manager.reset_all_statistics()


def get_api_key() -> str:
    """Get OpenAI API key from environment or config"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Please set it as an environment variable:\n"
            "  Windows: $env:OPENAI_API_KEY='your-key-here'\n"
            "  Linux/Mac: export OPENAI_API_KEY='your-key-here'"
        )
    return api_key


if __name__ == "__main__":
    import asyncio
    
    async def test_agents():
        print("=" * 70)
        print("REAL LLM AGENTS - ORCHESTRA v4.0")
        print("=" * 70)
        
        try:
            api_key = get_api_key()
            factory = RealAgentFactory(api_key)
            agents = factory.create_all_agents()
            
            print(f"\n✅ Created {len(agents)} real LLM agents")
            print("\nAgent List:")
            for i, agent in enumerate(agents, 1):
                stats = agent.get_statistics()
                print(f"  {i}. {agent.agent_id} ({stats['model']})")
            
            print("\n" + "=" * 70)
            print("Testing with a simple prompt...")
            print("=" * 70)
            
            test_prompt = "What is the best approach to optimize a distributed system?"
            
            agent = agents[0]
            print(f"\nTesting: {agent.agent_id}")
            response = await agent.execute(test_prompt)
            
            print(f"\n✅ Response received:")
            print(f"  Content: {response.content[:150]}...")
            print(f"  Tokens: {response.total_tokens}")
            print(f"  Cost: ${response.cost_estimate:.4f}")
            print(f"  Latency: {response.latency:.2f}s")
            
            print("\n" + "=" * 70)
            print("✅ All agents ready for benchmarking!")
            print("=" * 70)
            
        except ValueError as e:
            print(f"\n❌ Error: {e}")
            return 1
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        return 0
    
    exit(asyncio.run(test_agents()))
