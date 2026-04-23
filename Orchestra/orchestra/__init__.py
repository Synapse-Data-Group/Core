from .orchestrator import Orchestra
from .tree_orchestrator import TreeOrchestrator, DecisionNode
from .chain_of_thought import ChainOfThought, ReasoningStep
from .parallel_swarm import ParallelSwarm, SwarmAgent, ConsensusStrategy
from .integration import IntegrationLayer

from .llm import (
    LLMAgent,
    LLMResponse,
    LLMConfig,
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
    HuggingFaceProvider,
    LLMManager,
)

from .prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    FewShotPromptTemplate,
    OutputParser,
    JSONParser,
    StructuredParser,
    ListParser,
)

from .tools import (
    Tool,
    ToolResult,
    ToolSchema,
    ToolRegistry,
    ToolExecutor,
)

from .documents import (
    Document,
    DocumentLoader,
    TextLoader,
    JSONLoader,
    CSVLoader,
    PDFLoader,
    TextChunker,
    RecursiveChunker,
    SemanticChunker,
)

from .rag import (
    VectorStore,
    InMemoryVectorStore,
    Retriever,
    VectorRetriever,
    HybridRetriever,
    EmbeddingFunction,
    SimpleEmbedding,
)

from .agent_memory import (
    EmbeddedMemory,
    MemoryEntry,
    MemoryType,
    MemoryAwareAgent,
    MemoryCache,
    CacheStrategy,
)

from .multimodal import (
    VisionProvider,
    ImageInput,
    VisionResponse,
    AudioProvider,
    AudioInput,
    AudioResponse,
    TTSProvider,
    MultimodalAgent,
)

from .agents import (
    AutonomousAgent,
    Goal,
    Plan,
    Action,
    AgentState,
    CollaborationPattern,
    AgentTeam,
    MessageBus,
    AgentMessage,
)

from .wisdom import (
    WisdomLayer,
    WisdomPattern,
    PatternType,
    MetaLearner,
    MetaKnowledge,
    PatternExtractor,
    TaskPattern,
)

from .advanced_cot import (
    SelfVerifyingCoT,
    BacktrackingCoT,
    ReasoningPath,
    VerificationResult,
)

from .semantic import (
    TaskSimilarity,
    SimilarityMethod,
    TFIDFVectorizer,
    MinHasher,
    LSHIndex,
)

from .capability import (
    CapabilityDiscovery,
    AgentCapability,
    CapabilityProfile,
    CapabilityMatcher,
)

from .reinforcement import (
    QLearningRouter,
    QState,
    QAction,
    RoutingOptimizer,
)

__version__ = "4.0.0"
__all__ = [
    "Orchestra",
    "TreeOrchestrator",
    "DecisionNode",
    "ChainOfThought",
    "ReasoningStep",
    "ParallelSwarm",
    "SwarmAgent",
    "ConsensusStrategy",
    "IntegrationLayer",
    "LLMAgent",
    "LLMResponse",
    "LLMConfig",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "HuggingFaceProvider",
    "LLMManager",
    "PromptTemplate",
    "ChatPromptTemplate",
    "FewShotPromptTemplate",
    "OutputParser",
    "JSONParser",
    "StructuredParser",
    "ListParser",
    "Tool",
    "ToolResult",
    "ToolSchema",
    "ToolRegistry",
    "ToolExecutor",
    "Document",
    "DocumentLoader",
    "TextLoader",
    "JSONLoader",
    "CSVLoader",
    "PDFLoader",
    "TextChunker",
    "RecursiveChunker",
    "SemanticChunker",
    "VectorStore",
    "InMemoryVectorStore",
    "Retriever",
    "VectorRetriever",
    "HybridRetriever",
    "EmbeddingFunction",
    "SimpleEmbedding",
    "EmbeddedMemory",
    "MemoryEntry",
    "MemoryType",
    "MemoryAwareAgent",
    "MemoryCache",
    "CacheStrategy",
    "VisionProvider",
    "ImageInput",
    "VisionResponse",
    "AudioProvider",
    "AudioInput",
    "AudioResponse",
    "TTSProvider",
    "MultimodalAgent",
    "AutonomousAgent",
    "Goal",
    "Plan",
    "Action",
    "AgentState",
    "CollaborationPattern",
    "AgentTeam",
    "MessageBus",
    "AgentMessage",
    "WisdomLayer",
    "WisdomPattern",
    "PatternType",
    "MetaLearner",
    "MetaKnowledge",
    "PatternExtractor",
    "TaskPattern",
    "SelfVerifyingCoT",
    "BacktrackingCoT",
    "ReasoningPath",
    "VerificationResult",
    "TaskSimilarity",
    "SimilarityMethod",
    "TFIDFVectorizer",
    "MinHasher",
    "LSHIndex",
    "CapabilityDiscovery",
    "AgentCapability",
    "CapabilityProfile",
    "CapabilityMatcher",
    "QLearningRouter",
    "QState",
    "QAction",
    "RoutingOptimizer",
]
