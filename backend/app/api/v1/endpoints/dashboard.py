from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.db.models import HabitLog
from app.api.v1.endpoints.chat import get_or_create_profile

router= APIRouter()


@router.get("/dashboard")
async def get_dashboard_data(user_id: str = "user_default", db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    start_of_today = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    seven_days_ago = now - timedelta(days=7)

    # 1. Fetch Today's Logs
    today_query = await db.execute(
        select(HabitLog)
        .where(HabitLog.user_id == user_id)
        .where(HabitLog.timestamp >= start_of_today)
        .order_by(HabitLog.timestamp.desc())
    )
    today_logs = today_query.scalars().all()

    # 2. Fetch Past 7 Days Logs
    week_query = await db.execute(
        select(HabitLog)
        .where(HabitLog.user_id == user_id)
        .where(HabitLog.timestamp >= seven_days_ago)
        .order_by(HabitLog.timestamp.desc())
    )
    week_logs = week_query.scalars().all()

    # Aggregate Today's Totals
    water_today = sum(l.value for l in today_logs if l.category == "water" and l.value)
    sleep_today = sum(l.value for l in today_logs if l.category == "sleep" and l.value)
    workouts_today = [l for l in today_logs if l.category == "workout"]

    # Aggregate 7-Day Stats
    workouts_week = len([l for l in week_logs if l.category == "workout"])
    sleep_week_entries = [l.value for l in week_logs if l.category == "sleep" and l.value]
    avg_sleep_week = (sum(sleep_week_entries) / len(sleep_week_entries)) if sleep_week_entries else 0.0

    # Recent Activity Feed (Last 10 logs)
    recent_activity = [
        {
            "id": log.id,
            "category": log.category,
            "value": log.value,
            "unit": log.unit,
            "notes": log.notes,
            "timestamp": log.timestamp.isoformat()
        }
        for log in week_logs[:10]
    ]

    profile = await get_or_create_profile(user_id, db)

    return {
        "today": {
            "water_liters": round(water_today, 2),
            "water_goal": profile.daily_water_target,
            "sleep_hours": round(sleep_today, 1),
            "sleep_goal": profile.daily_sleep_target,
            "workouts_completed": len(workouts_today)
        },
        "trends": {
            "weekly_workouts": workouts_week,
            "weekly_workout_target": profile.weekly_workout_target,
            "avg_sleep_hours": round(avg_sleep_week, 1),
            "active_streak_days": min(workouts_week + (1 if water_today > 0 else 0), 7)
        },
        "profile": {
            "name": profile.display_name,
            "lifestyle_archetype": profile.lifestyle_archetype,
            "primary_goals": profile.primary_goals or []
        },
        "recent_activity": recent_activity
    }