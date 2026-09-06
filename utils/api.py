
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests

class AskRequest(BaseModel):
    question: str

class LearnRequest(BaseModel):
    topic: str

class CoreKnowAPI:
    def __init__(self, kg, llm_api_key=None):
        self.kg = kg
        self.llm_api_key = llm_api_key
        self.app = FastAPI(title="CoreKnow API")
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.get("/")
        async def root():
            return {"status": "CoreKnow is alive", "concepts": len(self.kg.get_all_concepts())}
        
        @self.app.post("/ask")
        async def ask(request: AskRequest):
            concepts = self.kg.get_all_concepts()[:50]
            headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"You are CoreKnow. You know: {', '.join(concepts)}"},
                    {"role": "user", "content": request.question}
                ],
                "max_tokens": 500
            }
            try:
                r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
                if r.status_code == 200:
                    return {"answer": r.json()["choices"][0]["message"]["content"]}
            except:
                pass
            raise HTTPException(status_code=500, detail="Failed to get answer")
        
        @self.app.post("/learn")
        async def learn(request: LearnRequest):
            # Simplified learning - would integrate with AutoLearner
            return {"status": "learning", "topic": request.topic}
        
        @self.app.get("/stats")
        async def stats():
            return {
                "concepts": len(self.kg.get_all_concepts()),
                "documents": self.kg.get_stats()["documents"],
            }
