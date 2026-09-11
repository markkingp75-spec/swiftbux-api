from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="NairaPulse Fresh API")

# Temporary in-memory database to let you test instantly without setup errors
fake_users_db = {
    "user_123": {
        "id": "user_123",
        "balance": 0.0,
        "created_at": datetime.utcnow()
    }
}

class TaskCompletion(BaseModel):
    user_id: str
    task_id: str
    reward_amount: float

@app.get("/")
def home():
    return {"message": "Welcome to NairaPulse API! Everything is running fresh."}

@app.post("/tasks/complete")
def complete_task(data: TaskCompletion):
    if data.user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Credit the user
    user = fake_users_db[data.user_id]
    user["balance"] += data.reward_amount
    
    return {
        "status": "success",
        "message": "Reward added successfully!",
        "new_balance": user["balance"]
    }

@app.get("/users/{user_id}/balance")
def get_balance(user_id: str):
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return fake_users_db[user_id]