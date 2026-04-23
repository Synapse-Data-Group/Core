import uuid
import random
from typing import Dict, List, Optional, Any
from sentient_agent import SentientAgent


class AgentArchetype:
    """Defines templates for different agent types that can be spawned"""
    
    ARCHETYPES = {
        "devil_advocate": {
            "description": "Challenges assumptions and finds flaws",
            "personality": {
                "creativity": 0.6,
                "boldness": 0.7,
                "aggressiveness": 0.9,
                "defensiveness": 0.4,
                "supportiveness": 0.1,
                "analytical_depth": 0.8,
                "evidence_reliance": 0.7,
                "confidence": 0.8,
                "optimism": 0.3,
                "verbosity": 0.6,
                "formality": 0.7
            }
        },
        "mediator": {
            "description": "Finds common ground and synthesizes views",
            "personality": {
                "creativity": 0.6,
                "boldness": 0.4,
                "aggressiveness": 0.2,
                "defensiveness": 0.3,
                "supportiveness": 0.9,
                "analytical_depth": 0.7,
                "evidence_reliance": 0.6,
                "confidence": 0.6,
                "optimism": 0.7,
                "verbosity": 0.5,
                "formality": 0.6
            }
        },
        "innovator": {
            "description": "Proposes novel and creative solutions",
            "personality": {
                "creativity": 0.95,
                "boldness": 0.9,
                "aggressiveness": 0.5,
                "defensiveness": 0.6,
                "supportiveness": 0.4,
                "analytical_depth": 0.5,
                "evidence_reliance": 0.4,
                "confidence": 0.8,
                "optimism": 0.9,
                "verbosity": 0.7,
                "formality": 0.4
            }
        },
        "analyst": {
            "description": "Provides data-driven analysis and evidence",
            "personality": {
                "creativity": 0.3,
                "boldness": 0.4,
                "aggressiveness": 0.4,
                "defensiveness": 0.5,
                "supportiveness": 0.5,
                "analytical_depth": 0.95,
                "evidence_reliance": 0.95,
                "confidence": 0.7,
                "optimism": 0.5,
                "verbosity": 0.8,
                "formality": 0.9
            }
        },
        "pragmatist": {
            "description": "Focuses on practical implementation",
            "personality": {
                "creativity": 0.4,
                "boldness": 0.5,
                "aggressiveness": 0.5,
                "defensiveness": 0.5,
                "supportiveness": 0.6,
                "analytical_depth": 0.6,
                "evidence_reliance": 0.7,
                "confidence": 0.7,
                "optimism": 0.5,
                "verbosity": 0.5,
                "formality": 0.6
            }
        },
        "visionary": {
            "description": "Thinks long-term and strategically",
            "personality": {
                "creativity": 0.85,
                "boldness": 0.8,
                "aggressiveness": 0.3,
                "defensiveness": 0.5,
                "supportiveness": 0.6,
                "analytical_depth": 0.7,
                "evidence_reliance": 0.5,
                "confidence": 0.8,
                "optimism": 0.8,
                "verbosity": 0.7,
                "formality": 0.5
            }
        },
        "skeptic": {
            "description": "Questions everything and demands proof",
            "personality": {
                "creativity": 0.5,
                "boldness": 0.6,
                "aggressiveness": 0.8,
                "defensiveness": 0.7,
                "supportiveness": 0.2,
                "analytical_depth": 0.9,
                "evidence_reliance": 0.9,
                "confidence": 0.7,
                "optimism": 0.2,
                "verbosity": 0.6,
                "formality": 0.8
            }
        },
        "optimist": {
            "description": "Sees opportunities and positive outcomes",
            "personality": {
                "creativity": 0.7,
                "boldness": 0.7,
                "aggressiveness": 0.3,
                "defensiveness": 0.4,
                "supportiveness": 0.8,
                "analytical_depth": 0.5,
                "evidence_reliance": 0.5,
                "confidence": 0.8,
                "optimism": 0.95,
                "verbosity": 0.6,
                "formality": 0.5
            }
        },
        "ethicist": {
            "description": "Evaluates moral and ethical implications",
            "personality": {
                "creativity": 0.6,
                "boldness": 0.5,
                "aggressiveness": 0.4,
                "defensiveness": 0.6,
                "supportiveness": 0.6,
                "analytical_depth": 0.8,
                "evidence_reliance": 0.7,
                "confidence": 0.7,
                "optimism": 0.5,
                "verbosity": 0.7,
                "formality": 0.8
            }
        },
        "specialist": {
            "description": "Deep expertise in specific domain",
            "personality": {
                "creativity": 0.5,
                "boldness": 0.6,
                "aggressiveness": 0.5,
                "defensiveness": 0.7,
                "supportiveness": 0.5,
                "analytical_depth": 0.9,
                "evidence_reliance": 0.9,
                "confidence": 0.9,
                "optimism": 0.6,
                "verbosity": 0.7,
                "formality": 0.8
            }
        }
    }
    
    @classmethod
    def get_archetype(cls, archetype_name: str) -> Dict[str, Any]:
        return cls.ARCHETYPES.get(archetype_name, cls.ARCHETYPES["pragmatist"])
    
    @classmethod
    def list_archetypes(cls) -> List[str]:
        return list(cls.ARCHETYPES.keys())
    
    @classmethod
    def get_random_archetype(cls) -> str:
        return random.choice(cls.list_archetypes())


