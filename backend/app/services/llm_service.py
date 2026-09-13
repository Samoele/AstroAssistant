import os
import json
from typing import List
from dotenv import load_dotenv
from groq import Groq
from app.models.schemas import AgentResponse, AvatarState, EmotionEnum, AnimationStateEnum, ChatHistoryMessage

load_dotenv()

# Initialize Groq Cloud Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Fast Groq LPU model with reliable JSON mode support
# (the "compound" models are agentic/tool-use models and don't
# consistently honor response_format={"type": "json_object"})
MODEL_NAME = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """You are Astro, an intelligent, empathetic, and witty 2D AI Lifestyle Companion.
You live on the user's screen and help them track their habits, health, workouts, and routines.

CORE BEHAVIORS:
1. Actively track and comment on habits mentioned (workouts, sleep, food, water, productivity).
2. Reference previous statements from the conversation history when relevant.
3. Keep responses punchy and expressive: 1 to 3 short sentences max.

OUTPUT INSTRUCTION:
You must respond ONLY with a valid JSON object matching this schema:
{
  "response_text": "Your short companion dialogue.",
  "avatar_emotion": "neutral" | "happy" | "excited" | "grumpy" | "sad" | "thinking",
  "animation_trigger": "idle" | "talking" | "reacting",
  "mood_reason": "Short reason for your emotion choice.",
  "suggested_actions": ["Action 1", "Action 2"]
}

EMOTIONS: neutral, happy, excited, grumpy, sad, thinking.
ANIMATIONS: idle, talking, reacting.
"""

def generate_companion_response(
    user_message: str, 
    history: List[ChatHistoryMessage] = None
) -> AgentResponse:
    """
    Processes user message with context history using Groq hardware JSON inference.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Inject last 8 turns of conversation memory for multi-turn awareness
    if history:
        for turn in history[-8:]:
            valid_role = "assistant" if turn.role == "assistant" else "user"
            messages.append({"role": valid_role, "content": turn.content})

    # If the user's latest message wasn't already at the end of history, append it
    if not history or history[-1].content != user_message:
        messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            response_format={"type": "json_object"},
            reasoning_effort="low",
            temperature=0.6,
            max_completion_tokens=300
        )

        raw_json = completion.choices[0].message.content.strip()
        if raw_json.startswith("```"):
            raw_json = raw_json.strip("`")
            if raw_json.lower().startswith("json"):
                raw_json = raw_json[4:]
            raw_json = raw_json.strip()
        data = json.loads(raw_json)

        # Robust enum conversion with safe defaults
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

        mood_reason = data.get("mood_reason", "Agent habit evaluation")
        response_text = data.get("response_text", "I'm listening and tracking with you!")
        suggested_actions = data.get("suggested_actions", ["Log Habit", "Drink Water"])

        return AgentResponse(
            response_text=response_text,
            avatar_state=AvatarState(
                emotion=emotion,
                animation=animation,
                mood_reason=mood_reason
            ),
            suggested_actions=suggested_actions
        )

    except Exception as e:
        print(f"\n[!!! Groq agent error]: {repr(e)}\n")
        if 'raw_json' in locals():
            print(f"[Raw output received from model was]:\n{raw_json}\n")
        return AgentResponse(
            response_text="I'm adjusting my sensors. Tell me more about what you're up to!",
            avatar_state=AvatarState(
                emotion=EmotionEnum.THINKING,
                animation=AnimationStateEnum.IDLE,
                mood_reason="Fallback"
            ),
            suggested_actions=["Try again"]
        )