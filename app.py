"""Interfață Streamlit pentru RAG public cu încărcare administrată de documente."""
import hmac
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from rag_backend import ask, list_documents, remove_document, upload_document

load_dotenv()

st.set_page_config(page_title="Asistent RAG", page_icon="📚", layout="centered")
st.title("📚 Asistent RAG")
st.caption("Pune întrebări și primește răspunsuri bazate pe documentele bibliotecii.")

api_key = os.getenv("OPENAI_API_KEY", "")
vector_store_id = os.getenv("VECTOR_STORE_ID", "")
admin_password = os.getenv("ADMIN_PASSWORD", "")
model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
max_session_questions = 20  # Protecție orientativă, NU rate limiting global.

if not api_key or not vector_store_id:
    st.error("Configurare incompletă: trebuie setate OPENAI_API_KEY și VECTOR_STORE_ID.")
    st.stop()

@st.cache_resource
def get_client(key: str) -> OpenAI:
    return OpenAI(api_key=key, timeout=90.0, max_retries=2)

client = get_client(api_key)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "questions_used" not in st.session_state:
    st.session_state.questions_used = 0
if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False

chat_tab, admin_tab = st.tabs(["💬 Întrebări și răspunsuri", "🔒 Administrare documente"])

with chat_tab:
    st.write("Răspunsurile se bazează pe documentele adăugate de administrator.")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption("Surse: " + ", ".join(message["sources"]))

    if st.session_state.questions_used >= max_session_questions:
        st.warning("Ai atins limita de 20 de întrebări în această sesiune.")
    else:
        prompt = st.chat_input("Scrie aici întrebarea ta...")
        if prompt:
            old_history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            st.session_state.messages.append({"role": "user", "content": prompt[:4000]})
            with st.chat_message("user"):
                st.markdown(prompt[:4000])
            with st.chat_message("assistant"):
                with st.spinner("Caut informația în documente..."):
                    try:
                        answer, sources = ask(client, vector_store_id, prompt, old_history, model)
                        st.session_state.questions_used += 1
                    except Exception:
                        answer, sources = "Nu am putut procesa întrebarea acum. Încearcă din nou.", []
                st.markdown(answer)
                if sources:
                    st.caption("Surse: " + ", ".join(sources))
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": sources}
            )
    if st.button("Șterge istoricul conversației", key="clear_history"):
        st.session_state.messages = []
        st.rerun()

with admin_tab:
    if not admin_password:
        st.warning("Administrarea este dezactivată. Setează ADMIN_PASSWORD în secretele serverului.")
    elif not st.session_state.admin_ok:
        supplied_password = st.text_input("Parola administratorului", type="password")
        if st.button("Autentificare", type="primary"):
            if hmac.compare_digest(supplied_password, admin_password):
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Parolă incorectă.")
    else:
        st.success("Autentificat ca administrator")
        if st.button("Deconectare"):
            st.session_state.admin_ok = False
            st.rerun()
        st.subheader("Adaugă documente în biblioteca RAG")
        st.caption("PDF, DOCX, TXT și MD; până la 20 MB per document. Fișierele se adaugă la cele existente.")
        selected = st.file_uploader(
            "Selectează unul sau mai multe documente",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            max_upload_size=20,
        )
        st.info("Nu încărca documente confidențiale: orice vizitator poate pune întrebări despre ele.")
        if st.button("Încarcă și indexează", type="primary", disabled=not selected):
            with st.spinner("Încarc și indexez documentele în OpenAI..."):
                for file in selected:
                    try:
                        upload_document(client, vector_store_id, file.name, file.getvalue())
                        st.success(f"Indexat: {file.name}")
                    except Exception as exc:
                        st.error(f"Nu am putut indexa {file.name}: {type(exc).__name__}")
        st.divider()
        with st.expander("Documente existente (maxim 100 afișate)"):
            try:
                items, has_more = list_documents(client, vector_store_id)
                if not items:
                    st.caption("Nu există documente indexate.")
                for file_id, filename, status in items:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{filename}** — {status}")
                    with col2:
                        if st.button("Elimină", key=f"delete_{file_id}"):
                            try:
                                remove_document(client, vector_store_id, file_id)
                                st.success(f"Document eliminat: {filename}")
                                st.rerun()
                            except Exception:
                                st.error("Nu s-a putut elimina documentul.")
                if has_more:
                    st.info("Sunt mai mult de 100 de documente; lista este parțială.")
            except Exception:
                st.error("Nu am putut obține lista documentelor.")

st.caption("Aplicație demonstrativă. Utilizarea OpenAI API poate genera costuri.")
