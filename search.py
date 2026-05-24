import os
import psycopg2
import google.generativeai as genai
from dotenv import load_dotenv

# قراءة المتغيرات من ملف .env
load_dotenv()

gemini_key = os.environ.get("GEMINI_API_KEY")
if not gemini_key:
    print(" خطأ: لم يتم العثور على GEMINI_API_KEY داخل ملف .env.")
    exit(1)

# إعداد Gemini API
genai.configure(api_key=gemini_key)


def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="mysecretpassword",
        port="5432"
    )


def search_database(query):
    print(f" جاري البحث في الداتابيس عن: '{query}'...\n")

    # 1. توليد Embedding للسؤال
    try:
        response = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query,
            task_type="retrieval_query"
        )

        query_embedding = response["embedding"]

    except Exception as e:
        print(f" خطأ أثناء توليد Embedding للسؤال: {e}")
        return []

    # 2. البحث داخل PostgreSQL باستخدام pgvector
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 
                text_content,
                embedding <=> %s::vector AS distance
            FROM my_knowledge_base
            ORDER BY embedding <=> %s::vector
            LIMIT 3;
            """,
            (query_embedding, query_embedding)
        )

        results = cur.fetchall()

        cur.close()
        conn.close()

        return results

    except Exception as e:
        print(f" خطأ أثناء البحث في الداتابيس: {e}")
        return []


if __name__ == "__main__":
    question = " describe the function of computer motherboard"

    results = search_database(question)

    if not results:
        print(" لم يتم العثور على نتائج متطابقة.")
    else:
        print(" أفضل النتائج:\n")

        for i, (text_content, distance) in enumerate(results, start=1):
            print("=" * 80)
            print(f" النتيجة رقم {i}")
            print(f" Distance: {distance}")
            print("-" * 80)
            print(text_content)
            print("=" * 80)
            print()