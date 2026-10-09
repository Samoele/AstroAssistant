================================ FRONTEND (REACT + VITE) ================================
  
       User types: "Ran 4 miles in 35 mins!"
                         │
                         ▼
             +-----------------------+
             |   frontend/src/       |
             |   ChatWindow.tsx      |
             +-----------┬-----------+
                         │ User submits message
                         ▼
             +-----------------------+
             |   frontend/src/       |
             |   services/api.ts     |  ──► POST /api/v1/chat  { message, user_id }
             +-----------┬-----------+
                         │
  ═══════════════════════╪══════════════════ HTTP BOUNDARY ════════════════════════════════
                         │
  =======================│=========== BACKEND (FASTAPI + SQLITE) =========================
                         ▼
             +-----------------------+
             |    backend/app/       |
             |    main.py            |  ──► Routes traffic to api_router (/api/v1)
             +-----------┬-----------+
                         │
                         ▼
  +---------------------------------------------------------------------------------------+
  | backend/app/api/v1/endpoints/chat.py                                                  |
  |                                                                                       |
  |  Step 1: Save incoming user message to SQLite session                                 |
  |  Step 2: SELECT last 6 messages FROM conversation_messages WHERE user_id = '...'      |
  |  Step 3: Hand message + fetched history to LLM Service                                |
  +------------------------------------------┬--------------------------------------------+
                                             │
                                             ▼
  +---------------------------------------------------------------------------------------+
  | backend/app/services/llm_service.py                                                   |
  |                                                                                       |
  |  • Injects System Prompt: "You are Astro... track habits... output JSON"              |
  |  • Injects DB History (preserves multi-turn context)                                  |
  |  • Injects Current User Query                                                         |
  +------------------------------------------┬--------------------------------------------+
                                             │
                                             ▼
  ══════════════════════════════════════ GROQ CLOUD LPU ══════════════════════════════════
  
             +-------------------------------------------------------+
             | Groq Inference Engine (llama-3.1-8b-instant / Qwen)   |
             | Sub-second inference (~400ms) with strict JSON schema |
             +---------------------------┬---------------------------+
                                         │
  ═══════════════════════════════════════╪════════════════════════════════════════════════
                                         │
                                         ▼
  +---------------------------------------------------------------------------------------+
  | Output Parsed into Pydantic AgentResponse:                                            |
  |                                                                                       |
  |  {                                                                                    |
  |    "response_text": "Incredible pace on that 4-mile run! Logging it now.",            |
  |    "avatar_state": { "emotion": "excited", "animation": "reacting" },                 |
  |    "habit_extracted": { "category": "workout", "value": 4.0, "unit": "miles" }        |
  |  }                                                                                    |
  +------------------------------------------┬--------------------------------------------+
                                             │
                                             ▼
  +---------------------------------------------------------------------------------------+
  | Database Commit (backend/app/db/):                                                    |
  |                                                                                       |
  |  • INSERT INTO conversation_messages (role="assistant", content=..., emotion=...)     |
  |  • INSERT INTO habit_logs (category="workout", value=4.0, unit="miles", ...)         |
  |  • await db.commit()                                                                  |
  +------------------------------------------┬--------------------------------------------+
                                             │
                                             ▼ Returns AgentResponse JSON
  ═══════════════════════════════════════╪════════════════════════════════════════════════
                                         │
  =======================================▼================================================
  
             +-----------------------+
             |   frontend/src/       |
             |   App.tsx             |
             +-----------┬-----------+
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
+------------------+           +------------------+
|  ChatWindow.tsx  |           | AvatarCanvas.tsx |
|                  |           |                  |
| Renders Astro's  |           | Triggers 64x64   |
| dialogue bubble  |           | "excited" sprite |
| with timestamp   |           | & "reacting" row |
+------------------+           +------------------+














New pipeline of Astro Thourhgt.


[ User Message: "I feel sluggish today" ]
                                     │
                                     ▼
                      +-----------------------------+
                      |   1. Aggregation Engine     |
                      |   (SQL Temporal Queries)    |
                      +--------------┬--------------+
                                     │
                                     ▼ Computes:
                      • Workouts logged past 7 days (count & volume)
                      • Mean sleep duration (hours/night)
                      • Hydration totals & Nutrition consistency
                                     │
                                     ▼
                      +-----------------------------+
                      |   2. Semantic Context       |
                      |   Synthesizer               |
                      +--------------┬--------------+
                                     │
                                     ▼ Outputs formatted string:
    "LIFESTYLE SNAPSHOT (Past 7 Days):
     - Workouts: 4 completed (Total volume: 16.5 miles)
     - Sleep: 3 records (Average: 5.8 hrs/night -> DEFICIT ALERT)
     - Hydration: 4.5 liters logged total"
                                     │
                                     ▼
                      +-----------------------------+
                      |   3. System Prompt Dynamic  |
                      |   Injection (/api/v1/chat)  |
                      +--------------┬--------------+
                                     │
                                     ▼ Passes to Groq LPU
                      Astro assesses: "Sluggish feeling correlates
                      with your 5.8h sleep deficit. Scold or empathize."