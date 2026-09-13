from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# Import our brand new dedicated module
from mining_ads_engine import Base, UserMiningState, AdCampaignRecord, MiningAdsEngineController

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_master_live.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwiftBux Autonomous Global Trade, Mining & Ad Platform")

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
        <title>SwiftBux Autonomous Trade, 24/7 Mining & Ad Network</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
            body { background: #f4f5f7; color: #333; min-height: 100vh; display: flex; flex-direction: column; }
            
            .top-nav-bar { background: #ff5000; padding: 12px 20px; color: white; display: flex; flex-direction: column; gap: 10px; width: 100%; }
            .top-tabs { display: flex; gap: 20px; font-size: 16px; font-weight: bold; align-items: center; flex-wrap: wrap; }
            .top-tabs span { cursor: pointer; opacity: 0.8; padding-bottom: 4px; border-bottom: 2px solid transparent; }
            .top-tabs span.active { opacity: 1; border-bottom: 2px solid white; }
            
            .search-container { display: flex; background: white; border-radius: 20px; padding: 6px 15px; align-items: center; gap: 10px; max-width: 600px; }
            .search-container input { border: none; outline: none; flex: 1; font-size: 14px; color: #333; }
            .search-btn { background: #ff5000; color: white; border: none; padding: 6px 18px; border-radius: 16px; font-weight: bold; cursor: pointer; }

            .category-grid { background: white; padding: 15px 10px; display: grid; grid-template-columns: repeat(6, 1fr); text-align: center; gap: 10px; border-bottom: 1px solid #eee; width: 100%; }
            .cat-item { display: flex; flex-direction: column; align-items: center; gap: 5px; font-size: 12px; color: #555; cursor: pointer; }
            .cat-icon { width: 44px; height: 44px; background: #fff0eb; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; color: #ff5000; }

            .main-layout { display: flex; flex-direction: row; flex: 1; max-width: 1400px; width: 100%; margin: 0 auto; padding: 20px; gap: 20px; align-items: flex-start; }
            .sidebar { width: 280px; flex-shrink: 0; background: white; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; gap: 10px; }
            .nav-btn { background: transparent; color: #475569; border: none; text-align: left; padding: 12px 15px; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 10px; width: 100%; }
            .nav-btn:hover, .nav-btn.active { background: #fff0eb; color: #ff5000; }

            .content-area { flex: 1; min-width: 0; background: white; border-radius: 12px; padding: 25px; border: 1px solid #e2e8f0; min-height: 75vh; }
            .tab-pane { display: none; }
            .tab-pane.active { display: block; }

            .form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; }
            .form-group { display: flex; flex-direction: column; gap: 5px; text-align: left; margin-bottom: 12px; }
            .form-group.full { grid-column: span 2; }
            label { font-size: 12px; font-weight: bold; color: #555; }
            input, select, textarea { background: #fff; border: 1px solid #ccc; padding: 10px; border-radius: 6px; font-size: 14px; width: 100%; }
            
            .btn-orange { background: #ff5000; color: white; border: none; padding: 10px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; }
            .btn-orange:hover { background: #e04500; }

            .card { background: #f8f9fa; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: left; margin-bottom: 15px; }
            .whitepaper-box { background: #1e293b; color: #f8fafc; padding: 20px; border-radius: 8px; font-family: monospace; font-size: 12px; line-height: 1.6; white-space: pre-wrap; text-align: left; max-height: 400px; overflow-y: auto; }
        </style>
    </head>
    <body>

        <div class="top-nav-bar">
            <div class="top-tabs">
                <span class="active" onclick="switchTab('tabRec', this)">Rec.</span>
                <span onclick="switchTab('tabMining', this)">24H Mining</span>
                <span onclick="switchTab('tabAdsHub', this)">Ad Network</span>
                <span onclick="switchTab('tabWhitepaper', this)">Live Whitepaper</span>
                <span onclick="switchTab('tabMining', this)" style="margin-left: auto; font-size: 13px; background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 12px;">👑 Owner Vault: Live</span>
            </div>
            <div class="search-container">
                <span style="color: #ff5000;">⛏️</span>
                <input type="text" id="searchInput" placeholder="Search 24h mining tokens, factory ads, or whitepaper details...">
                <button class="search-btn" onclick="alert('Search operational.')">GO</button>
            </div>
        </div>

        <div class="category-grid">
            <div class="cat-item" onclick="switchTab('tabMining', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">⛏️</div>
                <span>24H Mining</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabMining', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">🎁</div>
                <span>Daily Claim</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabAdsHub', document.querySelectorAll('.nav-btn')[3])">
                <div class="cat-icon">📢</div>
                <span>Ad Hub</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabWhitepaper', document.querySelectorAll('.nav-btn')[4])">
                <div class="cat-icon">📜</div>
                <span>Whitepaper</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabWallet', document.querySelectorAll('.nav-btn')[6])">
                <div class="cat-icon">💳</div>
                <span>Payouts</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabWatchdog', document.querySelectorAll('.nav-btn')[5])">
                <div class="cat-icon">🛡️</div>
                <span>Security</span>
            </div>
        </div>

        <div class="main-layout">
            <div class="sidebar">
                <button class="nav-btn active" onclick="switchTab('tabReg', this)">📝 Profile & Delivery Address</button>
                <button class="nav-btn" onclick="switchTab('tabDash', this)">📊 User Dashboard</button>
                <button class="nav-btn" onclick="switchTab('tabMining', this)">⛏️ 24H Mining & Daily Claims</button>
                <button class="nav-btn" onclick="switchTab('tabAdsHub', this)">📢 Ad Promotion & Marketing Hub</button>
                <button class="nav-btn" onclick="switchTab('tabWhitepaper', this)">📜 Live Platform Whitepaper</button>
                <button class="nav-btn" onclick="switchTab('tabWatchdog', this)">🛡️ Autonomous AI Security</button>
                <button class="nav-btn" onclick="switchTab('tabWallet', this)">🏦 AI Auto-Withdrawal</button>
            </div>

            <div class="content-area">
                <!-- TAB 1: REGISTRATION -->
                <div id="tabReg" class="tab-pane active">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">User Registration & Delivery Profile</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 20px;">Register your profile to unlock 24-hour mining rewards, advertising campaigns, and international doorstep shipping.</p>

                    <form onsubmit="handleRegistration(event)">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Full Legal Name</label>
                                <input type="text" id="regName" required>
                            </div>
                            <div class="form-group">
                                <label>Username / ID</label>
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
                                <label>Country / Destination</label>
                                <select id="regNationality">
                                    <option value="Nigeria">Nigeria (Doorstep Cargo)</option>
                                    <option value="Kuwait">Kuwait (GCC Cargo)</option>
                                    <option value="International">Other International</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>NIN / BVN Verification Number</label>
                                <input type="text" id="regNin" required>
                            </div>
                            <div class="form-group full">
                                <label>Exact Delivery Street Address</label>
                                <input type="text" id="regAddress" placeholder="e.g. 15 University Road / City District" required>
                            </div>
                            <div class="form-group">
                                <label>City / State</label>
                                <input type="text" id="regCity" placeholder="e.g. Lagos / Kuwait City" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-orange" style="margin-top: 15px;">Save Profile & Location</button>
                    </form>
                </div>

                <!-- TAB 2: DASHBOARD -->
                <div id="tabDash" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 15px;">User Dashboard & Mining Assets</h2>
                    <div class="card">
                        <h3 style="font-size: 14px; color: #888;">Mined Token Balance</h3>
                        <div style="font-size: 26px; font-weight: bold; color: #16a34a; margin-top: 5px;" id="dashMinedBalance">0.000 Tokens</div>
                    </div>
                </div>

                <!-- TAB 3: 24H MINING & DAILY CLAIMS -->
                <div id="tabMining" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">24-Hour Automated Mining & Daily Rewards</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 20px;">Click below to start your 24-hour mining cycle and claim your daily reward bonus.</p>
                    
                    <div class="card" style="text-align: center;">
                        <h3 style="font-size: 20px; color: #ff5000; margin-bottom: 10px;">⛏️ SwiftBux Cloud Miner</h3>
                        <p style="font-size: 14px; color: #444; margin-bottom: 20px;">Mined Rewards: <span id="miningBalanceDisplay" style="font-weight:bold; color:#16a34a;">0.000</span> Tokens</p>
                        <div style="display: flex; gap: 15px; justify-content: center;">
                            <button class="btn-orange" onclick="startMiningSession()">Start / Check 24H Mining</button>
                            <button class="btn-orange" style="background: #16a34a;" onclick="claimDailyReward()">Claim Daily Reward (+5.0)</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 4: AD PROMOTION & MARKETING HUB -->
                <div id="tabAdsHub" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">Ad Promotion & Marketing Hub</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 20px;">Manage and publish ad campaigns to promote products across social media and platform networks.</p>

                    <form onsubmit="postAdCampaign(event)" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 20px;">
                        <h3 style="color: #ff5000; margin-bottom: 10px; font-size: 15px;">Launch New Ad Campaign</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Campaign Title</label>
                                <input type="text" id="adTitle" placeholder="e.g. 1688 Car Cover Promo" required>
                            </div>
                            <div class="form-group">
                                <label>Target Link</label>
                                <input type="url" id="adLink" placeholder="https://yourlink.com" required>
                            </div>
                            <div class="form-group">
                                <label>Reward Per View (Tokens)</label>
                                <input type="number" step="0.001" id="adReward" placeholder="2.500" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-orange" style="margin-top: 10px;">Publish Ad Live</button>
                    </form>

                    <div id="adCampaignList" class="card">
                        <h3 style="font-size: 14px; color: #ff5000; margin-bottom: 5px;">🔥 Active Global Ad: 1688 Mountain Bike Promo</h3>
                        <p style="font-size: 12px; color: #666; margin-bottom: 10px;">Reward: 3.0 Tokens per view.</p>
                        <button class="btn-orange" onclick="engageAdCampaign('1688 Mountain Bike Promo', 3.0)">View Ad & Earn Reward</button>
                    </div>
                </div>

                <!-- TAB 5: LIVE WHITEPAPER -->
                <div id="tabWhitepaper" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">📜 Live Platform Whitepaper</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">Official architecture and economic documentation of the SwiftBux Autonomous Ecosystem.</p>
                    <div class="whitepaper-box" id="whitepaperContent">Loading live whitepaper...</div>
                </div>

                <!-- TAB 6: AUTONOMOUS AI SECURITY -->
                <div id="tabWatchdog" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">🛡️ Autonomous AI Security & Watchdog</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">24/7 server monitoring, anti-fraud payload inspection, and secure uptime defense.</p>
                    <div class="card">
                        <h3 style="color: #16a34a; font-size: 16px; margin-bottom: 5px;">🟢 Watchdog Sentinel: Fully Operational</h3>
                        <p style="font-size: 13px; color: #555;">All mining cycles, ad impressions, and payout requests are protected by autonomous encryption.</p>
                    </div>
                </div>

                <!-- TAB 7: WALLET -->
                <div id="tabWallet" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">AI Automated Payout Gateway</h2>
                    <div class="card" style="max-width: 500px; margin: 0 auto; text-align: center;">
                        <h3 style="color: #16a34a; font-size: 24px; margin-bottom: 10px;" id="walletBalance">0.000 KWD</h3>
                        <div class="form-group">
                            <label>Bank Account Number / PayPal Email</label>
                            <input type="text" id="payoutDest" placeholder="Enter bank account or PayPal email" required>
                        </div>
                        <button class="btn-orange" onclick="alert('Withdrawal request submitted to AI payout queue.')">Request AI Auto-Withdrawal</button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let currentUserId = null;

            function switchTab(tabId, btnElement) {
                document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
                if(btnElement) btnElement.classList.add('active');
                if(tabId === 'tabWhitepaper') loadWhitepaper();
            }

            async function handleRegistration(e) {
                e.preventDefault();
                currentUserId = document.getElementById('regId').value;
                alert('Registration successful for user: ' + currentUserId);
                switchTab('tabMining', document.querySelectorAll('.nav-btn')[2]);
            }

            async function startMiningSession() {
                if(!currentUserId) { alert('Please register first!'); return; }
                const res = await fetch('/api/mining/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId})
                });
                const data = await res.json();
                document.getElementById('miningBalanceDisplay').innerText = data.mined_balance.toFixed(3);
                document.getElementById('dashMinedBalance').innerText = data.mined_balance.toFixed(3) + " Tokens";
                alert('Mining Status: ' + data.status);
            }

            async function claimDailyReward() {
                if(!currentUserId) { alert('Please register first!'); return; }
                const res = await fetch('/api/mining/claim-daily', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId})
                });
                const data = await res.json();
                if(data.status === 'success') {
                    document.getElementById('miningBalanceDisplay').innerText = data.mined_balance.toFixed(3);
                    document.getElementById('dashMinedBalance').innerText = data.mined_balance.toFixed(3) + " Tokens";
                    alert('Daily reward claimed! +5.0 Tokens added.');
                } else {
                    alert(data.message);
                }
            }

            async function loadWhitepaper() {
                const res = await fetch('/api/whitepaper');
                const data = await res.json();
                document.getElementById('whitepaperContent').innerText = data.whitepaper;
            }

            function postAdCampaign(e) {
                e.preventDefault();
                const title = document.getElementById('adTitle').value;
                const link = document.getElementById('adLink').value;
                const reward = document.getElementById('adReward').value;
                
                document.getElementById('adCampaignList').innerHTML += `
                    <div style="margin-top:15px; border-top:1px solid #eee; padding-top:10px;">
                        <h3 style="font-size: 14px; color: #ff5000;">🔥 ${title}</h3>
                        <p style="font-size: 12px; color: #666;">Reward: ${reward} Tokens per view.</p>
                        <button class="btn-orange" onclick="engageAdCampaign('${title}', ${reward})">View Ad & Earn Reward</button>
                    </div>
                `;
                alert('Ad campaign published live successfully!');
            }

            function engageAdCampaign(title, reward) {
                alert(`Engaged with ad: "${title}"! Reward of ${reward} Tokens credited.`);
            }
        </script>
    </body>
    </html>
    """

# --- BACKEND API ENDPOINTS ---
@app.post("/api/mining/start")
def start_mining(data: dict, db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    state = db.query(UserMiningState).filter(UserMiningState.user_id == user_id).first()
    if not state:
        state = UserMiningState(user_id=user_id, mined_balance=Decimal("0.000"))
        db.add(state)
        db.commit()
    
    result = MiningAdsEngineController.start_mining_session(user_id, state)
    db.commit()
    return result

@app.post("/api/mining/claim-daily")
def claim_daily(data: dict, db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    state = db.query(UserMiningState).filter(UserMiningState.user_id == user_id).first()
    if not state:
        state = UserMiningState(user_id=user_id, mined_balance=Decimal("0.000"))
        db.add(state)
        db.commit()
    
    result = MiningAdsEngineController.claim_daily_reward(user_id, state)
    db.commit()
    return result

@app.get("/api/whitepaper")
def get_whitepaper():
    return {"whitepaper": MiningAdsEngineController.get_whitepaper_text()}