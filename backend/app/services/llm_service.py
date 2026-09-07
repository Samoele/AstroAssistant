import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.models.schemas import AgentResponse, AvatarState, EmotionEnum, AnimationStateEnum

load_dotenv()

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are a proactive, supportive, and emotionally expressive 2D AI Lifestyle Companion.
Your job is to talk with the user, encourage healthy daily habits, track their choices (food, sleep, workouts),
and guide them to meet their life goals.

CRITICAL INSTRUCTION - STRUCTURED OUTPUT:
You must ALWAYS respond with a JSON object matching this schema:
{
  "response_text": "Your conversational dialogue to the user.",
  "avatar_emotion": "neutral" | "happy" | "excited" | "grumpy" | "sad" | "thinking",
  "animation_trigger": "idle" | "talking" | "reacting",
  "mood_reason": "Brief explanation of why you chose this emotion based on user behavior.",
  "suggested_actions": ["Quick action 1", "Quick action 2"]
}

EMOTION GUIDELINES:
- "excited": User achieves a goal, exercises, eats healthy, or shows discipline.
- "happy": Welcoming the user, general friendly check-ins, or positive progress.
- "grumpy": User skips workouts, eats junk food, sleeps late, or breaks commitments.
- "sad": User feels stressed, down, sick, or discouraged.
- "thinking": Analyzing routines, calculating nutrition, or planning schedules.
- "neutral": Routine factual questions or standard queries.

ANIMATION GUIDELINES:
- Use "reacting" for celebratory news, shock, or high-energy moments.
- Use "talking" for standard conversational advice.
- Use "idle" when keeping calm or listening.
"""

def generate_companion_response(user_message: str) -> AgentResponse:
    """
    Sends user input to Google Gemini and parses the structured response into an AgentResponse schema.
    """
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.7,
            )
        )

        data = json.loads(response.text)

        emotion = EmotionEnum(data.get("avatar_emotion", "neutral"))
        animation = AnimationStateEnum(data.get("animation_trigger", "talking"))
        mood_reason = data.get("mood_reason", "Standard interaction")
        response_text = data.get("response_text", "I'm right here with you!")
        suggested_actions = data.get("suggested_actions", ["Log Activity", "Check Goals"])

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
        print(f"[Gemini Service Error]: {e}")
        return AgentResponse(
            response_text="I'm having a little trouble connecting right now, but I'm still listening!",
            avatar_state=AvatarState(
                emotion=EmotionEnum.THINKING,
                animation=AnimationStateEnum.IDLE,
                mood_reason="API error fallback"
            ),
            suggested_actions=["Try again"]
        )