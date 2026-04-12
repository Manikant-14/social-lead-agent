# 🎬 AutoStream Lead Agent
### Social-to-Lead Agentic Workflow — ML Intern Assignment
**Built by Manikant | ServiceHive × Inflx**

---

## 📌 Overview

A production-style conversational AI agent for **AutoStream** — a fictional AI-powered video editing SaaS. The agent handles product queries using RAG, detects high-intent users, and captures leads through a natural multi-turn conversation — all powered by **Groq (Llama 3.3 70B)** and built with **LangGraph + FastAPI + Streamlit**.

---

## 🏗️ Architecture

```
User (Streamlit UI)
        ↓
   FastAPI Backend (/chat endpoint)
        ↓
   LangGraph Agent
        ↓
   ┌────────────────────────────────┐
   │  classify_node                 │  ← Intent Classifier (Groq LLM)
   └────────┬───────────────────────┘
            │
     ┌──────┼──────────┐
     ↓      ↓          ↓
 greeting  product   lead_collection
  (Groq)   query      (rule-based
           (Groq +     state machine)
            FAISS         ↓
            RAG)      tools.py → leads.json
```

**Three intent classes:**
- `casual_greeting` → friendly LLM response
- `product_query` → RAG retrieval from knowledge base + LLM response
- `high_intent` → lead collection flow (name → email → platform)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq API — `llama-3.3-70b-versatile` (free) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (local, no API) |
| Vector Store | FAISS (in-memory) |
| Agent Framework | LangGraph (StateGraph) |
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Tunneling | localtunnel (npx) |
| Runtime | Google Colab |

---

## 📁 Project Structure

```
social_lead_agent/
├── agent.py              # LangGraph state machine — core agent logic
├── intent_classifier.py  # Groq-powered intent classification
├── rag.py                # FAISS vectorstore + HuggingFace embeddings
├── tools.py              # Lead capture → saves to leads/leads.json
├── main.py               # FastAPI backend (/chat, /leads endpoints)
├── app.py                # Streamlit frontend UI
├── AutoStream_Colab_groq.ipynb  # One-click Colab launcher
├── data/
│   └── knowledge_base.md # AutoStream product knowledge base
└── leads/
    └── leads.json        # Captured leads (auto-created)
```

---

## 🚀 How to Run (Google Colab)

### Prerequisites
- Google account with Drive
- Free Groq API key → [console.groq.com](https://console.groq.com) → API Keys → Create

### Steps

**1. Upload to Google Drive**
```
Upload the social_lead_agent/ folder to your Google Drive root
```

**2. Open the notebook**
```
Open AutoStream_Colab_groq.ipynb in Google Colab
```

**3. Run Cell 1** — installs all packages + localtunnel
```bash
pip install fastapi uvicorn langchain langgraph faiss-cpu streamlit \
    langchain-groq sentence-transformers ...
npm install -g localtunnel
```

**4. Run Cell 2** — mount Drive + paste your Groq API key
```python
GROQ_API_KEY = 'your_key_here'
```

**5. Run the launch cell** — starts backend, Streamlit, both tunnels, auto-patches URLs
```
✅ Backend up after 18s
✅ Streamlit started
🚀 OPEN THIS URL: https://xxxx.loca.lt
```

**6. Open the `loca.lt` URL** in your browser — the chatbot is live!

---

## 💬 Agent Capabilities

### Intent Detection
Every message is classified into one of three intents by the LLM before routing:

| Intent | Example | Action |
|---|---|---|
| `casual_greeting` | "hi", "how are you" | Friendly LLM response |
| `product_query` | "what's the Pro plan price?" | RAG + LLM response |
| `high_intent` | "I want to sign up" | Triggers lead collection |

### RAG Pipeline
- Knowledge base (`knowledge_base.md`) is chunked and embedded using `all-MiniLM-L6-v2`
- FAISS similarity search retrieves top-3 relevant chunks
- Retrieved context is injected into the LLM prompt
- Vectorstore is lazy-loaded and cached in memory

### Lead Collection Flow
Once high intent is detected, the agent collects details one at a time:
```
Agent: "That's awesome! Could I grab your name first?"
User:  "Manikant"
Agent: "Thanks! What's your email address?"
User:  "manikant@gmail.com"
Agent: "Perfect! Which platform do you mainly use?"
User:  "YouTube"
Agent: "You're all set, Manikant! Our team will reach out shortly."
→ Saved to leads/leads.json
```

### View Captured Leads
```
GET http://localhost:8000/leads
```

---

## 🔑 Environment Variables

| Variable | Description | Where to get |
|---|---|---|
| `GROQ_API_KEY` | Groq LLM API key | [console.groq.com](https://console.groq.com) |

---

## 📸 UI Features

- Dark branded UI with gradient header
- Intent badge in sidebar (color-coded per intent)
- Lead capture status panel showing collected details
- "Try These" sample prompts in sidebar
- Clear Chat button

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/chat` | Main chat endpoint |
| GET | `/leads` | View all captured leads |

### POST /chat — Request Body
```json
{
  "message": "I want to sign up for Pro",
  "history": [],
  "agent_state": {
    "collecting_lead": false,
    "lead_data": {},
    "lead_captured": false
  }
}
```

---

## ⚙️ Design Decisions

**Why Groq over OpenAI/Gemini?**
Groq's free tier offers 14,400 requests/day on Llama 3.3 70B with no credit card required — ideal for a demo assignment with zero cost.

**Why local HuggingFace embeddings for RAG?**
Removes the dependency on any embedding API key. `all-MiniLM-L6-v2` runs fully in Colab's RAM and is fast enough for a small knowledge base.

**Why LangGraph over a simple chain?**
LangGraph's StateGraph enables clean separation of intent routing, response generation, and stateful lead collection — making the agent extensible without spaghetti logic.

**Why FastAPI + Streamlit separately?**
Decouples the agent logic from the UI, making it easy to swap the frontend or expose the API to other clients.

---

## 👤 Author

**Manikant**
- GitHub: [github.com/Manikant-14](https://github.com/Manikant-14)
- LinkedIn: [linkedin.com/in/manikant14](https://linkedin.com/in/manikant14)
- Email: manikantmgr14@gmail.com

---

*Built for the ServiceHive × Inflx ML Intern Assignment — April 2026*
