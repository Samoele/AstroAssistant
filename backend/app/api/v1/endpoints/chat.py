from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import ConversationMessage, HabitLog
from app.models.schemas import ChatRequest, AgentResponse
from app.services.llm_service import generate_companion_response

router = APIRouter()

@router.get("/history")
async def get_history(user_id: str = "user_default", db: AsyncSession = Depends(get_db)):
    """Fetches full chat history from SQLite for frontend session restore."""
    result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.user_id == user_id)
        .order_by(ConversationMessage.timestamp.asc())
    )
    records = result.scalars().all()
    return [
        {"id": str(r.id), "role": r.role, "text": r.content, "emotion": r.emotion}
        for r in records
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
    response = generate_companion_response(request.message, formatted_history)

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