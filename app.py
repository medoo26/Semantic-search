import streamlit as st
import requests

# إعداد الصفحة
st.set_page_config(page_title="RAG ChatBot", )

st.title("RAG System")
st.write("اطرح أي سؤال .")

# خانة السؤال
question = st.text_input("سؤالك:", placeholder="مثلاً: ما هي وظيفة المعالج؟")

if st.button("بحث وإجابة"):
    if question:
        with st.spinner("جاري البحث في قاعدة البيانات..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/rag-chat",
                    json={"query": question, "top_k": 3}
                )

                if response.status_code == 200:
                    data = response.json()

                    st.success("إجابة النظام:")
                    st.write(data.get("answer", "لا توجد إجابة."))

                    with st.expander("عرض المصادر المستخدمة"):
                        sources = data.get("sources_used", [])

                        if not sources:
                            st.write("لا توجد مصادر.")
                        else:
                            for source in sources:
                                if isinstance(source, dict):
                                    st.write(f"**ID:** {source.get('id')}")
                                    st.write(f"**Similarity:** {source.get('similarity_score')}")
                                    st.write(source.get("text_content"))
                                    st.divider()
                                else:
                                    st.write(source)

                else:
                    st.error(f"مشكلة من الـ API: {response.status_code}")
                    st.write(response.text)

            except Exception as e:
                st.error(f"خطأ في الاتصال: {e}")
    else:
        st.warning("يرجى كتابة سؤال أولاً.")