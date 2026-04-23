import asyncio
import os
from orchestra.multimodal import VisionProvider, ImageInput, MultimodalAgent


async def main():
    print("=" * 70)
    print("ORCHESTRA v3.0 - MULTIMODAL VISION EXAMPLE")
    print("GPT-4V and Claude 3 Vision Capabilities")
    print("=" * 70)
    
    print("\n[1] Creating Vision Providers")
    print("-" * 70)
    
    gpt4v = VisionProvider(
        provider="openai",
        model="gpt-4-vision-preview",
        api_key=os.getenv("OPENAI_API_KEY", "your-key-here"),
        max_tokens=500
    )
    print("✓ GPT-4V provider created")
    
    claude3_vision = VisionProvider(
        provider="anthropic",
        model="claude-3-opus-20240229",
        api_key=os.getenv("ANTHROPIC_API_KEY", "your-key-here"),
        max_tokens=500
    )
    print("✓ Claude 3 Opus vision provider created")
    
    print("\n[2] Analyzing Image from URL")
    print("-" * 70)
    
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    
    image = ImageInput.from_url(image_url, detail="high")
    
    prompt = "Describe this image in detail. What do you see?"
    
    print(f"Prompt: {prompt}")
    print(f"Image: {image_url[:60]}...")
    
    try:
        print("\nAnalyzing with GPT-4V...")
        gpt4v_response = await gpt4v.analyze_image(prompt, [image])
        
        print(f"\nGPT-4V Response:")
        print(f"  {gpt4v_response.content[:200]}...")
        print(f"  Tokens: {gpt4v_response.total_tokens}")
        print(f"  Latency: {gpt4v_response.latency:.2f}s")
        print(f"  Images processed: {gpt4v_response.images_processed}")
    
    except Exception as e:
        print(f"✗ GPT-4V error: {str(e)}")
        print("Note: Set OPENAI_API_KEY environment variable")
    
    try:
        print("\nAnalyzing with Claude 3 Opus...")
        claude_response = await claude3_vision.analyze_image(prompt, [image])
        
        print(f"\nClaude 3 Response:")
        print(f"  {claude_response.content[:200]}...")
        print(f"  Tokens: {claude_response.total_tokens}")
        print(f"  Latency: {claude_response.latency:.2f}s")
        print(f"  Images processed: {claude_response.images_processed}")
    
    except Exception as e:
        print(f"✗ Claude 3 error: {str(e)}")
        print("Note: Set ANTHROPIC_API_KEY environment variable")
    
    print("\n[3] Analyzing Local Image")
    print("-" * 70)
    
    print("Example with local image file:")
    print("  image = ImageInput.from_path('./my_image.jpg', detail='high')")
    print("  response = await vision_provider.analyze_image(prompt, [image])")
    
    print("\n[4] Multi-Image Analysis")
    print("-" * 70)
    
    print("Example analyzing multiple images:")
    print("  images = [")
    print("    ImageInput.from_url('https://example.com/image1.jpg'),")
    print("    ImageInput.from_url('https://example.com/image2.jpg'),")
    print("    ImageInput.from_path('./local_image.jpg')")
    print("  ]")
    print("  prompt = 'Compare these images and describe the differences'")
    print("  response = await vision_provider.analyze_image(prompt, images)")
    
    print("\n[5] Creating Multimodal Agent")
    print("-" * 70)
    
    multimodal_agent = MultimodalAgent(
        agent_id="vision_agent",
        vision_provider=gpt4v
    )
    
    print("✓ Multimodal agent created with vision capabilities")
    
    vision_task = {
        "modality": "vision",
        "prompt": "What objects can you identify in this image?",
        "images": [image_url]
    }
    
    try:
        print("\nExecuting vision task through multimodal agent...")
        result = await multimodal_agent.execute(vision_task)
        
        print(f"\nAgent Result:")
        print(f"  Modality: {result['modality']}")
        print(f"  Response: {result['result'][:150]}...")
        print(f"  Images processed: {result['images_processed']}")
        print(f"  Latency: {result['latency']:.2f}s")
    
    except Exception as e:
        print(f"✗ Agent execution error: {str(e)}")
    
    print("\n[6] Use Cases for Vision Models")
    print("-" * 70)
    
    print("\n📸 Image Understanding:")
    print("  - Object detection and identification")
    print("  - Scene description and analysis")
    print("  - Text extraction (OCR)")
    print("  - Image classification")
    
    print("\n🎨 Creative Analysis:")
    print("  - Art and design critique")
    print("  - Style identification")
    print("  - Color palette extraction")
    print("  - Composition analysis")
    
    print("\n🏥 Specialized Domains:")
    print("  - Medical image analysis")
    print("  - Satellite imagery interpretation")
    print("  - Document processing")
    print("  - Quality control inspection")
    
    print("\n🤖 Agent Applications:")
    print("  - Visual question answering")
    print("  - Image-based decision making")
    print("  - Multi-modal reasoning")
    print("  - Visual grounding for actions")
    
    print("\n" + "=" * 70)
    print("✓ Multimodal Vision Example Complete")
    print("=" * 70)
    
    print("\nKey Features:")
    print("  ✓ GPT-4V and Claude 3 vision support")
    print("  ✓ URL and local file image input")
    print("  ✓ Multi-image analysis")
    print("  ✓ Detail level control (low/high/auto)")
    print("  ✓ Integrated with multimodal agents")
    print("  ✓ Token and latency tracking")


if __name__ == "__main__":
    asyncio.run(main())
