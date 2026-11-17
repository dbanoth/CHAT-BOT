# Groq Chatbots (Streamlit)

Two small LLM chat apps built with **Streamlit** and **Llama 3.1 8B Instant** via the **Groq** API.

| App | File | What it does |
|---|---|---|
| Simple chatbot | `app.py` | Minimal chat UI with in-session memory |
| Chatbot with history | `chatbot_with_history.py` | Adjustable model settings, a 10-message context window, and every exchange saved to a **Supabase** `chat_history` table |

> This repo merges the earlier `ChatBot-History` repository into `CHAT-BOT`.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py                    # simple chatbot
streamlit run chatbot_with_history.py   # chatbot with Supabase history
```

## Configuration

Set these in `.streamlit/secrets.toml` or as environment variables:

```toml
GROQ_API_KEY = "..."
# Only needed for chatbot_with_history.py
SUPABASE_URL = "https://<project>.supabase.co"
SUPABASE_KEY = "..."
```

Supabase table:

```sql
create table chat_history (
  id bigint generated always as identity primary key,
  user_name text,
  message text,
  response text,
  created_at timestamptz default now()
);
```

## Stack
Python · Streamlit · Groq (Llama 3.1) · Supabase · deployable on Render or Streamlit Community Cloud
