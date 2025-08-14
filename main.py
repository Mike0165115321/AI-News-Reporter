# main.py (Final Version with Frontend Hosting)

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import FileResponse 
from core.news_rag_engine import NewsRAGEngine
from news_generation import NewsGenerator

print("🚀 Initializing AI News Reporter System...")
start_time = time.time()
engine = NewsRAGEngine()
try:
    generator = NewsGenerator()
except ValueError as e:
    print(f"FATAL ERROR: {e}")
    print("Please ensure GEMINI_API_KEY is set in your .env file.")
    exit()
init_time = time.time() - start_time
print(f"✅ System initialized successfully in {init_time:.2f} seconds.")

app = FastAPI(
    title="AI News Reporter API",
    description="API สำหรับ AI นักข่าวที่ใช้ระบบ RAG ในการตอบคำถามจากข่าวล่าสุด",
    version="1.0.0"
)

origins = [
    "http://localhost:8010",
    "http://127.0.0.1:8010",
    "null"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/ask")
async def ask_news_reporter(request: QueryRequest):
    print(f"\n\n--- Received new query: {request.query} ---")
    
    print("Step 1: Retrieving context from RAG Engine...")
    context, sources = engine.retrieve_context(request.query, top_k=request.top_k)
    
    if "ไม่พบข่าวที่เกี่ยวข้อง" in context:
        print("  - No relevant context found.")
        return {"answer": "ขออภัยค่ะ ไม่พบข่าวสารที่เกี่ยวข้องกับคำถามของคุณในตอนนี้ค่ะ", "sources": []}

    print("Step 2: Generating answer with Gemini...")
    answer = generator.generate_answer(query=request.query, context=context)

    print("Step 3: Returning final response.")
    return {"answer": answer, "sources": sources}


@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')
app.mount("/", StaticFiles(directory="frontend"), name="frontend")

if __name__ == "__main__":
    print("Starting FastAPI server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=True)