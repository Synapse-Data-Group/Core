"""
CLM - Cognitive Language Model
perception/document.py

Document perception — reads local files as cognitive input.
Supports: .txt, .md, .json, .csv, .html
Pure stdlib only.
"""

from __future__ import annotations
import csv
import html.parser
import io
import json
import os
import re
from typing import Any, Dict, Iterator, List, Optional

from clm.perception.base import PerceptionSource, PerceptionSourceType, PerceptionConfig
from clm.core.signal import CognitiveSignal, SignalType, SignalOrigin


class DocumentPerception(PerceptionSource):
    """Reads local documents and yields CognitiveSignal objects."""

    def __init__(self, config: Optional[PerceptionConfig] = None, chunk_size: int = 600):
        super().__init__(config)
        self.source_type = PerceptionSourceType.DOCUMENT
        self.chunk_size  = chunk_size

    def perceive(self, input_data: Any) -> Iterator[CognitiveSignal]:
        """input_data: str (file path)"""
        if not self.is_allowed():
            return

        path = str(input_data).strip()
        if not os.path.exists(path):
            return

        ext  = os.path.splitext(path)[1].lower()
        text = self._read(path, ext)
        if not text:
            return

        chunks = self._chunk(text)
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 20:
                continue
            self.total_signals += 1
            yield CognitiveSignal(
                signal_type=SignalType.PERCEPTUAL,
                origin=SignalOrigin.EXTERNAL,
                content=chunk,
                strength=0.7,
                confidence=0.8,
                metadata={
                    "file_path":    path,
                    "chunk_index":  i,
                    "total_chunks": len(chunks),
                    "perception":   "document",
                },
            )

    def _read(self, path: str, ext: str) -> str:
        try:
            if ext in (".txt", ".md"):
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    return f.read(self.config.max_content_length)
            elif ext == ".json":
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return json.dumps(data, indent=2)[:self.config.max_content_length]
            elif ext == ".csv":
                rows = []
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        rows.append(", ".join(row))
                        if len("\n".join(rows)) > self.config.max_content_length:
                            break
                return "\n".join(rows)
            elif ext in (".html", ".htm"):
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    raw = f.read(self.config.max_content_length)
                return re.sub(r"<[^>]+>", " ", raw)
            else:
                # Try plain text for unknown extensions
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    return f.read(self.config.max_content_length)
        except Exception:
            return ""

    def _chunk(self, text: str) -> List[str]:
        sentences = re.split(r"(?<=[.!?\n])\s+", text)
        chunks, current, current_len = [], [], 0
        for s in sentences:
            if current_len + len(s) > self.chunk_size and current:
                chunks.append(" ".join(current))
                current, current_len = [s], len(s)
            else:
                current.append(s)
                current_len += len(s)
        if current:
            chunks.append(" ".join(current))
        return chunks
