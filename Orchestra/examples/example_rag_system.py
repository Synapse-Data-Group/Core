import asyncio
from orchestra import (
    TextLoader,
    RecursiveChunker,
    InMemoryVectorStore,
    VectorRetriever,
    SimpleEmbedding,
    PromptTemplate,
    LLMConfig,
    LLMProvider,
    LLMManager
)


async def main():
    print("=" * 70)
    print("ORCHESTRA v2.0 - RAG SYSTEM EXAMPLE")
    print("Retrieval-Augmented Generation with Vector Search")
    print("=" * 70)
    
    print("\n[1] Loading Documents")
    print("-" * 70)
    
    sample_docs = [
        "Orchestra is a foundational AI orchestration framework with parallel swarm coordination.",
        "The Parallel Swarm module allows multiple agents to explore tasks simultaneously.",
        "Orchestra integrates CLM for cognitive load monitoring and MEO for memory management.",
        "LangChain alternative features include LLM providers, prompt templates, and RAG.",
        "Vector stores enable semantic search for retrieval-augmented generation.",
    ]
    
    from orchestra.documents.document import Document
    documents = [
        Document(content=doc, metadata={"source": "orchestra_docs", "index": i})
        for i, doc in enumerate(sample_docs)
    ]
    
    print(f"✓ Loaded {len(documents)} documents")
    
    print("\n[2] Chunking Documents")
    print("-" * 70)
    
    chunker = RecursiveChunker(chunk_size=200, chunk_overlap=50)
    chunked_docs = chunker.chunk_documents(documents)
    
    print(f"✓ Created {len(chunked_docs)} chunks")
    for i, chunk in enumerate(chunked_docs[:3]):
        print(f"  Chunk {i}: {chunk.content[:60]}...")
    
    print("\n[3] Creating Embeddings")
    print("-" * 70)
    
    embedding_function = SimpleEmbedding(dimension=384)
    
    embeddings = []
    for doc in chunked_docs:
        embedding = embedding_function.embed_text(doc.content)
        embeddings.append(embedding)
    
    print(f"✓ Generated {len(embeddings)} embeddings")
    print(f"✓ Embedding dimension: {embedding_function.dimension}")
    
    print("\n[4] Building Vector Store")
    print("-" * 70)
    
    vector_store = InMemoryVectorStore()
    doc_ids = vector_store.add_documents(chunked_docs, embeddings)
    
    print(f"✓ Added {len(doc_ids)} documents to vector store")
    print(f"✓ Vector store statistics: {vector_store.get_statistics()}")
    
    print("\n[5] Creating Retriever")
    print("-" * 70)
    
    retriever = VectorRetriever(
        vector_store=vector_store,
        embedding_function=embedding_function,
        score_threshold=0.3
    )
    
    print("✓ Vector retriever created with similarity threshold: 0.3")
    
    print("\n[6] Performing Semantic Search")
    print("-" * 70)
    
    queries = [
        "What is parallel swarm coordination?",
        "How does Orchestra compare to LangChain?",
        "What monitoring capabilities does Orchestra have?"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = retriever.retrieve(query, k=2)
        
        print(f"  Found {len(results)} relevant documents:")
        for i, doc in enumerate(results, 1):
            print(f"    {i}. {doc.content[:80]}...")
    
    print("\n[7] RAG with LLM Integration")
    print("-" * 70)
    
    llm_manager = LLMManager()
    
    ollama_config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model="llama3",
        api_base="http://localhost:11434",
        temperature=0.7,
        max_tokens=300
    )
    
    llm_agent = llm_manager.create_agent(
        "rag_agent",
        ollama_config,
        system_prompt="You are a helpful assistant. Answer questions based on the provided context."
    )
    
    print("✓ LLM agent created for RAG")
    
    rag_template = PromptTemplate.from_template(
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer the question based on the context above. "
        "If the context doesn't contain relevant information, say so."
    )
    
    user_question = "What makes Orchestra different from other frameworks?"
    
    print(f"\nUser Question: {user_question}")
    
    relevant_docs = retriever.retrieve(user_question, k=3)
    context = "\n".join([doc.content for doc in relevant_docs])
    
    print(f"✓ Retrieved {len(relevant_docs)} relevant documents")
    
    rag_prompt = rag_template.format(
        context=context,
        question=user_question
    )
    
    print("\n[8] Generating RAG Response")
    print("-" * 70)
    
    try:
        response = await llm_agent.execute(rag_prompt)
        
        print(f"\nLLM Response:")
        print(f"  {response.content}")
        print(f"\nMetrics:")
        print(f"  Tokens: {response.total_tokens}")
        print(f"  Latency: {response.latency:.2f}s")
        print(f"  Model: {response.model}")
        
    except Exception as e:
        print(f"\n✗ LLM execution failed: {str(e)}")
        print("Note: Make sure Ollama is running: ollama serve")
        print("\nSimulated RAG Response (without LLM):")
        print("  Orchestra is different because it features parallel swarm coordination,")
        print("  cognitive load monitoring, and memory-embedded orchestration.")
    
    print("\n[9] Saving Vector Store")
    print("-" * 70)
    
    vector_store.save("./orchestra_vector_store.json")
    print("✓ Vector store saved to: ./orchestra_vector_store.json")
    
    print("\n[10] RAG System Statistics")
    print("-" * 70)
    stats = vector_store.get_statistics()
    print(f"Total Documents: {stats['total_documents']}")
    print(f"Total Embeddings: {stats['total_embeddings']}")
    print(f"Embedding Dimension: {embedding_function.dimension}")
    
    print("\n" + "=" * 70)
    print("✓ RAG System Example Complete")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Document loading and chunking")
    print("  ✓ Embedding generation")
    print("  ✓ Vector store creation and persistence")
    print("  ✓ Semantic similarity search")
    print("  ✓ Retrieval-augmented generation")
    print("  ✓ LLM integration with context")
    print("  ✓ Complete RAG pipeline")


if __name__ == "__main__":
    asyncio.run(main())
