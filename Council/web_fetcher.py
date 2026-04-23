import urllib.request
import urllib.parse
import urllib.error
import json
import time
from typing import Dict, List, Optional, Any
from html.parser import HTMLParser


class HTMLTextExtractor(HTMLParser):
    """Extract text content from HTML"""
    
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.in_script = False
        self.in_style = False
    
    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:
            self.in_script = True
    
    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.in_script = False
    
    def handle_data(self, data):
        if not self.in_script and not self.in_style:
            text = data.strip()
            if text:
                self.text_parts.append(text)
    
    def get_text(self) -> str:
        return ' '.join(self.text_parts)


class WebFetcher:
    """Pure Python web fetcher using urllib (no dependencies)"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.fetch_history: List[Dict[str, Any]] = []
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300
    
    def fetch_url(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """Fetch content from a URL"""
        
        if use_cache and url in self.cache:
            cached = self.cache[url]
            if time.time() - cached['timestamp'] < self.cache_ttl:
                return {
                    "success": True,
                    "url": url,
                    "content": cached['content'],
                    "cached": True,
                    "timestamp": cached['timestamp']
                }
        
        for attempt in range(self.max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Council Framework Agent)'
                }
                
                req = urllib.request.Request(url, headers=headers)
                
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    
                    result = {
                        "success": True,
                        "url": url,
                        "content": content,
                        "status_code": response.status,
                        "cached": False,
                        "timestamp": time.time()
                    }
                    
                    self.cache[url] = {
                        "content": content,
                        "timestamp": time.time()
                    }
                    
                    self.fetch_history.append({
                        "url": url,
                        "success": True,
                        "timestamp": time.time(),
                        "attempt": attempt + 1
                    })
                    
                    return result
                    
            except urllib.error.HTTPError as e:
                if attempt == self.max_retries - 1:
                    self.fetch_history.append({
                        "url": url,
                        "success": False,
                        "error": f"HTTP {e.code}",
                        "timestamp": time.time()
                    })
                    return {
                        "success": False,
                        "url": url,
                        "error": f"HTTP Error {e.code}: {e.reason}",
                        "timestamp": time.time()
                    }
                time.sleep(1)
                
            except urllib.error.URLError as e:
                if attempt == self.max_retries - 1:
                    self.fetch_history.append({
                        "url": url,
                        "success": False,
                        "error": str(e.reason),
                        "timestamp": time.time()
                    })
                    return {
                        "success": False,
                        "url": url,
                        "error": f"URL Error: {e.reason}",
                        "timestamp": time.time()
                    }
                time.sleep(1)
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    self.fetch_history.append({
                        "url": url,
                        "success": False,
                        "error": str(e),
                        "timestamp": time.time()
                    })
                    return {
                        "success": False,
                        "url": url,
                        "error": f"Error: {str(e)}",
                        "timestamp": time.time()
                    }
                time.sleep(1)
        
        return {
            "success": False,
            "url": url,
            "error": "Max retries exceeded",
            "timestamp": time.time()
        }
    
    def extract_text_from_html(self, html: str) -> str:
        """Extract readable text from HTML"""
        
        parser = HTMLTextExtractor()
        parser.feed(html)
        return parser.get_text()
    
    def fetch_and_extract(self, url: str) -> Dict[str, Any]:
        """Fetch URL and extract text content"""
        
        result = self.fetch_url(url)
        
        if result["success"]:
            text = self.extract_text_from_html(result["content"])
            result["extracted_text"] = text
            result["text_length"] = len(text)
        
        return result
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Simulate web search (in production, integrate with search API)
        For now, returns structured format that can be filled by actual API
        """
        
        search_results = []
        
        encoded_query = urllib.parse.quote(query)
        
        search_results.append({
            "title": f"Search result for: {query}",
            "url": f"https://example.com/search?q={encoded_query}",
            "snippet": f"This is a simulated search result for '{query}'. In production, integrate with a real search API.",
            "simulated": True
        })
        
        self.fetch_history.append({
            "action": "search",
            "query": query,
            "num_results": num_results,
            "timestamp": time.time()
        })
        
        return search_results[:num_results]
    
    def fetch_json_api(self, url: str) -> Dict[str, Any]:
        """Fetch and parse JSON from API"""
        
        result = self.fetch_url(url)
        
        if result["success"]:
            try:
                json_data = json.loads(result["content"])
                result["json_data"] = json_data
                result["parsed"] = True
            except json.JSONDecodeError as e:
                result["parsed"] = False
                result["parse_error"] = str(e)
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get fetcher statistics"""
        
        successful = sum(1 for h in self.fetch_history if h.get("success", False))
        failed = len(self.fetch_history) - successful
        
        return {
            "total_fetches": len(self.fetch_history),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(self.fetch_history) if self.fetch_history else 0,
            "cache_size": len(self.cache),
            "recent_fetches": self.fetch_history[-10:]
        }


class WebResearchTool:
    """Tool that agents can use to fetch web information"""
    
    def __init__(self, tool_id: str = "web_research"):
        self.tool_id = tool_id
        self.name = "Web Research Tool"
        self.fetcher = WebFetcher()
        self.is_active = True
        self.created_at = time.time()
    
    def execute(self, query: str, action: str = "search") -> str:
        """Execute web research action"""
        
        if not self.is_active:
            return "Tool is not active"
        
        if action == "search":
            results = self.fetcher.search_web(query)
            return self._format_search_results(results)
        
        elif action == "fetch":
            result = self.fetcher.fetch_and_extract(query)
            if result["success"]:
                text = result.get("extracted_text", "")
                return f"Fetched content from {query}: {text[:500]}..."
            else:
                return f"Failed to fetch {query}: {result.get('error', 'Unknown error')}"
        
        elif action == "api":
            result = self.fetcher.fetch_json_api(query)
            if result["success"] and result.get("parsed"):
                return f"API data from {query}: {json.dumps(result['json_data'], indent=2)[:500]}..."
            else:
                return f"Failed to fetch API {query}"
        
        return "Unknown action"
    
    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for agent consumption"""
        
        formatted = "Web search results:\n"
        for idx, result in enumerate(results, 1):
            formatted += f"{idx}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n"
            if not result.get('simulated', False):
                formatted += f"   URL: {result['url']}\n"
        
        return formatted
    
    def deactivate(self):
        """Deactivate the tool"""
        self.is_active = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        return self.fetcher.get_stats()
