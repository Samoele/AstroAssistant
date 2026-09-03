from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class EmotionEnum(str, Enum):
    """
    Core emotional states representing the assistant's psychological state
    evaluated from user habits, messages, and progress.
    """
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    GRUMPY = "grumpy"
    

class AnimationStateEnum(str, Enum):
    """
    Core animation states representing the assistant's visual behavior
    evaluated from user interactions and emotional state.
    """
    IDLE = "idle"
    WAVING = "waving"
    THINKING = "thinking"
    TALKING = "talking"
    REACTING = "reacting"

class AvatarState(BaseModel):
    """
    Combined state payload defining how the character should present visually.
    """
    emotion: EmotionEnum = Field(
        default=EmotionEnum.NEUTRAL,
        description="The emotional expression of the avatar"
    )
    animation: AnimationStateEnum = Field(
        default=AnimationStateEnum.IDLE,
        description="The physical animation of the avatar"
    )
    mood_reason: Optional[str] = Field(
        default=None,
        description="The reason for the avatar's current mood"
    )

class ChatRequest(BaseModel):
    """
    Incoming payload from the React frontend.
    """
    user_id: str= Field(default="user_default")
    message: str = Field(..., min_length=1, description="Message typed by the user")


class AgentResponse(BaseModel):
    """
    Outgoing payload to the React frontend.
    """
    response_text: str= Field(..., description="Response message spoken from the agent")
    avatar_state: AvatarState = Field(..., description="The visual state of the avatar")
    suggested_actions: List[str] = Field(
        default_factory=list, 
        description="Quick-reply action buttons (e.g., 'Log Meal', 'View Goals')"
    )


