"""
CLM - Cognitive Language Model
perception/web.py

Sovereign web perception — pure Python stdlib only.
No requests, no httpx, no BeautifulSoup, no Scrapy.
urllib.request + html.parser only.

The system can browse the web to learn, just like a person reads.
Gated by developmental phase — infant systems don't browse autonomously.

Sovereignty principles:
- No search API keys (Google, Bing, Serper, etc.)
- No third-party HTTP libraries
- No cloud scraping services
- Direct HTTP fetch + HTML parsing only
- Robots.txt respected (ethical crawling)
"""

from __future__ import annotations
import html
import html.parser
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import logging
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

from clm.perception.base import PerceptionSource, PerceptionSourceType, PerceptionConfig
from clm.core.signal import CognitiveSignal, SignalType, SignalOrigin

logger = logging.getLogger(__name__)

_DEFAULT_USER_AGENT = (
    "CLM-Cognitive/1.0 (Cognitive Language Model; "
    "educational/research; +https://github.com/synapse-data/clm)"
)
_FETCH_TIMEOUT    = 10    # seconds
_MAX_PAGE_BYTES   = 500_000   # 500KB max per page
_MIN_TEXT_LENGTH  = 50        # Ignore pages with less content


class _TextExtractor(html.parser.HTMLParser):
    """
    Pure stdlib HTML → plain text extractor.
    Strips scripts, styles, nav, footer, ads.
    Extracts meaningful body text only.
    """

    _SKIP_TAGS = {
        "script", "style", "noscript", "nav", "footer", "header",
        "aside", "form", "button", "input", "select", "option",
        "iframe", "embed", "object", "svg", "canvas", "meta", "link",
    }
    _BLOCK_TAGS = {
        "p", "div", "section", "article", "main", "h1", "h2", "h3",
        "h4", "h5", "h6", "li", "td", "th", "blockquote", "pre", "br",
    }

    def __init__(self):
        super().__init__()
        self._skip_depth  = 0
        self._chunks: List[str] = []
        self._current: List[str] = []
        self.title: str = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs):
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag in self._BLOCK_TAGS and self._current:
            text = " ".join(self._current).strip()
            if text:
                self._chunks.append(text)
            self._current = []

    def handle_endtag(self, tag: str):
        if tag in self._SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
        if tag == "title":
            self._in_title = False
        if tag in self._BLOCK_TAGS and self._current:
            text = " ".join(self._current).strip()
            if text:
                self._chunks.append(text)
            self._current = []

    def handle_data(self, data: str):
        if self._skip_depth > 0:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title += text
            return
        self._current.append(text)

    def get_text(self) -> str:
        if self._current:
            text = " ".join(self._current).strip()
            if text:
                self._chunks.append(text)
            self._current = []
        raw = " ".join(self._chunks)
        raw = html.unescape(raw)
        raw = re.sub(r"\s+", " ", raw)
        return raw.strip()


class _RobotsCache:
    """Cache robots.txt parsers per domain."""
    def __init__(self):
        self._cache: Dict[str, urllib.robotparser.RobotFileParser] = {}

    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        try:
            parsed = urllib.parse.urlparse(url)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            if domain not in self._cache:
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(f"{domain}/robots.txt")
                try:
                    rp.read()
                except Exception:
                    # If robots.txt unreachable, assume allowed
                    self._cache[domain] = None
                    return True
                self._cache[domain] = rp
            rp = self._cache[domain]
            if rp is None:
                return True
            return rp.can_fetch(user_agent, url)
        except Exception:
            return True  # Default allow on error


_robots_cache = _RobotsCache()


