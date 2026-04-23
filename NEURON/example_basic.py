"""
Basic example of Neuron system

Demonstrates self-organizing neural intelligence with dynamic neuron creation.
"""

import os
from neuron_core import OpenAIProvider, AnthropicProvider, GoogleProvider
from neuron_network import NeuronNetwork


def main():
    print("=" * 70)
    print("NEURON - Self-Organizing Neural Intelligence System")
    print("=" * 70)
    print("\nThis demonstrates a living neural organism that:")
    print("  • Starts with 1000 baseline neurons")
    print("  • Dynamically spawns specialists as needed")
    print("  • Reasons collectively (no single neuron decides)")
    print("  • Scales back down after task completion")
    print("\n" + "=" * 70 + "\n")
    
    # Choose LLM provider
    print("Available LLM providers:")
    print("  1. OpenAI (GPT-4o-mini)")
    print("  2. Anthropic (Claude)")
    print("  3. Google (Gemini)")
    
    choice = input("\nSelect provider (1-3) [1]: ").strip() or "1"
    
    if choice == "1":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            api_key = input("Enter OpenAI API key: ").strip()
        provider = OpenAIProvider(api_key=api_key, model="gpt-4o-mini")
    elif choice == "2":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            api_key = input("Enter Anthropic API key: ").strip()
        provider = AnthropicProvider(api_key=api_key)
    elif choice == "3":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            api_key = input("Enter Google API key: ").strip()
        provider = GoogleProvider(api_key=api_key)
    else:
        print("Invalid choice, using OpenAI")
        provider = OpenAIProvider()
    
    print(f"\n✓ Using {provider.get_provider_name()}")
    
    # Create neural network
    print("\nInitializing neural network...")
    network = NeuronNetwork(
        llm_provider=provider,
        baseline_neurons=1000,
        vector_dimension=128
    )
    
    # Example 1: Simple query (uses baseline neurons)
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Query")
    print("=" * 70)
    
    response = network.process("What is 2+2?")
    print(f"\nResponse:\n{response}\n")
    
    stats = network.get_statistics()
    print(f"Network stats: {stats['total_neurons']} neurons, "
          f"{stats['specialist_neurons']} specialists")
    
    # Example 2: Complex task (spawns specialists)
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Complex Task - React Landing Page")
    print("=" * 70)
    print("\nThis will demonstrate dynamic neuron creation:")
    print("  • Meta-neurons detect: 'No React expertise'")
    print("  • System spawns: React specialist neurons")
    print("  • Specialists learn: React concepts")
    print("  • Collective reasoning: Produces solution")
    print("  • Cleanup: Specialists pruned after task")
    
    input("\nPress Enter to continue...")
    
    response = network.process(
        "Create a modern React landing page with hero section, "
        "features, and call-to-action. Use TailwindCSS for styling."
    )
    
    print(f"\nCollective Response:\n{response}\n")
    
    stats = network.get_statistics()
    print(f"Network stats: {stats['total_neurons']} neurons, "
          f"{stats['specialist_neurons']} specialists")
    
    # Example 3: Custom query
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Your Query")
    print("=" * 70)
    
    user_query = input("\nEnter your query (or press Enter to skip): ").strip()
    
    if user_query:
        response = network.process(user_query)
        print(f"\nCollective Response:\n{response}\n")
        
        stats = network.get_statistics()
        print(f"Network stats: {stats['total_neurons']} neurons, "
              f"{stats['specialist_neurons']} specialists")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey insights:")
    print("  ✓ No fixed agent list - neurons created on-demand")
    print("  ✓ No master agent - collective intelligence decides")
    print("  ✓ Adaptive scaling - brain grows/shrinks with task")
    print("  ✓ Emergent capabilities - specialists learn as needed")
    print("\nThis replaces traditional agent workflows with living neural organism.")


if __name__ == "__main__":
    main()
