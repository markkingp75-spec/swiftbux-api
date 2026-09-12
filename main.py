from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import os
import requests

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_live_production.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LiveProductionUser(Base):
    __tablename__ = "live_production_users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    nationality = Column(String)
    identity_number = Column(String, unique=True, index=True)
    cash_balance = Column(Numeric(10, 3), default=Decimal("0.000"))
    tickets = Column(Numeric(10, 2), default=Decimal("100.00"))
    gems = Column(Numeric(10, 0), default=Decimal("5"))
    referral_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class LiveCampaign(Base):
    __tablename__ = "live_campaigns"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    product_link = Column(String)
    reward_amount = Column(Numeric(10, 3))
    advertiser = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwiftBux Live Production Gateway")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwiftBux Live Production Platform</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
            body { background: #f1f5f9; color: #1e293b; min-height: 100vh; display: flex; flex-direction: column; }
            
            header { background: #ffffff; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            header h1 { font-size: 22px; color: #2563eb; display: flex; align-items: center; gap: 10px; }
            .asset-badges { display: flex; gap: 15px; align-items: center; font-size: 14px; font-weight: bold; }
            .badge-box { background: #f8fafc; padding: 6px 14px; border-radius: 20px; border: 1px solid #cbd5e1; display: flex; align-items: center; gap: 6px; }

            .main-layout { display: flex; flex: 1; max-width: 1600px; width: 100%; margin: 0 auto; padding: 25px; gap: 25px; }
            .sidebar { width: 290px; background: #ffffff; border-radius: 12px; padding: 20px; border: 1px solid #cbd5e1; display: flex; flex-direction: column; gap: 10px; height: fit-content; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            .nav-btn { background: transparent; color: #475569; border: none; text-align: left; padding: 14px 18px; border-radius: 8px; font-size: 15px; cursor: pointer; transition: 0.2s; font-weight: 600; display: flex; align-items: center; gap: 12px; }
            .nav-btn:hover, .nav-btn.active { background: #eff6ff; color: #2563eb; }

            .content-area { flex: 1; background: #ffffff; border-radius: 12px; padding: 30px; border: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05); min-height: 75vh; }
            .tab-pane { display: none; }
            .tab-pane.active { display: block; }
            .hidden { display: none !important; }

            .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px; }
            .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }
            .card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; text-align: left; }
            .card h3 { font-size: 16px; color: #1e293b; margin-bottom: 8px; }
            .card p { font-size: 13px; color: #64748b; margin-bottom: 15px; }

            .form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 15px; }
            .form-group { display: flex; flex-direction: column; gap: 6px; text-align: left; margin-bottom: 15px; }
            .form-group.full { grid-column: span 2; }
            label { font-size: 13px; font-weight: bold; color: #475569; }
            input, select { background: #ffffff; border: 1px solid #cbd5e1; color: #1e293b; padding: 12px 14px; border-radius: 8px; font-size: 15px; width: 100%; }
            input:focus, select:focus { border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }

            .btn-primary { background: #2563eb; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; font-size: 15px; cursor: pointer; transition: 0.2s; width: 100%; }
            .btn-primary:hover { background: #1d4ed8; }
            .btn-green { background: #16a34a; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: bold; cursor: pointer; }
            .btn-green:hover { background: #15803d; }
            .btn-danger { background: #dc2626; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; }

            .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15,23,42,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
            .modal-box { background: white; padding: 30px; border-radius: 12px; width: 480px; text-align: center; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2); }
        </style>
    </head>
    <body>

        <header>
            <h1>⚡ SwiftBux Live Production Platform <span style="font-size: 12px; background: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 6px;">Live Gateway Active</span></h1>
            <div class="asset-badges">
                <div class="badge-box" style="color: #16a34a;">💵 Cash: <span id="headerCash">0.000</span> KWD</div>
                <div class="badge-box" style="color: #d97706;">🎟️ Tickets: <span id="headerTickets">100.00</span></div>
                <div class="badge-box" style="color: #db2777;">💎 Gems: <span id="headerGems">5</span></div>
            </div>
        </header>

        <div class="main-layout">
            <div class="sidebar">
                <button class="nav-btn active" onclick="switchTab('tabReg', this)">📝 User Registration & NIN</button>
                <button class="nav-btn" onclick="switchTab('tabDash', this)">📊 Earnings Dashboard</button>
                <button class="nav-btn" onclick="switchTab('tabAds', this)">📢 Promote & Advertise Products</button>
                <button class="nav-btn" onclick="switchTab('tabMarket', this)">🛒 Marketplace & Offers</button>
                <button class="nav-btn" onclick="switchTab('tabWallet', this)">🏦 Live Wallet & Withdrawals</button>
            </div>

            <div class="content-area">
                <div id="tabReg" class="tab-pane active">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Secure User Registration & Verification</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 25px;">Enter your real credentials to establish your verified account profile.</p>

                    <form onsubmit="handleRegistration(event)">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Full Legal Name</label>
                                <input type="text" id="regName" required>
                            </div>
                            <div class="form-group">
                                <label>Username / Unique ID</label>
                                <input type="text" id="regId" required>
                            </div>
                            <div class="form-group">
                                <label>Email Address</label>
                                <input type="email" id="regEmail" required>
                            </div>
                            <div class="form-group">
                                <label>Phone Number</label>
                                <input type="text" id="regPhone" required>
                            </div>
                            <div class="form-group">
                                <label>Nationality</label>
                                <select id="regNationality">
                                    <option value="Nigerian">Nigerian</option>
                                    <option value="Kuwaiti">Kuwaiti</option>
                                    <option value="International">International</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>NIN / BVN Number</label>
                                <input type="text" id="regNin" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-primary" style="margin-top: 15px;">Complete Registration</button>
                    </form>
                </div>

                <div id="tabDash" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 15px;">User Earnings & Activity Dashboard</h2>
                    <div class="grid-3" style="margin-bottom: 25px;">
                        <div class="card" style="border-left: 4px solid #2563eb;">
                            <h3>Current Balance</h3>
                            <div style="font-size: 28px; font-weight: bold; color: #16a34a; margin-top: 5px;" id="dashBalance">0.000 KWD</div>
                        </div>
                        <div class="card" style="border-left: 4px solid #16a34a;">
                            <h3>Min Withdrawal Limit</h3>
                            <div style="font-size: 28px; font-weight: bold; color: #1e293b; margin-top: 5px;">50.000 KWD</div>
                        </div>
                        <div class="card" style="border-left: 4px solid #d97706;">
                            <h3>Gateway Status</h3>
                            <div style="font-size: 16px; font-weight: bold; color: #16a34a; margin-top: 10px;">Connected (Live)</div>
                        </div>
                    </div>
                </div>

                <div id="tabAds" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Merchant & Creator Ad Promotion Hub</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Launch promotional campaigns for your products or platforms.</p>

                    <form onsubmit="createCampaign(event)" style="background: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 25px;">
                        <h3 style="margin-bottom: 15px; color: #2563eb;">Publish New Ad Campaign</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Campaign Title</label>
                                <input type="text" id="campTitle" placeholder="e.g. 1688 Imported Car Covers" required>
                            </div>
                            <div class="form-group">
                                <label>Product Link</label>
                                <input type="url" id="campLink" placeholder="https://yourwebsite.com" required>
                            </div>
                            <div class="form-group">
                                <label>Reward Per Engagement (KWD)</label>
                                <input type="number" step="0.001" id="campReward" placeholder="2.500" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-green" style="margin-top: 10px;">Launch Campaign Live</button>
                    </form>
                </div>

                <div id="tabMarket" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Active Marketplace Sponsored Offers</h2>
                    <div id="campaignList" class="grid-2">
                        <div class="card">
                            <h3>🚀 Sample AI Tool Promotion</h3>
                            <p>Explore cutting-edge AI tools.</p>
                            <button class="btn-green" onclick="interactWithAd('Sample AI Tool', 3.000, 'https://example.com')">Visit & Earn 3.000 KWD</button>
                        </div>
                    </div>
                </div>

                <div id="tabWallet" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Live Bank & Wallet Payouts</h2>
                    <div class="card" style="max-width: 500px; margin: 0 auto; text-align: center;">
                        <h3 style="color: #16a34a; font-size: 24px; margin-bottom: 10px;" id="walletBalance">0.000 KWD</h3>
                        <p style="margin-bottom: 15px;">Threshold required for real transfer: 50.000 KWD</p>
                        <div class="form-group">
                            <label>Destination Account Number / IBAN</label>
                            <input type="text" id="walletDest" placeholder="Enter bank account number" required>
                        </div>
                        <div class="form-group">
                            <label>Bank Code (e.g. 058 for GTB, etc.)</label>
                            <input type="text" id="bankCode" placeholder="Enter bank code" required>
                        </div>
                        <button class="btn-danger" onclick="requestLiveWithdrawal()">Request Live Transfer</button>
                    </div>
                </div>
            </div>
        </div>

        <div id="proofModal" class="modal-overlay hidden">
            <div class="modal-box">
                <h3 id="modalTitle" style="color: #16a34a; margin-bottom: 12px;">Success</h3>
                <p id="modalText" style="font-size: 14px; color: #334155; background: #f8fafc; padding: 12px; border-radius: 8px; text-align: left; margin-bottom: 20px; line-height: 1.5;"></p>
                <button class="btn-primary" onclick="closeModal()">Close Window</button>
            </div>
        </div>

        <script>
            let currentUserId = null;

            function switchTab(tabId, btnElement) {
                document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
                btnElement.classList.add('active');
            }

            async function handleRegistration(e) {
                e.preventDefault();
                const payload = {
                    id: document.getElementById('regId').value,
                    name: document.getElementById('regName').value,
                    email: document.getElementById('regEmail').value,
                    phone: document.getElementById('regPhone').value,
                    nationality: document.getElementById('regNationality').value,
                    identity_number: document.getElementById('regNin').value
                };

                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if(res.ok) {
                    currentUserId = data.user_id;
                    updateUI(data.cash_balance, data.tickets, data.gems);
                    showModal("Registration Successful", `User ID: ${currentUserId}\\nProfile verified on Live Gateway.`);
                    switchTab('tabDash', document.querySelectorAll('.nav-btn')[1]);
                } else {
                    alert('Error: ' + data.detail);
                }
            }

            async function updateUI(cash, tickets, gems) {
                document.getElementById('headerCash').innerText = cash.toFixed(3);
                document.getElementById('dashBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('walletBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('headerTickets').innerText = tickets.toLocaleString();
                document.getElementById('headerGems').innerText = gems;
            }

            async function createCampaign(e) {
                e.preventDefault();
                if(!currentUserId) {
                    alert('Please register an account first!');
                    switchTab('tabReg', document.querySelectorAll('.nav-btn')[0]);
                    return;
                }
                const payload = {
                    title: document.getElementById('campTitle').value,
                    product_link: document.getElementById('campLink').value,
                    reward_amount: parseFloat(document.getElementById('campReward').value),
                    advertiser: currentUserId
                };

                const res = await fetch('/api/campaigns', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(res.ok) {
                    alert('Campaign published successfully!');
                    loadCampaigns();
                    switchTab('tabMarket', document.querySelectorAll('.nav-btn')[3]);
                }
            }

            async function loadCampaigns() {
                const res = await fetch('/api/campaigns');
                const campaigns = await res.json();
                const container = document.getElementById('campaignList');
                let html = '<div class="card"><h3>🚀 Sample AI Tool Promotion</h3><p>Explore cutting-edge AI tools.</p><button class="btn-green" onclick="interactWithAd(\\'Sample AI Tool\\', 3.000, \\'https://example.com\\')">Visit & Earn 3.000 KWD</button></div>';
                
                campaigns.forEach(c => {
                    html += `
                        <div class="card">
                            <h3>📢 ${c.title}</h3>
                            <p>Promoted by: ${c.advertiser} | Reward: ${c.reward_amount.toFixed(3)} KWD</p>
                            <button class="btn-green" onclick="interactWithAd('${c.title}', ${c.reward_amount}, '${c.product_link}')">Visit Link & Earn</button>
                        </div>
                    `;
                });
                container.innerHTML = html;
            }

            async function interactWithAd(title, reward, link) {
                if(!currentUserId) {
                    alert('Please register first!');
                    switchTab('tabReg', document.querySelectorAll('.nav-btn')[0]);
                    return;
                }
                window.open(link, '_blank');
                const res = await fetch('/api/task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, reward: reward})
                });
                const data = await res.json();
                if(res.ok) {
                    updateUI(data.cash_balance, data.tickets, data.gems);
                    showModal("Reward Claimed!", `Successfully viewed campaign: ${title}\\nEarned +${reward.toFixed(3)} KWD.`);
                }
            }

            async function requestLiveWithdrawal() {
                if(!currentUserId) {
                    alert('Please register first!');
                    return;
                }
                const account_number = document.getElementById('walletDest').value;
                const bank_code = document.getElementById('bankCode').value;

                if(!account_number || !bank_code) {
                    alert('Please enter both account number and bank code.');
                    return;
                }

                const res = await fetch('/api/live-withdraw', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, account_number: account_number, bank_code: bank_code})
                });
                const data = await res.json();
                if(res.ok) {
                    showModal("🚀 LIVE TRANSFER INITIATED", `Status: ${data.status}\\nMessage: ${data.message}\\nFunds are being sent via live payment gateway.`);
                    updateUI(data.cash_balance, data.tickets, data.gems);
                } else {
                    alert('Transfer Error: ' + data.detail);
                }
            }

            function showModal(title, text) {
                document.getElementById('modalTitle').innerText = title;
                document.getElementById('modalText').innerText = text.replace(/\\n/g, '\\n');
                document.getElementById('proofModal').classList.remove('hidden');
            }

            function closeModal() {
                document.getElementById('proofModal').classList.add('hidden');
            }

            loadCampaigns();
        </script>
    </body>
    </html>
    """

# --- LIVE BACKEND API GATEWAY ENDPOINTS ---
class UserReg(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    nationality: str
    identity_number: str

@app.post("/api/register")
def register_user(user: UserReg, db: Session = Depends(get_db)):
    existing = db.query(LiveProductionUser).filter((LiveProductionUser.id == user.id) | (LiveProductionUser.identity_number == user.identity_number)).first()
    if existing:
        return {"user_id": existing.id, "cash_balance": float(existing.cash_balance), "tickets": float(existing.tickets), "gems": int(existing.gems)}
    
    new_user = LiveProductionUser(
        id=user.id, name=user.name, email=user.email, phone=user.phone,
        nationality=user.nationality, identity_number=user.identity_number,
        cash_balance=Decimal("0.000"), tickets=Decimal("100.00"), gems=Decimal("5"),
        referral_code=user.id + "_ref"
    )
    db.add(new_user)
    db.commit()
    return {"user_id": new_user.id, "cash_balance": float(new_user.cash_balance), "tickets": float(new_user.tickets), "gems": int(new_user.gems)}

@app.get("/api/user/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(LiveProductionUser).filter(LiveProductionUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.id, "cash_balance": float(user.cash_balance), "tickets": float(user.tickets), "gems": int(user.gems)}

class CampModel(BaseModel):
    title: str
    product_link: str
    reward_amount: float
    advertiser: str

@app.post("/api/campaigns")
def create_campaign(camp: CampModel, db: Session = Depends(get_db)):
    new_camp = LiveCampaign(
        id="camp_" + str(datetime.now().timestamp()),
        title=camp.title,
        product_link=camp.product_link,
        reward_amount=Decimal(str(camp.reward_amount)),
        advertiser=camp.advertiser
    )
    db.add(new_camp)
    db.commit()
    return {"status": "success"}

@app.get("/api/campaigns")
def get_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(LiveCampaign.id, LiveCampaign.title, LiveCampaign.product_link, LiveCampaign.reward_amount, LiveCampaign.advertiser).all()
    return [{"id": c.id, "title": c.title, "product_link": c.product_link, "reward_amount": float(c.reward_amount), "advertiser": c.advertiser} for c in campaigns]

class TaskPost(BaseModel):
    user_id: str
    reward: float

@app.post("/api/task")
def process_task(task: TaskPost, db: Session = Depends(get_db)):
    user = db.query(LiveProductionUser).filter(LiveProductionUser.id == task.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.cash_balance += Decimal(str(task.reward))
    user.tickets += Decimal("10.00")
    db.commit()
    return {"cash_balance": float(user.cash_balance), "tickets": float(user.tickets), "gems": int(user.gems)}

class WithdrawPost(BaseModel):
    user_id: str
    account_number: str
    bank_code: str

@app.post("/api/live-withdraw")
def live_withdraw(data: WithdrawPost, db: Session = Depends(get_db)):
    user = db.query(LiveProductionUser).filter(LiveProductionUser.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.cash_balance < Decimal("50.000"):
        raise HTTPException(status_code=400, detail="Minimum threshold is 50.000 KWD.")

    # Retrieve live gateway secret key from environment variable
    secret_key = os.getenv("FLW_SECRET_KEY", "FLWSECK_LIVE_SAMPLE_KEY")
    
    amount_to_send = float(user.cash_balance)
    
    # Live API payload to payment provider
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "account_bank": data.bank_code,
        "account_number": data.account_number,
        "amount": amount_to_send,
        "currency": "KWD",
        "narration": "SwiftBux Payout",
        "reference": f"swb_txn_{int(datetime.now().timestamp())}"
    }

    try:
        # Request transfer via payment gateway API
        response = requests.post("https://api.flutterwave.com/v3/transfers", json=payload, headers=headers, timeout=10)
        res_data = response.json()
        
        if response.status_code == 200 and res_data.get("status") == "success":
            # Deduct balance after successful live bank transfer queue
            user.cash_balance = Decimal("0.000")
            db.commit()
            return {"status": "success", "message": "Transfer successfully processed to bank account.", "cash_balance": float(user.cash_balance), "tickets": float(user.tickets), "gems": int(user.gems)}
        else:
            # Fallback error handling if API credentials or bank details are invalid
            error_msg = res_data.get("message", "Gateway transfer failed. Please verify API key configuration.")
            raise HTTPException(status_code=400, detail=error_msg)
            
    except Exception as e:
        # If running without a live-funded key, return clear diagnostics for setup
        if "FLWSECK_LIVE_SAMPLE_KEY" in secret_key:
            raise HTTPException(status_code=400, detail="Live Payout Error: Please add your actual Flutterwave live secret key to your Render Environment Variables as 'FLW_SECRET_KEY'.")
        raise HTTPException(status_code=400, detail=str(e))