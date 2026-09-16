import os
import json
from typing import List, Dict   
from dotenv import load_dotenv
from groq import Groq
from app.models.schemas import AgentResponse, AvatarState, EmotionEnum, AnimationStateEnum, ChatHistoryMessage, HabitExtracted

load_dotenv()

# Initialize Groq Cloud Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Fast Groq LPU model with reliable JSON mode support
# (the "compound" models are agentic/tool-use models and don't
# consistently honor response_format={"type": "json_object"})
MODEL_NAME = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """You are Astro, an intelligent 2D AI Lifestyle Companion with a distinct personality.
You track workouts, food, water, and sleep, and hold the user accountable.

CRITICAL INSTRUCTIONS:
1. Habit Extraction: Whenever the user mentions a lifestyle metric (e.g., ran 3 miles, slept 5 hours, drank 2L water, ate 600 kcal), extract it into habit_extracted. If no metric is present, set habit_extracted to null.
2. Output JSON ONLY adhering to this format:
{
  "response_text": "Your direct message to the user.",
  "avatar_emotion": "neutral" | "happy" | "excited" | "grumpy" | "sad" | "thinking",
  "animation_trigger": "idle" | "talking" | "reacting",
  "mood_reason": "Short reason for this state.",
  "suggested_actions": ["Action 1", "Action 2"],
  "habit_extracted": {
    "category": "workout" | "nutrition" | "sleep" | "water" | null,
    "value": float or null,
    "unit": string or null,
    "notes": string or null
  }
}
"""

def generate_companion_response(
    user_message: str,
    recent_history: List[Dict[str, str]] = None
) -> AgentResponse:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if recent_history:
        for turn in recent_history:
            messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=500
        )

        data = json.loads(completion.choices[0].message.content.strip())

        raw_emotion = str(data.get("avatar_emotion", "neutral")).lower()
        raw_animation = str(data.get("animation_trigger", "talking")).lower()

        try:
            emotion = EmotionEnum(raw_emotion)
        except ValueError:
            emotion = EmotionEnum.NEUTRAL

        try:
            animation = AnimationStateEnum(raw_animation)
        except ValueError:
            animation = AnimationStateEnum.TALKING

        raw_habit = data.get("habit_extracted")
        habit_obj = None
        if raw_habit and raw_habit.get("category"):
            habit_obj = HabitExtracted(
                category=raw_habit.get("category"),
                value=raw_habit.get("value"),
                unit=raw_habit.get("unit"),
                notes=raw_habit.get("notes")
            )

        return AgentResponse(
            response_text=data.get("response_text", "Got it!"),
            avatar_state=AvatarState(
                emotion=emotion,
                animation=animation,
                mood_reason=data.get("mood_reason", "Habit observation")
            ),
            suggested_actions=data.get("suggested_actions", ["Check habits"]),
            habit_extracted=habit_obj
        )

    except Exception as e:
        print(f"[LLM Service Error]: {e}")
        return AgentResponse(
            response_text="I noted that down!",
            avatar_state=AvatarState(
                emotion=EmotionEnum.THINKING,
                animation=AnimationStateEnum.IDLE,
                mood_reason="Fallback"
            ),
            suggested_actions=["Continue"]
        )