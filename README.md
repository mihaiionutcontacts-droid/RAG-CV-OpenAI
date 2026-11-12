# RAG web public cu OpenAI + Streamlit

Acest proiect pornește de la funcționalitatea din `rag.py`: încărcare documente, indexare, recuperare de fragmente relevante și răspuns printr-un model OpenAI. Pentru a avea o bibliotecă stabilă pe hosting fără disc persistent, **FAISS + HuggingFaceEmbeddings** din original sunt înlocuite cu **OpenAI Vector Stores + File Search**, care indexează automat documentele stocate în OpenAI Platform.

## Ce conține

- `app.py`: interfață web Streamlit (chat public și administrare cu parolă).
- `rag_backend.py`: încărcare, indexare, căutare, răspunsuri cu citări și eliminare documente.
- `setup_vector_store.py`: creează o singură dată baza vectorială gestionată în OpenAI.
- `.env.example`: exemplu pentru configurare locală.
- `requirements.txt`: bibliotecile Python.
- `.streamlit/config.toml`: limită de 20 MB per fișier.

## 1. Instalează și configurează local

Necesită Python 3.11+ și un **API key de pe platform.openai.com** cu facturare API configurată. Abonamentul ChatGPT Plus nu include automat credit API.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Copiază `.env.example` în `.env` și înlocuiește `OPENAI_API_KEY` cu cheia ta. **Nu încărca niciodată `.env` sau cheia API pe GitHub.**

```bash
python setup_vector_store.py
```

Copiază ID-ul `vs_...` rezultat în `.env` ca `VECTOR_STORE_ID`. Setează `ADMIN_PASSWORD` (parolă lungă și unică).

```bash
streamlit run app.py
```

Deschide URL-ul local afișat (de regulă `http://localhost:8501`). În tabul „Administrare documente”, autentifică-te, selectează simultan mai multe fișiere (PDF/DOCX/TXT/MD) și apasă „Încarcă și indexează”. Pentru întrebări, folosește tabul „Întrebări și răspunsuri”.

## 2. Publică în internet (Streamlit Community Cloud)

1. Creează un repository GitHub și încarcă fișierele proiectului (`app.py`, `rag_backend.py`, `requirements.txt`, `.streamlit/config.toml` etc.); **nu încărca** `.env`.
2. Accesează https://share.streamlit.io și autentifică-te cu GitHub.
3. Alege „Create app” și repository-ul tău; entrypoint: `app.py`.
4. În „Advanced settings” -> „Secrets”, introdu următorul conținut (cu valori reale):

```toml
OPENAI_API_KEY = "sk-..."
VECTOR_STORE_ID = "vs_..."
ADMIN_PASSWORD = "o-parola-foarte-puternica"
OPENAI_MODEL = "gpt-4.1-mini"
```

5. Apasă Deploy. Streamlit va oferi un URL public `https://...streamlit.app`, accesibil oricui. Administratorul încarcă documente cu parola; vizitatorii doar pun întrebări.

**Durabilitate:** fișierele și indexul sunt stocate în OpenAI Vector Store, nu pe discul temporar Streamlit; rămân disponibile la repornirea sau redeploy-ul interfeței, cât timp păstrezi același `VECTOR_STORE_ID`, nu ștergi vector store-ul și contul API rămâne activ.

## Siguranță / limite

- Oricine cunoaște URL-ul poate întreba despre documente. Nu indexa informații secrete sau personale pentru public.
- `ADMIN_PASSWORD` este o barieră simplă pentru demo; pentru producție folosește autentificare solidă, control de acces și audit. Codul **nu** implementează limitare globală anti-abuz: limita de 20 întrebări este doar per sesiune și poate fi ocolită.
- Setează buget și alerte în OpenAI Platform; fiecare întrebare poate genera costuri (model + File Search), iar stocarea vectorială este facturabilă conform tarifelor actuale.
- File Search nu înlocuiește OCR: PDF-urile scanate care conțin numai imagini pot necesita OCR înainte de indexare.
- În Streamlit Community Cloud, aplicațiile fără trafic pot hiberna; URL-ul rămâne disponibil și aplicația poate fi reactivată.
- `Elimină` scoate un fișier din vector store, dar nu șterge automat și obiectul original din Files din contul OpenAI. Eliminarea poate necesita timp până se reflectă în rezultatele de căutare.
- Dacă folosești date care nu pot părăsi infrastructura ta, păstrează FAISS/embeddings locale și alege un hosting cu disc persistent, de exemplu un serviciu Render plătit cu disk atașat.

## Documentație utilă

- OpenAI File Search: https://developers.openai.com/api/docs/guides/tools-file-search
- OpenAI Retrieval / Vector Stores: https://developers.openai.com/api/docs/guides/retrieval
- Streamlit deploy: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Streamlit secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- Costuri API: https://platform.openai.com/pricing
