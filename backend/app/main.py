from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import (EmotionEnum, AnimationStateEnum, AvatarState, ChatRequest, AgentResponse)
#import enum classes for avatar emotional and visual states

# Create FastAPI instance
app = FastAPI(
    title = "Astro AI API",
    description = "Astro assistant backend API for status and 2D states",
    version = "0.1.0",
)

#Configure CORS Middleware (connection allowed between backend port and frontend port)
origins = ["http://localhost:5173", 
           "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of allowed origins for CORS
    allow_credentials=True, # Allow credentials (cookies, authorization headers, etc.)
    allow_methods=["*"], # Allow all HTTP methods
    allow_headers=["*"], # Allow all headers
)

#first route decorator
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the Astro AI Assistant API",
        "version": "0.1.0"
    }




# @app.get binds HTTP GET requests targeting the '/health' URL to this function
@app.get("/health", tags=["Health System Check"])
async def health_check():
    '''
    Health check endpoint to verify the API is running.
    Returns a JSON response indicating the API status.
    '''
    return {
        "status": "online",
        "message": "Astro API is online and running smoothly."
    }


@app.post("/api/v1/mock-avatar-state", response_model=AgentResponse, tags=["Avatar"])
async def mock_avatar_reaction(request: ChatRequest):
    """
    Test endpoint returning a dynamic emotional state based on user keywords.
    """
    user_msg = request.message.lower()

    # Simple behavior-to-emotion heuristic test
    if "workout" in user_msg or "gym" in user_msg:
        emotion = EmotionEnum.EXCITED
        animation = AnimationStateEnum.REACTING
        text = "Awesome work! Getting your body moving is huge for your daily streak!"
        reason = "User completed or mentioned physical activity"
    elif "cake" in user_msg or "junk" in user_msg or "slept late" in user_msg:
        emotion = EmotionEnum.GRUMPY
        animation = AnimationStateEnum.TALKING
        text = "Again? You told me you wanted to build better habits! Let's get back on track."
        reason = "User deviated from target lifestyle goals"
    elif "sad" in user_msg or "tired" in user_msg:
        emotion = EmotionEnum.SAD
        animation = AnimationStateEnum.IDLE
        text = "I'm sorry you're feeling down. Take a deep breath, I'm here with you."
        reason = "User expressed low energy or distress"
    else:
        emotion = EmotionEnum.HAPPY
        animation = AnimationStateEnum.TALKING
        text = f"I noted that: '{request.message}'. What else is on the schedule today?"
        reason = "Standard interaction"

    return AgentResponse(
        response_text=text,
        avatar_state=AvatarState(
            emotion=emotion,
            animation=animation,
            mood_reason=reason
        ),
        suggested_actions=["Log Meal", "Drink Water", "Update Routine"]
    )




