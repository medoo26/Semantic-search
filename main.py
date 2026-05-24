import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from google import genai

# تحميل متغيرات البيئة
load_dotenv()

app = FastAPI(title="RAG Semantic Search with Gemini")

# Gemini Client
gemini_key = os.environ.get("GEMINI_API_KEY")
if not gemini_key:
    raise RuntimeError(" GEMINI_API_KEY غير موجود داخل ملف .env")

gemini_client = genai.Client(api_key=gemini_key)

# Database
DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# جلسة الداتابيس
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# شكل الطلب
class SearchQuery(BaseModel):
    query: str
    top_k: int = 3


# توليد Embedding بنفس موديل التخزين
def get_embedding(text_to_embed: str) -> list[float]:
    try:
        response = gemini_client.models.embed_content(
            model="gemini-embedding-001",
            contents=text_to_embed
        )

        return response.embeddings[0].values

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Embedding error: {str(e)}"
        )


# Endpoint عادي للبحث فقط
@app.post("/search")
def semantic_search(search_data: SearchQuery, db: Session = Depends(get_db)):
    query_vector = get_embedding(search_data.query)

    query_str = text("""
        SELECT 
            id,
            text_content,
            embedding <=> CAST(:vector AS vector) AS distance
        FROM public.my_knowledge_base
        ORDER BY embedding <=> CAST(:vector AS vector)
        LIMIT :limit;
    """)

    try:
        result = db.execute(
            query_str,
            {
                "vector": str(query_vector),
                "limit": search_data.top_k
            }
        ).fetchall()

        search_results = []

        for row in result:
            search_results.append({
                "id": row.id,
                "text_content": row.text_content,
                "distance": round(float(row.distance), 4),
                "similarity_score": round(1 - float(row.distance), 4)
            })

        return {
            "query": search_data.query,
            "top_k": search_data.top_k,
            "results": search_results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database query error: {str(e)}"
        )


# Endpoint RAG Chat
@app.post("/rag-chat")
def rag_chat(search_data: SearchQuery, db: Session = Depends(get_db)):
    query_vector = get_embedding(search_data.query)

    query_str = text("""
        SELECT 
            id,
            text_content,
            embedding <=> CAST(:vector AS vector) AS distance
        FROM public.my_knowledge_base
        ORDER BY embedding <=> CAST(:vector AS vector)
        LIMIT :limit;
    """)

    try:
        result = db.execute(
            query_str,
            {
                "vector": str(query_vector),
                "limit": search_data.top_k
            }
        ).fetchall()

        if not result:
            return {
                "answer": "لم أجد أي معلومات متعلقة بسؤالك في قاعدة البيانات.",
                "sources_used": []
            }

        context_chunks = [row.text_content for row in result]
        context_text = "\n---\n".join(context_chunks)

        full_prompt = f"""
You are a helpful assistant.

Answer the user's question using ONLY the provided context.
If the answer is not found in the context, say:
"I cannot find the answer in the provided documents."

Do not make up information.

Context:
{context_text}

Question:
{search_data.query}

Answer:
"""

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )

        sources_used = []

        for row in result:
            sources_used.append({
                "id": row.id,
                "text_content": row.text_content,
                "distance": round(float(row.distance), 4),
                "similarity_score": round(1 - float(row.distance), 4)
            })

        return {
            "query": search_data.query,
            "answer": response.text,
            "sources_used": sources_used
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RAG Error: {str(e)}"
        )


@app.get("/")
def home():
    return {
        "message": "RAG Semantic Search API is running ✅",
        "endpoints": {
            "search": "/search",
            "rag_chat": "/rag-chat",
            "docs": "/docs"
        }
    }