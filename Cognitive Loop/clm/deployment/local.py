"""
CLM - Cognitive Language Model
deployment/local.py

Local CLI interface — run CLM interactively in the terminal.
No server needed. Direct conversation with the cognitive system.
"""

from __future__ import annotations
import sys
import time
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clm.clm import CLM

logger = logging.getLogger(__name__)


def run_cli(clm_instance: "CLM"):
    """
    Interactive CLI session with CLM.
    Type messages, receive responses.
    Commands: /status /maturity /memory /web <url> /search <query> /quit
    """
    clm = clm_instance

    print("\n" + "=" * 60)
    print("  CLM — Cognitive Language Model")
    print(f"  Phase: {clm.maturity_tracker.phase.value.upper()}")
    print(f"  Maturity: {clm.maturity_tracker.score:.1%}")
    print("  Commands: /status /maturity /memory /web <url> /search <query> /quit")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nShutting down CLM...")
            clm.stop()
            break

        if not user_input:
            continue

        # ── Commands ──────────────────────────────────────────────────────────
        if user_input.startswith("/"):
            _handle_command(clm, user_input)
            continue

        # ── Normal conversation ───────────────────────────────────────────────
        print("CLM: ", end="", flush=True)
        start = time.time()
        response = clm.chat(user_input, timeout=30.0)
        elapsed = time.time() - start

        if response:
            print(response)
        else:
            print("[No response formed — still processing]")

        print(
            f"  [phase={clm.maturity_tracker.phase.value} "
            f"maturity={clm.maturity_tracker.score:.1%} "
            f"confidence={clm.state.confidence:.1%} "
            f"elapsed={elapsed:.1f}s]\n"
        )


def _handle_command(clm: "CLM", cmd: str):
    parts = cmd.split(maxsplit=1)
    command = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if command == "/quit" or command == "/exit":
        print("Shutting down CLM...")
        clm.stop()
        sys.exit(0)

    elif command == "/status":
        snap = clm.state.snapshot()
        print("\n── System Status ──")
        for k, v in snap.items():
            print(f"  {k}: {v}")
        print()

    elif command == "/maturity":
        stats = clm.maturity_tracker.get_stats()
        print("\n── Maturity Report ──")
        print(f"  Score:   {stats['maturity_score']:.1%}")
        print(f"  Phase:   {stats['phase']}")
        print(f"  LLM dep: {stats['llm_dependency_ratio']:.1%}")
        print(f"  Episodes: {stats['episode_count']}")
        print(f"  Insights: {stats['insight_count']}")
        print(f"  Neurons:  {stats['neuron_count']}")
        prog = stats.get("milestone_progress", {})
        if not prog.get("complete"):
            print(f"\n  → Next phase: {prog.get('next_phase', 'N/A')}")
            for metric, vals in prog.items():
                if isinstance(vals, dict) and "pct" in vals:
                    bar = "█" * (vals["pct"] // 10) + "░" * (10 - vals["pct"] // 10)
                    print(f"    {metric}: [{bar}] {vals['pct']}%")
        print()

    elif command == "/memory":
        insights = clm.semantic_memory.get_recent_insights(k=10)
        print(f"\n── Semantic Memory ({clm.semantic_memory.count()} total insights) ──")
        for ins in insights:
            conf = ins.get("confidence", 0)
            content = ins.get("content", "")
            print(f"  [{conf:.0%}] {content}")
        print()

    elif command == "/web":
        if not arg:
            print("Usage: /web <url>")
            return
        if not clm.web_perception:
            print("Web perception not enabled.")
            return
        phase_cfg = clm.maturity_tracker.phase_config
        if not phase_cfg.web_browsing_allowed:
            print(f"Web browsing not allowed in {clm.maturity_tracker.phase.value} phase.")
            return
        print(f"Fetching {arg}...")
        count = 0
        for signal in clm.web_perception.perceive(arg):
            clm.state.push_input(signal)
            count += 1
        print(f"Injected {count} signals from {arg}\n")

    elif command == "/search":
        if not arg:
            print("Usage: /search <query>")
            return
        if not clm.web_perception:
            print("Web perception not enabled.")
            return
        phase_cfg = clm.maturity_tracker.phase_config
        if not phase_cfg.web_browsing_allowed:
            print(f"Web browsing not allowed in {clm.maturity_tracker.phase.value} phase.")
            return
        print(f"Searching: {arg}...")
        count = 0
        for signal in clm.web_perception.search_and_perceive(arg, max_results=3):
            clm.state.push_input(signal)
            count += 1
        print(f"Injected {count} signals from search\n")

    elif command == "/network":
        stats = clm.network.get_stats()
        print("\n── Network Stats ──")
        for k, v in stats.items():
            print(f"  {k}: {v}")
        print()

    else:
        print(f"Unknown command: {command}")
        print("Commands: /status /maturity /memory /web <url> /search <query> /network /quit\n")
