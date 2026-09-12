from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_secure.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBUser(Base):
    __tablename__ = "secure_users"
    id = Column(String, primary_key=True, index=True)
    balance = Column(Numeric(10, 3), default=Decimal("117.000")) # KWD uses 3 decimal places
    currency = Column(String, default="KWD")
    referral_code = Column(String, unique=True, index=True)
    referred_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

# --- FASTAPI APP INITIALIZATION ---
app = FastAPI(title="SwiftBux App")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- VISUAL FRONTEND HOMEPAGE ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SwiftBux Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; background-color: #0f172a; color: white; padding: 20px; text-align: center; }
            .card { background: #1e293b; max-width: 400px; margin: 0 auto; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
            input, button { width: 90%; padding: 12px; margin: 10px 0; border-radius: 6px; border: none; font-size: 16px; }
            button { background: #22c55e; color: white; font-weight: bold; cursor: pointer; }
            button:hover { background: #16a34a; }
            .balance { font-size: 24px; color: #4ade80; margin: 15px 0; font-weight: bold; }
            .log { margin-top: 15px; color: #cbd5e1; font-size: 14px; background: #0f172a; padding: 10px; border-radius: 6px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>SwiftBux Reward Portal</h2>
            <input type="text" id="userId" placeholder="Enter User ID / Username" value="user_001">
            <button onclick="checkBalance()">Register / Load Account</button>
            <div class="balance" id="balanceDisplay">Balance: 0.000 KWD</div>
            <hr style="border: 0.5px solid #334155; margin: 20px 0;">
            <button onclick="claimReward()">Claim Task Reward (+5.000 KWD)</button>
            <button onclick="withdraw()" style="background: #e11d48;">Request Withdrawal</button>
            <div class="log" id="statusLog">Status: Ready</div>
        </div>
        <script>
            async function checkBalance() {
                const uid = document.getElementById('userId').value;
                const res = await fetch(`/user/${uid}`);
                const data = await res.json();
                document.getElementById('balanceDisplay').innerText = `Balance: ${data.balance.toFixed(3)} KWD`;
                document.getElementById('statusLog').innerText = `User loaded: ${uid}`;
            }
            async function claimReward() {
                const uid = document.getElementById('userId').value;
                const res = await fetch(`/tasks/claim-reward?user_id=${uid}&task_id=task1&base_ad_revenue=5.000`, { method: 'POST' });
                const data = await res.json();
                if(data.status === 'success') {
                    document.getElementById('balanceDisplay').innerText = `Balance: ${data.new_balance.toFixed(3)} KWD`;
                    document.getElementById('statusLog').innerText = `Reward claimed successfully!`;
                }
            }
            async function withdraw() {
                const uid = document.getElementById('userId').value;
                const res = await fetch(`/user/${uid}`);
                const data = await res.json();
                if(data.balance <= 0) {
                    alert('Insufficient balance for withdrawal!');
                } else {
                    alert(`Withdrawal Request Submitted for ${data.balance.toFixed(3)} KWD!\nTransaction Proof Generated.`);
                    document.getElementById('statusLog').innerText = `Withdrawal of ${data.balance.toFixed(3)} KWD processing...`;
                }
            }
        </script>
    </body>
    </html>
    """

# --- API ENDPOINTS ---
@app.get("/user/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        user = DBUser(id=user_id, balance=Decimal("117.000"), currency="KWD", referral_code=user_id + "_ref")
        db.add(user)
        db.commit()
        db.refresh(user)
    return {"user_id": user.id, "balance": float(user.balance), "currency": user.currency, "referral_code": user.referral_code}

@app.post("/tasks/claim-reward")
async def claim_task_reward(
    user_id: str,
    task_id: str,
    base_ad_revenue: float,
    db: Session = Depends(get_db)
):
    try:
        base_value = Decimal(str(base_ad_revenue))
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if not user:
            user = DBUser(id=user_id, balance=Decimal("117.000"), currency="KWD")
            db.add(user)
        
        user.balance += base_value
        db.commit()
        return {
            "status": "success",
            "user_id": user_id,
            "new_balance": float(user.balance),
            "currency": "KWD"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))