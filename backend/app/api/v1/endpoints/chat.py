from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import ConversationMessage, HabitLog, UserProfile
from app.models.schemas import ChatRequest, AgentResponse, UserProfileResponse, UserProfileUpdate
from app.services.llm_service import generate_companion_response

router = APIRouter()

@router.get("/history")
async def get_history(
    user_id: str = "user_default", 
    limit: int = 30, 
    db: AsyncSession = Depends(get_db)
):
    #Fetches the latest 'limit' messages ordered chronologically
    #so the UI displays the recent conversation without performance degradation.
    # 1. Fetch the newest records first using DESC + LIMIT
    result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.user_id == user_id)
        .order_by(ConversationMessage.timestamp.desc())
        .limit(limit)
    )
    records = result.scalars().all()

    # 2. Reverse the list so messages display chronologically (oldest to newest)
    chronological_records = list(reversed(records))

    return [
        {
            "id": str(r.id),
            "role": r.role,
            "text": r.content,
            "emotion": r.emotion
        }
        for r in chronological_records
    ]

@router.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    # 1. Fetch recent conversation turns from DB for contextual memory
    history_query = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.user_id == request.user_id)
        .order_by(ConversationMessage.timestamp.desc())
        .limit(20)  # Fetch last 20 messages for context
    )
    db_history = list(reversed(history_query.scalars().all()))
    formatted_history = [{"role": msg.role, "content": msg.content} for msg in db_history]

    # 2. Persist user message to SQLite
    user_msg_record = ConversationMessage(
        user_id=request.user_id,
        role="user",
        content=request.message
    )
    db.add(user_msg_record)

    # 3. Query LLM with injected DB history
    profile = await get_or_create_profile(request.user_id, db)
    profile_dict = {
        "avatar_name": profile.avatar_name,
        "display_name": profile.display_name,
        "lifestyle_archetype": profile.lifestyle_archetype,
        "daily_water_target": profile.daily_water_target,
        "daily_sleep_target": profile.daily_sleep_target,
        "weekly_workout_target": profile.weekly_workout_target,
        "primary_goals": profile.primary_goals or [],
    }

    response = generate_companion_response(
        user_message=request.message,
        recent_history=formatted_history,
        lifestyle_summary=lifestyle_summary,
        profile_data=profile_dict
    )

    # 4. Persist assistant reply to SQLite
    assistant_msg_record = ConversationMessage(
        user_id=request.user_id,
        role="assistant",
        content=response.response_text,
        emotion=response.avatar_state.emotion.value
    )
    db.add(assistant_msg_record)

    # 5. Persist extracted habit metrics if present
    if response.habit_extracted and response.habit_extracted.category:
        habit_record = HabitLog(
            user_id=request.user_id,
            category=response.habit_extracted.category,
            value=response.habit_extracted.value,
            unit=response.habit_extracted.unit,
            notes=response.habit_extracted.notes or request.message
        )
        db.add(habit_record)

    await db.commit()
    return response


async def get_or_create_profile(user_id: str, db: AsyncSession) -> UserProfile:
    """Fetches user profile or seeds default values if first time."""
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalars().first()
    if not profile:
        profile = UserProfile(
            user_id=user_id,
            display_name="User",
            avatar_name="Astro",
            lifestyle_archetype="High-Energy Builder",
            daily_water_target=3.0,
            daily_sleep_target=7.5,
            weekly_workout_target=4,
            primary_goals=[
                "Hit daily hydration target",
                "Maintain consistent sleep schedule",
                "Hit weekly workout consistency"
            ]
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(user_id: str = "user_default", db: AsyncSession = Depends(get_db)):
    profile = await get_or_create_profile(user_id, db)
    return profile

@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    update_data: UserProfileUpdate,
    user_id: str = "user_default",
    db: AsyncSession = Depends(get_db)
):
    profile = await get_or_create_profile(user_id, db)
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(profile, key, value)
        
    await db.commit()
    await db.refresh(profile)
    return profile