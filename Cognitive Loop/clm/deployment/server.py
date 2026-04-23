"""
CLM - Cognitive Language Model
deployment/server.py

FastAPI server — deploys CLM as an HTTP API.
Compatible with the OpenAI API interface so existing apps
need zero changes to switch from an LLM to CLM.

Endpoints:
  POST /v1/chat/completions   ← OpenAI-compatible (drop-in replacement)
  POST /v1/perceive           ← Raw signal injection
  GET  /v1/status             ← System state snapshot
  GET  /v1/maturity           ← Developmental maturity report
  POST /v1/perceive/web       ← Trigger web perception
  POST /v1/perceive/feed      ← Add RSS feed
  GET  /v1/memory/insights    ← Semantic memory contents
  DELETE /v1/session          ← Clear session state

Requires: pip install fastapi uvicorn
Both are optional — CLM works without them for local use.
"""

from __future__ import annotations
import time
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clm.clm import CLM


def create_app(clm_instance: "CLM"):
    """
    Create and return a FastAPI app wrapping a CLM instance.
    Called by CLM.serve().
    """
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
    except ImportError:
        raise RuntimeError(
            "FastAPI not installed. Run: pip install fastapi uvicorn"
        )

    app = FastAPI(
        title="CLM — Cognitive Language Model",
        description="A self-developing cognitive AI system. Drop-in OpenAI API replacement.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    clm = clm_instance

    # ── Request/Response models ───────────────────────────────────────────────

    class ChatMessage(BaseModel):
        role:    str
        content: str

    class ChatCompletionRequest(BaseModel):
        messages:    List[ChatMessage]
        model:       Optional[str] = "clm-1"
        max_tokens:  Optional[int] = None
        temperature: Optional[float] = None
        stream:      Optional[bool] = False
        timeout:     Optional[float] = 30.0

    class PerceiveRequest(BaseModel):
        content:  str
        metadata: Optional[Dict[str, Any]] = None
        wait:     bool = True
        timeout:  float = 30.0

    class WebPerceiveRequest(BaseModel):
        url:   Optional[str] = None
        query: Optional[str] = None

    class FeedRequest(BaseModel):
        url: str

    # ── OpenAI-compatible endpoint ────────────────────────────────────────────

    @app.post("/v1/chat/completions")
    async def chat_completions(request: ChatCompletionRequest):
        """
        OpenAI-compatible chat completions endpoint.
        Drop-in replacement — existing apps need zero changes.
        """
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        # Use the last user message as input
        last_user = next(
            (m for m in reversed(request.messages) if m.role == "user"),
            None
        )
        if not last_user:
            raise HTTPException(status_code=400, detail="No user message found")

        start = time.time()
        response_text = clm.chat(
            last_user.content,
            timeout=request.timeout or 30.0,
        )
        elapsed = time.time() - start

        if response_text is None:
            response_text = "I'm still processing. Please try again in a moment."

        # OpenAI-compatible response format
        return {
            "id":      f"clm-{int(time.time())}",
            "object":  "chat.completion",
            "created": int(time.time()),
            "model":   request.model or "clm-1",
            "choices": [{
                "index":         0,
                "message":       {"role": "assistant", "content": response_text},
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens":     len(last_user.content.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens":      len(last_user.content.split()) + len(response_text.split()),
            },
            "clm_metadata": {
                "maturity_score":   clm.maturity_tracker.score,
                "phase":            clm.maturity_tracker.phase.value,
                "confidence":       clm.state.confidence,
                "elapsed_ms":       round(elapsed * 1000, 1),
            },
        }

    # ── CLM-specific endpoints ────────────────────────────────────────────────

    @app.post("/v1/perceive")
    async def perceive(request: PerceiveRequest):
        """Inject a raw signal into the cognitive system."""
        if request.wait:
            response = clm.chat(request.content, timeout=request.timeout)
            return {"response": response, "state": clm.state.snapshot()}
        else:
            signal_id = clm.loop.perceive(request.content, request.metadata)
            return {"signal_id": signal_id, "status": "queued"}

    @app.get("/v1/status")
    async def status():
        """Full system state snapshot."""
        return {
            "status":   "running" if clm.loop._running else "stopped",
            "state":    clm.state.snapshot(),
            "maturity": clm.maturity_tracker.get_stats(),
            "network":  clm.network.get_stats(),
        }

    @app.get("/v1/maturity")
    async def maturity():
        """Developmental maturity report."""
        return clm.maturity_tracker.get_stats()

    @app.post("/v1/perceive/web")
    async def perceive_web(request: WebPerceiveRequest):
        """Trigger web perception (URL fetch or search)."""
        if not clm.web_perception:
            raise HTTPException(status_code=503, detail="Web perception not enabled")

        phase_cfg = clm.maturity_tracker.phase_config
        if not phase_cfg.web_browsing_allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Web browsing not allowed in {clm.maturity_tracker.phase.value} phase"
            )

        signals_injected = 0
        if request.url:
            for signal in clm.web_perception.perceive(request.url):
                clm.state.push_input(signal)
                signals_injected += 1
        elif request.query:
            for signal in clm.web_perception.search_and_perceive(request.query, max_results=3):
                clm.state.push_input(signal)
                signals_injected += 1

        return {"signals_injected": signals_injected, "status": "queued"}

    @app.post("/v1/perceive/feed")
    async def add_feed(request: FeedRequest):
        """Add an RSS/Atom feed for continuous learning."""
        if not clm.feed_perception:
            raise HTTPException(status_code=503, detail="Feed perception not enabled")
        clm.feed_perception.add_feed(request.url)
        return {"status": "added", "url": request.url}

    @app.get("/v1/memory/insights")
    async def memory_insights(k: int = 20):
        """Return recent semantic memory insights."""
        insights = clm.semantic_memory.get_recent_insights(k=k)
        return {
            "count":    clm.semantic_memory.count(),
            "insights": insights,
        }

    @app.delete("/v1/session")
    async def clear_session():
        """Clear session state between conversations."""
        clm.state.clear_session()
        return {"status": "cleared"}

    @app.get("/health")
    async def health():
        return {"status": "ok", "phase": clm.maturity_tracker.phase.value}

    return app


def serve(clm_instance: "CLM", host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the CLM server."""
    try:
        import uvicorn
    except ImportError:
        raise RuntimeError("uvicorn not installed. Run: pip install uvicorn")

    app = create_app(clm_instance)
    logger.info(f"Starting CLM server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, reload=reload)
