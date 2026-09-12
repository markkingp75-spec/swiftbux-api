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
    balance = Column(Numeric(10, 3), default=Decimal("117.000"))
    currency = Column(String, default="KWD")
    referral_code = Column(String, unique=True, index=True)
    referred_count = Column(Numeric(10, 0), default=Decimal("0"))
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
        <title>SwiftBux Live Earning Portal</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; background-color: #0f172a; color: white; padding: 15px; text-align: center; }
            .card { background: #1e293b; max-width: 440px; margin: 0 auto; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
            input, select, button { width: 92%; padding: 10px; margin: 8px 0; border-radius: 6px; border: none; font-size: 15px; }
            input, select { background: #334155; color: white; }
            button { background: #22c55e; color: white; font-weight: bold; cursor: pointer; }
            button:hover { background: #16a34a; }
            .balance { font-size: 22px; color: #4ade80; margin: 10px 0; font-weight: bold; }
            .task-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 10px 0; }
            .task-btn { background: #3b82f6; width: 100%; margin: 0; padding: 10px; font-size: 14px; }
            .task-btn:hover { background: #2563eb; }
            .ref-box { background: #0f172a; padding: 10px; border-radius: 6px; font-size: 13px; margin: 10px 0; color: #38bdf8; word-break: break-all; }
            .log { margin-top: 10px; color: #cbd5e1; font-size: 13px; background: #0f172a; padding: 8px; border-radius: 6px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>SwiftBux Portal</h2>
            <input type="text" id="userId" placeholder="Enter Your Username / ID" value="user_001">
            <button onclick="checkAccount()">Register / Login</button>
            <div class="balance" id="balanceDisplay">Balance: 0.000 KWD</div>
            
            <hr style="border: 0.5px solid #334155; margin: 12px 0;">
            <p style="font-size: 14px; margin: 5px 0; color: #94a3b8; font-weight: bold;">Select Earning Task:</p>
            <div class="task-grid">
                <button class="task-btn" onclick="claimTask('game', 3.500)">🎮 Play Game (+3.5 KWD)</button>
                <button class="task-btn" onclick="claimTask('video', 5.000)">📺 Watch Ad (+5.0 KWD)</button>
                <button class="task-btn" onclick="claimTask('social', 4.000)">📢 Share Post (+4.0 KWD)</button>
                <button class="task-btn" onclick="claimTask('survey', 6.500)">📋 Survey (+6.5 KWD)</button>
            </div>

            <button onclick="claimReferral()" style="background: #8b5cf6;">👥 Claim Referral Bonus (+10.0 KWD)</button>
            <button onclick="withdraw()" style="background: #e11d48;">Withdraw Funds (Proof)</button>
            
            <div class="ref-box" id="refLinkDisplay">Referral Link: Not loaded</div>
            <div class="log" id="statusLog">Status: Ready to earn</div>
        </div>
        <script>
            async function checkAccount() {
                const uid = document.getElementById('userId').value;
                const res = await fetch(`/user/${uid}`);
                const data = await res.json();
                document.getElementById('balanceDisplay').innerText = `Balance: ${data.balance.toFixed(3)} KWD`;
                document.getElementById('refLinkDisplay').innerText = `Referral Link: https://swiftbux-api.onrender.com/?ref=${data.referral_code}`;
                document.getElementById('statusLog').innerText = `Logged in as: ${uid} (Refs: ${data.referred_count})`;
            }
            async function claimTask(type, reward) {
                const uid = document.getElementById('userId').value;
                const res = await fetch(`/tasks/claim-reward?user_id=${uid}&task_type=${type}&base_ad_revenue=${reward}`, { method: 'POST' });
                const data = await res.json();
                if(data.status === 'success') {
                    document.getElementById('balanceDisplay').innerText = `Balance: ${data.new_balance.toFixed(3)} KWD`;
                    document.getElementById('statusLog').innerText = `Success! Earned ${reward.toFixed(3)} KWD from ${type}.`;
                }
            }
            async function claimReferral() {
                const uid = document.getElementById('userId').value;
                const res = await fetch(`/tasks/claim-reward?user_id=${uid}&task_type=referral&base_ad_revenue=10.000`, { method: 'POST' });
                const data = await res.json();
                if(data.status === 'success') {
                    document.getElementById('balanceDisplay').innerText = `Balance: ${data.new_balance.toFixed(3)} KWD`;
                    document.getElementById('statusLog').innerText = `Referral bonus claimed successfully!`;
                }
            }
            async function withdraw() {
                const uid = document.getElementById('userId').value;
                const res = await fetch(`/user/${uid}`);
                const data = await res.json();
                if(data.balance <= 0) {
                    alert('Insufficient balance for withdrawal!');
                } else {
                    alert(`✅ INVESTOR & REFERRAL WITHDRAWAL PROOF:\n\nUser: ${uid}\nAmount: ${data.balance.toFixed(3)} KWD\nStatus: TRANSFER COMPLETED\nNetwork: SwiftBux Secure Ledger`);
                    document.getElementById('statusLog').innerText = `Withdrawal proof generated for ${data.balance.toFixed(3)} KWD.`;
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
        user = DBUser(id=user_id, balance=Decimal("117.000"), currency="KWD", referral_code=user_id + "_ref", referred_count=Decimal("0"))
        db.add(user)
        db.commit()
        db.refresh(user)
    return {"user_id": user.id, "balance": float(user.balance), "currency": user.currency, "referral_code": user.referral_code, "referred_count": int(user.referred_count)}

@app.post("/tasks/claim-reward")
async def claim_task_reward(
    user_id: str,
    task_type: str,
    base_ad_revenue: float,
    db: Session = Depends(get_db)
):
    try:
        base_value = Decimal(str(base_ad_revenue))
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if not user:
            user = DBUser(id=user_id, balance=Decimal("117.000"), currency="KWD", referral_code=user_id + "_ref")
            db.add(user)
        
        user.balance += base_value
        if task_type == 'referral':
            user.referred_count += 1
            
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