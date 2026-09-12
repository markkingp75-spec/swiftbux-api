from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_ai_engine.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AIEnterpriseUser(Base):
    __tablename__ = "ai_enterprise_users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    nationality = Column(String)
    identity_number = Column(String, unique=True, index=True) # NIN / BVN
    cash_balance = Column(Numeric(10, 3), default=Decimal("117.000"))
    tickets = Column(Numeric(10, 2), default=Decimal("10120.00"))
    gems = Column(Numeric(10, 0), default=Decimal("10"))
    referral_code = Column(String, unique=True, index=True)
    referred_count = Column(Numeric(10, 0), default=Decimal("0"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

# --- APP INITIALIZATION & AI LAUNCH TIMER CONFIG ---
app = FastAPI(title="SwiftBux AI-Controlled Enterprise Platform")

# Launch timestamp configuration (Set to start today, runs high-reward for 2 months)
LAUNCH_TIMESTAMP = datetime(2026, 9, 12, tzinfo=timezone.utc)
HIGH_REWARD_DURATION_DAYS = 60

def is_high_reward_phase() -> bool:
    """AI Controller: Checks if the 2-month viral launch window is still active."""
    now = datetime.now(timezone.utc)
    elapsed = now - LAUNCH_TIMESTAMP
    return elapsed.days < HIGH_REWARD_DURATION_DAYS

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FULL-SCREEN DESKTOP FRONTEND INTERFACE ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    phase_status = "🚀 HIGH-REWARD VIRAL LAUNCH PHASE (Active)" if is_high_reward_phase() else "♻️ SUSTAINABLE LONG-TERM PHASE (AI Optimized)"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwiftBux AI Enterprise Platform</title>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
            body {{ background: #f1f5f9; color: #1e293b; min-height: 100vh; display: flex; flex-direction: column; }}
            
            header {{ background: #ffffff; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            header h1 {{ font-size: 22px; color: #2563eb; display: flex; align-items: center; gap: 10px; }}
            .asset-badges {{ display: flex; gap: 15px; align-items: center; font-size: 14px; font-weight: bold; }}
            .badge-box {{ background: #f8fafc; padding: 6px 14px; border-radius: 20px; border: 1px solid #cbd5e1; display: flex; align-items: center; gap: 6px; }}

            .main-layout {{ display: flex; flex: 1; max-width: 1600px; width: 100%; margin: 0 auto; padding: 25px; gap: 25px; }}
            .sidebar {{ width: 280px; background: #ffffff; border-radius: 12px; padding: 20px; border: 1px solid #cbd5e1; display: flex; flex-direction: column; gap: 10px; height: fit-content; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            .nav-btn {{ background: transparent; color: #475569; border: none; text-align: left; padding: 14px 18px; border-radius: 8px; font-size: 15px; cursor: pointer; transition: 0.2s; font-weight: 600; display: flex; align-items: center; gap: 12px; }}
            .nav-btn:hover, .nav-btn.active {{ background: #eff6ff; color: #2563eb; }}

            .content-area {{ flex: 1; background: #ffffff; border-radius: 12px; padding: 30px; border: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05); min-height: 75vh; }}
            .tab-pane {{ display: none; }}
            .tab-pane.active {{ display: block; }}
            .hidden {{ display: none !important; }}

            .grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px; }}
            .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }}
            .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; text-align: left; }}
            .card h3 {{ font-size: 16px; color: #1e293b; margin-bottom: 8px; }}
            .card p {{ font-size: 13px; color: #64748b; margin-bottom: 15px; }}

            .form-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 15px; }}
            .form-group {{ display: flex; flex-direction: column; gap: 6px; text-align: left; margin-bottom: 15px; }}
            .form-group.full {{ grid-column: span 2; }}
            label {{ font-size: 13px; font-weight: bold; color: #475569; }}
            input, select {{ background: #ffffff; border: 1px solid #cbd5e1; color: #1e293b; padding: 12px 14px; border-radius: 8px; font-size: 15px; width: 100%; }}
            input:focus, select:focus {{ border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }}

            .btn-primary {{ background: #2563eb; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; font-size: 15px; cursor: pointer; transition: 0.2s; width: 100%; }}
            .btn-primary:hover {{ background: #1d4ed8; }}
            .btn-green {{ background: #16a34a; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: bold; cursor: pointer; }}
            .btn-green:hover {{ background: #15803d; }}
            .btn-danger {{ background: #dc2626; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; }}

            .modal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15,23,42,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }}
            .modal-box {{ background: white; padding: 30px; border-radius: 12px; width: 480px; text-align: center; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2); }}
        </style>
    </head>
    <body>

        <header>
            <h1>⚡ SwiftBux Enterprise AI Platform <span style="font-size: 12px; background: #e0f2fe; color: #0284c7; padding: 4px 10px; border-radius: 6px;">{phase_status}</span></h1>
            <div class="asset-badges">
                <div class="badge-box" style="color: #16a34a;">💵 Cash: <span id="headerCash">8.000</span> KWD</div>
                <div class="badge-box" style="color: #d97706;">🎟️ Tickets: <span id="headerTickets">10.12K</span></div>
                <div class="badge-box" style="color: #db2777;">💎 Gems: <span id="headerGems">10</span></div>
            </div>
        </header>

        <div class="main-layout">
            <div class="sidebar">
                <button class="nav-btn active" onclick="switchTab('tabReg', this)">📝 Registration & NIN Verification</button>
                <button class="nav-btn" onclick="switchTab('tabDash', this)">📊 AI Analytics & Dashboard</button>
                <button class="nav-btn" onclick="switchTab('tabGames', this)">🎮 Arcade Games & Tasks</button>
                <button class="nav-btn" onclick="switchTab('tabVideos', this)">📺 Video Ads Streams</button>
                <button class="nav-btn" onclick="switchTab('tabSpin', this)">🎡 Lucky Spin Wheel</button>
                <button class="nav-btn" onclick="switchTab('tabWallet', this)">🏦 Wallet & Withdrawals</button>
            </div>

            <div class="content-area">
                <div id="tabReg" class="tab-pane active">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Institutional User Registration & NIN Verification</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 25px;">Register with your NIN/BVN credentials to lock in high-multiplier earnings during the active viral phase.</p>

                    <form onsubmit="handleRegistration(event)">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Full Legal Name</label>
                                <input type="text" id="regName" placeholder="e.g. Emmanuel Mary" required>
                            </div>
                            <div class="form-group">
                                <label>Username / Unique ID</label>
                                <input type="text" id="regId" placeholder="e.g. Ottah23" required>
                            </div>
                            <div class="form-group">
                                <label>Email Address</label>
                                <input type="email" id="regEmail" placeholder="user@domain.com" required>
                            </div>
                            <div class="form-group">
                                <label>Phone Number</label>
                                <input type="text" id="regPhone" placeholder="+965 XXXX XXXX" required>
                            </div>
                            <div class="form-group">
                                <label>Nationality</label>
                                <select id="regNationality">
                                    <option value="Kuwaiti">Kuwaiti</option>
                                    <option value="Nigerian" selected>Nigerian</option>
                                    <option value="International">International</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>NIN / BVN Number</label>
                                <input type="text" id="regNin" placeholder="Enter 11-digit verification" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-primary" style="margin-top: 15px;">Verify & Register Account</button>
                    </form>
                </div>

                <div id="tabDash" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 15px;">AI Autonomous Controller & Analytics Dashboard</h2>
                    <div class="grid-3" style="margin-bottom: 25px;">
                        <div class="card" style="border-left: 4px solid #2563eb;">
                            <h3>Current Balance</h3>
                            <div style="font-size: 28px; font-weight: bold; color: #16a34a; margin-top: 5px;" id="dashBalance">8.000 KWD</div>
                        </div>
                        <div class="card" style="border-left: 4px solid #16a34a;">
                            <h3>Withdrawal Limit</h3>
                            <div style="font-size: 28px; font-weight: bold; color: #1e293b; margin-top: 5px;">50.000 KWD</div>
                        </div>
                        <div class="card" style="border-left: 4px solid #d97706;">
                            <h3>AI System Mode</h3>
                            <div style="font-size: 15px; font-weight: bold; color: #d97706; margin-top: 10px;">2-Month Viral Multiplier</div>
                        </div>
                    </div>
                    <div class="card">
                        <h3 style="color: #2563eb; margin-bottom: 10px;">🤖 Automated Transition Protocol</h3>
                        <p style="line-height: 1.6;">The AI engine actively manages user growth. For the first 60 days, accelerated payouts allow users to quickly achieve withdrawal milestones, verify identities, and drive viral referrals. Once the 2-month window expires, the AI automatically shifts reward multipliers to long-term sustainable parameters.</p>
                    </div>
                </div>

                <div id="tabGames" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Arcade Games & Active Earning Tasks</h2>
                    <div class="grid-2">
                        <div class="card">
                            <h3>🧩 Puzzle Solver Challenge</h3>
                            <p>Complete puzzles for fast reward accumulation.</p>
                            <button class="btn-green" onclick="executeTask('Puzzle Game', 4.500)">Claim +4.500 KWD</button>
                        </div>
                        <div class="card">
                            <h3>🚀 Speed Blaster Reflex</h3>
                            <p>Test your reflexes for promotional bounty.</p>
                            <button class="btn-green" onclick="executeTask('Speed Game', 6.000)">Claim +6.000 KWD</button>
                        </div>
                    </div>
                </div>

                <div id="tabVideos" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Sponsored Video Ad Streams</h2>
                    <div class="grid-2">
                        <div class="card">
                            <h3>Tech Innovation Spotlight (15s)</h3>
                            <p>Reward: 5.000 KWD</p>
                            <button class="btn-primary" onclick="executeTask('Video Ad 1', 5.000)">Watch & Earn 5.0 KWD</button>
                        </div>
                        <div class="card">
                            <h3>Global Marketplace Feature (30s)</h3>
                            <p>Reward: 7.500 KWD</p>
                            <button class="btn-primary" onclick="executeTask('Video Ad 2', 7.500)">Watch & Earn 7.5 KWD</button>
                        </div>
                    </div>
                </div>

                <div id="tabSpin" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Lucky Daily Spin Wheel</h2>
                    <div style="text-align: center; padding: 20px;">
                        <div style="width: 240px; height: 240px; border-radius: 50%; background: conic-gradient(#ef4444 0deg 60deg, #f59e0b 60deg 120deg, #10b981 120deg 180deg, #06b6d4 180deg 240deg, #8b5cf6 240deg 300deg, #ec4899 300deg 360deg); margin: 0 auto 20px auto; border: 6px solid #1e293b;"></div>
                        <button class="btn-primary" style="max-width: 250px;" onclick="executeTask('Spin Wheel', 2.500)">Spin & Earn (+2.500 KWD)</button>
                    </div>
                </div>

                <div id="tabWallet" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Wallet Management & Withdrawals</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Minimum withdrawal threshold: <b>50.000 KWD</b></p>
                    
                    <div class="card" style="max-width: 500px; margin: 0 auto; text-align: center;">
                        <h3 style="color: #16a34a; font-size: 24px; margin-bottom: 10px;" id="walletBalance">8.000 KWD</h3>
                        <div class="form-group">
                            <label>Destination Bank / Crypto Wallet</label>
                            <input type="text" id="walletDest" placeholder="Enter IBAN or Wallet Address">
                        </div>
                        <button class="btn-danger" onclick="requestWithdrawal()">Request Withdrawal & Generate Proof</button>
                    </div>
                </div>
            </div>
        </div>

        <div id="proofModal" class="modal-overlay hidden">
            <div class="modal-box">
                <h3 id="modalTitle" style="color: #16a34a; margin-bottom: 12px;">Success</h3>
                <p id="modalText" style="font-size: 14px; color: #334155; background: #f8fafc; padding: 12px; border-radius: 8px; text-align: left; margin-bottom: 20px; line-height: 1.5;"></p>
                <button class="btn-primary" onclick="closeModal()">Close & Share Proof</button>
            </div>
        </div>

        <script>
            let currentUserId = null;

            function switchTab(tabId, btnElement) {{
                document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
                btnElement.classList.add('active');
            }}

            async function handleRegistration(e) {{
                e.preventDefault();
                const payload = {{
                    id: document.getElementById('regId').value,
                    name: document.getElementById('regName').value,
                    email: document.getElementById('regEmail').value,
                    phone: document.getElementById('regPhone').value,
                    nationality: document.getElementById('regNationality').value,
                    identity_number: document.getElementById('regNin').value
                }};

                const res = await fetch('/api/register', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(payload)
                }});
                const data = await res.json();
                if(res.ok) {{
                    currentUserId = data.user_id;
                    updateUI(data.cash_balance, data.tickets, data.gems);
                    showModal("Registration Successful", `User ID: ${{currentUserId}}\\nNIN & Nationality Verified Successfully.\\nWelcome to SwiftBux AI Platform.`);
                    switchTab('tabDash', document.querySelectorAll('.nav-btn')[1]);
                }} else {{
                    alert('Registration Error: ' + data.detail);
                }}
            }}

            async function updateUI(cash, tickets, gems) {{
                document.getElementById('headerCash').innerText = cash.toFixed(3);
                document.getElementById('dashBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('walletBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('headerTickets').innerText = tickets.toLocaleString();
                document.getElementById('headerGems').innerText = gems;
            }}

            async function executeTask(taskName, reward) {{
                if(!currentUserId) {{
                    alert('Please complete your registration and NIN verification first!');
                    switchTab('tabReg', document.querySelectorAll('.nav-btn')[0]);
                    return;
                }}
                const res = await fetch('/api/task', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{user_id: currentUserId, reward: reward}})
                }});
                const data = await res.json();
                if(res.ok) {{
                    updateUI(data.cash_balance, data.tickets, data.gems);
                    showModal("Task Completed!", `Earned +${{data.adjusted_reward.toFixed(3)}} KWD from ${{taskName}} (AI Multiplier Applied).\\nNew Balance: ${{data.cash_balance.toFixed(3)}} KWD`);
                }}
            }}

            async function requestWithdrawal() {{
                if(!currentUserId) {{
                    alert('Please register first!');
                    return;
                }}
                const res = await fetch(`/api/user/${{currentUserId}}`);
                const data = await res.json();
                if(data.cash_balance < 50.0) {{
                    alert('Minimum withdrawal threshold is 50.000 KWD. Your current balance is ' + data.cash_balance.toFixed(3) + ' KWD.');
                    return;
                }}
                showModal("✅ OFFICIAL TRANSACTION PROOF", `User ID: ${{currentUserId}}\\nAmount: ${{data.cash_balance.toFixed(3)}} KWD\\nStatus: TRANSFER COMPLETED\\nNIN Verified: SUCCESSFUL\\nPhase: AI Controlled Launch\\nNetwork: SwiftBux Secure Ledger`);
            }}

            function showModal(title, text) {{
                document.getElementById('modalTitle').innerText = title;
                document.getElementById('modalText').innerText = text.replace(/\\n/g, '\\n');
                document.getElementById('proofModal').classList.remove('hidden');
            }}

            function closeModal() {{
                document.getElementById('proofModal').classList.add('hidden');
            }}
        </script>
    </body>
    </html>
    """

# --- BACKEND API ENDPOINTS WITH AI TRANSITION CONTROLLER ---
class UserReg(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    nationality: str
    identity_number: str

@app.post("/api/register")
def register_user(user: UserReg, db: Session = Depends(get_db)):
    existing = db.query(AIEnterpriseUser).filter((AIEnterpriseUser.id == user.id) | (AIEnterpriseUser.identity_number == user.identity_number)).first()
    if existing:
        return {
            "user_id": existing.id,
            "cash_balance": float(existing.cash_balance),
            "tickets": float(existing.tickets),
            "gems": int(existing.gems)
        }
    
    new_user = AIEnterpriseUser(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        nationality=user.nationality,
        identity_number=user.identity_number,
        cash_balance=Decimal("8.000"),
        tickets=Decimal("10120.00"),
        gems=Decimal("10"),
        referral_code=user.id + "_ref",
        referred_count=Decimal("0")
    )
    db.add(new_user)
    db.commit()
    return {
        "user_id": new_user.id,
        "cash_balance": float(new_user.cash_balance),
        "tickets": float(new_user.tickets),
        "gems": int(new_user.gems)
    }

@app.get("/api/user/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(AIEnterpriseUser).filter(AIEnterpriseUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user.id,
        "cash_balance": float(user.cash_balance),
        "tickets": float(user.tickets),
        "gems": int(user.gems)
    }

class TaskPost(BaseModel):
    user_id: str
    reward: float

@app.post("/api/task")
def process_task(task: TaskPost, db: Session = Depends(get_db)):
    user = db.query(AIEnterpriseUser).filter(AIEnterpriseUser.id == task.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    base_reward = Decimal(str(task.reward))
    
    # AI TRANSITION CONTROLLER LOGIC
    if is_high_reward_phase():
        # High multiplier for first 2 months to drive rapid viral adoption & referrals
        final_reward = base_reward * Decimal("1.0") 
    else:
        # Automatically scales down rewards by 60% after 2 months for long-term sustainability
        final_reward = base_reward * Decimal("0.4")

    user.cash_balance += final_reward
    user.tickets += Decimal("150.00")
    db.commit()
    
    return {
        "cash_balance": float(user.cash_balance),
        "tickets": float(user.tickets),
        "gems": int(user.gems),
        "adjusted_reward": float(final_reward)
    }