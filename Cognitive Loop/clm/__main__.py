"""
CLM — Cognitive Language Model
__main__.py

Entry point for `python -m clm` and `clm` CLI command.

Usage:
    python -m clm                          # Interactive CLI (Ollama default)
    python -m clm --serve                  # HTTP server on :8000
    python -m clm --provider openai        # Use OpenAI for grounding
    python -m clm --serve --port 8080      # Custom port
    python -m clm --status                 # Print status and exit
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="clm",
        description="CLM — Cognitive Language Model. A self-developing cognitive AI.",
    )
    parser.add_argument(
        "--serve", action="store_true",
        help="Start as HTTP server (OpenAI-compatible API)"
    )
    parser.add_argument(
        "--host", default="0.0.0.0",
        help="Server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--provider", default="ollama",
        choices=["ollama", "openai", "anthropic", "none"],
        help="LLM provider for grounding (default: ollama)"
    )
    parser.add_argument(
        "--model", default=None,
        help="LLM model override"
    )
    parser.add_argument(
        "--api-key", default=None,
        help="API key for OpenAI/Anthropic (or set OPENAI_API_KEY / ANTHROPIC_API_KEY env var)"
    )
    parser.add_argument(
        "--ollama-url", default="http://localhost:11434",
        help="Ollama base URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--ollama-model", default="llama3.2",
        help="Ollama model name (default: llama3.2)"
    )
    parser.add_argument(
        "--data-dir", default="./clm_data",
        help="Directory for persistent state (default: ./clm_data)"
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Print system status and exit"
    )
    parser.add_argument(
        "--log-level", default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: WARNING)"
    )

    args = parser.parse_args()

    # Resolve API key from env if not provided
    api_key = args.api_key
    if api_key is None:
        if args.provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
        elif args.provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY")

    # Build config
    from clm.config import CLMConfig, LLMConfig, MemoryConfig

    if args.provider == "none":
        config = CLMConfig.sovereign()
    else:
        config = CLMConfig()
        config.llm.provider        = args.provider
        config.llm.api_key         = api_key
        config.llm.ollama_base_url = args.ollama_url
        config.llm.ollama_model    = args.ollama_model
        if args.model:
            config.llm.model = args.model

    config.memory.storage_dir = args.data_dir
    config.log_level          = args.log_level

    # Create CLM instance
    from clm.clm import CLM
    clm = CLM(config)

    if args.status:
        import json
        clm.start()
        print(json.dumps(clm.status(), indent=2, default=str))
        clm.stop()
        return

    if args.serve:
        print(f"Starting CLM server on {args.host}:{args.port}")
        print(f"OpenAI-compatible API: http://{args.host}:{args.port}/v1/chat/completions")
        print(f"Phase: {clm.maturity_tracker.phase.value} | Maturity: {clm.maturity_tracker.score:.1%}")
        clm.serve(host=args.host, port=args.port)
    else:
        clm.cli()


if __name__ == "__main__":
    main()
