
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random

class AutoLearner:
    def __init__(self, kg, llm_api_key=None):
        self.kg = kg
        self.llm_api_key = llm_api_key
        self.learned_topics = set()
        self.learning_sources = []
    
    def learn_from_wikipedia(self, topic, max_articles=3):
        """Automatically learn about a topic from Wikipedia."""
        base_url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
        results = []
        
        try:
            r = requests.get(base_url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Extract main content
            content = soup.find('div', {'id': 'mw-content-text'})
            if content:
                # Remove unwanted elements
                for element in content.find_all(['sup', 'table', 'div']):
                    element.decompose()
                text = content.get_text(separator="\n", strip=True)
                
                # Add to knowledge graph
                self.kg.add_document(text[:5000], f"wiki:{topic}", self.llm_api_key)
                self.learned_topics.add(topic)
                results.append(topic)
                
                # Find related articles
                links = content.find_all('a', href=True)
                related_topics = []
                for link in links[:20]:
                    href = link.get('href', '')
                    if href.startswith('/wiki/') and ':' not in href:
                        related = href.replace('/wiki/', '').replace('_', ' ')
                        if related not in self.learned_topics:
                            related_topics.append(related)
                            if len(related_topics) >= max_articles:
                                break
                
                # Learn related topics (recursive)
                for related in related_topics:
                    if related not in self.learned_topics:
                        time.sleep(random.uniform(0.5, 1.5))
                        self.learn_from_wikipedia(related, max_articles=1)
        except Exception as e:
            pass
        
        return results
    
    def learn_from_google(self, query, max_results=5):
        """Learn from Google search results."""
        # Note: This is a simplified version. Real Google scraping requires API or more complex setup.
        # We'll use DuckDuckGo as fallback
        try:
            url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            results = []
            for link in soup.find_all('a', {'class': 'result__a'})[:max_results]:
                href = link.get('href', '')
                title = link.get_text()
                if href and href.startswith('http'):
                    results.append({"title": title, "url": href})
            
            return results
        except:
            return []
    
    def auto_expand_knowledge(self, topics, max_per_topic=2):
        """Automatically expand knowledge on given topics."""
        for topic in topics:
            if topic not in self.learned_topics:
                self.learn_from_wikipedia(topic, max_articles=max_per_topic)
                self.learning_sources.append(f"wiki:{topic}")
        return len(self.learned_topics)
