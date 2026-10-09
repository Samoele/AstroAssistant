from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import HabitLog

async def get_weekly_lifestyle_summary(user_id: str, db: AsyncSession) -> str:
    """
    Queries habit_logs for the last 7 days, aggregates quantitative data,
    and returns a clean semantic string ready for LLM prompt injection.
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)

    # Fetch all habit entries from the past 7 days
    result = await db.execute(
        select(HabitLog)
        .where(HabitLog.user_id == user_id)
        .where(HabitLog.timestamp >= cutoff_date)
    )
    logs = result.scalars().all()

    if not logs:
        return "No habit activity logged in the past 7 days. The user is just getting started."

    #Divide by category
    workouts = [log for log in logs if log.category == "workout"]
    sleep_logs = [log for log in logs if log.category == "sleep"]
    nutrition_logs = [log for log in logs if log.category == "nutrition"]
    water_logs = [log for log in logs if log.category == "water"]

    summary_lines = []

    # 1. Workout Analysis
    if workouts:
        total_sessions = len(workouts)
        total_metric = sum(w.value for w in workouts if w.value is not None)
        units = {w.unit for w in workouts if w.unit}
        unit_str = f" ({total_metric} {', '.join(units)})" if total_metric > 0 else ""
        summary_lines.append(f"- Workouts: {total_sessions} completed in the past 7 days{unit_str}.")
    else:
        summary_lines.append("- Workouts: 0 logged this week (Sedentary alert).")

    # 2. Sleep Analysis (Mean Duration)
    if sleep_logs:
        sleep_values = [s.value for s in sleep_logs if s.value is not None]
        if sleep_values:
            avg_sleep = sum(sleep_values) / len(sleep_values)
            summary_lines.append(f"- Sleep: {len(sleep_values)} entries, averaging {avg_sleep:.1f} hours/night.")
    else:
        summary_lines.append("- Sleep: No sleep logged this week.")

    # 3. Water & Hydration
    if water_logs:
        water_total = sum(w.value for w in water_logs if w.value is not None)
        water_units = {w.unit for w in water_logs if w.unit}
        summary_lines.append(f"- Hydration: {water_total} {', '.join(water_units)} tracked.")

    # 4. Nutrition Log Count
    if nutrition_logs:
        summary_lines.append(f"- Nutrition: {len(nutrition_logs)} meals/intakes logged.")

    return "\n".join(summary_lines)