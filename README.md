# RAG Semantic Search System

نظام ذكي للبحث والاسترجاع المعزز بالذكاء الاصطناعي (RAG). يتيح النظام البحث في البيانات الخاصة باستخدام **Semantic Search** عوضاً عن البحث التقليدي بالكلمات المفتاحية، مما يضمن دقة عالية في النتائج.

##  الميزات التقنية
- **Semantic Search:** استخدام الـ Embeddings (3072-dimension) لفهم المعنى السيمانتيكي للاستفسارات.
- **Vector Database:** تكامل كامل مع PostgreSQL باستخدام إضافة `pgvector`.
- **Backend:** مبني باستخدام إطار عمل FastAPI لضمان سرعة واستجابة عالية.
- **AI Integration:** الربط مع نماذج Google Gemini لعملية التوليد (Generation).
- **Frontend:** واجهة تفاعلية بسيطة ومباشرة باستخدام Streamlit.

##  التقنيات المستخدمة (Stack)
* **OS:** Linux (WSL/Ubuntu)
* **Database:** PostgreSQL + pgvector
* **API:** FastAPI
* **UI:** Streamlit
* **AI Engine:** Google Gemini (Gemini-2.0-flash / Embedding-001)

##  هيكلية المشروع
```text
├── main.py           # عقل النظام (Backend API)
├── app.py            # واجهة المستخدم (Frontend)
├── requirements.txt  # قائمة المكتبات والمتطلبات
├── .env              # متغيرات البيئة (API Keys)
└── README.md         
```
##   طريقة التشغيل

تشغيل الخدمات:

لتشغيل المشروع، يتم استخدام ثلاث نوافذ Terminal منفصلة:

1. تشغيل قاعدة البيانات داخل Docker:
docker start my_postgres

2. تشغيل الـ Backend باستخدام FastAPI:
source venv/bin/activate
uvicorn main:app --reload

3. تشغيل الواجهة باستخدام Streamlit:
source venv/bin/activate
streamlit run app.py

