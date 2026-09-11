import streamlit as st
from fastapi import FastAPI
import threading
import uvicorn

# Initialize FastAPI backend app
api = FastAPI(title="NairaPulse Reward API")

# Simple in-memory user ledger for testing
users_db = {"user_123": 0.0}

@api.get("/")
def read_root():
    return {"message": "NairaPulse API is live!"}

@api.post("/earn/{user_id}")
def earn_reward(user_id: str, amount: float):
    if user_id not in users_db:
        users_db[user_id] = 0.0
    users_db[user_id] += amount
    return {"status": "success", "new_balance": users_db[user_id]}

@api.get("/balance/{user_id}")
def get_balance(user_id: str):
    return {"user_id": user_id, "balance": users_db.get(user_id, 0.0)}

# Run FastAPI in the background thread so Streamlit can run concurrently
def run_fastapi():
    uvicorn.run(api, host="127.0.0.1", port=8000, log_level="warning")

@st.cache_resource
def start_server():
    t = threading.Thread(target=run_fastapi, daemon=True)
    t.start()

start_server()

# Streamlit Frontend UI
st.title("🇳🇬 NairaPulse: Earn & Cash Out")
st.write("Welcome to your reward platform! Complete tasks, watch videos, and grow your balance.")

user_id = st.text_input("Enter Your User ID", value="user_123")

if st.button("🎁 Watch Video & Earn ₦50"):
    users_db[user_id] = users_db.get(user_id, 0.0) + 50.0
    st.success("Task completed! You earned ₦50.")

# Display balance
current_balance = users_db.get(user_id, 0.0)
st.metric(label="Your Current Balance", value=f"₦ {current_balance:.2f}")

if current_balance >= 500:
    if st.button("Withdraw Funds"):
        st.balloons()
        st.success("Withdrawal request sent to your bank account!")
else:
    st.info("Reach ₦500.00 or more to unlock instant cash withdrawals.")