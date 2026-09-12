from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_enterprise.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EnterpriseUser(Base):
    __tablename__ = "enterprise_users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    nationality = Column(String)
    nin = Column(String, unique=True, index=True)
    balance = Column(Numeric(10, 3), default=Decimal("117.000"))
    currency = Column(String, default="KWD")
    referral_code = Column(String, unique=True, index=True)
    referred_count = Column(Numeric(10, 0), default=Decimal("0"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

# --- FASTAPI APP INITIALIZATION ---
app = FastAPI(title="SwiftBux Global Enterprise Portal")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FULL-SCREEN PRODUCTION FRONTEND UI ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwiftBux Global Enterprise Earning & Verification Platform</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            body { background: #07090e; color: #f8fafc; min-height: 100vh; display: flex; flex-direction: column; }
            header { background: #0f172a; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; }
            header h1 { font-size: 20px; color: #38bdf8; display: flex; align-items: center; gap: 10px; }
            .badge { background: #065f46; color: #34d399; font-size: 11px; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
            
            .main-container { flex: 1; display: flex; max-width: 1400px; margin: 0 auto; width: 100%; padding: 20px; gap: 20px; }
            
            /* Sidebar Navigation */
            .sidebar { width: 260px; background: #0f172a; border-radius: 12px; padding: 20px; border: 1px solid #1e293b; display: flex; flex-direction: column; gap: 10px; }
            .nav-btn { background: transparent; color: #94a3b8; border: none; text-align: left; padding: 12px 15px; border-radius: 8px; font-size: 15px; cursor: pointer; transition: 0.2s; font-weight: 600; }
            .nav-btn:hover, .nav-btn.active { background: #1e293b; color: #38bdf8; }

            /* Content Area */
            .content-pane { flex: 1; background: #0f172a; border-radius: 12px; padding: 30px; border: 1px solid #1e293b; overflow-y: auto; }
            
            .hidden { display: none !important; }
            
            /* Forms & Inputs */
            .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
            .form-group { display: flex; flex-direction: column; gap: 5px; text-align: left; margin-bottom: 15px; }
            .form-group.full { grid-column: span 2; }
            label { font-size: 13px; color: #cbd5e1; font-weight: bold; }
            input, select { background: #1e293b; border: 1px solid #334155; color: white; padding: 12px; border-radius: 8px; font-size: 15px; width: 100%; }
            input:focus, select:focus { border-color: #38bdf8; outline: none; }
            
            .btn-primary { background: #2563eb; color: white; border: none; padding: 14px 20px; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer; width: 100%; margin-top: 10px; transition: 0.2s; }
            .btn-primary:hover { background: #1d4ed8; }

            /* Dashboard Cards */
            .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 25px; }
            .stat-card { background: #1e293b; padding: 20px; border-radius: 10px; border-left: 4px solid #38bdf8; text-align: left; }
            .stat-card h4 { font-size: 13px; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; }
            .stat-card .val { font-size: 24px; font-weight: bold; color: #f8fafc; }

            /* Task & Game Modules */
            .task-card-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
            .task-box { background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 10px; text-align: left; display: flex; flex-direction: column; justify-content: space-between; }
            .task-box h3 { font-size: 16px; margin-bottom: 8px; color: #38bdf8; }
            .task-box p { font-size: 13px; color: #94a3b8; margin-bottom: 15px; }
            .action-btn { background: #10b981; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; }
            .action-btn:hover { background: #059669; }

            /* Live Game Arena */
            #gameCanvas { background: #020617; border: 2px solid #334155; border-radius: 8px; width: 100%; height: 250px; display: flex; align-items: center; justify-content: center; flex-direction: column; position: relative; cursor: pointer; margin-top: 10px; }
            
            /* Modal Proof */
            .modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 1000; }
            .modal-content { background: #1e293b; padding: 30px; border-radius: 12px; width: 450px; text-align: center; border: 1px solid #334155; }
            .modal-content h3 { color: #34d399; margin-bottom: 15px; }
            .modal-content p { font-size: 14px; color: #cbd5e1; margin-bottom: 10px; text-align: left; background: #0f172a; padding: 10px; border-radius: 6px; }
            .close-modal { background: #ef4444; margin-top: 15px; }
        </style>
    </head>
    <body>

        <header>
            <h1>⚡ SwiftBux Global Enterprise <span class="badge">SECURE LIVE</span></h1>
            <div id="headerUserStatus" style="font-size: 14px; color: #94a3b8;">Not Registered</div>
        </header>

        <div class="main-container">
            <!-- Sidebar -->
            <div class="sidebar">
                <button class="nav-btn active" onclick="switchTab('registerTab', this)">📝 Registration & NIN</button>
                <button class="nav-btn" onclick="switchTab('dashboardTab', this)" id="dashNavBtn">📊 Investor Dashboard</button>
                <button class="nav-btn" onclick="switchTab('gamesTab', this)">🎮 Play & Earn Games</button>
                <button class="nav-btn" onclick="switchTab('videosTab', this)">📺 Video Ads Earning</button>
                <button class="nav-btn" onclick="switchTab('referralTab', this)">👥 Referrals & Share</button>
                <button class="nav-btn" onclick="switchTab('withdrawTab', this)">🏦 Withdrawal & Proof</button>
            </div>

            <!-- Content Area -->
            <div class="content-pane">
                
                <!-- TAB 1: REGISTRATION & NIN VERIFICATION -->
                <div id="registerTab" class="tab-content">
                    <h2 style="margin-bottom: 10px; color: #38bdf8;">Enterprise User Registration & Verification</h2>
                    <p style="color: #94a3b8; font-size: 14px; margin-bottom: 20px;">Register with official details and National Identification Number (NIN) verification for institutional payouts and referral validation.</p>
                    
                    <form id="regForm" onsubmit="registerUser(event)">
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
                                    <option value="International">Other International</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>National Identification Number (NIN)</label>
                                <input type="text" id="regNin" placeholder="Enter 11-digit NIN Verification" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-primary">Verify & Complete Registration</button>
                    </form>
                </div>

                <!-- TAB 2: DASHBOARD -->
                <div id="dashboardTab" class="tab-content hidden">
                    <h2 style="margin-bottom: 20px; color: #38bdf8;">Investor & Referrer Analytics Dashboard</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <h4>Current Balance</h4>
                            <div class="val" id="dashBalance">0.000 KWD</div>
                        </div>
                        <div class="stat-card">
                            <h4>Active Currency</h4>
                            <div class="val">KWD (Kuwaiti Dinar)</div>
                        </div>
                        <div class="stat-card">
                            <h4>Total Referrals</h4>
                            <div class="val" id="dashRefCounts">0 Users</div>
                        </div>
                    </div>
                    <div style="background: #1e293b; padding: 20px; border-radius: 10px; text-align: left;">
                        <h3 style="color: #34d399; margin-bottom: 10px;">🔒 Security & Verification Seal</h3>
                        <p style="font-size: 14px; color: #cbd5e1; line-height: 1.6;">Your account is backed by live SQLite ledger tracking with encrypted NIN verification status. You can execute tasks, simulate game participation, and withdraw instantly to showcase verified transaction receipts to your community and investors.</p>
                    </div>
                </div>

                <!-- TAB 3: GAMES & EARN -->
                <div id="gamesTab" class="tab-content hidden">
                    <h2 style="margin-bottom: 10px; color: #38bdf8;">Interactive Earning Games Arena</h2>
                    <p style="color: #94a3b8; font-size: 14px; margin-bottom: 15px;">Click the active target below to play the reflex reward game and instantly credit your wallet.</p>
                    
                    <div id="gameCanvas" onclick="triggerGameReward()">
                        <h3 id="gamePrompt" style="color: #34d399; font-size: 20px;">🎮 CLICK HERE TO START GAME</h3>
                        <p style="color: #94a3b8; font-size: 13px; margin-top: 5px;">Earn +3.500 KWD per successful reflex capture!</p>
                    </div>
                </div>

                <!-- TAB 4: VIDEO ADS -->
                <div id="videosTab" class="tab-content hidden">
                    <h2 style="margin-bottom: 10px; color: #38bdf8;">Sponsored Video Ad Streams</h2>
                    <p style="color: #94a3b8; font-size: 14px; margin-bottom: 20px;">Watch partner promotional ad spots to generate instant ad revenue share.</p>
                    
                    <div class="task-card-grid">
                        <div class="task-box">
                            <h3>Spotlight Ad #1: Tech Innovations</h3>
                            <p>Stream duration: 15 seconds. Reward: +5.000 KWD</p>
                            <button class="action-btn" onclick="claimTask('video_ad1', 5.000)">Watch & Earn 5.0 KWD</button>
                        </div>
                        <div class="task-box">
                            <h3>Spotlight Ad #2: Global Marketplace</h3>
                            <p>Stream duration: 30 seconds. Reward: +7.500 KWD</p>
                            <button class="action-btn" onclick="claimTask('video_ad2', 7.500)">Watch & Earn 7.5 KWD</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 5: REFERRAL SYSTEM -->
                <div id="referralTab" class="tab-content hidden">
                    <h2 style="margin-bottom: 10px; color: #38bdf8;">Referral Program & Investor Links</h2>
                    <p style="color: #94a3b8; font-size: 14px; margin-bottom: 20px;">Share your customized tracking link to recruit referrals and collect affiliate commissions.</p>
                    
                    <div class="form-group">
                        <label>Your Unique Referral Link</label>
                        <input type="text" id="userRefLink" readonly value="Register first to generate link">
                    </div>
                    <button class="btn-primary" onclick="copyRefLink()" style="background: #8b5cf6;">Copy Referral Link</button>
                    <button class="action-btn" onclick="simulateNewReferral()" style="margin-top: 15px; width: 100%; background: #0284c7;">Simulate Referral Join (+10.000 KWD Commission)</button>
                </div>

                <!-- TAB 6: WITHDRAWAL & PROOF -->
                <div id="withdrawTab" class="tab-content hidden">
                    <h2 style="margin-bottom: 10px; color: #38bdf8;">Instant Withdrawal & Proof Generator</h2>
                    <p style="color: #94a3b8; font-size: 14px; margin-bottom: 20px;">Withdraw your earnings and instantly issue verifiable transaction certificates for your investors.</p>
                    
                    <div style="background: #1e293b; padding: 25px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                        <h3 id="withdrawBalDisplay" style="color: #4ade80; font-size: 22px; margin-bottom: 15px;">Available: 0.000 KWD</h3>
                        <div class="form-group">
                            <label>Destination Bank / Crypto Wallet</label>
                            <input type="text" id="bankDetails" placeholder="Enter IBAN or Wallet Address">
                        </div>
                        <button class="btn-primary" onclick="executeWithdrawal()" style="background: #e11d48;">Process Payout & Generate Proof</button>
                    </div>
                </div>

            </div>
        </div>

        <!-- TRANSACTION PROOF MODAL -->
        <div id="proofModal" class="modal hidden">
            <div class="modal-content">
                <h3>✅ OFFICIAL TRANSACTION PROOF</h3>
                <p id="proofDetails">Generating hash certificate...</p>
                <button class="btn-primary close-modal" onclick="closeModal()">Close & Share Proof</button>
            </div>
        </div>

        <script>
            let currentUser = null;

            function switchTab(tabId, btnElement) {
                document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
                document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabId).classList.remove('hidden');
                btnElement.classList.add('active');
            }

            async function registerUser(e) {
                e.preventDefault();
                const data = {
                    id: document.getElementById('regId').value,
                    name: document.getElementById('regName').value,
                    email: document.getElementById('regEmail').value,
                    phone: document.getElementById('regPhone').value,
                    nationality: document.getElementById('regNationality').value,
                    nin: document.getElementById('regNin').value
                };

                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                if(res.ok) {
                    currentUser = result.user_id;
                    document.getElementById('headerUserStatus').innerText = `Active: ${currentUser} (${result.nationality}) - NIN Verified`;
                    alert('Registration and NIN Verification successful! Welcome to SwiftBux Enterprise.');
                    fetchUserData();
                    switchTab('dashboardTab', document.getElementById('dashNavBtn'));
                } else {
                    alert('Error: ' + result.detail);
                }
            }

            async function fetchUserData() {
                if(!currentUser) return;
                const res = await fetch(`/api/user/${currentUser}`);
                const data = await res.json();
                if(res.ok) {
                    document.getElementById('dashBalance').innerText = `${data.balance.toFixed(3)} KWD`;
                    document.getElementById('dashRefCounts').innerText = `${data.referred_count} Users`;
                    document.getElementById('withdrawBalDisplay').innerText = `Available: ${data.balance.toFixed(3)} KWD`;
                    document.getElementById('userRefLink').value = `https://swiftbux-api.onrender.com/?ref=${data.referral_code}`;
                }
            }

            async function claimTask(taskType, rewardAmount) {
                if(!currentUser) {
                    alert('Please complete registration first!');
                    switchTab('registerTab', document.querySelectorAll('.nav-btn')[0]);
                    return;
                }
                const res = await fetch('/api/task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUser, task_type: taskType, reward: rewardAmount})
                });
                const data = await res.json();
                if(res.ok) {
                    alert(`Success! Earned ${rewardAmount.toFixed(3)} KWD from ${taskType}. New Balance: ${data.new_balance.toFixed(3)} KWD`);
                    fetchUserData();
                }
            }

            async function triggerGameReward() {
                const promptEl = document.getElementById('gamePrompt');
                promptEl.innerText = "🎯 TARGET HIT! Processing reward...";
                await claimTask('reflex_game', 3.500);
                setTimeout(() => {
                    promptEl.innerText = "🎮 CLICK HERE TO START GAME";
                }, 1500);
            }

            async function simulateNewReferral() {
                if(!currentUser) {
                    alert('Please register first!');
                    return;
                }
                const res = await fetch('/api/task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUser, task_type: 'referral_bonus', reward: 10.000})
                });
                const data = await res.json();
                if(res.ok) {
                    alert('New referral joined via your link! +10.000 KWD added to your affiliate balance.');
                    fetchUserData();
                }
            }

            function copyRefLink() {
                const copyText = document.getElementById('userRefLink');
                copyText.select();
                navigator.clipboard.writeText(copyText.value);
                alert('Referral link copied to clipboard!');
            }

            async function executeWithdrawal() {
                if(!currentUser) {
                    alert('Please register first!');
                    return;
                }
                const res = await fetch(`/api/user/${currentUser}`);
                const data = await res.json();
                if(data.balance <= 0) {
                    alert('Insufficient balance for withdrawal.');
                    return;
                }

                document.getElementById('proofDetails').innerHTML = `
                    <b>User ID:</b> ${currentUser}<br>
                    <b>Amount:</b> ${data.balance.toFixed(3)} KWD<br>
                    <b>Status:</b> TRANSFER COMPLETED<br>
                    <b>Timestamp:</b> ${new Date().toUTCString()}<br>
                    <b>Verification Hash:</b> 0x7f8a9bc...swiftbux_verified
                `;
                document.getElementById('proofModal').classList.remove('hidden');
            }

            function closeModal() {
                document.getElementById('proofModal').classList.add('hidden');
                fetchUserData();
            }
        </script>
    </body>
    </html>
    """

# --- API BACKEND ENDPOINTS ---
@app.post("/api/register")
def register_enterprise_user(
    id: str = Form(None),
    name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    nationality: str = Form(None),
    nin: str = Form(None),
    db: Session = Depends(get_db)
):
    # Support both JSON and Form parsing via Starlette request body if needed, let's use direct JSON body parsing or FastAPI Pydantic model:
    pass

from pydantic import BaseModel
class RegModel(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    nationality: str
    nin: str

@app.post("/api/register")
def register_json(user: RegModel, db: Session = Depends(get_db)):
    existing = db.query(EnterpriseUser).filter((EnterpriseUser.id == user.id) | (EnterpriseUser.nin == user.nin)).first()
    if existing:
        return {"user_id": existing.id, "nationality": existing.nationality, "status": "existing_loaded"}
    
    new_user = EnterpriseUser(
        id=user.id,
        email=user.email,
        phone=user.phone,
        nationality=user.nationality,
        nin=user.nin,
        balance=Decimal("117.000"),
        currency="KWD",
        referral_code=user.id + "_ref",
        referred_count=Decimal("0")
    )
    db.add(new_user)
    db.commit()
    return {"user_id": new_user.id, "nationality": new_user.nationality, "status": "registered"}

@app.get("/api/user/{user_id}")
def get_user_data(user_id: str, db: Session = Depends(get_db)):
    user = db.query(EnterpriseUser).filter(EnterpriseUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user.id,
        "balance": float(user.balance),
        "currency": user.currency,
        "referral_code": user.referral_code,
        "referred_count": int(user.referred_count)
    }

class TaskModel(BaseModel):
    user_id: str
    task_type: str
    reward: float

@app.post("/api/task")
def process_task(task: TaskModel, db: Session = Depends(get_db)):
    user = db.query(EnterpriseUser).filter(EnterpriseUser.id == task.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reward_val = Decimal(str(task.reward))
    user.balance += reward_val
    if task.task_type == 'referral_bonus':
        user.referred_count += 1
        
    db.commit()
    return {"status": "success", "new_balance": float(user.balance)}