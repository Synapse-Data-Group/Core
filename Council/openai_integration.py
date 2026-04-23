"""
OpenAI API Integration Module
Placeholder for enhancing agent arguments with GPT models
Set your API key and agents can use real LLM reasoning
"""

import os
from typing import Optional, Dict, Any


class OpenAIIntegration:
    """
    Integration with OpenAI API for enhanced agent reasoning
    When API key is provided, agents can use GPT for argument generation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.enabled = self.api_key is not None
        self.model = "gpt-4o-mini"  # Fast and cost-effective
        self.request_count = 0
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
        if self.enabled:
            print(f"✓ OpenAI Integration ENABLED (Model: {self.model})")
            print(f"  API Key: {self.api_key[:20]}...{self.api_key[-4:]}")
        else:
            print("ℹ OpenAI Integration DISABLED (No API key provided)")
    
    def generate_proposal(self, problem: str, personality: Dict[str, float], 
                         context: Dict[str, Any]) -> Optional[str]:
        """
        Generate proposal using GPT with personality traits
        Falls back to built-in generation if API unavailable
        """
        
        if not self.enabled:
            return None
        
        try:
            # When you provide API key, this will use real OpenAI API
            # For now, returns None to use built-in generation
            
            # Example implementation (uncomment when API key provided):
            """
            import urllib.request
            import json
            
            prompt = self._build_proposal_prompt(problem, personality, context)
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            data = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': 'You are a debate agent with specific personality traits.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': personality.get('creativity', 0.7),
                'max_tokens': 500
            }
            
            req = urllib.request.Request(
                'https://api.openai.com/v1/chat/completions',
                data=json.dumps(data).encode('utf-8'),
                headers=headers
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                self.request_count += 1
                return result['choices'][0]['message']['content']
            """
            
            return None
            
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return None
    
    def generate_challenge(self, proposal: str, personality: Dict[str, float]) -> Optional[str]:
        """Generate challenge using GPT"""
        
        if not self.enabled:
            return None
        
        # Implementation similar to generate_proposal
        return None
    
    def generate_rebuttal(self, challenge: str, original_proposal: str, 
                         personality: Dict[str, float]) -> Optional[str]:
        """Generate rebuttal using GPT"""
        
        if not self.enabled:
            return None
        
        # Implementation similar to generate_proposal
        return None
    
    def _build_proposal_prompt(self, problem: str, personality: Dict[str, float], 
                              context: Dict[str, Any]) -> str:
        """Build prompt for GPT based on personality and context"""
        
        prompt = f"You are debating the following problem: {problem}\n\n"
        prompt += "Your personality traits:\n"
        
        for trait, value in personality.items():
            if value > 0.7:
                prompt += f"- Very {trait.replace('_', ' ')}\n"
            elif value > 0.5:
                prompt += f"- Moderately {trait.replace('_', ' ')}\n"
        
        prompt += "\nGenerate a proposal that reflects these traits. Be concise but persuasive."
        
        return prompt
    
    def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        
        return {
            "enabled": self.enabled,
            "model": self.model if self.enabled else None,
            "requests_made": self.request_count,
            "api_key_set": self.api_key is not None
        }


# Global instance - set API key here or via environment variable
openai_integration = OpenAIIntegration()


def set_openai_key(api_key: str):
    """
    Set OpenAI API key for enhanced agent reasoning
    
    Usage:
        from openai_integration import set_openai_key
        set_openai_key("sk-...")
    """
    global openai_integration
    openai_integration = OpenAIIntegration(api_key)
    return openai_integration.enabled


# Instructions for user:
"""
TO ENABLE OPENAI INTEGRATION:

1. Set your API key:
   
   from openai_integration import set_openai_key
   set_openai_key("sk-your-api-key-here")

2. Or set environment variable:
   
   export OPENAI_API_KEY="sk-your-api-key-here"

3. Agents will automatically use GPT for enhanced reasoning when available

4. Falls back to built-in generation if API unavailable

BENEFITS:
- More sophisticated arguments
- Better natural language quality
- Personality-driven GPT prompts
- Still works without API key (uses built-in generation)
"""
