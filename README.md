# CBK Chatbot (RAG-enabled, minimal installs)

- FastAPI backend
- OpenAI Chat + Embeddings (no sentence-transformers, no FAISS)
- NumPy cosine similarity for retrieval
- Deterministic Treasury Bill calculators
- CLI REPL for interactive chat

## Quickstart

```bash
cp .env.example .env
# put your OPENAI_API_KEY into .env
make ingest    # build index from docs/cbk_pdfs
make dev       # build and run
```
