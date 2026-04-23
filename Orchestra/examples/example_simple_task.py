import asyncio
from orchestra import Orchestra


async def step_1_analyze(context):
    print("Step 1: Analyzing task...")
    task_data = context["context"]["task"]
    return {"analysis": f"Analyzed: {task_data.get('description', 'N/A')}"}


async def step_2_process(context):
    print("Step 2: Processing based on analysis...")
    analysis = context.get("step_1", {})
    return {"processed": True, "details": analysis}


async def step_3_finalize(context):
    print("Step 3: Finalizing results...")
    processed = context.get("step_2", {})
    return {"final_result": "Task completed successfully", "data": processed}


async def main():
    print("=" * 60)
    print("Example 1: Simple Task with Tree + Chain-of-Thought")
    print("=" * 60)
    
    orchestra = Orchestra()
    
    chain = orchestra.create_chain("simple_task_chain")
    
    chain.add_step(
        step_id="step_1",
        description="Analyze the task requirements",
        executor=step_1_analyze
    )
    
    chain.add_step(
        step_id="step_2",
        description="Process the analyzed data",
        executor=step_2_process,
        dependencies=["step_1"]
    )
    
    chain.add_step(
        step_id="step_3",
        description="Finalize and return results",
        executor=step_3_finalize,
        dependencies=["step_2"]
    )
    
    task = {
        "id": "task_001",
        "description": "Process a simple data transformation",
        "complexity": "simple",
        "chain_id": "simple_task_chain"
    }
    
    print("\n[Executing Task]")
    result = await orchestra.execute(task)
    
    print("\n[Execution Results]")
    print(f"Task Type: {result['routing']['task_type']}")
    print(f"Execution Mode: {result['routing']['execution_mode']}")
    print(f"Routing Path: {result['routing']['path']}")
    print(f"Final Output: {result['output']}")
    
    print("\n[Cognitive Load Report]")
    chain_report = chain.get_cognitive_load_report()
    print(f"Total Cognitive Load: {chain_report['total_load']:.3f}")
    print(f"Average Load per Step: {chain_report['average_load']:.3f}")
    
    print("\n[Step-by-Step Execution Log]")
    for log_entry in result['output']['execution_log']:
        print(f"  - {log_entry['step_id']}: {log_entry['status']} "
              f"(time: {log_entry['execution_time']:.3f}s, "
              f"load: {log_entry['cognitive_load']:.3f})")
    
    print("\n[Intermediate Outputs]")
    intermediate = chain.get_intermediate_outputs()
    for step_id, output in intermediate.items():
        print(f"  {step_id}: {output}")


if __name__ == "__main__":
    asyncio.run(main())
