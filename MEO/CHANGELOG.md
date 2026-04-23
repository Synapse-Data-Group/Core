# Changelog

All notable changes to MEO (Memory Embedded Orchestration) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-07

### Added
- Initial release of MEO (Memory Embedded Orchestration)
- Core memory module with episodic and semantic memory
- Evaluation system with configurable reward functions
- Meta-policy adaptation with rule-based and learning-based adapters
- WisdomOrchestrator main class for wrapping any agent framework
- Hook system for intercepting tool calls, agent calls, and planning
- Storage backends: JSONL and SQLite
- LangChain integration wrapper
- Autogen integration wrapper
- Utility modules for encoding and logging
- Comprehensive documentation (README, QUICKSTART, STRUCTURE)
- Working examples for basic usage, LangChain, Autogen, and custom components
- Test suite covering all major components
- Apache 2.0 license with patent grant

### Features
- Framework-agnostic orchestration layer
- Persistent memory across workflow runs
- Automatic pattern recognition and learning
- Configurable evaluation metrics
- Policy-guided decision making
- Minimal dependencies for easy adoption
- Extensible architecture with clear ABCs

---

© 2026 Synapse Data / Ivan Lluch
