[ User Message ] 
       |
       v
[ FastAPI Agent Service ]
       |
       +---> 1. Fetch User Profile & Goals (SQLite: "Goal is 2000 kcal, workout 4x/week")
       +---> 2. Query Long-Term Memory (ChromaDB: Past preferences, habits, recent chat history)
       +---> 3. Inject Context into System Prompt
       |
       v
[ Free-Tier LLM (Groq / Gemini / Ollama) via Structured Output / JSON Mode ]
       |
       |  LLM Prompt: "Analyze the user's lifestyle behavior against their goals.
       |  Determine emotional reaction (neutral, happy, grumpy, excited, sad, thinking),
       |  animation movement, and dialogue response."
       |
       v
[ LLM Outputs Validated JSON matching AgentResponse Schema ]
       |
       v
[ React Frontend updates Avatar Expression & animates text bubble ]