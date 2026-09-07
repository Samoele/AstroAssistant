# AstroAssistant
Astro Assistant for daily tasks and conversation


commands:
Run uvicorn backend server
uvicorn app.main:app --reload --port 8000  

Run react frontend server
npm run dev

File structure:
ai-lifestyle-companion/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── chat.py
│   │   │       │   └── lifestyle.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   └── memory_service.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── public/
    │   ├── icons/          # PWA iOS icons (192x192, 512x512)
    │   └── sprites/        # 2D character emotion assets
    ├── src/
    │   ├── components/
    │   │   ├── Avatar/
    │   │   │   └── AvatarCanvas.tsx
    │   │   └── Chat/
    │   │       ├── ChatWindow.tsx
    │   │       └── MessageBubble.tsx
    │   ├── types/
    │   │   └── index.ts
    │   ├── App.tsx
    │   └── main.tsx
    ├── package.json
    ├── vite.config.ts
    └── tailwind.config.js

================================================================================
PROJECT ARCHITECTURAL BLUEPRINT & ROADMAP: AI LIFESTYLE COMPANION (2D AVATAR)
================================================================================

1. EXECUTIVE SUMMARY & PROJECT VISION
--------------------------------------------------------------------------------
The objective is to engineer a personalized, proactive 2D AI Companion web application
(Progressive Web App - PWA) capable of learning user habits, daily routines, nutritional
choices, fitness metrics, and schedule constraints. The assistant provides conversational
advice, contextual reminders, and emotive 2D avatar feedback (dynamic sprite/SVG/canvas 
expressions) while operating entirely on free-tier, modern open-source technologies.

The system features:
- A reactive, mobile-optimized PWA frontend (React + Vite + Tailwind CSS / Canvas).
- A robust, modular asynchronous backend (FastAPI / Python).
- Multi-tier memory architecture (Short-term working memory, Long-term semantic memory,
  and episodic graph/vector storage).
- Free-tier / Local LLM integration (Ollama / HuggingFace / Groq free tier / Gemini API free tier)
  combined with Retrieval-Augmented Generation (RAG) and parameter-efficient fine-tuning (PEFT/LoRA).
- 2D animated avatar rendering engine with state-driven emotional animations.


2. CONCEPTUAL DEEP DIVE: "TRAINING FROM SCRATCH" VS. MODERN ARCHITECTURAL REALITY
--------------------------------------------------------------------------------
In AI engineering, there is a fundamental distinction between training a foundational 
Large Language Model from scratch and building a personalized, domain-adapted agent:

A. Training a Base LLM from Scratch:
   - Requires terabytes of tokens, clusters of H100 GPUs ($50k-$1M+ compute), and months
     of pre-training on general language syntax.
   - For an individual assistant, pre-training from scratch is neither cost-effective nor
     optimal because the base model does not know general world facts or grammar without it.

B. The Modern 4-Pillar Architecture for Personalized Agents:
   1. Base Open-Weights Model:
      - Start with high-performing open models (e.g., Llama-3 8B, Mistral-7B, Phi-3 Mini)
        running locally via Ollama or via high-speed free inference APIs (Groq Free Tier,
        HuggingFace Inference API, Gemini API Free Tier).
   2. Retrieval-Augmented Generation (RAG) & Vector Database:
      - Store external static datasets (USDA Food Data, workout routines, weather history)
        in a local vector database (ChromaDB / FAISS). The agent queries this data in real-time.
   3. Dynamic Long-Term Memory & Episodic Profiling:
      - Extract entities, habits, preferences, and daily logs into a structured SQLite/PostgreSQL
        database and semantic vector store. When you speak, relevant past facts are retrieved into
        the system prompt context.
   4. Parameter-Efficient Fine-Tuning (PEFT / LoRA / QLoRA):
      - Fine-tune a lightweight adapter on Google Colab (Free T4 GPU) using your accumulated
        chat logs and personality datasets so the model adopts custom tone, emotional cadence,
        and unique behavioral cues without retraining the entire neural network.


3. FULL TECH STACK RECOMMENDATION (100% FREE & MODERN)
--------------------------------------------------------------------------------
[Frontend]:
- Framework: React (v18+) with Vite (ultra-fast HMR, lightweight bundling).
- Language: TypeScript (strict type safety for complex avatar states and chat schemas).
- Styling & Animations: Tailwind CSS + Framer Motion (smooth UI transitions).
- Avatar Rendering: HTML5 Canvas / PixiJS / Spine 2D Web Runtime or SVG Sprite Sheet Player.
- Mobile/PWA Layer: Vite PWA Plugin (`vite-plugin-pwa`) with Service Workers and Web App Manifest
  for seamless iOS "Add to Home Screen" standalone app experience (zero browser chrome, native feel).

[Backend & API]:
- Runtime/Framework: Python 3.11+ with FastAPI (Asynchronous ASGI, high throughput, auto-generated OpenAPI docs).
- Asynchronous Task Queue / Scheduler: APScheduler or Asyncio Background Tasks (for daily proactive check-ins).
- Tool/Agent Framework: LangChain / LlamaIndex or Custom Lightweight Agent Loop.

[Database & Storage]:
- Relational / Structured State: SQLite (Local zero-config) or PostgreSQL (Supabase Free Tier / Neon Free Tier).
- Vector Database (Memory & RAG): ChromaDB (Embedded local vector store, 100% free) or FAISS.
- Embeddings Model: `all-MiniLM-L6-v2` or `bge-small-en-v1.5` via HuggingFace `sentence-transformers` (runs locally on CPU).