class AgentFactory:
    """Factory for creating agents dynamically during debates"""
    
    def __init__(self, memory_directory: str = "./dynamic_memories"):
        self.memory_directory = memory_directory
        self.created_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_counter = 0
        
    def create_agent(self, archetype: str, name: Optional[str] = None, 
                    memory_path: Optional[str] = None) -> SentientAgent:
        """Create an agent based on archetype"""
        
        archetype_data = AgentArchetype.get_archetype(archetype)
        
        if name is None:
            self.agent_counter += 1
            name = f"{archetype.title()}_{self.agent_counter}"
        
        agent_id = str(uuid.uuid4())
        
        personality = archetype_data["personality"].copy()
        personality = self._add_personality_variation(personality)
        
        if memory_path is None:
            memory_path = f"{self.memory_directory}/{archetype}_{agent_id}_memory.pkl"
        
        agent = SentientAgent(agent_id, name, personality, memory_path)
        
        self.created_agents[agent_id] = {
            "agent": agent,
            "archetype": archetype,
            "name": name,
            "created_at": agent.created_at,
            "purpose": archetype_data["description"]
        }
        
        return agent
    
    def _add_personality_variation(self, personality: Dict[str, float], 
                                   variation: float = 0.1) -> Dict[str, float]:
        """Add slight random variation to personality traits"""
        varied = {}
        for trait, value in personality.items():
            noise = random.gauss(0, variation)
            varied[trait] = max(0.0, min(1.0, value + noise))
        return varied
    
    def create_complementary_agent(self, existing_agents: List[SentientAgent], 
                                   debate_context: Dict[str, Any]) -> SentientAgent:
        """Create an agent that complements existing agents"""
        
        existing_archetypes = []
        for agent in existing_agents:
            for agent_id, data in self.created_agents.items():
                if data["agent"].agent_id == agent.agent_id:
                    existing_archetypes.append(data["archetype"])
                    break
        
        avg_creativity = sum(a.personality.get("creativity", 0.5) for a in existing_agents) / len(existing_agents)
        avg_aggressiveness = sum(a.personality.get("aggressiveness", 0.5) for a in existing_agents) / len(existing_agents)
        avg_analytical = sum(a.personality.get("analytical_depth", 0.5) for a in existing_agents) / len(existing_agents)
        
        if avg_creativity < 0.5 and "innovator" not in existing_archetypes:
            archetype = "innovator"
        elif avg_aggressiveness < 0.4 and "devil_advocate" not in existing_archetypes:
            archetype = "devil_advocate"
        elif avg_analytical < 0.5 and "analyst" not in existing_archetypes:
            archetype = "analyst"
        elif "mediator" not in existing_archetypes and len(existing_agents) > 3:
            archetype = "mediator"
        else:
            available = [a for a in AgentArchetype.list_archetypes() if a not in existing_archetypes]
            archetype = random.choice(available) if available else AgentArchetype.get_random_archetype()
        
        return self.create_agent(archetype)
    
    def create_role_specific_agent(self, role: str, debate_context: Dict[str, Any]) -> SentientAgent:
        """Create an agent for a specific role needed in the debate"""
        
        role_to_archetype = {
            "challenge": "devil_advocate",
            "support": "optimist",
            "analyze": "analyst",
            "mediate": "mediator",
            "innovate": "innovator",
            "question": "skeptic",
            "implement": "pragmatist",
            "envision": "visionary",
            "ethics": "ethicist",
            "expert": "specialist"
        }
        
        archetype = role_to_archetype.get(role.lower(), "pragmatist")
        return self.create_agent(archetype)
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a created agent"""
        return self.created_agents.get(agent_id)
    
    def list_created_agents(self) -> List[Dict[str, Any]]:
        """List all agents created by this factory"""
        return [
            {
                "agent_id": agent_id,
                "name": data["name"],
                "archetype": data["archetype"],
                "purpose": data["purpose"],
                "is_active": data["agent"].is_active
            }
            for agent_id, data in self.created_agents.items()
        ]
