"""Rulează o singură dată pentru a crea vector store-ul în OpenAI Platform."""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("Lipsește OPENAI_API_KEY în .env sau variabilele de mediu.")

client = OpenAI()
vector_store = client.vector_stores.create(name="RAG - Biblioteca documente")
print("Vector store creat:")
print(f"VECTOR_STORE_ID={vector_store.id}")
print("Copiază ID-ul în .env local și în secretele aplicației publicate.")
