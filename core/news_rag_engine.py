# core/news_rag_engine.py

import faiss
import json
import os
import torch
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class NewsRAGEngine:
    def __init__(self,
                 embedder_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 news_index_dir: str = "data/news_index"):

        print("🚀 Initializing News RAG Engine...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  - Using device: {self.device.upper()}")

        self.embedder = SentenceTransformer(embedder_model, device=self.device)
        self.index = None
        self.mapping = None
        
        self._load_index(news_index_dir)

    def _load_index(self, path: str):
        faiss_path = os.path.join(path, "news_faiss.index")
        mapping_path = os.path.join(path, "news_mapping.json")

        if not os.path.exists(faiss_path) or not os.path.exists(mapping_path):
            print(f"  - ⚠️ WARNING: Index files not found in '{path}'. RAG search will be disabled.")
            return

        try:
            print(f"  - Loading FAISS index from '{faiss_path}'...")
            self.index = faiss.read_index(faiss_path)
            
            print(f"  - Loading news mapping from '{mapping_path}'...")
            with open(mapping_path, "r", encoding="utf-8") as f:
                self.mapping = json.load(f)
            
            print(f"  - ✅ RAG Engine ready with {len(self.mapping)} articles.")
        except Exception as e:
            print(f"  - ❌ CRITICAL: Failed to load index files: {e}")
            self.index = None
            self.mapping = None

    def retrieve_context(self, query: str, top_k: int = 5) -> tuple[str, list[dict]]:
        if not self.index or not self.mapping:
            return "ไม่พบข่าวที่เกี่ยวข้อง", []

        print(f"\n🔎 Searching for query: '{query}'")

        query_embedding = self.embedder.encode(
            [query], convert_to_tensor=True, show_progress_bar=False
        ).cpu().numpy()

        distances, indices = self.index.search(query_embedding, top_k)
        
        retrieved_articles = [self.mapping[str(i)] for i in indices[0] if str(i) in self.mapping]
        
        if not retrieved_articles:
            return "ไม่พบข่าวที่เกี่ยวข้อง", []

        print(f"  - Found {len(retrieved_articles)} relevant articles.")
        
        context_for_llm = ""
        for i, article in enumerate(retrieved_articles):
            context_for_llm += f"--- ข่าวอ้างอิง {i+1} ---\n"
            context_for_llm += f"หัวข้อ: {article.get('title', 'N/A')}\n"
            context_for_llm += f"เนื้อหา: {article.get('full_content', 'N/A')}\n\n"
        
        sources_for_ui = [
            {"title": article.get("title"), "url": article.get("url")}
            for article in retrieved_articles
        ]
            
        return context_for_llm, sources_for_ui