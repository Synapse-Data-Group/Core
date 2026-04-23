"""
LLM-Powered Agent - Uses OpenAI API for real reasoning
Agents think, propose, challenge, and rebut using GPT
"""

import uuid
import time
import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional, Any
from learning_engine import ExperienceMemory, QLearningEngine, GeneticEvolution


class LLMPoweredAgent:
    """Agent that uses OpenAI API for actual reasoning"""
    
    def __init__(self, name: str, api_key: str, personality: Dict[str, float] = None, model: str = "gpt-4o-mini"):
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.api_key = api_key
        self.model = model
        self.personality = personality or self._generate_random_personality()
        self.is_active = True
        self.score = 0.0
        
        # Tracking
        self.proposals_made = []
        self.challenges_made = []
        self.rebuttals_made = []
        self.tools = []
        
        # Learning (still tracked for framework compatibility)
        self.memory = ExperienceMemory()
        self.q_learning = QLearningEngine()
        
    def _generate_random_personality(self) -> Dict[str, float]:
        import random
        return {
            "creativity": random.uniform(0.3, 0.9),
            "boldness": random.uniform(0.3, 0.9),
            "aggressiveness": random.uniform(0.2, 0.8),
            "analytical_depth": random.uniform(0.4, 0.95),
            "optimism": random.uniform(0.3, 0.9),
            "evidence_reliance": random.uniform(0.4, 0.95)
        }
    
    def _call_openai(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_retries: int = 3) -> str:
        """Make actual OpenAI API call with retry logic"""
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': 500
        }
        
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(
                    'https://api.openai.com/v1/chat/completions',
                    data=json.dumps(data).encode('utf-8'),
                    headers=headers
                )
                
                print(f"  [Attempt {attempt + 1}/{max_retries}] Calling OpenAI API...")
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    return result['choices'][0]['message']['content']
            
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                print(f"  OpenAI API Error: {e.code} - {error_body}")
                if e.code == 429 and attempt < max_retries - 1:  # Rate limit
                    print(f"  Rate limited, waiting 5s before retry...")
                    time.sleep(5)
                    continue
                return f"[API Error {e.code}: {error_body[:100]}]"
            
            except urllib.error.URLError as e:
                print(f"  Network error: {e}")
                if attempt < max_retries - 1:
                    print(f"  Retrying in 3s...")
                    time.sleep(3)
                    continue
                return "[Network error - could not reach OpenAI]"
            
            except Exception as e:
                print(f"  Error calling OpenAI: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    print(f"  Retrying in 2s...")
                    time.sleep(2)
                    continue
                return f"[Error: {type(e).__name__}]"
        
        return "[Failed after all retries]"
    
    def _build_personality_prompt(self) -> str:
        """Build personality description for system prompt"""
        
        traits = []
        for trait, value in self.personality.items():
            if value > 0.75:
                traits.append(f"very {trait.replace('_', ' ')}")
            elif value > 0.55:
                traits.append(f"moderately {trait.replace('_', ' ')}")
        
        return f"You are {self.name}, a debate agent with these traits: {', '.join(traits)}. " + \
               "Argue from your perspective based on these traits."
    
    def generate_proposal(self, problem: str, context: Dict[str, Any]) -> str:
        """Generate proposal using GPT"""
        
        system_prompt = self._build_personality_prompt()
        system_prompt += " Generate a clear, well-reasoned proposal addressing the problem."
        
        user_prompt = f"Problem: {problem}\n\n"
        
        # Add web research if available
        if context.get('web_research'):
            user_prompt += f"Research findings: {context['web_research'][:500]}\n\n"
        
        user_prompt += "Provide your proposal (2-3 paragraphs):"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        temperature = self.personality.get('creativity', 0.7)
        response = self._call_openai(messages, temperature)
        
        return response
    
    def generate_challenge(self, proposal_content: str, proposal_agent: str, context: Dict[str, Any]) -> str:
        """Generate challenge using GPT"""
        
        system_prompt = self._build_personality_prompt()
        system_prompt += " Critically analyze and challenge the proposal with specific concerns."
        
        aggressiveness = self.personality.get('aggressiveness', 0.5)
        if aggressiveness > 0.7:
            system_prompt += " Be direct and forceful in your critique."
        elif aggressiveness < 0.4:
            system_prompt += " Be diplomatic but firm in your concerns."
        
        user_prompt = f"Proposal by {proposal_agent}:\n{proposal_content}\n\n"
        user_prompt += "Provide a specific challenge (1-2 paragraphs):"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._call_openai(messages, 0.6)
        
        return response
    
    def generate_rebuttal(self, challenge_content: str, challenge_agent: str, 
                         original_proposal: str, context: Dict[str, Any]) -> str:
        """Generate rebuttal using GPT"""
        
        system_prompt = self._build_personality_prompt()
        system_prompt += " Defend your proposal against the challenge with evidence and reasoning."
        
        user_prompt = f"Your original proposal:\n{original_proposal}\n\n"
        user_prompt += f"Challenge by {challenge_agent}:\n{challenge_content}\n\n"
        user_prompt += "Provide your rebuttal (1-2 paragraphs):"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._call_openai(messages, 0.6)
        
        return response
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "personality": self.personality,
            "is_active": self.is_active,
            "score": self.score,
            "proposals_made": len(self.proposals_made),
            "challenges_made": len(self.challenges_made),
            "rebuttals_made": len(self.rebuttals_made)
        }
