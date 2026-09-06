
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class WebCrawler:
    def __init__(self, max_pages=10, delay=1):
        self.max_pages = max_pages
        self.delay = delay
        self.visited = set()
    
    def crawl(self, start_url):
        """Crawl from start URL and return list of (url, text)."""
        results = []
        queue = [start_url]
        
        while queue and len(self.visited) < self.max_pages:
            url = queue.pop(0)
            if url in self.visited:
                continue
            
            self.visited.add(url)
            try:
                r = requests.get(url, timeout=10)
                soup = BeautifulSoup(r.text, 'html.parser')
                
                # Extract text
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator="\n", strip=True)
                results.append((url, text[:2000]))
                
                # Find links
                for link in soup.find_all('a', href=True):
                    absolute = urljoin(url, link['href'])
                    if urlparse(absolute).netloc == urlparse(start_url).netloc:
                        if absolute not in self.visited:
                            queue.append(absolute)
                
                time.sleep(self.delay)
            except Exception as e:
                continue
        
        return results
    
    def crawl_and_learn(self, start_url, kg, llm_api_key=None):
        """Crawl and add all pages to knowledge graph."""
        pages = self.crawl(start_url)
        for url, text in pages:
            kg.add_document(text, url, llm_api_key)
        return len(pages)