class WebPerception(PerceptionSource):
    """
    Sovereign web perception.

    Fetches web pages and converts them to CognitiveSignal objects.
    The system learns from web content the same way it learns from
    conversations — through the cognitive loop.

    Gated by developmental phase:
      INFANCY    → disabled (too much noise)
      ADOLESCENT → requires_approval=True (user approves URLs)
      MATURE     → autonomous within allowed_domains
      SOVEREIGN  → fully autonomous
    """

    def __init__(
        self,
        config: Optional[PerceptionConfig] = None,
        user_agent: str = _DEFAULT_USER_AGENT,
        chunk_size: int = 500,    # chars per signal chunk
    ):
        super().__init__(config)
        self.source_type = PerceptionSourceType.WEB
        self.user_agent  = user_agent
        self.chunk_size  = chunk_size
        self._visited: Set[str] = set()

    def perceive(self, input_data: Any) -> Iterator[CognitiveSignal]:
        """
        Fetch a URL and yield CognitiveSignal objects from its content.

        input_data: str (URL) or dict {"url": str, "depth": int}
        """
        if not self.is_allowed():
            return

        if not self._check_rate_limit():
            logger.warning("Web perception rate limit reached")
            return

        url = input_data if isinstance(input_data, str) else input_data.get("url", "")
        if not url:
            return

        url = self._normalize_url(url)
        if not url:
            return

        # Domain filter
        if not self._is_domain_allowed(url):
            logger.debug(f"Domain blocked: {url}")
            return

        # Dedup
        if url in self._visited:
            return
        self._visited.add(url)

        # Robots.txt check
        if not _robots_cache.can_fetch(url, self.user_agent):
            logger.debug(f"Robots.txt disallows: {url}")
            return

        # Fetch
        title, text, fetch_meta = self._fetch(url)
        if not text or len(text) < _MIN_TEXT_LENGTH:
            return

        # Yield title as first signal
        if title:
            yield self._make_signal(
                content=f"Page title: {title}",
                url=url,
                chunk_index=0,
                total_chunks=1,
                meta=fetch_meta,
                strength=0.9,
            )

        # Chunk body text into signals
        chunks = self._chunk_text(text)
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 20:
                continue
            self.total_signals += 1
            yield self._make_signal(
                content=chunk,
                url=url,
                chunk_index=i + 1,
                total_chunks=len(chunks),
                meta=fetch_meta,
                strength=0.7,
            )

    def fetch_text(self, url: str) -> Tuple[str, str, Dict[str, Any]]:
        """Public method: fetch URL and return (title, text, meta)."""
        url = self._normalize_url(url)
        if not url:
            return "", "", {}
        return self._fetch(url)

    def search_and_perceive(
        self, query: str, max_results: int = 3
    ) -> Iterator[CognitiveSignal]:
        """
        Sovereign search: uses DuckDuckGo HTML (no API key needed).
        Fetches search results page and extracts result URLs,
        then fetches each result.
        """
        if not self.is_allowed():
            return

        urls = self._ddg_search(query, max_results)
        for url in urls:
            yield from self.perceive(url)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _fetch(self, url: str) -> Tuple[str, str, Dict[str, Any]]:
        """Fetch URL using urllib. Returns (title, text, metadata)."""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent":      self.user_agent,
                    "Accept":          "text/html,application/xhtml+xml",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "identity",
                    "Connection":      "close",
                },
            )
            with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type and "text/plain" not in content_type:
                    return "", "", {"url": url, "error": "non-html content"}

                raw_bytes = resp.read(_MAX_PAGE_BYTES)
                # Detect encoding
                encoding = "utf-8"
                charset_match = re.search(r"charset=([^\s;]+)", content_type)
                if charset_match:
                    encoding = charset_match.group(1).strip().lower()

                try:
                    html_text = raw_bytes.decode(encoding, errors="replace")
                except LookupError:
                    html_text = raw_bytes.decode("utf-8", errors="replace")

                extractor = _TextExtractor()
                extractor.feed(html_text)
                text  = extractor.get_text()
                title = extractor.title.strip()

                meta = {
                    "url":          url,
                    "title":        title,
                    "content_type": content_type,
                    "bytes_fetched": len(raw_bytes),
                    "fetched_at":   time.time(),
                    "source":       "web",
                }
                return title, text[:self.config.max_content_length], meta

        except urllib.error.HTTPError as e:
            logger.debug(f"HTTP {e.code} fetching {url}")
            return "", "", {"url": url, "error": f"HTTP {e.code}"}
        except urllib.error.URLError as e:
            logger.debug(f"URL error fetching {url}: {e.reason}")
            return "", "", {"url": url, "error": str(e.reason)}
        except Exception as e:
            logger.debug(f"Fetch error {url}: {e}")
            return "", "", {"url": url, "error": str(e)}

    def _ddg_search(self, query: str, max_results: int = 3) -> List[str]:
        """
        Sovereign search via DuckDuckGo HTML interface.
        No API key. No third-party library.
        Parses the HTML results page directly.
        """
        try:
            encoded_query = urllib.parse.quote_plus(query)
            search_url    = f"https://html.duckduckgo.com/html/?q={encoded_query}"

            req = urllib.request.Request(
                search_url,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept":     "text/html",
                },
            )
            with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
                html_text = resp.read(200_000).decode("utf-8", errors="replace")

            # Extract result URLs from DDG HTML
            # DDG HTML results have links like: //duckduckgo.com/l/?uddg=<encoded_url>
            urls = []
            pattern = re.compile(r'uddg=([^&"]+)', re.IGNORECASE)
            for match in pattern.finditer(html_text):
                encoded = match.group(1)
                try:
                    decoded = urllib.parse.unquote(encoded)
                    if decoded.startswith("http") and decoded not in urls:
                        urls.append(decoded)
                except Exception:
                    continue
                if len(urls) >= max_results:
                    break

            return urls

        except Exception as e:
            logger.debug(f"DDG search failed: {e}")
            return []

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks of approximately chunk_size chars at sentence boundaries."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks    = []
        current   = []
        current_len = 0

        for sentence in sentences:
            if current_len + len(sentence) > self.chunk_size and current:
                chunks.append(" ".join(current))
                current     = [sentence]
                current_len = len(sentence)
            else:
                current.append(sentence)
                current_len += len(sentence)

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _make_signal(
        self,
        content: str,
        url: str,
        chunk_index: int,
        total_chunks: int,
        meta: Dict[str, Any],
        strength: float = 0.7,
    ) -> CognitiveSignal:
        return CognitiveSignal(
            signal_type=SignalType.PERCEPTUAL,
            origin=SignalOrigin.EXTERNAL,
            content=content,
            strength=strength,
            confidence=0.6,
            metadata={
                **meta,
                "chunk_index":  chunk_index,
                "total_chunks": total_chunks,
                "perception":   "web",
            },
        )

    def _normalize_url(self, url: str) -> str:
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.netloc:
                return ""
            return url
        except Exception:
            return ""

    def _is_domain_allowed(self, url: str) -> bool:
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()

            # Check blocked domains first
            for blocked in self.config.blocked_domains:
                if blocked.lower() in domain:
                    return False

            # If allowed_domains specified, must match one
            if self.config.allowed_domains:
                return any(
                    allowed.lower() in domain
                    for allowed in self.config.allowed_domains
                )

            return True
        except Exception:
            return False
