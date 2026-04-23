import asyncio
from orchestra import (
    ToolRegistry,
    ToolExecutor,
    PromptTemplate,
    JSONParser,
    LLMConfig,
    LLMProvider,
    LLMManager
)


def calculate_sum(a: int, b: int) -> int:
    return a + b


def calculate_product(a: int, b: int) -> int:
    return a * b


def search_database(query: str, limit: int = 5) -> list:
    mock_results = [
        f"Result {i}: Information about {query}"
        for i in range(1, limit + 1)
    ]
    return mock_results


async def fetch_weather(city: str) -> dict:
    await asyncio.sleep(0.1)
    return {
        "city": city,
        "temperature": 72,
        "condition": "sunny",
        "humidity": 45
    }


async def main():
    print("=" * 70)
    print("ORCHESTRA v2.0 - TOOL CALLING EXAMPLE")
    print("Function Calling with LLM Integration")
    print("=" * 70)
    
    print("\n[1] Creating Tool Registry")
    print("-" * 70)
    
    registry = ToolRegistry()
    
    registry.register(
        name="calculate_sum",
        func=calculate_sum,
        description="Calculate the sum of two numbers",
        parameters={
            "a": {"type": "integer", "description": "First number"},
            "b": {"type": "integer", "description": "Second number"}
        },
        required=["a", "b"],
        category="math"
    )
    
    registry.register(
        name="calculate_product",
        func=calculate_product,
        description="Calculate the product of two numbers",
        parameters={
            "a": {"type": "integer", "description": "First number"},
            "b": {"type": "integer", "description": "Second number"}
        },
        required=["a", "b"],
        category="math"
    )
    
    registry.register(
        name="search_database",
        func=search_database,
        description="Search the database for information",
        parameters={
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "description": "Maximum results", "default": 5}
        },
        required=["query"],
        category="data"
    )
    
    registry.register(
        name="fetch_weather",
        func=fetch_weather,
        description="Fetch current weather for a city",
        parameters={
            "city": {"type": "string", "description": "City name"}
        },
        required=["city"],
        category="api"
    )
    
    print(f"✓ Registered {len(registry.get_tool_names())} tools")
    for name in registry.get_tool_names():
        tool = registry.get_tool(name)
        print(f"  - {name}: {tool.description}")
    
    print("\n[2] Creating Tool Executor")
    print("-" * 70)
    
    executor = ToolExecutor(registry)
    
    print("✓ Tool executor created")
    
    print("\n[3] Executing Individual Tools")
    print("-" * 70)
    
    result1 = await executor.execute("calculate_sum", {"a": 15, "b": 27})
    print(f"calculate_sum(15, 27) = {result1.output}")
    print(f"  Success: {result1.success}, Time: {result1.execution_time:.4f}s")
    
    result2 = await executor.execute("calculate_product", {"a": 8, "b": 9})
    print(f"calculate_product(8, 9) = {result2.output}")
    print(f"  Success: {result2.success}, Time: {result2.execution_time:.4f}s")
    
    result3 = await executor.execute("search_database", {"query": "Orchestra framework", "limit": 3})
    print(f"search_database('Orchestra framework', limit=3):")
    for item in result3.output:
        print(f"  - {item}")
    
    result4 = await executor.execute("fetch_weather", {"city": "San Francisco"})
    print(f"fetch_weather('San Francisco'):")
    print(f"  Temperature: {result4.output['temperature']}°F")
    print(f"  Condition: {result4.output['condition']}")
    
    print("\n[4] Batch Tool Execution (Parallel)")
    print("-" * 70)
    
    tool_calls = [
        {"tool_name": "calculate_sum", "parameters": {"a": 10, "b": 20}},
        {"tool_name": "calculate_product", "parameters": {"a": 5, "b": 6}},
        {"tool_name": "fetch_weather", "parameters": {"city": "New York"}},
    ]
    
    print("Executing 3 tools in parallel...")
    batch_results = await executor.execute_batch(tool_calls, parallel=True)
    
    for i, result in enumerate(batch_results, 1):
        print(f"  Result {i}: {result.output}")
    
    print("\n[5] Tool Chain Execution")
    print("-" * 70)
    
    tool_chain = [
        {"tool_name": "calculate_sum", "parameters": {"a": 5, "b": 10}},
        {"tool_name": "calculate_product", "parameters": {"a": 3, "b": 2}, "use_previous_output": False},
    ]
    
    print("Executing tool chain: sum(5, 10) -> product(3, 2)")
    chain_result = await executor.execute_chain(tool_chain)
    print(f"  Final result: {chain_result.output}")
    
    print("\n[6] Tool Execution with Fallback")
    print("-" * 70)
    
    print("Attempting primary tool with fallbacks...")
    fallback_result = await executor.execute_with_fallback(
        primary_tool="nonexistent_tool",
        fallback_tools=["calculate_sum", "calculate_product"],
        parameters={"a": 7, "b": 8}
    )
    
    if fallback_result.success:
        print(f"  Fallback succeeded: {fallback_result.output}")
        print(f"  Used fallback: {fallback_result.metadata.get('used_fallback')}")
    
    print("\n[7] OpenAI Function Format")
    print("-" * 70)
    
    openai_functions = registry.get_openai_functions()
    print(f"✓ Generated {len(openai_functions)} OpenAI function definitions")
    print("\nExample function definition:")
    print(f"  {openai_functions[0]}")
    
    print("\n[8] Anthropic Tool Format")
    print("-" * 70)
    
    anthropic_tools = registry.get_anthropic_tools()
    print(f"✓ Generated {len(anthropic_tools)} Anthropic tool definitions")
    print("\nExample tool definition:")
    print(f"  {anthropic_tools[0]}")
    
    print("\n[9] Tool Statistics")
    print("-" * 70)
    
    registry_stats = registry.get_statistics()
    print(f"Total Tools: {registry_stats['total_tools']}")
    print(f"Categories: {registry_stats['categories']}")
    
    print("\nTool Usage Statistics:")
    for tool_name, stats in registry_stats['tool_stats'].items():
        if stats['execution_count'] > 0:
            print(f"  {tool_name}:")
            print(f"    Executions: {stats['execution_count']}")
            print(f"    Success Rate: {stats['success_rate']:.1%}")
            print(f"    Avg Time: {stats['avg_execution_time']:.4f}s")
    
    print("\n[10] Executor Statistics")
    print("-" * 70)
    
    executor_stats = executor.get_statistics()
    print(f"Total Executions: {executor_stats['total_executions']}")
    print(f"Success Rate: {executor_stats['success_rate']:.1%}")
    print(f"Tool Usage: {executor_stats['tool_usage']}")
    
    print("\n[11] LLM + Tool Integration Example")
    print("-" * 70)
    
    tool_prompt = PromptTemplate.from_template(
        "You have access to these tools:\n{tools}\n\n"
        "User request: {request}\n\n"
        "Which tool should be called and with what parameters?\n"
        "Respond in JSON format: {{'tool': 'tool_name', 'parameters': {{'param': 'value'}}}}"
    )
    
    tools_description = "\n".join([
        f"- {name}: {registry.get_tool(name).description}"
        for name in registry.get_tool_names()
    ])
    
    user_request = "What's the weather in London?"
    
    prompt = tool_prompt.format(
        tools=tools_description,
        request=user_request
    )
    
    print(f"User Request: {user_request}")
    print("\nGenerated prompt for LLM:")
    print(f"{prompt[:200]}...")
    
    print("\nSimulated LLM response (would call fetch_weather tool):")
    print("  {'tool': 'fetch_weather', 'parameters': {'city': 'London'}}")
    
    simulated_tool_call = {"tool_name": "fetch_weather", "parameters": {"city": "London"}}
    tool_result = await executor.execute(
        simulated_tool_call["tool_name"],
        simulated_tool_call["parameters"]
    )
    
    print(f"\nTool execution result:")
    print(f"  {tool_result.output}")
    
    print("\n" + "=" * 70)
    print("✓ Tool Calling Example Complete")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Tool registration with schemas")
    print("  ✓ Individual tool execution")
    print("  ✓ Parallel batch execution")
    print("  ✓ Sequential chain execution")
    print("  ✓ Fallback mechanisms")
    print("  ✓ OpenAI function format")
    print("  ✓ Anthropic tool format")
    print("  ✓ Tool usage statistics")
    print("  ✓ LLM + Tool integration pattern")


if __name__ == "__main__":
    asyncio.run(main())
