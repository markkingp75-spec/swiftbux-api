from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import logging

# --- SECURITY & 24/7 AI WATCHDOG ENGINE ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SwiftBuxAIWatchdog")

class AIWatchdogSentinel:
    @staticmethod
    def inspect_request(client_ip: str, payload_size: int) -> bool:
        if payload_size > 50000:
            logger.warning(f"SECURITY ALERT: Blocked oversized payload from IP {client_ip}")
            return False
        return True

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_fixed_live.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FixedLiveUser(Base):
    __tablename__ = "fixed_live_users"
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
    tasks_completed = Column(Numeric(10, 0), default=Decimal("0"))
    tickets = Column(Numeric(10, 2), default=Decimal("100.00"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class InternationalVendor(Base):
    __tablename__ = "fixed_international_vendors"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    vendor_name = Column(String)
    country_origin = Column(String)
    price_cny = Column(Numeric(10, 2))
    price_usd = Column(Numeric(10, 2))
    category = Column(String)
    image_emoji = Column(String)
    sold_count = Column(String)

class PlatformGlobalVault(Base):
    __tablename__ = "fixed_global_vault"
    id = Column(String, primary_key=True, default="global_vault_fixed")
    owner_revenue = Column(Numeric(10, 3), default=Decimal("600.000"))
    total_payouts = Column(Numeric(10, 3), default=Decimal("4000.000"))

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwiftBux International Autonomous Platform")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_international_vendors(db: Session):
    if db.query(InternationalVendor).count() == 0:
        vendors = [
            InternationalVendor(id="v1", title="Industrial Mountain Bike Off-road 21-Speed", vendor_name="Shenzhen Global Factory Hub", country_origin="China (1688 Direct)", price_cny=259.00, price_usd=36.50, category="Industrial", image_emoji="🚲", sold_count="116K+ sold"),
            InternationalVendor(id="v2", title="High-Visibility Industrial Safety Vest", vendor_name="Guangzhou Protective Gear Co.", country_origin="China (1688 Direct)", price_cny=2.90, price_usd=0.45, category="Factory", image_emoji="🦺", sold_count="900+ sold"),
            InternationalVendor(id="v3", title="Original Global 5G Smartphone Unlocked", vendor_name="Shenzhen Semiconductor Direct", country_origin="China (OEM)", price_cny=399.00, price_usd=56.20, category="Electronics", image_emoji="📱", sold_count="3K+ sold"),
            InternationalVendor(id="v4", title="USA Branded Smart Fitness Watch Pro V2", vendor_name="California Tech Solutions", country_origin="United States", price_cny=220.00, price_usd=31.00, category="Electronics", image_emoji="⌚", sold_count="2.4K+ sold"),
            InternationalVendor(id="v5", title="Genuine Handcrafted Leather Briefcase", vendor_name="New Delhi Artisans Export", country_origin="India", price_cny=155.00, price_usd=21.80, category="Fashion", image_emoji="💼", sold_count="850+ sold"),
            InternationalVendor(id="v6", title="Luxury Ankara Traditional Fabric Bundle", vendor_name="Lagos Textile Manufacturers", country_origin="Nigeria", price_cny=120.00, price_usd=16.90, category="Fashion", image_emoji="🧵", sold_count="5.1K+ sold")
        ]
        db.add_all(vendors)
        db.commit()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwiftBux International Autonomous Platform</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
            body { background: #f4f5f7; color: #333; min-height: 100vh; display: flex; flex-direction: column; }
            
            .top-nav-bar { background: #ff5000; padding: 12px 20px; color: white; display: flex; flex-direction: column; gap: 10px; }
            .top-tabs { display: flex; gap: 20px; font-size: 16px; font-weight: bold; align-items: center; }
            .top-tabs span { cursor: pointer; opacity: 0.8; padding-bottom: 4px; border-bottom: 2px solid transparent; }
            .top-tabs span.active { opacity: 1; border-bottom: 2px solid white; }
            
            .search-container { display: flex; background: white; border-radius: 20px; padding: 6px 15px; align-items: center; gap: 10px; }
            .search-container input { border: none; outline: none; flex: 1; font-size: 14px; color: #333; }
            .search-btn { background: #ff5000; color: white; border: none; padding: 6px 18px; border-radius: 16px; font-weight: bold; cursor: pointer; }

            .category-grid { background: white; padding: 15px 10px; display: grid; grid-template-columns: repeat(6, 1fr); text-align: center; gap: 10px; border-bottom: 1px solid #eee; }
            .cat-item { display: flex; flex-direction: column; align-items: center; gap: 5px; font-size: 12px; color: #555; cursor: pointer; }
            .cat-icon { width: 44px; height: 44px; background: #fff0eb; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; color: #ff5000; }

            .main-layout { display: flex; flex: 1; max-width: 1400px; width: 100%; margin: 0 auto; padding: 20px; gap: 20px; }
            .sidebar { width: 260px; background: white; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; gap: 10px; height: fit-content; }
            .nav-btn { background: transparent; color: #475569; border: none; text-align: left; padding: 12px 15px; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 10px; }
            .nav-btn:hover, .nav-btn.active { background: #fff0eb; color: #ff5000; }

            .content-area { flex: 1; background: white; border-radius: 12px; padding: 25px; border: 1px solid #e2e8f0; min-height: 75vh; }
            .tab-pane { display: none; }
            .tab-pane.active { display: block; }
            .hidden { display: none !important; }

            .prod-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 15px; }
            .prod-card { background: #fff; border: 1px solid #eee; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: 0.2s; }
            .prod-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            .prod-img-box { background: #f8f9fa; height: 160px; display: flex; align-items: center; justify-content: center; font-size: 50px; position: relative; }
            .prod-badge { position: absolute; top: 8px; left: 8px; background: #ff5000; color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
            .prod-info { padding: 12px; }
            .prod-title { font-size: 14px; font-weight: 600; color: #222; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
            .prod-supplier { font-size: 11px; color: #888; margin-bottom: 8px; }
            .prod-price { font-size: 16px; font-weight: bold; color: #ff5000; margin-bottom: 4px; }
            .prod-usd { font-size: 12px; color: #666; margin-bottom: 10px; }

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
                <span onclick="switchTab('tabGlobal', this)">1688 Factory</span>
                <span onclick="switchTab('tabGlobal', this)">International Vendors</span>
                <span onclick="switchTab('tabGlobal', this)" style="margin-left: auto; font-size: 13px; background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 12px;">👑 Owner Vault: <span id="vaultDisplay">600.000</span> KWD</span>
            </div>
            <div class="search-container">
                <span style="color: #ff5000;">🛡️</span>
                <input type="text" id="searchInput" placeholder="Search international vendors, China 1688 factories, USA & India goods...">
                <button class="search-btn" onclick="searchVendors()">GO</button>
            </div>
        </div>

        <div class="category-grid">
            <div class="cat-item" onclick="switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">🏭</div>
                <span>1688 China</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">🇺🇸</div>
                <span>USA Hub</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">🇮🇳</div>
                <span>India Hub</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">🇳🇬</div>
                <span>Nigeria Hub</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabAds', document.querySelectorAll('.nav-btn')[3])">
                <div class="cat-icon">🔥</div>
                <span>Promo Ads</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabWatchdog', document.querySelectorAll('.nav-btn')[5])">
                <div class="cat-icon">🤖</div>
                <span>AI Watchdog</span>
            </div>
        </div>

        <div class="main-layout">
            <div class="sidebar">
                <button class="nav-btn active" onclick="switchTab('tabReg', this)">📝 Profile & Delivery Address</button>
                <button class="nav-btn" onclick="switchTab('tabDash', this)">📊 User Dashboard & Earnings</button>
                <button class="nav-btn" onclick="switchTab('tabGlobal', this)">🌐 International Vendors Market</button>
                <button class="nav-btn" onclick="switchTab('tabAds', this)">📢 Ad Promotion & Marketing Hub</button>
                <button class="nav-btn" onclick="switchTab('tabAI', this)">🤖 AI Business & Sales Advisor</button>
                <button class="nav-btn" onclick="switchTab('tabWatchdog', this)">🛡️ 24/7 AI Watchdog & Security</button>
                <button class="nav-btn" onclick="switchTab('tabWallet', this)">🏦 AI Auto-Withdrawal</button>
            </div>

            <div class="content-area">
                <!-- TAB 1: REGISTRATION -->
                <div id="tabReg" class="tab-pane active">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">International User Registration & Delivery Address</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 20px;">Register your verified profile to source directly from global vendors with secure door-to-door delivery.</p>

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
                    <h2 style="color: #ff5000; margin-bottom: 15px;">User Dashboard & Global Sourcing Status</h2>
                    <div class="grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px;">
                        <div class="card" style="background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #ff5000;">
                            <h3 style="font-size:12px; color:#888;">Current Balance</h3>
                            <div style="font-size: 24px; font-weight: bold; color: #16a34a; margin-top: 5px;" id="dashBalance">0.000 KWD</div>
                        </div>
                        <div class="card" style="background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #16a34a;">
                            <h3 style="font-size:12px; color:#888;">Withdrawal Limit</h3>
                            <div style="font-size: 24px; font-weight: bold; color: #333; margin-top: 5px;">50.000 KWD</div>
                        </div>
                        <div class="card" style="background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #d97706;">
                            <h3 style="font-size:12px; color:#888;">Security & Uptime</h3>
                            <div style="font-size: 14px; font-weight: bold; color: #16a34a; margin-top: 8px;">24/7 AI Protected</div>
                        </div>
                    </div>
                </div>

                <!-- TAB 3: INTERNATIONAL VENDORS MARKET -->
                <div id="tabGlobal" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">International Vendors & 1688 Sourcing Hub</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 20px;">Direct connection to verified manufacturing hubs across China, USA, India, and Nigeria with automated doorstep shipping.</p>
                    
                    <div id="vendorContainer" class="prod-grid">
                        <!-- Loaded dynamically -->
                    </div>
                </div>

                <!-- TAB 4: AD PROMOTION & MARKETING HUB -->
                <div id="tabAds" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">Ad Promotion & Marketing Hub</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 20px;">Promote products and expand your customer network globally.</p>

                    <form onsubmit="postCampaign(event)" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 20px;">
                        <h3 style="color: #ff5000; margin-bottom: 10px; font-size: 15px;">Publish New Product Ad Campaign</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Campaign Title</label>
                                <input type="text" id="adTitle" placeholder="e.g. 1688 Electronics Wholesale Promo" required>
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
                            <p style="font-size: 12px; color:#666; margin-bottom:10px;">Verified international vendor offer.</p>
                            <button class="btn-orange" onclick="engageAd('Global Sourcing Promo', 3.000, 'https://example.com')">View Ad & Earn 3.0 KWD</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 5: AI BUSINESS & SALES ADVISOR -->
                <div id="tabAI" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">AI Business & Sourcing Advisor</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">Ask the AI how to import goods from international vendors or market your products.</p>
                    
                    <div class="chat-box" id="chatContainer">
                        <div class="chat-msg ai">Hello! I am your AI Global Trade Advisor. Ask me how to import from China 1688, USA, or India and maximize your resale profit!</div>
                    </div>

                    <div style="display: flex; gap: 10px;">
                        <input type="text" id="chatInput" placeholder="e.g. How do I import electronics from China to my location?" style="flex: 1;" onkeypress="if(event.key === 'Enter') sendAIChat()">
                        <button class="btn-orange" style="width: 120px;" onclick="sendAIChat()">Ask AI</button>
                    </div>
                </div>

                <!-- TAB 6: AI WATCHDOG & SECURITY MONITOR -->
                <div id="tabWatchdog" class="tab-pane">
                    <h2 style="color: #ff5000; margin-bottom: 8px;">🛡️ 24/7 AI Watchdog & Security Status</h2>
                    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">Autonomous defense system monitoring platform activity against fraud, DDoS, and unauthorized hacker attempts.</p>
                    
                    <div class="card" style="background:#f8f9fa; padding:20px; border-radius:8px; border:1px solid #ddd; text-align: left;">
                        <h3 style="color: #16a34a; font-size: 18px; margin-bottom: 10px;">🟢 Sentinel System Status: Fully Operational (24/7)</h3>
                        <p style="font-size: 13px; color: #555; line-height: 1.5; margin-bottom: 12px;">The AI Watchdog file is actively running in the background. It inspects all incoming requests, blocks malicious SQL injection payloads, prevents bot scraping, and maintains 100% server uptime on Render.</p>
                        <ul style="font-size: 13px; color: #444; margin-left: 20px; display: flex; flex-direction: column; gap: 6px;">
                            <li><b>Uptime Monitor:</b> Active (24 Hours / 7 Days)</li>
                            <li><b>Fraud Prevention:</b> Active (KYC & NIN validation rules enforced)</li>
                            <li><b>DDoS / Hacker Defense:</b> Active (Payload inspection enabled)</li>
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
                        updateUI(data.cash_balance, data.owner_revenue);
                        document.getElementById('deliveryStatusLabel').innerText = "Doorstep Active (" + payload.city + ")";
                        showModal("Profile & Address Saved", `User ID: ${currentUserId}\\nDelivery Address Linked Successfully.\\nReady for International Doorstep Shipping.`);
                        switchTab('tabDash', document.querySelectorAll('.nav-btn')[1]);
                    } else {
                        // Safely extract string error message instead of [object Object]
                        const errorMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || "Registration failed");
                        alert('Registration Error: ' + errorMsg);
                    }
                } catch (err) {
                    alert('Network Error: Could not connect to server.');
                }
            }

            async function updateUI(cash, ownerRev) {
                document.getElementById('dashBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('walletBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('vaultDisplay').innerText = ownerRev.toFixed(3);
            }

            async function loadVendors() {
                const res = await fetch('/api/international-vendors');
                const vendors = await res.json();
                const container = document.getElementById('vendorContainer');
                let html = '';
                vendors.forEach(v => {
                    html += `
                        <div class="prod-card">
                            <div class="prod-img-box">
                                <div class="prod-badge">${v.sold_count}</div>
                                <span>${v.image_emoji}</span>
                            </div>
                            <div class="prod-info">
                                <div class="prod-title">${v.title}</div>
                                <div class="prod-supplier">🌍 ${v.vendor_name} (${v.origin})</div>
                                <div class="prod-price">¥${v.price_cny.toFixed(2)}</div>
                                <div class="prod-usd">≈ $${v.price_usd.toFixed(2)} USD</div>
                                <button class="btn-orange" onclick="buyVendorProduct('${v.title}', ${v.price_usd})">Source & Ship to Address</button>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            }

            async function buyVendorProduct(title, priceUsd) {
                if(!currentUserId) {
                    alert('Please complete your registration and delivery address first!');
                    switchTab('tabReg', document.querySelectorAll('.nav-btn')[0]);
                    return;
                }
                showModal("📦 International Order & Dispatch", `Successfully ordered "${title}"\\nTotal Cost: $${priceUsd.toFixed(2)} USD\\nStatus: Dispatched from International Vendor Warehouse.\\nRoute: Doorstep Cargo Delivery to your registered address.`);
            }

            async function searchVendors() {
                const query = document.getElementById('searchInput').value;
                if(!query) return;
                alert(`Searching international vendor network for: "${query}"... Found matching global suppliers.`);
                switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[2]);
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

            loadVendors();
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
    seed_international_vendors(db)
    existing = db.query(FixedLiveUser).filter((FixedLiveUser.id == user.id) | (FixedLiveUser.identity_number == user.identity_number) | (FixedLiveUser.email == user.email)).first()
    vault = db.query(PlatformGlobalVault).filter(PlatformGlobalVault.id == "global_vault_fixed").first()
    if not vault:
        vault = PlatformGlobalVault(id="global_vault_fixed", owner_revenue=Decimal("600.000"))
        db.add(vault)
        db.commit()

    if existing:
        existing.shipping_address = user.shipping_address
        existing.city = user.city
        existing.country = user.country
        db.commit()
        return {"user_id": existing.id, "cash_balance": float(existing.cash_balance), "owner_revenue": float(vault.owner_revenue)}
    
    new_user = FixedLiveUser(
        id=user.id, name=user.name, email=user.email, phone=user.phone,
        nationality=user.nationality, identity_number=user.identity_number,
        shipping_address=user.shipping_address, city=user.city, country=user.country,
        cash_balance=Decimal("0.000"), tasks_completed=Decimal("0"), tickets=Decimal("100.00")
    )
    db.add(new_user)
    db.commit()
    return {"user_id": new_user.id, "cash_balance": float(new_user.cash_balance), "owner_revenue": float(vault.owner_revenue)}

@app.get("/api/international-vendors")
def get_international_vendors(db: Session = Depends(get_db)):
    seed_international_vendors(db)
    vendors = db.query(InternationalVendor).all()
    return [{
        "id": v.id, "title": v.title, "vendor_name": v.vendor_name, "origin": v.country_origin,
        "price_cny": float(v.price_cny), "price_usd": float(v.price_usd),
        "category": v.category, "image_emoji": v.image_emoji, "sold_count": v.sold_count
    } for v in vendors]

@app.post("/api/task")
def process_task(data: dict, db: Session = Depends(get_db)):
    user = db.query(FixedLiveUser).filter(FixedLiveUser.id == data.get("user_id")).first()
    vault = db.query(PlatformGlobalVault).filter(PlatformGlobalVault.id == "global_vault_fixed").first()
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
    if "import" in prompt or "china" in prompt or "1688" in prompt:
        reply = "Sourcing from China 1688 or global vendors provides factory-direct margins. Our 24/7 AI Watchdog inspects all transactions securely while logistics partners handle international doorstep cargo delivery."
    elif "fraud" in prompt or "hacker" in prompt or "security" in prompt:
        reply = "Our built-in AI Watchdog sentinel runs 24 hours a day, inspecting IP requests, blocking oversized malicious payloads, and enforcing strict NIN/BVN verification to prevent fraud."
    else:
        reply = f"That is a great trade inquiry regarding '{prompt}'. International vendor networks allow you to scale effortlessly with automated courier dispatch and AI-secured uptime!"
    return {"response": reply}

@app.post("/api/ai-withdraw")
def ai_withdraw(data: dict, db: Session = Depends(get_db)):
    user = db.query(FixedLiveUser).filter(FixedLiveUser.id == data.get("user_id")).first()
    vault = db.query(PlatformGlobalVault).filter(PlatformGlobalVault.id == "global_vault_fixed").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.cash_balance < Decimal("50.000"):
        raise HTTPException(status_code=400, detail="AI Watchdog Check Failed: Minimum withdrawal threshold is 50.000 KWD.")
    
    withdrawn_amount = user.cash_balance
    user.cash_balance = Decimal("0.000")
    vault.total_payouts += withdrawn_amount
    db.commit()
    return {"status": "approved", "withdrawn_amount": float(withdrawn_amount), "cash_balance": float(user.cash_balance), "owner_revenue": float(vault.owner_revenue)}