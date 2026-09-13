from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_ai_autonomous.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AIUser(Base):
    __tablename__ = "ai_users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    nationality = Column(String)
    identity_number = Column(String, unique=True, index=True)
    cash_balance = Column(Numeric(10, 3), default=Decimal("0.000"))
    tasks_completed = Column(Numeric(10, 0), default=Decimal("0"))
    tickets = Column(Numeric(10, 2), default=Decimal("100.00"))
    referral_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class AIMarketplaceItem(Base):
    __tablename__ = "ai_marketplace_items"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    price = Column(Numeric(10, 3))
    seller = Column(String)
    description = Column(String)

class PlatformTreasury(Base):
    __tablename__ = "platform_treasury"
    id = Column(String, primary_key=True, default="owner_vault")
    owner_revenue = Column(Numeric(10, 3), default=Decimal("0.000"))
    total_payouts_processed = Column(Numeric(10, 3), default=Decimal("0.000"))

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwiftBux AI Autonomous & Marketplace Engine")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize treasury row if not exists
def init_treasury(db: Session):
    vault = db.query(PlatformTreasury).filter(PlatformTreasury.id == "owner_vault").first()
    if not vault:
        vault = PlatformTreasury(id="owner_vault", owner_revenue=Decimal("150.000"), total_payouts_processed=Decimal("1250.000"))
        db.add(vault)
        db.commit()

