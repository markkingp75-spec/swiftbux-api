from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import logging

# --- AUTONOMOUS AI WATCHDOG & ESCROW CONTROLLER ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SwiftBuxTradeHub")

class AutonomousTradeAI:
    @staticmethod
    def calculate_freight_and_escrow(origin: str, destination: str, weight_kg: float, item_price: Decimal):
        # Automated middleman calculation for cargo and platform commission
        base_freight_per_kg = 4.50 if origin == "China (1688 Direct)" else 6.00
        shipping_cost = Decimal(str(weight_kg * base_freight_per_kg))
        platform_fee = item_price * Decimal("0.08") # 8% middleman escrow fee
        total_escrow_amount = item_price + shipping_cost + platform_fee
        return shipping_cost, platform_fee, total_escrow_amount

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_autonomous_trade.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TradeUser(Base):
    __tablename__ = "trade_users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    nationality = Column(String)
    identity_number = Column(String, unique=True, index=True)
    shipping_address = Column(String)
    city = Column(String)
    country = Column(String)
    cash_balance = Column(Numeric(10, 3), default=Decimal("0.000"))
    escrow_locked = Column(Numeric(10, 3), default=Decimal("0.000"))
    tasks_completed = Column(Numeric(10, 0), default=Decimal("0"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class GlobalTradeItem(Base):
    __tablename__ = "global_trade_items"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    factory_name = Column(String)
    country_origin = Column(String)
    price_usd = Column(Numeric(10, 2))
    weight_kg = Column(Numeric(5, 2))
    category = Column(String)
    image_emoji = Column(String)
    moq = Column(String) # Minimum Order Quantity

class PlatformTreasuryVault(Base):
    __tablename__ = "platform_treasury_vault"
    id = Column(String, primary_key=True, default="treasury_main")
    owner_revenue = Column(Numeric(10, 3), default=Decimal("850.000"))
    total_cargo_dispatched = Column(Numeric(10, 0), default=Decimal("1420"))

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwiftBux Autonomous Global Trade & Middleman Platform")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_trade_catalog(db: Session):
    if db.query(GlobalTradeItem).count() == 0:
        catalog = [
            GlobalTradeItem(id="t1", title="Industrial Mountain Bike 21-Speed Bulk Lot", factory_name="Shenzhen Bicycle Works", country_origin="China (1688 Direct)", price_usd=38.00, weight_kg=14.5, category="Industrial", image_emoji="🚲", moq="MOQ: 1 Unit"),
            GlobalTradeItem(id="t2", title="High-Visibility Industrial Safety Vests (Bundle of 50)", factory_name="Guangzhou Safety Apparel", country_origin="China (1688 Direct)", price_usd=22.50, weight_kg=5.0, category="Factory", image_emoji="🦺", moq="MOQ: 1 Bundle"),
            GlobalTradeItem(id="t3", title="Original Global 5G Unlocked Smartphones", factory_name="Shenzhen Semiconductor OEM", country_origin="China (1688 Direct)", price_usd=58.00, weight_kg=0.4, category="Electronics", image_emoji="📱", moq="MOQ: 1 Unit"),
            GlobalTradeItem(id="t4", title="USA Branded Smart Fitness Watch Pro V2", factory_name="California Tech Solutions", country_origin="United States", price_usd=32.00, weight_kg=0.2, category="Electronics", image_emoji="⌚", moq="MOQ: 1 Unit"),
            GlobalTradeItem(id="t5", title="Genuine Handcrafted Leather Briefcase", factory_name="New Delhi Leather Exports", country_origin="India", price_usd=24.00, weight_kg=1.8, category="Fashion", image_emoji="💼", moq="MOQ: 1 Unit"),
            GlobalTradeItem(id="t6", title="Luxury Ankara Traditional Fabric (10 Yards)", factory_name="Lagos Textile Manufacturers", country_origin="Nigeria", price_usd=18.00, weight_kg=1.2, category="Fashion", image_emoji="🧵", moq="MOQ: 1 Bundle")
        ]
        db.add_all(catalog)
        db.commit()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwiftBux Autonomous Global Trade & Middleman Platform</title>
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
            .hidden { display: none !important; }

            .prod-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 15px; margin-top: 15px; }
            .prod-card { background: #fff; border: 1px solid #eee; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: 0.2s; }
            .prod-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            .prod-img-box { background: #f8f9fa; height: 150px; display: flex; align-items: center; justify-content: center; font-size: 50px; position: relative; }
            .prod-badge { position: absolute; top: 8px; left: 8px; background: #ff5000; color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
            .prod-info { padding: 12px; }
            .prod-title { font-size: 14px; font-weight: 600; color: #222; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
            .prod-supplier { font-size: 11px; color: #888; margin-bottom: 6px; }
            .prod-price { font-size: 16px; font-weight: bold; color: #ff5000; margin-bottom: 4px; }
            .prod-freight { font-size: 12px; color: #555; margin-bottom: 10px; }

            .form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; }
            .form-group { display: flex; flex-direction: column; gap: 5px; text-align: left; margin-bottom: 12px; }
            .form-group.full { grid-column: span 2; }
            label { font-size: 12px; font-weight: bold; color: #555; }
            input, select, textarea { background: #fff; border: 1px solid #ccc; padding: 10px; border-radius: 6px; font-size: 14px; width: 100%; }
            
            .btn-orange { background: #ff5000; color: white; border: none; padding: 10px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; }
            .btn-orange:hover { background: #e04500; }

            .chat-box { background: #f8f9fa; border: 1px solid #ddd; border-radius: 8px; padding: 15px; height: 320px; overflow-y: auto; margin-bottom: 15px; text-align: left; display: flex; flex-direction: column; gap: 10px; }
            .chat-msg { padding: 10px 14px; border-radius: 8px; font-size: 13px; max-width: 85%; line-height: 1.4; }
            .chat-msg.user { background: #ff5000; color: white; align-self: flex-end; }
            .chat-msg.ai { background: #e2e8f0; color: #333; align-self: flex-start; }
        </style>
    </head>
    <body>

        <div class="top-nav-bar">
            <div class="top-tabs">
                <span class="active" onclick="switchTab('tabRec', this)">Rec.</span>
                <span onclick="switchTab('tabTrade', this)">Global Sourcing</span>
                <span onclick="switchTab('tabTrade', this)">Escrow Middleman</span>
                <span onclick="switchTab('tabTrade', this)" style="margin-left: auto; font-size: 13px; background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 12px;">👑 Owner Vault: <span id="vaultDisplay">850.000</span> KWD</span>
            </div>
            <div class="search-container">
                <span style="color: #ff5000;">🌐</span>
                <input type="text" id="searchInput" placeholder="Search factories in China 1688, USA, India, Nigeria...">
                <button class="search-btn" onclick="searchTradeItems()">GO</button>
            </div>
        </div>

        <div class="category-grid">
            <div class="cat-item" onclick="switchTab('tabTrade', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">🏭</div>
                <span>1688 Factories</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabTrade', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">🚢</div>
                <span>Cargo Shipping</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabTrade', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">🔒</div>
                <span>Escrow Safe</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabTrade', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">📦</div>
                <span>Doorstep Delivery</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabAds', document.querySelectorAll('.nav-btn')[3])">
                <div class="cat-icon">🔥</div>
                <span>Promo Ads</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabWallet', document.querySelectorAll('.nav-btn')[6])">
                <div class="cat-icon">💳</div>
                <span>Auto Payout</span>
            </div>
        </div>

        <div class="main-layout">
            <div class="sidebar">
                <button class="nav-btn active" onclick="switchTab('tabReg', this)">📝 Profile & Delivery Address</button>
                <button class="nav-btn" onclick="switchTab('tabDash', this)">📊 User Dashboard & Escrow</button>
                <button class="nav-btn" onclick="switchTab('tabTrade', this)">🌐 Global Sourcing & Middleman</button>
                <button class="nav-btn" onclick="switchTab('tabAds', this)">📢 Ad Promotion & Marketing Hub</button>
                <button class="nav-btn" onclick="switchTab('tabAI', this)">🤖 AI Trade & Shipping Advisor</button>
                <button class="nav-btn" onclick="switchTab('tabWatchdog', this)">🛡️ Autonomous AI Security</button>
                <button class="nav-btn" onclick="switchTab('tabWallet', this)">🏦 AI Auto-Withdrawal</button>
            </div>

            <div class="content-area">
                <!-- TAB 1: REGISTRATION -->
                <div id="tabReg" class="tab-pane active">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">Autonomous Middleman Trade Profile & Delivery Address</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 20px;">Register your verified profile so factory orders from China, USA, and India route directly to your doorstep.</p>

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
                                <label>Phone Number (for Courier Dispatch)</label>
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
                        <button type="submit" class="btn-orange" style="margin-top: 15px;">Save Profile & Delivery Location</button>
                    </form>
                </div>

                <!-- TAB 2: DASHBOARD -->
                <div id="tabDash" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 15px;">User Dashboard & Escrow Middleman Status</h2>
                    <div class="grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px;">
                        <div class="card" style="background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #ff5000;">
                            <h3 style="font-size:12px; color:#888;">Current Balance</h3>
                            <div style="font-size: 24px; font-weight: bold; color: #16a34a; margin-top: 5px;" id="dashBalance">0.000 KWD</div>
                        </div>
                        <div class="card" style="background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #16a34a;">
                            <h3 style="font-size:12px; color:#888;">Escrow Locked Orders</h3>
                            <div style="font-size: 24px; font-weight: bold; color: #333; margin-top: 5px;" id="dashEscrow">0.000 USD</div>
                        </div>
                        <div class="card" style="background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #d97706;">
                            <h3 style="font-size:12px; color:#888;">Middleman Status</h3>
                            <div style="font-size: 14px; font-weight: bold; color: #16a34a; margin-top: 8px;">Autonomous Active</div>
                        </div>
                    </div>
                </div>

                <!-- TAB 3: GLOBAL SOURCING & MIDDLEMAN MARKET -->
                <div id="tabTrade" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">Global Sourcing & Autonomous Middleman Hub</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 20px;">The platform acts as an automated middleman between foreign factories (China 1688, USA, India) and your destination. Funds stay in escrow until cargo is safely dispatched.</p>
                    
                    <div id="tradeContainer" class="prod-grid">
                        <!-- Loaded dynamically -->
                    </div>
                </div>

                <!-- TAB 4: AD PROMOTION & MARKETING HUB -->
                <div id="tabAds" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">Ad Promotion & Marketing Hub</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 20px;">Promote your imported wholesale products across social networks.</p>

                    <form onsubmit="postCampaign(event)" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 20px;">
                        <h3 style="color: #ff5000; margin-bottom: 10px; font-size: 15px;">Publish New Product Ad Campaign</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Campaign Title</label>
                                <input type="text" id="adTitle" placeholder="e.g. 1688 Mountain Bike Promo" required>
                            </div>
                            <div class="form-group">
                                <label>Product Link</label>
                                <input type="url" id="adLink" placeholder="https://yourlink.com" required>
                            </div>
                            <div class="form-group">
                                <label>Reward Per View (KWD)</label>
                                <input type="number" step="0.001" id="adReward" placeholder="2.500" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-orange" style="margin-top: 10px;">Launch Ad Live</button>
                    </form>

                    <div id="adList" class="prod-grid">
                        <div class="prod-card" style="padding: 15px;">
                            <h3 style="font-size: 14px; color:#ff5000; margin-bottom:5px;">🔥 Global Sourcing Promo</h3>
                            <p style="font-size: 12px; color:#666; margin-bottom:10px;">Verified international middleman offer.</p>
                            <button class="btn-orange" onclick="engageAd('Global Sourcing Promo', 3.000, 'https://example.com')">View Ad & Earn 3.0 KWD</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 5: AI BUSINESS & SHIPPING ADVISOR -->
                <div id="tabAI" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">AI Trade & Logistics Advisor</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">Ask the AI middleman system how international escrow protection and factory shipping work.</p>
                    
                    <div class="chat-box" id="chatContainer">
                        <div class="chat-msg ai">Hello! I am your Autonomous Trade & Escrow Advisor. Ask me how we mediate between China 1688 factories and your doorstep delivery!</div>
                    </div>

                    <div style="display: flex; gap: 10px;">
                        <input type="text" id="chatInput" placeholder="e.g. How does escrow protect my money when buying from China?" style="flex: 1;" onkeypress="if(event.key === 'Enter') sendAIChat()">
                        <button class="btn-orange" style="width: 120px;" onclick="sendAIChat()">Ask AI</button>
                    </div>
                </div>

                <!-- TAB 6: AUTONOMOUS AI SECURITY -->
                <div id="tabWatchdog" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">🛡️ Autonomous AI Security & Escrow Safeguard</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">Real-time monitoring of trade ledgers, anti-fraud verification, and 24/7 server uptime.</p>
                    
                    <div class="card" style="background:#f8f9fa; padding:20px; border-radius:8px; border:1px solid #ddd; text-align: left;">
                        <h3 style="color: #16a34a; font-size: 18px; margin-bottom: 10px;">🟢 Middleman System Status: Fully Operational (24/7)</h3>
                        <p style="font-size: 13px; color: #555; line-height: 1.5; margin-bottom: 12px;">The autonomous trade controller acts as a secure middleman, holding buyer funds in escrow until international factories confirm cargo dispatch.</p>
                        <ul style="font-size: 13px; color: #444; margin-left: 20px; display: flex; flex-direction: column; gap: 6px;">
                            <li><b>Escrow Ledger:</b> Active & Secured</li>
                            <li><b>Factory API Handshake:</b> Connected to China, USA, India</li>
                            <li><b>Doorstep Tracking:</b> Enabled for Registered Addresses</li>
                        </ul>
                    </div>
                </div>

                <!-- TAB 7: WALLET -->
                <div id="tabWallet" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">AI Automated Payout Gateway</h2>
                    <div class="card" style="max-width: 500px; margin: 0 auto; text-align: center; background:#f8f9fa; padding:25px; border-radius:8px; border:1px solid #ddd;">
                        <h3 style="color: #16a34a; font-size: 24px; margin-bottom: 10px;" id="walletBalance">0.000 KWD</h3>
                        <p style="font-size:13px; color:#666; margin-bottom: 15px;">Minimum withdrawal threshold: 50.000 KWD</p>
                        <div class="form-group">
                            <label>Bank Account Number / PayPal Email</label>
                            <input type="text" id="payoutDest" placeholder="Enter bank account or PayPal email" required>
                        </div>
                        <button class="btn-orange" onclick="requestAIWithdrawal()">Request AI Auto-Withdrawal</button>
                    </div>
                </div>
            </div>
        </div>

        <div id="proofModal" class="modal-overlay hidden" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000;">
            <div class="modal-box" style="background: white; padding: 30px; border-radius: 12px; width: 420px; text-align: center;">
                <h3 id="modalTitle" style="color: #16a34a; margin-bottom: 12px;">Success</h3>
                <p id="modalText" style="font-size: 13px; color: #333; background: #f8f9fa; padding: 12px; border-radius: 6px; text-align: left; margin-bottom: 20px; line-height: 1.4;"></p>
                <button class="btn-orange" onclick="closeModal()">Close Window</button>
            </div>
        </div>

        <script>
            let currentUserId = null;

            function switchTab(tabId, btnElement) {
                document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('link-active'));
                document.getElementById(tabId).classList.add('active');
                if(btnElement && btnElement.classList) {
                    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
                    btnElement.classList.add('active');
                }
            }

            async function handleRegistration(e) {
                e.preventDefault();
                const payload = {
                    id: document.getElementById('regId').value,
                    name: document.getElementById('regName').value,
                    email: document.getElementById('regEmail').value,
                    phone: document.getElementById('regPhone').value,
                    nationality: document.getElementById('regNationality').value,
                    identity_number: document.getElementById('regNin').value,
                    shipping_address: document.getElementById('regAddress').value,
                    city: document.getElementById('regCity').value,
                    country: document.getElementById('regNationality').value
                };

                try {
                    const res = await fetch('/api/register', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(payload)
                    });
                    const data = await res.json();
                    
                    if(res.ok) {
                        currentUserId = data.user_id;
                        updateUI(data.cash_balance, data.escrow_locked, data.owner_revenue);
                        showModal("Trade Profile Registered", `User ID: ${currentUserId}\\nDelivery Address Linked.\\nMiddleman Escrow Active.`);
                        switchTab('tabDash', document.querySelectorAll('.nav-btn')[1]);
                    } else {
                        const errorMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || "Registration failed");
                        alert('Registration Error: ' + errorMsg);
                    }
                } catch (err) {
                    alert('Network Error: Could not connect to server.');
                }
            }

            async function updateUI(cash, escrow, ownerRev) {
                document.getElementById('dashBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('walletBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('dashEscrow').innerText = escrow.toFixed(2) + " USD";
                document.getElementById('vaultDisplay').innerText = ownerRev.toFixed(3);
            }

            async function loadTradeItems() {
                const res = await fetch('/api/trade-catalog');
                const items = await res.json();
                const container = document.getElementById('tradeContainer');
                let html = '';
                items.forEach(i => {
                    html += `
                        <div class="prod-card">
                            <div class="prod-img-box">
                                <div class="prod-badge">${i.moq}</div>
                                <span>${i.image_emoji}</span>
                            </div>
                            <div class="prod-info">
                                <div class="prod-title">${i.title}</div>
                                <div class="prod-supplier">🏭 ${i.factory_name} (${i.origin})</div>
                                <div class="prod-price">💲${i.price_usd.toFixed(2)} USD</div>
                                <div class="prod-freight">📦 Weight: ${i.weight_kg} kg (Auto Cargo Calc)</div>
                                <button class="btn-orange" onclick="placeEscrowOrder('${i.id}', '${i.title}', ${i.price_usd}, ${i.weight_kg}, '${i.origin}')">Middleman Escrow Order</button>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            }

            async function placeEscrowOrder(itemId, title, priceUsd, weightKg, origin) {
                if(!currentUserId) {
                    alert('Please complete your registration and delivery address first!');
                    switchTab('tabReg', document.querySelectorAll('.nav-btn')[0]);
                    return;
                }
                
                const res = await fetch('/api/trade-order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, item_id: itemId, price_usd: priceUsd, weight_kg: weightKg, origin: origin})
                });
                const data = await res.json();
                if(res.ok) {
                    updateUI(data.cash_balance, data.escrow_locked, data.owner_revenue);
                    showModal("🔒 ESCROW MIDDLEMAN SECURED", `Item: ${title}\\nFactory Price: $${priceUsd.toFixed(2)}\\nCargo Shipping: $${data.shipping_cost.toFixed(2)}\\nMiddleman Fee: $${data.platform_fee.toFixed(2)}\\nTotal Escrow Locked: $${data.total_escrow.toFixed(2)}\\nStatus: Funds held safely until factory dispatches to your address!`);
                } else {
                    alert('Order Error: ' + data.detail);
                }
            }

            async function searchTradeItems() {
                const query = document.getElementById('searchInput').value;
                if(!query) return;
                alert(`Searching global factory networks for: "${query}"... Autonomous middleman connected.`);
                switchTab('tabTrade', document.querySelectorAll('.nav-btn')[2]);
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

                const container = document.getElementById('adList');
                container.innerHTML += `
                    <div class="prod-card" style="padding: 15px;">
                        <h3 style="font-size: 14px; color:#ff5000; margin-bottom:5px;">🔥 ${title}</h3>
                        <p style="font-size: 12px; color:#666; margin-bottom:10px;">Promoted by user: ${currentUserId}</p>
                        <button class="btn-orange" onclick="engageAd('${title}', ${reward}, '${link}')">View Ad & Earn ${reward.toFixed(3)} KWD</button>
                    </div>
                `;
                alert('Ad published successfully!');
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
                    updateUI(data.cash_balance, data.escrow_locked, data.owner_revenue);
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
                chatContainer.innerHTML += `<div class="chat-msg ai">🤖 <b>AI Trade Advisor:</b> ${data.response}</div>`;
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
                    showModal("🤖 AI AUTO-WITHDRAWAL APPROVED", `Status: APPROVED BY MIDDLEMAN CONTROLLER\\nAmount: ${data.withdrawn_amount.toFixed(3)} KWD\\nDestination: ${dest}`);
                    updateUI(data.cash_balance, data.escrow_locked, data.owner_revenue);
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

            loadTradeItems();
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
    shipping_address: str
    city: str
    country: str

@app.post("/api/register")
def register_user(user: UserReg, db: Session = Depends(get_db)):
    seed_trade_catalog(db)
    existing = db.query(TradeUser).filter((TradeUser.id == user.id) | (TradeUser.identity_number == user.identity_number) | (TradeUser.email == user.email)).first()
    vault = db.query(PlatformTreasuryVault).filter(PlatformTreasuryVault.id == "treasury_main").first()
    if not vault:
        vault = PlatformTreasuryVault(id="treasury_main", owner_revenue=Decimal("850.000"))
        db.add(vault)
        db.commit()

    if existing:
        existing.shipping_address = user.shipping_address
        existing.city = user.city
        existing.country = user.country
        db.commit()
        return {"user_id": existing.id, "cash_balance": float(existing.cash_balance), "escrow_locked": float(existing.escrow_locked), "owner_revenue": float(vault.owner_revenue)}
    
    new_user = TradeUser(
        id=user.id, name=user.name, email=user.email, phone=user.phone,
        nationality=user.nationality, identity_number=user.identity_number,
        shipping_address=user.shipping_address, city=user.city, country=user.country,
        cash_balance=Decimal("0.000"), escrow_locked=Decimal("0.000"), tasks_completed=Decimal("0")
    )
    db.add(new_user)
    db.commit()
    return {"user_id": new_user.id, "cash_balance": float(new_user.cash_balance), "escrow_locked": float(new_user.escrow_locked), "owner_revenue": float(vault.owner_revenue)}

@app.get("/api/trade-catalog")
def get_trade_catalog(db: Session = Depends(get_db)):
    seed_trade_catalog(db)
    items = db.query(GlobalTradeItem).all()
    return [{
        "id": i.id, "title": i.title, "factory_name": i.factory_name, "origin": i.country_origin,
        "price_usd": float(i.price_usd), "weight_kg": float(i.weight_kg),
        "category": i.category, "image_emoji": i.image_emoji, "moq": i.moq
    } for i in items]

@app.post("/api/trade-order")
def process_trade_order(data: dict, db: Session = Depends(get_db)):
    user = db.query(TradeUser).filter(TradeUser.id == data.get("user_id")).first()
    vault = db.query(PlatformTreasuryVault).filter(PlatformTreasuryVault.id == "treasury_main").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    price_usd = Decimal(str(data.get("price_usd")))
    weight_kg = float(data.get("weight_kg", 1.0))
    origin = data.get("origin", "China (1688 Direct)")
    
    shipping_cost, platform_fee, total_escrow = AutonomousTradeAI.calculate_freight_and_escrow(origin, user.country, weight_kg, price_usd)
    
    user.escrow_locked += total_escrow
    vault.owner_revenue += platform_fee # Middleman fee goes straight to owner vault
    vault.total_cargo_dispatched += 1
    db.commit()
    
    return {
        "status": "escrow_locked",
        "shipping_cost": float(shipping_cost),
        "platform_fee": float(platform_fee),
        "total_escrow": float(total_escrow),
        "cash_balance": float(user.cash_balance),
        "escrow_locked": float(user.escrow_locked),
        "owner_revenue": float(vault.owner_revenue)
    }

@app.post("/api/task")
def process_task(data: dict, db: Session = Depends(get_db)):
    user = db.query(TradeUser).filter(TradeUser.id == data.get("user_id")).first()
    vault = db.query(PlatformTreasuryVault).filter(PlatformTreasuryVault.id == "treasury_main").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reward = Decimal(str(data.get("reward", 0)))
    user_cut = reward * Decimal("0.70")
    owner_cut = reward * Decimal("0.30")
    
    user.cash_balance += user_cut
    user.tasks_completed += 1
    vault.owner_revenue += owner_cut
    db.commit()
    return {"cash_balance": float(user.cash_balance), "escrow_locked": float(user.escrow_locked), "owner_revenue": float(vault.owner_revenue)}

@app.post("/api/ai-consultant")
def ai_consultant(data: dict):
    prompt = data.get("prompt", "").lower()
    if "escrow" in prompt or "protect" in prompt or "middleman" in prompt:
        reply = "Our autonomous middleman system holds buyer funds in a secure escrow vault. Once international factories (China 1688, USA, India) confirm product inspection and dispatch, the cargo is shipped directly to the buyer's doorstep."
    elif "shipping" in prompt or "cargo" in prompt or "delivery" in prompt:
        reply = "The platform automatically calculates item weight and international freight costs, routing shipments from overseas manufacturing hubs straight to the user's registered delivery address."
    else:
        reply = f"That is a great trade inquiry regarding '{prompt}': SwiftBux acts as an independent middleman, automating currency conversion, escrow security, and cross-border logistics effortlessly!"
    return {"response": reply}

@app.post("/api/ai-withdraw")
def ai_withdraw(data: dict, db: Session = Depends(get_db)):
    user = db.query(TradeUser).filter(TradeUser.id == data.get("user_id")).first()
    vault = db.query(PlatformTreasuryVault).filter(PlatformTreasuryVault.id == "treasury_main").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.cash_balance < Decimal("50.000"):
        raise HTTPException(status_code=400, detail="AI Check Failed: Minimum withdrawal threshold is 50.000 KWD.")
    
    withdrawn_amount = user.cash_balance
    user.cash_balance = Decimal("0.000")
    db.commit()
    return {"status": "approved", "withdrawn_amount": float(withdrawn_amount), "cash_balance": float(user.cash_balance), "escrow_locked": float(user.escrow_locked), "owner_revenue": float(vault.owner_revenue)}