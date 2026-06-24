"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from typing import Dict

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities: Dict[str, Dict] = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


def _summarize_activity(activity: Dict) -> Dict:
    """Return a public summary for an activity (does not expose participant emails)."""
    participants = activity.get("participants", [])
    max_p = activity.get("max_participants", 0)
    spots_left = max_p - len(participants)
    return {
        "description": activity.get("description"),
        "schedule": activity.get("schedule"),
        "max_participants": max_p,
        "participants_count": len(participants),
        "spots_left": max(0, spots_left),
    }


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Return a dictionary of activity summaries."""
    return {name: _summarize_activity(details) for name, details in activities.items()}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity with basic validation.

    Rules:
    - Activity must exist (404)
    - Email must look like an email (basic check) (400)
    - Activity must have available spots (409)
    - Student cannot be signed up twice (409)
    """
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    # Basic email validation
    if "@" not in email or email.count("@") != 1 or email.startswith("@") or email.endswith("@"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email address")

    # Get the specific activity
    activity = activities[activity_name]
    participants = activity.setdefault("participants", [])
    max_p = activity.get("max_participants", 0)

    # Check capacity
    if len(participants) >= max_p:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Activity is full")

    # Prevent duplicate signups
    if email in participants:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already signed up for this activity")

    # Add student
    participants.append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
