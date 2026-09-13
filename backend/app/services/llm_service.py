import os
import json
from dotenv import load_dotenv
from groq import Groq
from app.models.schemas import AgentResponse, AvatarState, EmotionEnum, AnimationStateEnum

load_dotenv()

# Initialize Groq Cloud Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# High-throughput production model on Groq LPU
MODEL_NAME = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """
You are Astro, an emotionally expressive and supportive 2D AI Lifestyle Companion.
Analyze the user's message, encourage healthy daily habits, and select the corresponding avatar reaction.

You must ALWAYS respond with a JSON object matching this schema:
{
  "response_text": "Your conversational dialogue to the user.",
  "avatar_emotion": "neutral" | "happy" | "excited" | "grumpy" | "sad" | "thinking",
  "animation_trigger": "idle" | "talking" | "reacting",
  "mood_reason": "Brief explanation of why you chose this emotion.",
  "suggested_actions": ["Quick action 1", "Quick action 2"]
}

EMOTION RULES:
- "excited": User achieves a goal, works out, eats clean, or shows discipline.
- "happy": Friendly greetings, positive progress, steady habits.
- "grumpy": Skipping workouts, eating junk food, late bedtimes, breaking habits.
- "sad": Feeling exhausted, stressed, down, or overwhelmed.
- "thinking": Nutrition math, planning schedules, or analyzing routines.
- "neutral": Routine factual questions.

ANIMATION RULES:
- "reacting": Celebrations, surprises, or strong emotional shifts.
- "talking": Standard conversational responses.
- "idle": Listening or quiet statements.
"""

def generate_companion_response(user_message: str) -> AgentResponse:
    """
    Calls Groq LPU endpoints for sub-second, hardware-enforced JSON inference.
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.6,
            max_completion_tokens=250
        )

        raw_text = completion.choices[0].message.content
        data = json.loads(raw_text)

        raw_emotion = data.get("avatar_emotion", "neutral").lower()
        raw_animation = data.get("animation_trigger", "talking").lower()

        try:
            emotion = EmotionEnum(raw_emotion)
        except ValueError:
            emotion = EmotionEnum.NEUTRAL

        try:
            animation = AnimationStateEnum(raw_animation)
        except ValueError:
            animation = AnimationStateEnum.TALKING

        return AgentResponse(
            response_text=data.get("response_text", "I'm right here with you!"),
            avatar_state=AvatarState(
                emotion=emotion,
                animation=animation,
                mood_reason=data.get("mood_reason", "Habit evaluation")
            ),
            suggested_actions=data.get("suggested_actions", ["Track Progress", "Set Reminder"])
        )

    except Exception as e:
        print(f"[Groq Service Error]: {e}")
        return AgentResponse(
            response_text="I had a slight connection blip, but I'm still listening!",
            avatar_state=AvatarState(
                emotion=EmotionEnum.THINKING,
                animation=AnimationStateEnum.IDLE,
                mood_reason="API fallback"
            ),
            suggested_actions=["Try again"]
        )