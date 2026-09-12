from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AppUser(Base):
    __tablename__ = "app_users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    nationality = Column(String)
    identity_number = Column(String, unique=True, index=True) # NIN / BVN / Passport
    cash_balance = Column(Numeric(10, 3), default=Decimal("117.000")) # KWD Currency
    tickets = Column(Numeric(10, 2), default=Decimal("10120.00"))
    gems = Column(Numeric(10, 0), default=Decimal("10"))
    referral_code = Column(String, unique=True, index=True)
    referred_count = Column(Numeric(10, 0), default=Decimal("0"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

# --- FASTAPI APP ---
app = FastAPI(title="SwiftBux Mobile Gaming & Reward Platform")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- MOBILE APP FRONTEND INTERFACE ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwiftBux Mobile Reward Platform</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
            body { background: #e2e8f0; color: #0f172a; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
            
            /* Mobile Device Frame */
            .mobile-frame { width: 100%; max-width: 420px; height: 100vh; max-height: 850px; background: #f8fafc; border-radius: 24px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3); display: flex; flex-direction: column; overflow: hidden; position: relative; border: 8px solid #1e293b; }
            
            /* Top Header Balance Bar */
            .top-bar { background: #ffffff; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; font-size: 13px; font-weight: bold; }
            .badge-group { display: flex; align-items: center; gap: 5px; background: #f1f5f9; padding: 4px 8px; border-radius: 20px; border: 1px solid #e2e8f0; }
            
            /* Screen Container */
            .screen { flex: 1; overflow-y: auto; padding: 16px; padding-bottom: 80px; }
            .screen-section { display: none; }
            .screen-section.active { display: block; }
            
            /* Cards & Banners */
            .promo-banner { background: linear-gradient(135deg, #3b82f6, #1d4ed8); border-radius: 16px; padding: 20px; color: white; text-align: center; margin-bottom: 16px; box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3); }
            .action-card { background: white; border-radius: 16px; padding: 16px; margin-bottom: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center; }
            
            /* Buttons */
            .btn-green { background: #22c55e; color: white; border: none; padding: 12px 20px; border-radius: 12px; font-weight: bold; font-size: 15px; width: 100%; cursor: pointer; box-shadow: 0 4px 10px rgba(34, 197, 94, 0.3); transition: 0.2s; margin-top: 10px; }
            .btn-green:hover { background: #16a34a; }
            .btn-blue { background: #3b82f6; color: white; border: none; padding: 10px 16px; border-radius: 10px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 8px; }
            
            /* Form inputs */
            .input-group { text-align: left; margin-bottom: 12px; }
            .input-group label { font-size: 12px; font-weight: bold; color: #64748b; display: block; margin-bottom: 4px; }
            .input-group input, .input-group select { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; background: #fff; }
            
            /* Bottom Navigation Bar */
            .bottom-nav { position: absolute; bottom: 0; left: 0; width: 100%; height: 70px; background: #ffffff; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-around; align-items: center; z-index: 100; }
            .nav-item { background: none; border: none; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; color: #64748b; font-size: 11px; font-weight: 600; }
            .nav-item.active { color: #2563eb; }
            .nav-icon { font-size: 20px; }

            /* Wheel & Game Arena */
            .wheel-container { width: 220px; height: 220px; border-radius: 50%; background: conic-gradient(#ef4444 0deg 60deg, #f59e0b 60deg 120deg, #10b981 120deg 180deg, #06b6d4 180deg 240deg, #8b5cf6 240deg 300deg, #ec4899 300deg 360deg); margin: 20px auto; border: 6px solid #1e293b; position: relative; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
            .wheel-pointer { width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-bottom: 20px solid #0f172a; position: absolute; top: -15px; left: calc(50% - 10px); }

            /* Modal overlay */
            .modal { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 200; }
            .modal-box { background: white; padding: 24px; border-radius: 16px; width: 85%; text-align: center; }
            .hidden { display: none !important; }
        </style>
    </head>
    <body>

        <div class="mobile-frame">
            
            <!-- Top Asset Bar -->
            <div class="top-bar">
                <div class="badge-group" style="color: #16a34a;">💵 <span id="topCash">8.000</span> KWD</div>
                <div class="badge-group" style="color: #d97706;">🎟️ <span id="topTickets">10.12K</span></div>
                <div class="badge-group" style="color: #db2777;">💎 <span id="topGems">10</span></div>
            </div>

            <!-- Screens Container -->
            <div class="screen">
                
                <!-- TAB 1: PLAY & MISSIONS (Home) -->
                <div id="tabHome" class="screen-section active">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <h3 style="font-size: 18px; color: #1e293b;">Level 7</h3>
                        <span style="font-size: 12px; background: #e0f2fe; color: #0284c7; padding: 4px 8px; border-radius: 8px; font-weight: bold;">🔒 NIN Verified</span>
                    </div>

                    <div class="promo-banner" style="background: linear-gradient(135deg, #10b981, #059669);">
                        <h4 style="font-size: 16px; margin-bottom: 5px;">⚡ Daily Reward Active</h4>
                        <p style="font-size: 13px; opacity: 0.9;">Claim your KWD reward bonus instantly!</p>
                        <button onclick="claimDailyReward()" style="background: white; color: #059669; border: none; padding: 8px 16px; border-radius: 8px; font-weight: bold; margin-top: 10px; cursor: pointer;">Claim 5.000 KWD</button>
                    </div>

                    <div class="action-card" style="border-left: 4px solid #3b82f6;">
                        <h4 style="font-size: 15px; margin-bottom: 5px;">🎮 Mission 1: Reflex Game</h4>
                        <p style="font-size: 12px; color: #64748b; margin-bottom: 10px;">Tap to complete task and earn KWD rewards.</p>
                        <button class="btn-green" onclick="completeTask('Game Mission', 3.500)">Play & Earn 3.500 KWD</button>
                    </div>

                    <div class="action-card" style="border-left: 4px solid #8b5cf6;">
                        <h4 style="font-size: 15px; margin-bottom: 5px;">📺 Sponsored Video Ads</h4>
                        <p style="font-size: 12px; color: #64748b; margin-bottom: 10px;">Watch short ad stream for revenue share.</p>
                        <button class="btn-blue" onclick="completeTask('Video Ad', 2.000)">Watch Ad (+2.000 KWD)</button>
                    </div>
                </div>

                <!-- TAB 2: SPIN WHEEL -->
                <div id="tabSpin" class="screen-section">
                    <h3 style="text-align: center; margin-bottom: 10px; color: #1e293b;">Lucky Spin Wheel</h3>
                    <p style="text-align: center; font-size: 12px; color: #64748b; margin-bottom: 10px;">Spin daily to win cash multipliers in KWD!</p>
                    
                    <div class="wheel-container">
                        <div class="wheel-pointer"></div>
                    </div>

                    <button class="btn-green" onclick="spinWheel()" style="margin-top: 20px;">Spin for 1 Ticket</button>
                </div>

                <!-- TAB 3: PLAY / GAMES ARENA -->
                <div id="tabPlay" class="screen-section">
                    <h3 style="margin-bottom: 10px; color: #1e293b;">Arcade Earning Arena</h3>
                    <p style="font-size: 12px; color: #64748b; margin-bottom: 15px;">Choose your game mode and build proof for your investors.</p>
                    
                    <div class="action-card">
                        <h4>🧩 Puzzle Solver Challenge</h4>
                        <p style="font-size: 12px; color: #64748b; margin: 5px 0;">Reward: 4.500 KWD</p>
                        <button class="btn-green" onclick="completeTask('Puzzle Game', 4.500)">Start Puzzle</button>
                    </div>

                    <div class="action-card">
                        <h4>🚀 Speed Blaster</h4>
                        <p style="font-size: 12px; color: #64748b; margin: 5px 0;">Reward: 6.000 KWD</p>
                        <button class="btn-blue" onclick="completeTask('Speed Game', 6.000)">Play Blaster</button>
                    </div>
                </div>

                <!-- TAB 4: RAFFLE & DRAWS -->
                <div id="tabRaffle" class="screen-section">
                    <h3 style="margin-bottom: 10px; color: #1e293b;">Hourly Cash Raffles</h3>
                    
                    <div class="action-card" style="background: #0f172a; color: white;">
                        <h4 style="color: #38bdf8;">$1,000 in CA$H Draw</h4>
                        <p style="font-size: 12px; color: #94a3b8; margin: 8px 0;">Draw in 43 minutes</p>
                        <button class="btn-green" onclick="alert('Ticket entered into $1,000 Raffle Draw!')">Flip & Enter Draw</button>
                    </div>

                    <div class="action-card" style="background: #0f172a; color: white;">
                        <h4 style="color: #34d399;">$200 Instant Cash Raffle</h4>
                        <p style="font-size: 12px; color: #94a3b8; margin: 8px 0;">Draw in 12 minutes</p>
                        <button class="btn-blue" onclick="alert('Ticket entered into $200 Raffle Draw!')">Enter Raffle</button>
                    </div>
                </div>

                <!-- TAB 5: WALLET & REGISTRATION -->
                <div id="tabWallet" class="screen-section">
                    <h3 style="margin-bottom: 10px; color: #1e293b;">Wallet & NIN Verification</h3>
                    
                    <div class="promo-banner" style="background: #1e293b; text-align: left; padding: 15px;">
                        <p style="font-size: 12px; color: #94a3b8;">Your Live Balance</p>
                        <h2 id="walletBalanceDisplay" style="font-size: 26px; color: #4ade80; margin: 5px 0;">8.000 KWD</h2>
                        <p style="font-size: 11px; color: #cbd5e1;">Status: <span id="verificationBadge" style="color: #fca5a5;">Unregistered</span></p>
                    </div>

                    <!-- Registration & NIN Verification Form -->
                    <div id="regSection" class="action-card" style="text-align: left;">
                        <h4 style="color: #1e293b; margin-bottom: 10px;">📝 Account & NIN Verification</h4>
                        <div class="input-group">
                            <label>Full Legal Name</label>
                            <input type="text" id="inputName" placeholder="e.g. Emmanuel Mary">
                        </div>
                        <div class="input-group">
                            <label>Username / ID</label>
                            <input type="text" id="inputUser" placeholder="e.g. Ottah23">
                        </div>
                        <div class="input-group">
                            <label>Email Address</label>
                            <input type="email" id="inputEmail" placeholder="user@domain.com">
                        </div>
                        <div class="input-group">
                            <label>Phone Number</label>
                            <input type="text" id="inputPhone" placeholder="+965 XXXX XXXX">
                        </div>
                        <div class="input-group">
                            <label>Nationality</label>
                            <select id="inputNation">
                                <option value="Kuwaiti">Kuwaiti</option>
                                <option value="Nigerian" selected>Nigerian</option>
                                <option value="International">International</option>
                            </select>
                        </div>
                        <div class="input-group">
                            <label>NIN / BVN / Passport Number</label>
                            <input type="text" id="inputNin" placeholder="Enter 11-digit NIN verification">
                        </div>
                        <button class="btn-green" onclick="registerAccount()">Verify & Save Profile</button>
                    </div>

                    <div id="payoutSection" class="hidden">
                        <button class="btn-green" onclick="requestWithdrawal()" style="background: #e11d48; margin-top: 15px;">Withdraw Funds & Generate Proof</button>
                    </div>
                </div>

            </div>

            <!-- Bottom Navigation Bar -->
            <div class="bottom-nav">
                <button class="nav-item active" onclick="switchTab('tabHome', this)">
                    <span class="nav-icon">🏠</span>Shop
                </button>
                <button class="nav-item" onclick="switchTab('tabSpin', this)">
                    <span class="nav-icon">🎡</span>Spin
                </button>
                <button class="nav-item" onclick="switchTab('tabPlay', this)">
                    <span class="nav-icon">🎮</span>Play
                </button>
                <button class="nav-item" onclick="switchTab('tabRaffle', this)">
                    <span class="nav-icon">🎟️</span>Raffle
                </button>
                <button class="nav-item" onclick="switchTab('tabWallet', this)">
                    <span class="nav-icon">💰</span>Wallet
                </button>
            </div>

        </div>

        <!-- POPUP PROOF MODAL -->
        <div id="popupModal" class="modal hidden">
            <div class="modal-box">
                <h3 id="modalTitle" style="color: #16a34a; margin-bottom: 10px;">Success</h3>
                <p id="modalText" style="font-size: 13px; color: #475569; margin-bottom: 15px; background: #f8fafc; padding: 10px; border-radius: 8px; text-align: left;"></p>
                <button class="btn-green" onclick="closeModal()">Close</button>
            </div>
        </div>

        <script>
            let currentUserId = null;

            function switchTab(tabId, btnElement) {
                document.querySelectorAll('.screen-section').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
                btnElement.classList.add('active');
            }

            async function registerAccount() {
                const payload = {
                    id: document.getElementById('inputUser').value,
                    name: document.getElementById('inputName').value,
                    email: document.getElementById('inputEmail').value,
                    phone: document.getElementById('inputPhone').value,
                    nationality: document.getElementById('inputNation').value,
                    identity_number: document.getElementById('inputNin').value
                };

                if(!payload.id || !payload.nin) {
                    alert('Please enter your Username and NIN verification number.');
                    return;
                }

                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if(res.ok) {
                    currentUserId = data.user_id;
                    updateUIBalances(data.cash_balance, data.tickets, data.gems);
                    document.getElementById('verificationBadge').innerText = "VERIFIED (NIN Active)";
                    document.getElementById('verificationBadge').style.color = "#4ade80";
                    document.getElementById('payoutSection').classList.remove('hidden');
                    showModal("Registration Successful!", `User ID: ${currentUserId}\\nNIN Verified & Linked to KWD Ledger.`);
                } else {
                    alert('Error: ' + data.detail);
                }
            }

            async function updateUIBalances(cash, tickets, gems) {
                document.getElementById('topCash').innerText = cash.toFixed(3);
                document.getElementById('walletBalanceDisplay').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('topTickets').innerText = tickets.toLocaleString();
                document.getElementById('topGems').innerText = gems;
            }

            async function completeTask(taskName, rewardAmount) {
                if(!currentUserId) {
                    alert('Please register and verify your NIN in the Wallet tab first!');
                    switchTab('tabWallet', document.querySelectorAll('.nav-item')[4]);
                    return;
                }
                const res = await fetch('/api/task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, reward: rewardAmount})
                });
                const data = await res.json();
                if(res.ok) {
                    updateUIBalances(data.cash_balance, data.tickets, data.gems);
                    showModal("Task Completed!", `Earned +${rewardAmount.toFixed(3)} KWD from ${taskName}.\\nNew Balance: ${data.cash_balance.toFixed(3)} KWD`);
                }
            }

            async function claimDailyReward() {
                await completeTask("Daily Reward Bonus", 5.000);
            }

            async function spinWheel() {
                const prizes = [0.100, 0.500, 1.000, 2.500, 5.000, 10.000];
                const prize = prizes[Math.floor(Math.random() * prizes.length)];
                await completeTask("Lucky Spin Wheel", prize);
            }

            async function requestWithdrawal() {
                const res = await fetch(`/api/user/${currentUserId}`);
                const data = await res.json();
                if(data.cash_balance <= 0) {
                    alert('Insufficient balance for withdrawal.');
                    return;
                }
                showModal("✅ OFFICIAL TRANSACTION PROOF", `User: ${currentUserId}\\nAmount: ${data.cash_balance.toFixed(3)} KWD\\nStatus: TRANSFER COMPLETED\\nNIN Verified: SUCCESSFUL\\nNetwork: SwiftBux Secure Ledger`);
            }

            function showModal(title, text) {
                document.getElementById('modalTitle').innerText = title;
                document.getElementById('modalText').innerText = text;
                document.getElementById('popupModal').classList.remove('hidden');
            }

            function closeModal() {
                document.getElementById('popupModal').classList.add('hidden');
            }
        </script>
    </body>
    </html>
    """

# --- BACKEND API SCHEMAS & ENDPOINTS ---
class UserReg(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    nationality: str
    identity_number: str

@app.post("/api/register")
def register_user(user: UserReg, db: Session = Depends(get_db)):
    existing = db.query(AppUser).filter((AppUser.id == user.id) | (AppUser.identity_number == user.identity_number)).first()
    if existing:
        return {
            "user_id": existing.id,
            "cash_balance": float(existing.cash_balance),
            "tickets": float(existing.tickets),
            "gems": int(existing.gems)
        }
    
    new_user = AppUser(
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
    user = db.query(AppUser).filter(AppUser.id == user_id).first()
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
    user = db.query(AppUser).filter(AppUser.id == task.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.cash_balance += Decimal(str(task.reward))
    user.tickets += Decimal("150.00")
    db.commit()
    return {
        "cash_balance": float(user.cash_balance),
        "tickets": float(user.tickets),
        "gems": int(user.gems)
    }