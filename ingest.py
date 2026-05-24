import os
import psycopg2
from datasets import load_dataset
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


def fetch_and_store_data():
    print(" 1. جاري سحب الـ Dataset من Hugging Face...")

    try:
        dataset = load_dataset("tatsu-lab/alpaca", split="train[:20]")
        print(f" تم سحب {len(dataset)} أسطر بنجاح!")
    except Exception as e:
        print(f" خطأ أثناء سحب البيانات: {e}")
        return

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        print(" تم الاتصال بقاعدة البيانات بنجاح!")
    except Exception as e:
        print(f" خطأ في الاتصال بقاعدة البيانات: {e}")
        return

    print(" 2. جاري توليد الـ Embeddings وضخها في الداتابيس...")

    success_count = 0

    for index, row in enumerate(dataset, start=1):
        text_to_embed = (
            f"Instruction: {row['instruction']}\n"
            f"Input: {row['input']}\n"
            f"Output: {row['output']}"
        )

        try:
            # موديل Gemini الصحيح للـ Embeddings
            response = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text_to_embed,
                task_type="retrieval_document"
            )

            embedding = response["embedding"]

            # إدخال النص والـ embedding داخل PostgreSQL
            cur.execute(
                """
                INSERT INTO my_knowledge_base (text_content, embedding)
                VALUES (%s, %s);
                """,
                (text_to_embed, embedding)
            )

            success_count += 1
            print(f"🔹 تم ضخ السطر رقم [{success_count}/20] بنجاح عبر Gemini.")

        except Exception as e:
            print(f" تخطينا السطر رقم [{index}] بسبب خطأ: {e}")
            continue

    conn.commit()
    cur.close()
    conn.close()

    print("\n 3. اكتملت العملية!")
    print(f" تم تحويل وتخزين {success_count} نصوص مع الـ Embeddings داخل الدوكر.")


if __name__ == "__main__":
    fetch_and_store_data()