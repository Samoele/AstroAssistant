import os
import json
from typing import List, Dict, Any, Optional 
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
    recent_history: List[Dict[str, str]] = None,
    lifestyle_summary: Optional[str] = None,
    profile_data: Optional[Dict[str, Any]] = None,
) -> AgentResponse:
    system_instruction = build_system_prompt(lifestyle_summary, profile_data)
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

def build_system_prompt(lifestyle_summary: Optional[str] = None, profile_data: Optional[Dict[str, Any]] = None) -> str:
    summary_text = lifestyle_summary or "No habit data available yet."
    profile = profile_data or {}
    
    avatar_name = profile.get("avatar_name", "Astro")
    user_name = profile.get("display_name", "User")
    archetype = profile.get("lifestyle_archetype", "High-Energy Builder")
    water_goal = profile.get("daily_water_target", 3.0)
    sleep_goal = profile.get("daily_sleep_target", 7.5)
    workout_goal = profile.get("weekly_workout_target", 4)
    goals = ", ".join(profile.get("primary_goals", []))

    return f"""You are {avatar_name}, an intelligent, witty, and supportive 2D AI Lifestyle Companion for {user_name}.
User Persona Archetype: {archetype}
User Custom Targets:
- Daily Hydration Target: {water_goal} Liters
- Daily Sleep Target: {sleep_goal} Hours
- Weekly Workout Target: {workout_goal} Sessions
- Primary Focus Goals: {goals}

CURRENT 7-DAY LIFESTYLE SNAPSHOT:
{summary_text}

AGENT BEHAVIORS:
1. Actively reference trends and hold {user_name} accountable against THEIR exact customized targets above.
2. Empathize when sleep is under {sleep_goal}h or cheer them when they hit hydration ({water_goal}L) or workout targets ({workout_goal}/week).
3. Keep responses punchy and motivating: 2 to 3 sentences maximum.
4. Extract any quantifiable metrics mentioned in the current user message into habit_extracted (category, value, unit, notes).

CRITICAL FORMAT REQUIREMENT:
Return ONLY a valid JSON object matching the standard agent schema.
"""