[AI Model & Inference]:
- Local Option: Ollama running `llama3:8b` or `phi3:mini` (100% free, offline, private).
- Cloud Free Tier: Groq API (ultra-fast Llama-3 inference, generous free tier) or Google Gemini API (free tier).

[Deployment / Hosting]:
- Frontend: Vercel / Cloudflare Pages / Netlify (Free unlimited static hosting).
- Backend: Render Free Web Service / Railway Free Trial / Fly.io / Self-hosted via ngrok / Cloudflare Tunnels.


4. SYSTEM ARCHITECTURE & DATA FLOW
--------------------------------------------------------------------------------
+-------------------------------------------------------------------------------+
|                             iOS / Client Device                               |
|   (Progressive Web App - Add to Home Screen, Standalone Canvas & Chat UI)     |
+---------------------------------------+---------------------------------------+
                                        | (HTTPS / WebSocket / REST)
                                        v
+-------------------------------------------------------------------------------+
|                            FastAPI Backend Server                             |
|                                                                               |
|   1. Request Ingestion & Session Handler                                      |
|   2. Emotion / Sentiment Extractor (Determines Avatar State)                  |
|   3. Memory Retrieval Engine (Past interactions, user preferences)            |
|   4. External Tools & RAG:                                                    |
|      - Open-Meteo API (Free Real-time Weather)                                |
|      - USDA FoodData / OpenFoodFacts (Nutrition Vector DB)                     |
|      - Fitness & Habit Tracker DB                                             |
|   5. LLM Prompt Synthesis & Generation (Ollama / Groq / Gemini)               |
|   6. Response Streamer & Memory Writer (Updates habit history in DB)          |
+---------------------------------------+---------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
  +-----------------------------+               +-----------------------------+
  |    SQLite / PostgreSQL      |               |     ChromaDB Vector Store   |
  |  - User Profile & Goals     |               |  - Semantic Past Memories   |
  |  - Daily Food & Water Logs  |               |  - Nutritional Knowledge    |
  |  - Habit Streaks & Tasks    |               |  - Workout & Health Rules   |
  +-----------------------------+               +-----------------------------+


5. AVATAR EMOTION & ANIMATION SUBSYSTEM
--------------------------------------------------------------------------------
The 2D character avatar reflects dynamic emotional states driven by backend classification:
- Emotional States: Neutral, Enthusiastic/Excited, Encouraging, Grumpy/Stern (if goals missed),
  Empathetic/Sad, Curious, Thinking.
- Architecture:
  1. Sentiment & Mood Tagging: Backend returns a structured JSON schema:
     {
       "response_text": "Great job crushing your 5k run today! Let's log your dinner.",
       "avatar_emotion": "excited",
       "animation_trigger": "jump_celebrate",
       "suggested_actions": ["Log Meal", "View Streak"]
     }
  2. Frontend Sprite Controller: The Canvas/SVG engine listens for state transitions and
     interpolates sprite keyframes or triggers CSS-based micro-animations (bouncing, blinking,
     eye direction, mouth lip-sync flapping).


6. MVP BREAKDOWN & ESTIMATED TIMEFRAMES
--------------------------------------------------------------------------------
PHASE 1: Core Foundation & Chat Engine (Weeks 1 - 2)
- Set up React + Vite + TypeScript PWA template with iOS manifest configuration.
- Implement FastAPI backend with chat endpoint connected to LLM (Ollama or Groq/Gemini free tier).
- Set up SQLite schema for basic user profiling (name, basic goals, conversation history).
- Verify iPhone installation via Chrome/Safari "Add to Home Screen".

PHASE 2: 2D Avatar Integration & State Machine (Weeks 3 - 4)
- Create 2D character asset slots (SVG/Sprite sheets for 5-6 core emotions).
- Build Canvas/Sprite component in React capable of switching animations based on backend JSON tags.
- Implement streaming text response with synchronized visual state transitions.

PHASE 3: Memory Architecture & Daily Lifestyle Tracking (Weeks 5 - 6)
- Integrate ChromaDB for semantic memory (extracting user preferences, favorite foods, wake times).
- Build tools/endpoints for logging meals, habits, sleep, and workouts.
- Integrate free external APIs (Open-Meteo for local weather-aware suggestions).

PHASE 4: Proactive Notifications, Analytics & Custom Fine-Tuning (Weeks 7 - 8)
- Implement proactive scheduled reminders/alerts (morning briefing, evening recap).
- Implement LoRA fine-tuning pipeline on Google Colab for hyper-personalized character voice.
- Production deployment on free hosting tiers (Vercel + Render/Cloudflare Tunnel).


7. EDUCATIONAL LEARNING MODULES (CURRICULUM)
--------------------------------------------------------------------------------
As we build this project step-by-step, we will master:
1. Low-Level Asynchronous Backend Development (FastAPI, Pydantic, Python asyncio).
2. Agent Architectures & Vector Search (Embeddings, cosine similarity, ChromaDB, RAG pipeline).
3. PWA & Web Animation Engineering (Service workers, offline caching, 2D Canvas rendering).
4. Prompt Engineering & Structured Outputs (JSON mode, function calling, tool use).
5. Dataset Preparation & LoRA Fine-Tuning (Google Colab, HuggingFace TRL, Unsloth).