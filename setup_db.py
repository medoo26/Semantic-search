import os 
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="mysecretpassword",
        port="5432"
    )
    return conn


def init_database():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    cur.execute("DROP TABLE IF EXISTS my_knowledge_base;")

    cur.execute("""
        CREATE TABLE my_knowledge_base (
            id SERIAL PRIMARY KEY,
            text_content TEXT NOT NULL,
            embedding vector(3072)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

    print(" تم حذف الجدول القديم وإنشاء جدول جديد بحجم vector(3072) بنجاح!")


if __name__ == "__main__":
    init_database()