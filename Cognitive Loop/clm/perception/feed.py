"""
CLM - Cognitive Language Model
perception/feed.py

RSS/Atom feed perception — sovereign, pure stdlib.
The system can subscribe to feeds and continuously learn
from new content as it's published.

No feedparser library. Pure xml.etree.ElementTree.
"""

from __future__ import annotations
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import logging
from typing import Any, Dict, Iterator, List, Optional, Set

from clm.perception.base import PerceptionSource, PerceptionSourceType, PerceptionConfig
from clm.core.signal import CognitiveSignal, SignalType, SignalOrigin

logger = logging.getLogger(__name__)

_FETCH_TIMEOUT = 10
_MAX_ITEMS_PER_FETCH = 20

# XML namespaces used in RSS/Atom
_NS = {
    "atom":    "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc":      "http://purl.org/dc/elements/1.1/",
    "media":   "http://search.yahoo.com/mrss/",
}


class FeedPerception(PerceptionSource):
    """
    Subscribes to RSS/Atom feeds and yields signals from new items.
    Tracks seen items to avoid re-processing.
    """

    def __init__(
        self,
        config: Optional[PerceptionConfig] = None,
        user_agent: str = "CLM-Cognitive/1.0",
    ):
        super().__init__(config)
        self.source_type  = PerceptionSourceType.FEED
        self.user_agent   = user_agent
        self._seen_ids:   Set[str] = set()
        self._feed_urls:  List[str] = []

    def add_feed(self, url: str):
        if url not in self._feed_urls:
            self._feed_urls.append(url)

    def perceive(self, input_data: Any) -> Iterator[CognitiveSignal]:
        """
        input_data: str (feed URL) or None (poll all registered feeds)
        """
        if not self.is_allowed():
            return
        if not self._check_rate_limit():
            return

        urls = [input_data] if isinstance(input_data, str) else self._feed_urls
        for url in urls:
            yield from self._process_feed(url)

    def _process_feed(self, url: str) -> Iterator[CognitiveSignal]:
        raw_xml = self._fetch_feed(url)
        if not raw_xml:
            return

        items = self._parse_feed(raw_xml)
        new_count = 0

        for item in items[:_MAX_ITEMS_PER_FETCH]:
            item_id = item.get("id") or item.get("link") or item.get("title", "")
            if item_id in self._seen_ids:
                continue
            self._seen_ids.add(item_id)

            content = self._build_content(item)
            if len(content) < 20:
                continue

            self.total_signals += 1
            new_count += 1
            yield CognitiveSignal(
                signal_type=SignalType.PERCEPTUAL,
                origin=SignalOrigin.EXTERNAL,
                content=content,
                strength=0.65,
                confidence=0.7,
                metadata={
                    "feed_url":   url,
                    "item_id":    item_id,
                    "item_link":  item.get("link", ""),
                    "published":  item.get("published", ""),
                    "perception": "feed",
                },
            )

        if new_count:
            logger.debug(f"Feed {url}: {new_count} new items")

    def _fetch_feed(self, url: str) -> Optional[str]:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": self.user_agent, "Accept": "application/rss+xml,application/atom+xml,text/xml,*/*"},
            )
            with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
                return resp.read(500_000).decode("utf-8", errors="replace")
        except Exception as e:
            logger.debug(f"Feed fetch error {url}: {e}")
            return None

    def _parse_feed(self, xml_text: str) -> List[Dict[str, str]]:
        """Parse RSS or Atom feed. Returns list of item dicts."""
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []

        tag = root.tag.lower()

        # Atom feed
        if "atom" in tag or root.tag == f"{{{_NS['atom']}}}feed":
            return self._parse_atom(root)

        # RSS feed
        channel = root.find("channel")
        if channel is not None:
            return self._parse_rss(channel)

        return []

    def _parse_rss(self, channel: ET.Element) -> List[Dict[str, str]]:
        items = []
        for item in channel.findall("item"):
            d: Dict[str, str] = {}
            d["title"]     = self._text(item, "title")
            d["link"]      = self._text(item, "link")
            d["id"]        = self._text(item, "guid") or d["link"]
            d["published"] = self._text(item, "pubDate")
            d["summary"]   = (
                self._text(item, f"{{{_NS['content']}}}encoded")
                or self._text(item, "description")
            )
            items.append(d)
        return items

    def _parse_atom(self, feed: ET.Element) -> List[Dict[str, str]]:
        ns = _NS["atom"]
        items = []
        for entry in feed.findall(f"{{{ns}}}entry"):
            d: Dict[str, str] = {}
            d["title"]     = self._text(entry, f"{{{ns}}}title")
            d["id"]        = self._text(entry, f"{{{ns}}}id")
            d["published"] = self._text(entry, f"{{{ns}}}published") or self._text(entry, f"{{{ns}}}updated")
            d["summary"]   = self._text(entry, f"{{{ns}}}summary") or self._text(entry, f"{{{ns}}}content")
            # Link
            link_el = entry.find(f"{{{ns}}}link")
            d["link"] = link_el.get("href", "") if link_el is not None else ""
            items.append(d)
        return items

    def _text(self, el: ET.Element, tag: str) -> str:
        child = el.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return ""

    def _build_content(self, item: Dict[str, str]) -> str:
        parts = []
        if item.get("title"):
            parts.append(item["title"])
        if item.get("summary"):
            # Strip HTML tags from summary
            import re
            summary = re.sub(r"<[^>]+>", " ", item["summary"])
            summary = re.sub(r"\s+", " ", summary).strip()
            if summary:
                parts.append(summary[:500])
        return " — ".join(parts)
