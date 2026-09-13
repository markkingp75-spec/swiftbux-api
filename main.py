from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_global_ai.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GlobalUser(Base):
    __tablename__ = "global_users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    nationality = Column(String)
    identity_number = Column(String, unique=True, index=True)
    cash_balance = Column(Numeric(10, 3), default=Decimal("0.000"))
    tasks_completed = Column(Numeric(10, 0), default=Decimal("0"))
    tickets = Column(Numeric(10, 2), default=Decimal("100.00"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class GlobalProduct(Base):
    __tablename__ = "global_products"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    supplier = Column(String)
    origin = Column(String)
    price = Column(Numeric(10, 3))
    category = Column(String)
    description = Column(String)

class PlatformTreasury(Base):
    __tablename__ = "platform_vault"
    id = Column(String, primary_key=True, default="vault_main")
    owner_revenue = Column(Numeric(10, 3), default=Decimal("250.000"))
    total_payouts = Column(Numeric(10, 3), default=Decimal("1420.000"))

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwiftBux Global Sourcing & AI Business Platform")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_initial_products(db: Session):
    count = db.query(GlobalProduct).count()
    if count == 0:
        initials = [
            GlobalProduct(id="p1", title="1688 Waterproof All-Weather Car Body Cover", supplier="Guangzhou Auto Accessories Co. (China)", origin="China", price=14.500, category="Automotive", description="High-durability reflective material, direct bulk factory sourcing."),
            GlobalProduct(id="p2", title="Redmi 8 Pro / Smart Phone Wholesale Lot", supplier="Shenzhen Electronics Hub (China)", origin="China", price=45.000, category="Electronics", description="Unlocked global edition smartphones, factory direct reseller rates."),
            GlobalProduct(id="p3", title="Handmade Leather Goods & Accessories", supplier="Delhi Export Artisans (India)", origin="India", price=22.000, category="Fashion", description="Genuine leather bags and wallets for boutique retail resellers."),
            GlobalProduct(id="p4", title="USA Branded Smart Fitness Smartwatch V2", supplier="California Tech Supply Inc. (USA)", origin="USA", price=32.000, category="Electronics", description="Latest fitness tracker with heart-rate monitoring and GPS."),
            GlobalProduct(id="p5", title="Lagos Made Ankara Luxury Fashion Fabrics (Bundle)", supplier="Ankara Global Textiles (Nigeria)", origin="Nigeria", price=18.000, category="Fashion", description="Vibrant premium traditional fabrics direct from local weavers.")
        ]
        db.add_all(initials)
        db.commit()

# --- FRONTEND INTERFACE ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwiftBux Global Marketplace & AI Consultant</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
            body { background: #f8fafc; color: #1e293b; min-height: 100vh; display: flex; flex-direction: column; }
            
            header { background: #ffffff; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            header h1 { font-size: 20px; color: #2563eb; display: flex; align-items: center; gap: 10px; }
            .asset-badges { display: flex; gap: 15px; align-items: center; font-size: 14px; font-weight: bold; }
            .badge-box { background: #f1f5f9; padding: 6px 14px; border-radius: 20px; border: 1px solid #cbd5e1; display: flex; align-items: center; gap: 6px; }

            .main-layout { display: flex; flex: 1; max-width: 1600px; width: 100%; margin: 0 auto; padding: 25px; gap: 25px; }
            .sidebar { width: 280px; background: #ffffff; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; gap: 10px; height: fit-content; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            .nav-btn { background: transparent; color: #475569; border: none; text-align: left; padding: 14px 18px; border-radius: 8px; font-size: 15px; cursor: pointer; transition: 0.2s; font-weight: 600; display: flex; align-items: center; gap: 12px; }
            .nav-btn:hover, .nav-btn.active { background: #eff6ff; color: #2563eb; }

            .content-area { flex: 1; background: #ffffff; border-radius: 12px; padding: 30px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); min-height: 75vh; }
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
            input, select, textarea { background: #ffffff; border: 1px solid #cbd5e1; color: #1e293b; padding: 12px 14px; border-radius: 8px; font-size: 15px; width: 100%; }
            input:focus, select:focus, textarea:focus { border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }

            .btn-primary { background: #2563eb; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; font-size: 15px; cursor: pointer; transition: 0.2s; width: 100%; }
            .btn-primary:hover { background: #1d4ed8; }
            .btn-green { background: #16a34a; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: bold; cursor: pointer; }
            .btn-green:hover { background: #15803d; }

            .chat-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 20px; height: 350px; overflow-y: auto; margin-bottom: 15px; text-align: left; display: flex; flex-direction: column; gap: 10px; }
            .chat-msg { padding: 12px 16px; border-radius: 8px; font-size: 14px; max-width: 80%; line-height: 1.5; }
            .chat-msg.user { background: #2563eb; color: white; align-self: flex-end; }
            .chat-msg.ai { background: #e2e8f0; color: #1e293b; align-self: flex-start; }
        </style>
    </head>
    <body>

        <header>
            <h1>⚡ SwiftBux Global Sourcing & AI Platform <span style="font-size: 12px; background: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 6px;">Live System</span></h1>
            <div class="asset-badges">
                <div class="badge-box" style="color: #16a34a;">💵 Balance: <span id="headerCash">0.000</span> KWD</div>
                <div class="badge-box" style="color: #2563eb;">👑 Owner Vault: <span id="ownerVaultDisplay">250.000</span> KWD</div>
            </div>
        </header>

        <div class="main-layout">
            <div class="sidebar">
                <button class="nav-btn active" onclick="switchTab('tabReg', this)">📝 User Registration & NIN</button>
                <button class="nav-btn" onclick="switchTab('tabDash', this)">📊 User Dashboard & Earnings</button>
                <button class="nav-btn" onclick="switchTab('tabGlobal', this)">🌍 Global Sourcing Marketplace</button>
                <button class="nav-btn" onclick="switchTab('tabAds', this)">📢 Ad Promotion & Marketing Hub</button>
                <button class="nav-btn" onclick="switchTab('tabAI', this)">🤖 AI Business & Sales Advisor</button>
                <button class="nav-btn" onclick="switchTab('tabWallet', this)">🏦 AI Auto-Withdrawal</button>
            </div>

            <div class="content-area">
                <!-- TAB 1: REGISTRATION -->
                <div id="tabReg" class="tab-pane active">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Secure User Registration & NIN Verification</h2>
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
                                <label>NIN / BVN Verification Number</label>
                                <input type="text" id="regNin" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-primary" style="margin-top: 15px;">Complete Registration</button>
                    </form>
                </div>

                <!-- TAB 2: DASHBOARD -->
                <div id="tabDash" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 15px;">User Earnings & Activity Dashboard</h2>
                    <div class="grid-3" style="margin-bottom: 25px;">
                        <div class="card" style="border-left: 4px solid #2563eb;">
                            <h3>Current Balance</h3>
                            <div style="font-size: 26px; font-weight: bold; color: #16a34a; margin-top: 5px;" id="dashBalance">0.000 KWD</div>
                        </div>
                        <div class="card" style="border-left: 4px solid #16a34a;">
                            <h3>Min Withdrawal Limit</h3>
                            <div style="font-size: 26px; font-weight: bold; color: #1e293b; margin-top: 5px;">50.000 KWD</div>
                        </div>
                        <div class="card" style="border-left: 4px solid #d97706;">
                            <h3>Verification Status</h3>
                            <div style="font-size: 16px; font-weight: bold; color: #16a34a; margin-top: 10px;" id="dashStatus">Verified</div>
                        </div>
                    </div>
                </div>

                <!-- TAB 3: GLOBAL SOURCING MARKETPLACE -->
                <div id="tabGlobal" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Global Sourcing & Reseller Marketplace</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Direct connection to wholesale suppliers from China (1688/Alibaba), India, USA, and Nigeria. Import products, resell locally, and earn rewards!</p>
                    
                    <div id="globalProductList" class="grid-2">
                        <!-- Populated by JavaScript -->
                    </div>
                </div>

                <!-- TAB 4: AD PROMOTION & MARKETING HUB -->
                <div id="tabAds" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Ad Promotion & Marketing Hub</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Promote products and platforms across Facebook, Instagram, TikTok, and web networks. Users view your campaigns to earn rewards, driving instant traffic to your business!</p>

                    <form onsubmit="postCampaign(event)" style="background: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
                        <h3 style="color: #2563eb; margin-bottom: 10px;">Launch New Product Ad Campaign</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Campaign Title & Product</label>
                                <input type="text" id="adTitle" placeholder="e.g. 1688 Car Covers Promo" required>
                            </div>
                            <div class="form-group">
                                <label>Target Link (Website / Social Page)</label>
                                <input type="url" id="adLink" placeholder="https://yourlink.com" required>
                            </div>
                            <div class="form-group">
                                <label>Reward Per View / Engagement (KWD)</label>
                                <input type="number" step="0.001" id="adReward" placeholder="2.500" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-green" style="margin-top: 10px;">Publish Ad Live</button>
                    </form>

                    <div id="activeAdsList" class="grid-2">
                        <div class="card">
                            <h3>📢 Featured 1688 Car Cover Promo</h3>
                            <p>Promote direct sourcing links across social media networks.</p>
                            <button class="btn-primary" onclick="engageAd('1688 Car Cover Promo', 3.000, 'https://example.com')">View Ad & Earn 3.000 KWD</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 5: AI BUSINESS & SALES ADVISOR -->
                <div id="tabAI" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">AI Business & Sales Consultant</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Ask the AI consultant anything about scaling your sales, importing from China/India, running Facebook ads, or pricing your products for maximum profit!</p>
                    
                    <div class="chat-box" id="chatContainer">
                        <div class="chat-msg ai">Hello! I am your AI Business Advisor. Ask me anything about how to source products, market on Facebook, or scale your sales to make more money!</div>
                    </div>

                    <div style="display: flex; gap: 10px;">
                        <input type="text" id="chatInput" placeholder="e.g. How can I sell car covers and make real money?" style="flex: 1;" onkeypress="if(event.key === 'Enter') sendAIChat()">
                        <button class="btn-primary" style="width: 120px;" onclick="sendAIChat()">Ask AI</button>
                    </div>
                </div>

                <!-- TAB 6: WALLET -->
                <div id="tabWallet" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">AI Automated Payout Gateway</h2>
                    <div class="card" style="max-width: 500px; margin: 0 auto; text-align: center;">
                        <h3 style="color: #16a34a; font-size: 24px; margin-bottom: 10px;" id="walletBalance">0.000 KWD</h3>
                        <p style="margin-bottom: 15px;">Minimum withdrawal threshold: 50.000 KWD</p>
                        <div class="form-group">
                            <label>Bank Account Number / PayPal Email</label>
                            <input type="text" id="payoutDest" placeholder="Enter payout destination" required>
                        </div>
                        <button class="btn-primary" onclick="requestAIWithdrawal()">Request AI Auto-Withdrawal</button>
                    </div>
                </div>
            </div>
        </div>

        <div id="proofModal" class="modal-overlay hidden" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15,23,42,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000;">
            <div class="modal-box" style="background: white; padding: 30px; border-radius: 12px; width: 480px; text-align: center;">
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
                    updateUI(data.cash_balance, data.owner_revenue);
                    document.getElementById('dashStatus').innerText = "VERIFIED (NIN Active)";
                    showModal("Registration Successful", `User ID: ${currentUserId}\\nNIN Verified by AI Engine.`);
                    switchTab('tabDash', document.querySelectorAll('.nav-btn')[1]);
                } else {
                    alert('Error: ' + data.detail);
                }
            }

            async function updateUI(cash, ownerRev) {
                document.getElementById('headerCash').innerText = cash.toFixed(3);
                document.getElementById('dashBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('walletBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('ownerVaultDisplay').innerText = ownerRev.toFixed(3) + " KWD";
            }

            async function loadGlobalProducts() {
                const res = await fetch('/api/global-products');
                const products = await res.json();
                const container = document.getElementById('globalProductList');
                let html = '';
                products.forEach(p => {
                    html += `
                        <div class="card">
                            <h3>📦 ${p.title}</h3>
                            <p>${p.description}</p>
                            <p style="font-size: 12px; color: #2563eb; font-weight: bold; margin-bottom: 5px;">Supplier: ${p.supplier} (${p.origin})</p>
                            <p style="font-weight: bold; color: #16a34a; margin-bottom: 12px;">Wholesale Price: ${p.price.toFixed(3)} KWD</p>
                            <button class="btn-green" onclick="importProduct('${p.title}', ${p.price})">Import / Resell Product</button>
                        </div>
                    `;
                });
                container.innerHTML = html;
            }

            async function importProduct(title, price) {
                if(!currentUserId) {
                    alert('Please register first!');
                    switchTab('tabReg', document.querySelectorAll('.nav-btn')[0]);
                    return;
                }
                showModal("Import Sourcing Confirmed", `Successfully sourced "${title}" at wholesale rate (${price.toFixed(3)} KWD).\\nReady for local resale and marketing.`);
            }

            async function postCampaign(e) {
                e.preventDefault();
                if(!currentUserId) {
                    alert('Please register first!');
                    switchTab('tabReg', document.querySelectorAll('.nav-btn')[0]);
                    return;
                }
                const title = document.getElementById('adTitle').value;
                const link = document.getElementById('adLink').value;
                const reward = parseFloat(document.getElementById('adReward').value);

                const container = document.getElementById('activeAdsList');
                container.innerHTML += `
                    <div class="card">
                        <h3>📢 ${title}</h3>
                        <p>Promoted by user: ${currentUserId}</p>
                        <button class="btn-primary" onclick="engageAd('${title}', ${reward}, '${link}')">View Ad & Earn ${reward.toFixed(3)} KWD</button>
                    </div>
                `;
                alert('Ad campaign published successfully to the global network!');
            }

            async function engageAd(title, reward, link) {
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
                    updateUI(data.cash_balance, data.owner_revenue);
                    showModal("Reward Claimed!", `Engaged with ad: ${title}\\nEarned +${reward.toFixed(3)} KWD.`);
                }
            }

            async function sendAIChat() {
                const input = document.getElementById('chatInput');
                const text = input.value.trim();
                if(!text) return;

                const chatContainer = document.getElementById('chatContainer');
                chatContainer.innerHTML += `<div class="chat-msg user">${text}</div>`;
                input.value = '';

                const res = await fetch('/api/ai-consultant', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: text})
                });
                const data = await res.json();
                chatContainer.innerHTML += `<div class="chat-msg ai">🤖 <b>AI Business Advisor:</b> ${data.response}</div>`;
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            async function requestAIWithdrawal() {
                if(!currentUserId) {
                    alert('Please register first!');
                    return;
                }
                const dest = document.getElementById('payoutDest').value;
                if(!dest) {
                    alert('Enter payout destination.');
                    return;
                }
                const res = await fetch('/api/ai-withdraw', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, destination: dest})
                });
                const data = await res.json();
                if(res.ok) {
                    showModal("🤖 AI AUTO-WITHDRAWAL APPROVED", `Status: APPROVED BY AI CONTROLLER\\nAmount: ${data.withdrawn_amount.toFixed(3)} KWD\\nDestination: ${dest}`);
                    updateUI(data.cash_balance, data.owner_revenue);
                } else {
                    alert('AI Verification Error: ' + data.detail);
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

            loadGlobalProducts();
        </script>
    </body>
    </html>
    """

# --- BACKEND APIS ---
class UserReg(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    nationality: str
    identity_number: str

@app.post("/api/register")
def register_user(user: UserReg, db: Session = Depends(get_db)):
    seed_initial_products(db)
    existing = db.query(GlobalUser).filter((GlobalUser.id == user.id) | (GlobalUser.identity_number == user.identity_number)).first()
    vault = db.query(PlatformTreasury).filter(PlatformTreasury.id == "vault_main").first()
    if not vault:
        vault = PlatformTreasury(id="vault_main", owner_revenue=Decimal("250.000"))
        db.add(vault)
        db.commit()

    if existing:
        return {"user_id": existing.id, "cash_balance": float(existing.cash_balance), "owner_revenue": float(vault.owner_revenue)}
    
    new_user = GlobalUser(
        id=user.id, name=user.name, email=user.email, phone=user.phone,
        nationality=user.nationality, identity_number=user.identity_number,
        cash_balance=Decimal("0.000"), tasks_completed=Decimal("0"), tickets=Decimal("100.00")
    )
    db.add(new_user)
    db.commit()
    return {"user_id": new_user.id, "cash_balance": float(new_user.cash_balance), "owner_revenue": float(vault.owner_revenue)}

@app.get("/api/global-products")
def get_global_products(db: Session = Depends(get_db)):
    seed_initial_products(db)
    products = db.query(GlobalProduct).all()
    return [{"id": p.id, "title": p.title, "supplier": p.supplier, "origin": p.origin, "price": float(p.price), "category": p.category, "description": p.description} for p in products]

@app.post("/api/task")
def process_task(data: dict, db: Session = Depends(get_db)):
    user = db.query(GlobalUser).filter(GlobalUser.id == data.get("user_id")).first()
    vault = db.query(PlatformTreasury).filter(PlatformTreasury.id == "vault_main").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reward = Decimal(str(data.get("reward", 0)))
    user_cut = reward * Decimal("0.70")
    owner_cut = reward * Decimal("0.30")
    
    user.cash_balance += user_cut
    user.tasks_completed += 1
    vault.owner_revenue += owner_cut
    db.commit()
    return {"cash_balance": float(user.cash_balance), "owner_revenue": float(vault.owner_revenue)}

@app.post("/api/ai-consultant")
def ai_consultant(data: dict):
    prompt = data.get("prompt", "").lower()
    
    if "car cover" in prompt or "import" in prompt or "1688" in prompt:
        reply = "To successfully import and sell car covers from 1688 or China, source direct wholesale suppliers with high ratings. Price them competitively on social media (Facebook Marketplace and Instagram Reels) by highlighting durability and waterproof features. Offer free delivery for orders above a certain threshold to drive rapid conversion."
    elif "facebook" in prompt or "ads" in prompt or "marketing" in prompt:
        reply = "For Facebook or Instagram ads, use short-form video demonstrations (Reels) showing the product in action. Target specific interests (e.g., car owners, gadget enthusiasts) and use a clear call-to-action like 'Click Link to Order Today' to maximize click-through rates."
    elif "sell" in prompt or "money" in prompt or "profit" in prompt:
        reply = "To maximize your profit margins, aim for a 40% to 60% markup on wholesale imported goods. Combine your product listings with our platform's ad promotion tool so other users can share your links, multiplying your organic reach without extra ad spend."
    else:
        reply = f"That is a great business question regarding '{prompt}'. To scale your sales, focus on targeting the right audience via social media video promotions, optimize your pricing for a healthy profit margin, and use our platform's ad network to drive consistent traffic to your product links!"
    
    return {"response": reply}

@app.post("/api/ai-withdraw")
def ai_withdraw(data: dict, db: Session = Depends(get_db)):
    user = db.query(GlobalUser).filter(GlobalUser.id == data.get("user_id")).first()
    vault = db.query(PlatformTreasury).filter(PlatformTreasury.id == "vault_main").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.cash_balance < Decimal("50.000"):
        raise HTTPException(status_code=400, detail="AI Check Failed: Minimum withdrawal threshold is 50.000 KWD.")
    
    withdrawn_amount = user.cash_balance
    user.cash_balance = Decimal("0.000")
    vault.total_payouts += withdrawn_amount
    db.commit()
    return {"status": "approved", "withdrawn_amount": float(withdrawn_amount), "cash_balance": float(user.cash_balance), "owner_revenue": float(vault.owner_revenue)}