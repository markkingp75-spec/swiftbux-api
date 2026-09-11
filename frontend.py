from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

app = FastAPI(title="NairaPulse Global USD API")

# In-memory user database tracking USD balances
users_db = {
    "user_123": {
        "id": "user_123",
        "balance": Decimal("0.00"),
        "currency": "USD",
        "created_at": datetime.utcnow()
    }
}

class TaskCompletion(BaseModel):
    user_id: str
    task_id: str
    reward_amount: float  # e.g., 0.05 for 5 cents

@app.get("/users/{user_id}/balance")
def get_user_balance(user_id: str):
    if user_id not in users_db:
        users_db[user_id] = {
            "id": user_id,
            "balance": Decimal("0.00"),
            "currency": "USD",
            "created_at": datetime.utcnow()
        }
    user = users_db[user_id]
    return {
        "id": user["id"],
        "balance": float(user["balance"]),
        "currency": user["currency"]
    }

@app.post("/tasks/complete")
def complete_task(data: TaskCompletion):
    if data.user_id not in users_db:
        users_db[data.user_id] = {
            "id": data.user_id,
            "balance": Decimal("0.00"),
            "currency": "USD",
            "created_at": datetime.utcnow()
        }
    
    user = users_db[data.user_id]
    reward = Decimal(str(data.reward_amount))
    user["balance"] += reward
    
    return {
        "status": "success",
        "earned": float(reward),
        "new_balance": float(user["balance"]),
        "currency": "USD"
    }