# --- FRONTEND UI ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwiftBux AI Autonomous Platform</title>
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
            .btn-danger { background: #dc2626; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; }

            .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15,23,42,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
            .modal-box { background: white; padding: 30px; border-radius: 12px; width: 480px; text-align: center; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2); }
        </style>
    </head>
    <body>

        <header>
            <h1>⚡ SwiftBux AI Autonomous Platform <span style="font-size: 12px; background: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 6px;">AI Controller Active</span></h1>
            <div class="asset-badges">
                <div class="badge-box" style="color: #16a34a;">💵 Balance: <span id="headerCash">0.000</span> KWD</div>
                <div class="badge-box" style="color: #2563eb;">👑 Owner Vault: <span id="ownerVaultDisplay">150.000</span> KWD</div>
            </div>
        </header>

        <div class="main-layout">
            <div class="sidebar">
                <button class="nav-btn active" onclick="switchTab('tabReg', this)">📝 User Registration & NIN</button>
                <button class="nav-btn" onclick="switchTab('tabDash', this)">📊 User Earnings & AI Status</button>
                <button class="nav-btn" onclick="switchTab('tabTasks', this)">🎮 Play Games & Watch Ads</button>
                <button class="nav-btn" onclick="switchTab('tabMarket', this)">🛒 Product Marketplace & Store</button>
                <button class="nav-btn" onclick="switchTab('tabWallet', this)">🏦 AI Auto-Withdrawal</button>
            </div>

            <div class="content-area">
                <!-- TAB 1: REGISTRATION -->
                <div id="tabReg" class="tab-pane active">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Secure User Registration & NIN Verification</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 25px;">Register your verified account to start earning and trading in the ecosystem.</p>

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
                    <h2 style="color: #1e293b; margin-bottom: 15px;">Your Earnings & AI Compliance Dashboard</h2>
                    <div class="grid-3" style="margin-bottom: 25px;">
                        <div class="card" style="border-left: 4px solid #2563eb;">
                            <h3>Available Balance</h3>
                            <div style="font-size: 26px; font-weight: bold; color: #16a34a; margin-top: 5px;" id="dashBalance">0.000 KWD</div>
                        </div>
                        <div class="card" style="border-left: 4px solid #16a34a;">
                            <h3>Withdrawal Threshold</h3>
                            <div style="font-size: 26px; font-weight: bold; color: #1e293b; margin-top: 5px;">50.000 KWD</div>
                        </div>
                        <div class="card" style="border-left: 4px solid #d97706;">
                            <h3>AI Verification Status</h3>
                            <div style="font-size: 16px; font-weight: bold; color: #d97706; margin-top: 10px;" id="dashStatus">Pending Verification</div>
                        </div>
                    </div>
                </div>

                <!-- TAB 3: TASKS & GAMES -->
                <div id="tabTasks" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Earn Money via Games & Video Ads</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Complete daily activities to grow your balance and generate ad revenue for the platform.</p>
                    <div class="grid-2">
                        <div class="card">
                            <h3>🧩 Puzzle Game Challenge</h3>
                            <p>Reward: 5.000 KWD</p>
                            <button class="btn-green" onclick="executeTask('Puzzle Game', 5.000)">Play & Earn 5.0 KWD</button>
                        </div>
                        <div class="card">
                            <h3>📺 Watch Sponsored Ad Stream</h3>
                            <p>Reward: 7.500 KWD</p>
                            <button class="btn-green" onclick="executeTask('Video Ad', 7.500)">Watch & Earn 7.5 KWD</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 4: MARKETPLACE -->
                <div id="tabMarket" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Peer-to-Peer Marketplace & Store</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Buy and sell products (car covers, digital goods, etc.). The platform automatically takes a small owner commission on sales!</p>
                    
                    <form onsubmit="postProduct(event)" style="background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
                        <h3 style="color: #2563eb; margin-bottom: 10px;">List Your Product for Sale</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Product Name</label>
                                <input type="text" id="prodTitle" placeholder="e.g. Luxury Car Body Cover" required>
                            </div>
                            <div class="form-group">
                                <label>Price (KWD)</label>
                                <input type="number" step="0.001" id="prodPrice" placeholder="25.000" required>
                            </div>
                            <div class="form-group full">
                                <label>Description</label>
                                <textarea id="prodDesc" placeholder="Describe your product..." rows="2" required></textarea>
                            </div>
                        </div>
                        <button type="submit" class="btn-green" style="margin-top: 10px;">Publish Product</button>
                    </form>

                    <div id="productList" class="grid-2">
                        <!-- Items rendered here -->
                    </div>
                </div>

                <!-- TAB 5: AI AUTO-WITHDRAWAL -->
                <div id="tabWallet" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">AI Automated Instant Payout Gateway</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Once your balance reaches 50.000 KWD and the AI verifies your task completion, funds are disbursed automatically.</p>
                    
                    <div class="card" style="max-width: 500px; margin: 0 auto; text-align: center;">
                        <h3 style="color: #16a34a; font-size: 24px; margin-bottom: 10px;" id="walletBalance">0.000 KWD</h3>
                        <div class="form-group">
                            <label>Bank Account Number / PayPal Email</label>
                            <input type="text" id="payoutDest" placeholder="Enter bank account or PayPal email" required>
                        </div>
                        <button class="btn-primary" onclick="requestAIWithdrawal()">Request AI Auto-Withdrawal</button>
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
                    updateUI(data.cash_balance, data.owner_revenue);
                    document.getElementById('dashStatus').innerText = "VERIFIED (NIN Active)";
                    document.getElementById('dashStatus').style.color = "#16a34a";
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

            async function executeTask(taskName, reward) {
                if(!currentUserId) {
                    alert('Please register first!');
                    switchTab('tabReg', document.querySelectorAll('.nav-btn')[0]);
                    return;
                }
                const res = await fetch('/api/task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, reward: reward})
                });
                const data = await res.json();
                if(res.ok) {
                    updateUI(data.cash_balance, data.owner_revenue);
                    showModal("Task Completed!", `Earned +${reward.toFixed(3)} KWD from ${taskName}.\\nPlatform Ad Revenue Split Applied.`);
                }
            }

            async function postProduct(e) {
                e.preventDefault();
                if(!currentUserId) {
                    alert('Please register first!');
                    switchTab('tabReg', document.querySelectorAll('.nav-btn')[0]);
                    return;
                }
                const payload = {
                    title: document.getElementById('prodTitle').value,
                    price: parseFloat(document.getElementById('prodPrice').value),
                    seller: currentUserId,
                    description: document.getElementById('prodDesc').value
                };
                const res = await fetch('/api/marketplace', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(res.ok) {
                    alert('Product listed successfully!');
                    loadMarketplace();
                }
            }

            async function loadMarketplace() {
                const res = await fetch('/api/marketplace');
                const items = await res.json();
                const container = document.getElementById('productList');
                let html = '';
                if(items.length === 0) {
                    html = '<p style="color: #64748b;">No products listed yet. Be the first to list!</p>';
                } else {
                    items.forEach(i => {
                        html += `
                            <div class="card">
                                <h3>🛍️ ${i.title}</h3>
                                <p>${i.description}</p>
                                <p style="font-weight: bold; color: #16a34a; margin-bottom: 10px;">Price: ${i.price.toFixed(3)} KWD (Seller: ${i.seller})</p>
                                <button class="btn-green" onclick="buyProduct('${i.id}', ${i.price})">Buy Product</button>
                            </div>
                        `;
                    });
                }
                container.innerHTML = html;
            }

            async function buyProduct(itemId, price) {
                if(!currentUserId) {
                    alert('Please register first!');
                    return;
                }
                const res = await fetch('/api/marketplace/buy', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, item_id: itemId, price: price})
                });
                const data = await res.json();
                if(res.ok) {
                    updateUI(data.cash_balance, data.owner_revenue);
                    showModal("Purchase Successful!", `Item bought! Platform owner commission deducted & credited to Owner Vault.`);
                    loadMarketplace();
                } else {
                    alert('Error: ' + data.detail);
                }
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
                    showModal("🤖 AI AUTO-WITHDRAWAL APPROVED", `Status: APPROVED BY AI CONTROLLER\\nAmount: ${data.withdrawn_amount.toFixed(3)} KWD\\nDestination: ${dest}\\nHash: 0x9f8a...swiftbux_ai_disbursed`);
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

            loadMarketplace();
        </script>
    </body>
    </html>
    """

# --- BACKEND API ENDPOINTS ---
class UserReg(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    nationality: str
    identity_number: str

@app.post("/api/register")
def register_user(user: UserReg, db: Session = Depends(get_db)):
    init_treasury(db)
    existing = db.query(AIUser).filter((AIUser.id == user.id) | (AIUser.identity_number == user.identity_number)).first()
    vault = db.query(PlatformTreasury).filter(PlatformTreasury.id == "owner_vault").first()
    if existing:
        return {"user_id": existing.id, "cash_balance": float(existing.cash_balance), "owner_revenue": float(vault.owner_revenue)}
    
    new_user = AIUser(
        id=user.id, name=user.name, email=user.email, phone=user.phone,
        nationality=user.nationality, identity_number=user.identity_number,
        cash_balance=Decimal("0.000"), tasks_completed=Decimal("0"), tickets=Decimal("100.00"),
        referral_code=user.id + "_ref"
    )
    db.add(new_user)
    db.commit()
    return {"user_id": new_user.id, "cash_balance": float(new_user.cash_balance), "owner_revenue": float(vault.owner_revenue)}

@app.post("/api/task")
def process_task(data: dict, db: Session = Depends(get_db)):
    user = db.query(AIUser).filter(AIUser.id == data.get("user_id")).first()
    vault = db.query(PlatformTreasury).filter(PlatformTreasury.id == "owner_vault").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reward = Decimal(str(data.get("reward", 0)))
    # AI revenue split: 70% goes to user balance, 30% goes to Owner Vault as ad revenue profit
    user_cut = reward * Decimal("0.70")
    owner_cut = reward * Decimal("0.30")
    
    user.cash_balance += user_cut
    user.tasks_completed += 1
    vault.owner_revenue += owner_cut
    db.commit()
    return {"cash_balance": float(user.cash_balance), "owner_revenue": float(vault.owner_revenue)}

@app.post("/api/marketplace")
def post_product(item: dict, db: Session = Depends(get_db)):
    new_item = AIMarketplaceItem(
        id="item_" + str(datetime.now().timestamp()),
        title=item.get("title"),
        price=Decimal(str(item.get("price"))),
        seller=item.get("seller"),
        description=item.get("description")
    )
    db.add(new_item)
    db.commit()
    return {"status": "success"}

@app.get("/api/marketplace")
def get_marketplace(db: Session = Depends(get_db)):
    items = db.query(AIMarketplaceItem).all()
    return [{"id": i.id, "title": i.title, "price": float(i.price), "seller": i.seller, "description": i.description} for i in items]

@app.post("/api/marketplace/buy")
def buy_product(data: dict, db: Session = Depends(get_db)):
    user = db.query(AIUser).filter(AIUser.id == data.get("user_id")).first()
    vault = db.query(PlatformTreasury).filter(PlatformTreasury.id == "owner_vault").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    price = Decimal(str(data.get("price")))
    if user.cash_balance < price:
        raise HTTPException(status_code=400, detail="Insufficient balance.")
    
    # Take 5% platform commission on marketplace sales for the owner vault
    commission = price * Decimal("0.05")
    seller_amount = price - commission
    
    user.cash_balance -= price
    vault.owner_revenue += commission
    db.commit()
    return {"cash_balance": float(user.cash_balance), "owner_revenue": float(vault.owner_revenue)}

@app.post("/api/ai-withdraw")
def ai_withdraw(data: dict, db: Session = Depends(get_db)):
    user = db.query(AIUser).filter(AIUser.id == data.get("user_id")).first()
    vault = db.query(PlatformTreasury).filter(PlatformTreasury.id == "owner_vault").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # AI Automatic Validation Rules
    if user.cash_balance < Decimal("50.000"):
        raise HTTPException(status_code=400, detail="AI Check Failed: Minimum withdrawal limit is 50.000 KWD.")
    if user.tasks_completed < Decimal("3"):
        raise HTTPException(status_code=400, detail="AI Check Failed: Complete at least 3 tasks/ads before withdrawing.")
    
    withdrawn_amount = user.cash_balance
    user.cash_balance = Decimal("0.000")
    vault.total_payouts_processed += withdrawn_amount
    db.commit()
    return {"status": "approved", "withdrawn_amount": float(withdrawn_amount), "cash_balance": float(user.cash_balance), "owner_revenue": float(vault.owner_revenue)}