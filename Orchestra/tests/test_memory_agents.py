import pytest
from orchestra.agent_memory import (
    EmbeddedMemory,
    MemoryType,
    MemoryCache,
    CacheStrategy,
    MemoryAwareAgent
)


class TestEmbeddedMemory:
    def test_memory_storage(self):
        memory = EmbeddedMemory("test_agent")
        
        memory.store(
            MemoryType.EPISODIC,
            "Test event occurred",
            {"timestamp": 123},
            {"importance": "high"}
        )
        
        entries = memory.retrieve(MemoryType.EPISODIC, {}, k=5)
        
        assert len(entries) == 1
        assert entries[0].content == "Test event occurred"
    
    def test_memory_types(self):
        memory = EmbeddedMemory("test_agent")
        
        memory.store(MemoryType.EPISODIC, "Event 1", {}, {})
        memory.store(MemoryType.SEMANTIC, "Fact 1", {}, {})
        memory.store(MemoryType.PROCEDURAL, "Skill 1", {}, {})
        memory.store(MemoryType.WORKING, "Current 1", {}, {})
        
        assert len(memory.retrieve(MemoryType.EPISODIC, {}, k=10)) == 1
        assert len(memory.retrieve(MemoryType.SEMANTIC, {}, k=10)) == 1
        assert len(memory.retrieve(MemoryType.PROCEDURAL, {}, k=10)) == 1
        assert len(memory.retrieve(MemoryType.WORKING, {}, k=10)) == 1
    
    def test_memory_consolidation(self):
        memory = EmbeddedMemory("test_agent", capacity={
            MemoryType.EPISODIC: 5
        })
        
        for i in range(10):
            memory.store(MemoryType.EPISODIC, f"Event {i}", {}, {"importance": i})
        
        memory.consolidate()
        
        entries = memory.retrieve(MemoryType.EPISODIC, {}, k=10)
        assert len(entries) <= 5


class TestMemoryCache:
    def test_lru_cache(self):
        cache = MemoryCache(strategy=CacheStrategy.LRU, capacity=3)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        assert cache.get("key1") == "value1"
        
        cache.put("key4", "value4")
        
        # key2 should be evicted (least recently used)
        assert cache.get("key2") is None
    
    def test_lfu_cache(self):
        cache = MemoryCache(strategy=CacheStrategy.LFU, capacity=2)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        cache.get("key1")
        cache.get("key1")
        cache.get("key2")
        
        cache.put("key3", "value3")
        
        # key2 should be evicted (least frequently used)
        assert cache.get("key1") == "value1"
    
    def test_ttl_cache(self):
        import time
        
        cache = MemoryCache(strategy=CacheStrategy.TTL, ttl_seconds=0.1)
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        time.sleep(0.15)
        
        assert cache.get("key1") is None


class TestMemoryAwareAgent:
    @pytest.mark.asyncio
    async def test_cache_hit(self):
        def executor(task, context):
            return {"result": "computed", "task_id": task.get("id")}
        
        memory = EmbeddedMemory("cached_agent")
        agent = MemoryAwareAgent(
            "cached_agent",
            executor,
            memory,
            cache_strategy=CacheStrategy.LRU
        )
        
        task1 = {"id": "task1", "query": "test"}
        
        # First execution - cache miss
        result1 = await agent.execute(task1, {})
        assert result1["result"] == "computed"
        
        # Second execution - cache hit
        result2 = await agent.execute(task1, {})
        assert result2["result"] == "computed"
        
        stats = agent.get_statistics()
        assert stats["cache_hits"] >= 1
    
    @pytest.mark.asyncio
    async def test_memory_learning(self):
        def executor(task, context):
            return {"learned": True}
        
        memory = EmbeddedMemory("learning_agent")
        agent = MemoryAwareAgent("learning_agent", executor, memory)
        
        task = {"id": "learn_task", "content": "Learn this"}
        
        await agent.execute(task, {})
        
        # Check if memory was stored
        episodic = memory.retrieve(MemoryType.EPISODIC, {}, k=5)
        assert len(episodic) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
