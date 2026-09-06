
import requests

class Creativity:
    def __init__(self, kg, llm_api_key=None):
        self.kg = kg
        self.llm_api_key = llm_api_key
        self.creations = []
    
    def write_poem(self, topic, style="free verse"):
        """Generate a poem."""
        if not self.llm_api_key:
            return "Poetry requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"You are CoreKnow's poet. Write a {style} poem about {topic}."},
                {"role": "user", "content": f"Write a poem about {topic}."}
            ],
            "max_tokens": 500,
            "temperature": 0.9
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                poem = r.json()["choices"][0]["message"]["content"]
                self.creations.append({"type": "poem", "content": poem})
                return poem
        except:
            pass
        return "Poetry generation failed."
    
    def compose_song(self, theme, genre="afrobeat"):
        """Generate song lyrics."""
        if not self.llm_api_key:
            return "Song composition requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"You are CoreKnow's songwriter. Write {genre} song lyrics about {theme}."},
                {"role": "user", "content": f"Write a song about {theme}."}
            ],
            "max_tokens": 500,
            "temperature": 0.9
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                song = r.json()["choices"][0]["message"]["content"]
                self.creations.append({"type": "song", "content": song})
                return song
        except:
            pass
        return "Song generation failed."
    
    def write_story(self, prompt, length="short"):
        """Generate a creative story."""
        if not self.llm_api_key:
            return "Story writing requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's storyteller. Write engaging stories."},
                {"role": "user", "content": f"Write a {length} story about: {prompt}"}
            ],
            "max_tokens": 800,
            "temperature": 0.8
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                story = r.json()["choices"][0]["message"]["content"]
                self.creations.append({"type": "story", "content": story})
                return story
        except:
            pass
        return "Story generation failed."
    
    def get_creations_count(self):
        return len(self.creations)
