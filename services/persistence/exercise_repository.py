import logging

from services.persistence.supabase_client import supabase


# =========================================================
# HELPERS
# =========================================================

def _clean_user_id(user_id):
    """
    Normalize user IDs coming from either:
    - integer
    - string
    - user dictionary
    """
    if isinstance(user_id, dict):
        user_id = user_id.get("id", 0)

    try:
        return int(user_id) if user_id is not None else 0
    except (ValueError, TypeError):
        return 0


# =========================================================
# DATABASE INITIALIZATION / CONNECTION CHECK
# =========================================================

def init_db():
    """
    Supabase replaces SQLite table initialization.

    Database tables must already exist in Supabase.
    This function simply verifies that the connection works.
    """
    try:
        response = (
            supabase
            .table("users")
            .select("id")
            .limit(1)
            .execute()
        )

        logging.info(
            "[exercise_repository] Supabase connection successful."
        )

        return True

    except Exception as e:
        logging.error(
            f"[exercise_repository] Supabase connection failed: {e}",
            exc_info=True
        )
        return False


# =========================================================
# USER
# =========================================================

def get_or_create_user(username):
    """
    Get an existing user or create a new user.
    Returns a dictionary compatible with the old SQLite version.
    """
    try:
        username = str(username).strip()

        if not username:
            return None

        # -------------------------------------------------
        # Find existing user
        # -------------------------------------------------

        response = (
            supabase
            .table("users")
            .select("*")
            .eq("username", username)
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if rows:
            return rows[0]

        # -------------------------------------------------
        # Create new user
        # -------------------------------------------------

        new_user = {
            "username": username,
            "current_streak": 0,
            "longest_streak": 0,
            "last_workout_date": None,
            "user_goal": "General Fitness",
            "body_weight_kg": 70.0,
            "height_cm": 170.0,
            "age": 25,
        }

        response = (
            supabase
            .table("users")
            .insert(new_user)
            .execute()
        )

        rows = response.data or []

        if rows:
            return rows[0]

        return None

    except Exception as e:
        logging.error(
            f"[exercise_repository] "
            f"get_or_create_user failed for '{username}': {e}",
            exc_info=True
        )
        return None


# =========================================================
# USER STREAKS
# =========================================================

def update_user_streaks(
    user_id,
    current_streak,
    longest_streak,
    last_workout_date
):
    """
    Update user's streak information.
    """
    try:
        user_id = _clean_user_id(user_id)

        if user_id <= 0:
            return

        (
            supabase
            .table("users")
            .update({
                "current_streak": int(current_streak),
                "longest_streak": int(longest_streak),
                "last_workout_date": last_workout_date,
            })
            .eq("id", user_id)
            .execute()
        )

    except Exception as e:
        logging.error(
            f"[exercise_repository] "
            f"update_user_streaks failed: {e}",
            exc_info=True
        )


# =========================================================
# USER PROFILE
# =========================================================

def update_user_profile(
    user_id,
    user_goal: str = None,
    body_weight_kg: float = None,
    height_cm: float = None,
    age: int = None
):
    """
    Update only the profile fields supplied by the caller.
    """
    try:
        user_id = _clean_user_id(user_id)

        if user_id <= 0:
            return

        updates = {}

        if user_goal is not None:
            updates["user_goal"] = user_goal

        if body_weight_kg is not None:
            updates["body_weight_kg"] = float(body_weight_kg)

        if height_cm is not None:
            updates["height_cm"] = float(height_cm)

        if age is not None:
            updates["age"] = int(age)

        if not updates:
            return

        (
            supabase
            .table("users")
            .update(updates)
            .eq("id", user_id)
            .execute()
        )

    except Exception as e:
        logging.error(
            f"[exercise_repository] "
            f"update_user_profile failed: {e}",
            exc_info=True
        )


# =========================================================
# WORKOUT SCHEDULE
# =========================================================

def save_schedule(
    user_id: int,
    days: list,
    workout_time: str,
    program_name: str
):
    """
    Replace the user's existing workout schedule.
    """
    try:
        user_id = _clean_user_id(user_id)

        if user_id <= 0:
            return

        # -------------------------------------------------
        # Remove existing schedule
        # -------------------------------------------------

        (
            supabase
            .table("workout_schedule")
            .delete()
            .eq("user_id", user_id)
            .execute()
        )

        # -------------------------------------------------
        # Nothing to insert
        # -------------------------------------------------

        if not days:
            return

        # -------------------------------------------------
        # Insert schedule rows
        # -------------------------------------------------

        schedule_rows = []

        for day in days:
            schedule_rows.append({
                "user_id": user_id,
                "day_of_week": int(day),
                "workout_time": workout_time,
                "program_name": program_name,
                "active": 1,
            })

        (
            supabase
            .table("workout_schedule")
            .insert(schedule_rows)
            .execute()
        )

    except Exception as e:
        logging.error(
            f"[exercise_repository] save_schedule failed: {e}",
            exc_info=True
        )


def get_schedule(user_id: int) -> list:
    """
    Return active workout schedule rows for a user.
    """
    try:
        user_id = _clean_user_id(user_id)

        if user_id <= 0:
            return []

        response = (
            supabase
            .table("workout_schedule")
            .select("*")
            .eq("user_id", user_id)
            .eq("active", 1)
            .order("day_of_week", desc=False)
            .execute()
        )

        return response.data or []

    except Exception as e:
        logging.error(
            f"[exercise_repository] get_schedule failed: {e}",
            exc_info=True
        )
        return []


# =========================================================
# EXERCISE HISTORY
# =========================================================

def get_users_exercises(user_id):
    """
    Get exercise history for a user.

    Return format intentionally matches the old SQLite repository.
    """
    try:
        user_id = _clean_user_id(user_id)

        if user_id <= 0:
            return []

        response = (
            supabase
            .table("exercises")
            .select(
                "exercise_name,"
                "reps,"
                "sets,"
                "time,"
                "average_form_score,"
                "best_form_score,"
                "feedback_summary,"
                "strongest_area,"
                "weakest_area,"
                "improvement_percentage,"
                "created_at"
            )
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    except Exception as e:
        logging.error(
            f"[exercise_repository] "
            f"get_users_exercises failed: {e}",
            exc_info=True
        )
        return []


# =========================================================
# SAVE EXERCISE
# =========================================================

def save_exercise(
    user_id,
    exercise_name,
    reps,
    sets,
    time_spent,
    average_form_score=None,
    best_form_score=None,
    feedback_summary=None,
    strongest_area=None,
    weakest_area=None,
    improvement_percentage=None
):
    """
    Save one completed exercise/set.
    """
    try:
        user_id = _clean_user_id(user_id)

        if user_id <= 0:
            return False

        exercise_data = {
            "user_id": user_id,
            "exercise_name": exercise_name,
            "reps": int(reps or 0),
            "sets": int(sets or 0),
            "time": float(time_spent or 0.0),
            "average_form_score": (
                float(average_form_score)
                if average_form_score is not None
                else None
            ),
            "best_form_score": (
                float(best_form_score)
                if best_form_score is not None
                else None
            ),
            "feedback_summary": feedback_summary,
            "strongest_area": strongest_area,
            "weakest_area": weakest_area,
            "improvement_percentage": (
                float(improvement_percentage)
                if improvement_percentage is not None
                else None
            ),
        }

        response = (
            supabase
            .table("exercises")
            .insert(exercise_data)
            .execute()
        )

        return bool(response.data)

    except Exception as e:
        logging.error(
            f"[exercise_repository] save_exercise failed: {e}",
            exc_info=True
        )
        return False


# =========================================================
# UPDATE LATEST EXERCISE FEEDBACK
# =========================================================

def update_latest_exercise_feedback(
    user_id,
    exercise_name,
    feedback_summary,
    strongest_area,
    weakest_area,
    improvement_percentage
):
    """
    Update the latest exercise record for a user/exercise.
    """
    try:
        user_id = _clean_user_id(user_id)

        if user_id <= 0:
            return

        # -------------------------------------------------
        # Find latest exercise row
        # -------------------------------------------------

        response = (
            supabase
            .table("exercises")
            .select("id")
            .eq("user_id", user_id)
            .eq("exercise_name", exercise_name)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if not rows:
            return

        latest_id = rows[0]["id"]

        # -------------------------------------------------
        # Update it
        # -------------------------------------------------

        (
            supabase
            .table("exercises")
            .update({
                "feedback_summary": feedback_summary,
                "strongest_area": strongest_area,
                "weakest_area": weakest_area,
                "improvement_percentage": (
                    float(improvement_percentage)
                    if improvement_percentage is not None
                    else 0.0
                ),
            })
            .eq("id", latest_id)
            .execute()
        )

    except Exception as e:
        logging.error(
            f"[exercise_repository] "
            f"update_latest_exercise_feedback failed: {e}",
            exc_info=True
        )