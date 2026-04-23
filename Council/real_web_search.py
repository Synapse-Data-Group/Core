"""
Real Web Search - Uses DuckDuckGo HTML scraping (no API key needed)
"""

import urllib.request
import urllib.parse
import re
import json
from typing import List, Dict, Any


class RealWebSearch:
    """Real web search using DuckDuckGo HTML scraping"""
    
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.cache = {}
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Perform real web search"""
        
        # Check cache
        if query in self.cache:
            return self.cache[query]
        
        try:
            # DuckDuckGo HTML search
            encoded_query = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': self.user_agent
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
            
            # Parse results
            results = self._parse_duckduckgo_html(html, max_results)
            
            # Cache results
            self.cache[query] = results
            
            return results
        
        except Exception as e:
            print(f"Web search error: {e}")
            return [{
                "title": "Search unavailable",
                "url": "",
                "snippet": f"Could not perform web search: {str(e)}"
            }]
    
    def _parse_duckduckgo_html(self, html: str, max_results: int) -> List[Dict[str, str]]:
        """Parse DuckDuckGo HTML results"""
        
        results = []
        
        # Try multiple parsing strategies
        
        # Strategy 1: Look for result links and snippets
        link_pattern = r'<a[^>]*class="[^"]*result[^"]*"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
        snippet_pattern = r'<div[^>]*class="[^"]*snippet[^"]*"[^>]*>([^<]+)</div>'
        
        links = re.findall(link_pattern, html)
        snippets = re.findall(snippet_pattern, html)
        
        for i, (url, title) in enumerate(links[:max_results]):
            snippet = snippets[i] if i < len(snippets) else "No description available"
            
            title = self._clean_text(title)
            snippet = self._clean_text(snippet)
            
            if title and len(title) > 3:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
        
        # Strategy 2: If no results, try simpler pattern
        if not results:
            simple_pattern = r'href="(https?://[^"]+)"[^>]*>([^<]{10,})</a>'
            matches = re.findall(simple_pattern, html)
            
            for url, title in matches[:max_results]:
                if 'duckduckgo.com' not in url and len(title.strip()) > 10:
                    results.append({
                        "title": self._clean_text(title),
                        "url": url,
                        "snippet": "Result from web search"
                    })
        
        # Strategy 3: Extract any meaningful text blocks
        if not results:
            # Find text blocks that look like search results
            text_blocks = re.findall(r'<[^>]*>([^<]{50,200})</[^>]*>', html)
            
            for i, text in enumerate(text_blocks[:max_results]):
                cleaned = self._clean_text(text)
                if len(cleaned) > 50 and not any(x in cleaned.lower() for x in ['cookie', 'privacy', 'settings', 'javascript']):
                    results.append({
                        "title": f"Search Result {i+1}",
                        "url": "",
                        "snippet": cleaned[:200]
                    })
        
        # If still no results, return generic message
        if not results:
            results = [{
                "title": "Web search performed",
                "url": "",
                "snippet": "Search was executed but specific results could not be extracted from the page structure. The search functionality is working, but result parsing needs adjustment for current DuckDuckGo HTML format."
            }]
        
        return results[:max_results]
    
    def _clean_text(self, text: str) -> str:
        """Clean HTML entities and whitespace"""
        
        # Decode HTML entities
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&nbsp;', ' ')
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        return text
    
    def fetch_url(self, url: str) -> str:
        """Fetch content from URL"""
        
        try:
            headers = {
                'User-Agent': self.user_agent
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # Extract text (simple approach)
            text = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<.*?>', ' ', text)
            text = self._clean_text(text)
            
            return text[:2000]  # Limit to 2000 chars
        
        except Exception as e:
            return f"Could not fetch URL: {str(e)}"


class RealWebResearchTool:
    """Web research tool using real search"""
    
    def __init__(self):
        self.name = "Real Web Research Tool"
        self.search_engine = RealWebSearch()
    
    def execute(self, query: str, action: str = "search") -> str:
        """Execute web research"""
        
        if action == "search":
            results = self.search_engine.search(query, max_results=3)
            
            output = f"Web search results for '{query}':\n\n"
            for idx, result in enumerate(results, 1):
                output += f"{idx}. {result['title']}\n"
                output += f"   {result['snippet']}\n"
                if result['url']:
                    output += f"   URL: {result['url']}\n"
                output += "\n"
            
            return output
        
        elif action == "fetch":
            content = self.search_engine.fetch_url(query)
            return f"Content from {query}:\n\n{content}"
        
        else:
            return "Unknown action"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "capabilities": ["search", "fetch"]
        }
