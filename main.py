from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_global_hub.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GlobalHubUser(Base):
    __tablename__ = "global_hub_users"
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
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class GlobalProductItem(Base):
    __tablename__ = "global_product_items"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    factory_name = Column(String)
    country_origin = Column(String)
    price_usd = Column(Numeric(10, 2))
    weight_kg = Column(Numeric(5, 2))
    category = Column(String)
    image_emoji = Column(String)
    moq = Column(String)
    sold_count = Column(String)

class PlatformVault(Base):
    __tablename__ = "global_hub_vault"
    id = Column(String, primary_key=True, default="vault_hub")
    owner_revenue = Column(Numeric(10, 3), default=Decimal("950.000"))
    total_orders = Column(Numeric(10, 0), default=Decimal("1850"))

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwiftBux Global Factory Sourcing & Marketplace Hub")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_global_catalog(db: Session):
    if db.query(GlobalProductItem).count() == 0:
        catalog = [
            GlobalProductItem(id="g1", title="Industrial 5G Smartphone Global Edition", factory_name="Shenzhen Semiconductor OEM", country_origin="China", price_usd=65.00, weight_kg=0.4, category="Electronics", image_emoji="📱", moq="MOQ: 1 Unit", sold_count="12K+ sold"),
            GlobalProductItem(id="g2", title="All-Terrain Mountain Bike 21-Speed", factory_name="Hangzhou Industrial Assembly", country_origin="China", price_usd=45.00, weight_kg=14.0, category="Automotive", image_emoji="🚲", sold_count="5.4K+ sold"),
            GlobalProductItem(id="g3", title="USA Branded Smart Fitness Watch Pro V2", factory_name="California Tech Solutions", country_origin="United States", price_usd=32.00, weight_kg=0.2, category="Electronics", image_emoji="⌚", sold_count="8.1K+ sold"),
            GlobalProductItem(id="g4", title="Genuine Handcrafted Leather Briefcase", factory_name="New Delhi Export Artisans", country_origin="India", price_usd=28.00, weight_kg=1.5, category="Fashion", image_emoji="💼", sold_count="3.2K+ sold"),
            GlobalProductItem(id="g5", title="Luxury Ankara Traditional Fabric Bundle", factory_name="Lagos Textile Manufacturers", country_origin="Nigeria", price_usd=18.00, weight_kg=1.0, category="Fashion", image_emoji="🧵", sold_count="14K+ sold"),
            GlobalProductItem(id="g6", title="Heavy Duty Solar Power Generator 5kW", factory_name="Berlin Clean Energy Works", country_origin="Germany", price_usd=320.00, weight_kg=22.0, category="Industrial", image_emoji="⚡", sold_count="920+ sold")
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
        <title>SwiftBux Global Factory Sourcing & Marketplace Hub</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
            body { background: #f4f5f7; color: #333; min-height: 100vh; display: flex; flex-direction: column; }
            
            .top-nav-bar { background: #1e293b; padding: 14px 25px; color: white; display: flex; flex-direction: column; gap: 12px; width: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .top-tabs { display: flex; gap: 20px; font-size: 15px; font-weight: bold; align-items: center; flex-wrap: wrap; }
            .top-tabs span { cursor: pointer; opacity: 0.8; padding-bottom: 4px; border-bottom: 2px solid transparent; transition: 0.2s; }
            .top-tabs span:hover, .top-tabs span.active { opacity: 1; border-bottom: 2px solid #ff5000; color: #ff5000; }
            
            .search-container { display: flex; background: white; border-radius: 24px; padding: 6px 15px; align-items: center; gap: 10px; max-width: 700px; border: 2px solid #ff5000; }
            .search-container input { border: none; outline: none; flex: 1; font-size: 15px; color: #333; }
            .search-btn { background: #ff5000; color: white; border: none; padding: 8px 22px; border-radius: 20px; font-weight: bold; cursor: pointer; transition: 0.2s; }
            .search-btn:hover { background: #e04500; }

            .category-grid { background: white; padding: 15px 10px; display: grid; grid-template-columns: repeat(6, 1fr); text-align: center; gap: 10px; border-bottom: 1px solid #eee; width: 100%; }
            .cat-item { display: flex; flex-direction: column; align-items: center; gap: 6px; font-size: 12px; color: #555; cursor: pointer; transition: 0.2s; }
            .cat-item:hover { color: #ff5000; }
            .cat-icon { width: 46px; height: 46px; background: #fff0eb; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22px; color: #ff5000; }

            .main-layout { display: flex; flex-direction: row; flex: 1; max-width: 1450px; width: 100%; margin: 0 auto; padding: 20px; gap: 20px; align-items: flex-start; }
            .sidebar { width: 280px; flex-shrink: 0; background: white; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; gap: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            .nav-btn { background: transparent; color: #475569; border: none; text-align: left; padding: 12px 15px; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 10px; width: 100%; transition: 0.2s; }
            .nav-btn:hover, .nav-btn.active { background: #fff0eb; color: #ff5000; }

            .content-area { flex: 1; min-width: 0; background: white; border-radius: 12px; padding: 30px; border: 1px solid #e2e8f0; min-height: 75vh; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            .tab-pane { display: none; }
            .tab-pane.active { display: block; }

            .prod-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; margin-top: 20px; }
            .prod-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: 0.2s; }
            .prod-card:hover { box-shadow: 0 8px 20px rgba(0,0,0,0.08); transform: translateY(-2px); }
            .prod-img-box { background: #f8fafc; height: 160px; display: flex; align-items: center; justify-content: center; font-size: 55px; position: relative; }
            .prod-badge { position: absolute; top: 10px; left: 10px; background: #ff5000; color: white; font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
            .prod-info { padding: 15px; }
            .prod-title { font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
            .prod-supplier { font-size: 12px; color: #64748b; margin-bottom: 8px; }
            .prod-price { font-size: 18px; font-weight: bold; color: #ff5000; margin-bottom: 4px; }
            .prod-freight { font-size: 12px; color: #475569; margin-bottom: 15px; }

            .form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; }
            .form-group { display: flex; flex-direction: column; gap: 6px; text-align: left; margin-bottom: 12px; }
            .form-group.full { grid-column: span 2; }
            label { font-size: 13px; font-weight: bold; color: #475569; }
            input, select, textarea { background: #fff; border: 1px solid #cbd5e1; padding: 12px; border-radius: 8px; font-size: 14px; width: 100%; }
            input:focus, select:focus, textarea:focus { border-color: #ff5000; outline: none; box-shadow: 0 0 0 3px rgba(255,80,0,0.1); }
            
            .btn-orange { background: #ff5000; color: white; border: none; padding: 12px 18px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; transition: 0.2s; }
            .btn-orange:hover { background: #e04500; }

            .card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; text-align: left; margin-bottom: 20px; }
            .chat-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 15px; height: 350px; overflow-y: auto; margin-bottom: 15px; text-align: left; display: flex; flex-direction: column; gap: 10px; }
            .chat-msg { padding: 12px 16px; border-radius: 8px; font-size: 14px; max-width: 85%; line-height: 1.5; }
            .chat-msg.user { background: #ff5000; color: white; align-self: flex-end; }
            .chat-msg.ai { background: #e2e8f0; color: #1e293b; align-self: flex-start; }
        </style>
    </head>
    <body>

        <div class="top-nav-bar">
            <div class="top-tabs">
                <span class="active" onclick="switchTab('tabGlobal', this)">🌐 Global Factory Sourcing Hub</span>
                <span onclick="switchTab('tabSell', this)">🛒 Sell Your Product</span>
                <span onclick="switchTab('tabAds', this)">📢 Ad Promotion Network</span>
                <span onclick="switchTab('tabAI', this)">🤖 AI Trade & Sourcing Consultant</span>
                <span onclick="switchTab('tabGlobal', this)" style="margin-left: auto; font-size: 13px; background: rgba(255,255,255,0.15); padding: 5px 14px; border-radius: 20px;">👑 Owner Vault Active</span>
            </div>
            <div class="search-container">
                <span style="color: #ff5000; font-size: 18px;">🔍</span>
                <input type="text" id="searchInput" placeholder="Search worldwide factories: smartphones, car covers, generators, clothes...">
                <button class="search-btn" onclick="searchGlobalCatalog()">SEARCH WORLD</button>
            </div>
        </div>

        <div class="category-grid">
            <div class="cat-item" onclick="filterCategory('All')">
                <div class="cat-icon">🌍</div>
                <span>All Factories</span>
            </div>
            <div class="cat-item" onclick="filterCategory('Electronics')">
                <div class="cat-icon">📱</div>
                <span>Electronics</span>
            </div>
            <div class="cat-item" onclick="filterCategory('Automotive')">
                <div class="cat-icon">🚗</div>
                <span>Automotive</span>
            </div>
            <div class="cat-item" onclick="filterCategory('Fashion')">
                <div class="cat-icon">👔</div>
                <span>Fashion & Textiles</span>
            </div>
            <div class="cat-item" onclick="filterCategory('Industrial')">
                <div class="cat-icon">⚡</div>
                <span>Industrial Power</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabSell', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">📦</div>
                <span>List Product</span>
            </div>
        </div>

        <div class="main-layout">
            <div class="sidebar">
                <button class="nav-btn active" onclick="switchTab('tabReg', this)">📝 Profile & Delivery Address</button>
                <button class="nav-btn" onclick="switchTab('tabDash', this)">📊 User Sourcing Dashboard</button>
                <button class="nav-btn" onclick="switchTab('tabGlobal', this)">🌐 Worldwide Factory Marketplace</button>
                <button class="nav-btn" onclick="switchTab('tabSell', this)">🛒 Sell & List Your Goods</button>
                <button class="nav-btn" onclick="switchTab('tabAds', this)">📢 Ad Promotion & Marketing Hub</button>
                <button class="nav-btn" onclick="switchTab('tabAI', this)">🤖 AI Sourcing & Sales Advisor</button>
                <button class="nav-btn" onclick="switchTab('tabWallet', this)">🏦 AI Auto-Withdrawal</button>
            </div>

            <div class="content-area">
                <!-- TAB 1: REGISTRATION -->
                <div id="tabReg" class="tab-pane active">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Global Buyer & Vendor Registration</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 25px;">Enter your verified details and doorstep delivery address to buy, sell, or import from worldwide factories.</p>

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
                                <label>Destination Country</label>
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
                    <h2 style="color: #1e293b; margin-bottom: 15px;">User Dashboard & Escrow Ledger</h2>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 25px;">
                        <div class="card" style="border-left: 4px solid #ff5000; margin-bottom:0;">
                            <h3 style="font-size: 13px; color: #64748b;">Available Balance</h3>
                            <div style="font-size: 26px; font-weight: bold; color: #16a34a; margin-top: 5px;" id="dashBalance">0.000 KWD</div>
                        </div>
                        <div class="card" style="border-left: 4px solid #16a34a; margin-bottom:0;">
                            <h3 style="font-size: 13px; color: #64748b;">Escrow Locked Orders</h3>
                            <div style="font-size: 26px; font-weight: bold; color: #1e293b; margin-top: 5px;" id="dashEscrow">0.00 USD</div>
                        </div>
                        <div class="card" style="border-left: 4px solid #d97706; margin-bottom:0;">
                            <h3 style="font-size: 13px; color: #64748b;">Account Status</h3>
                            <div style="font-size: 16px; font-weight: bold; color: #16a34a; margin-top: 8px;">Verified & Active</div>
                        </div>
                    </div>
                </div>

                <!-- TAB 3: GLOBAL MARKETPLACE -->
                <div id="tabGlobal" class="tab-pane active">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Worldwide Factory Direct Sourcing</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Browse verified manufacturing hubs across China, USA, India, Europe, and Nigeria. Place escrow orders for direct doorstep delivery.</p>
                    
                    <div id="productContainer" class="prod-grid">
                        <!-- Loaded dynamically -->
                    </div>
                </div>

                <!-- TAB 4: SELL & LIST YOUR GOODS -->
                <div id="tabSell" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">List & Sell Your Products Worldwide</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Are you a manufacturer, local vendor, or reseller? List your products here so thousands of buyers can discover, buy, and ship them worldwide.</p>

                    <form onsubmit="postVendorProduct(event)" class="card">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Product Title</label>
                                <input type="text" id="sellTitle" placeholder="e.g. Luxury Car Body Cover" required>
                            </div>
                            <div class="form-group">
                                <label>Price (USD)</label>
                                <input type="number" step="0.01" id="sellPrice" placeholder="25.00" required>
                            </div>
                            <div class="form-group">
                                <label>Category</label>
                                <select id="sellCategory">
                                    <option value="Automotive">Automotive</option>
                                    <option value="Electronics">Electronics</option>
                                    <option value="Fashion">Fashion & Textiles</option>
                                    <option value="Industrial">Industrial Power</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Estimated Weight (kg)</label>
                                <input type="number" step="0.1" id="sellWeight" placeholder="1.2" required>
                            </div>
                            <div class="form-group full">
                                <label>Product Description & Sourcing Details</label>
                                <textarea id="sellDesc" rows="3" placeholder="Describe your product specs, minimum order quantity, and delivery terms..." required></textarea>
                            </div>
                        </div>
                        <button type="submit" class="btn-orange" style="margin-top: 15px;">Publish Product Live</button>
                    </form>
                </div>

                <!-- TAB 5: AD PROMOTION HUB -->
                <div id="tabAds" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Ad Promotion & Marketing Network</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Boost your product listings or website links across social networks. Users view your ads to earn rewards, driving instant viral traffic to your store.</p>

                    <form onsubmit="postAdCampaign(event)" class="card">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Campaign Title</label>
                                <input type="text" id="adTitle" placeholder="e.g. Car Cover Special Promo" required>
                            </div>
                            <div class="form-group">
                                <label>Target Link (Website / Product URL)</label>
                                <input type="url" id="adLink" placeholder="https://yourstore.com" required>
                            </div>
                            <div class="form-group">
                                <label>Reward Per View (Tokens)</label>
                                <input type="number" step="0.001" id="adReward" placeholder="2.500" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-orange" style="margin-top: 15px;">Launch Ad Campaign Live</button>
                    </form>

                    <div id="adList" class="prod-grid">
                        <div class="prod-card" style="padding: 15px;">
                            <h3 style="font-size: 14px; color: #1e293b; margin-bottom: 5px;">🔥 Featured Global Factory Promo</h3>
                            <p style="font-size: 12px; color: #64748b; margin-bottom: 12px;">Reward: 3.0 Tokens per view.</p>
                            <button class="btn-orange" onclick="engageAd('Featured Factory Promo', 3.0)">View Ad & Earn Reward</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 6: AI SOURCING & SALES ADVISOR -->
                <div id="tabAI" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">AI Sourcing & Sales Consultant</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Ask the AI advisor how to source products from international factories, price items for maximum profit, or run marketing campaigns.</p>
                    
                    <div class="chat-box" id="chatContainer">
                        <div class="chat-msg ai">Hello! I am your AI Sourcing and Trade Advisor. Ask me how to find worldwide factories, import goods, or scale your sales!</div>
                    </div>

                    <div style="display: flex; gap: 10px;">
                        <input type="text" id="chatInput" placeholder="e.g. How can I import electronics from China and sell them in Nigeria?" style="flex: 1;" onkeypress="if(event.key === 'Enter') sendAIChat()">
                        <button class="btn-orange" style="width: 130px;" onclick="sendAIChat()">Ask AI</button>
                    </div>
                </div>

                <!-- TAB 7: WALLET -->
                <div id="tabWallet" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">AI Automated Payout Gateway</h2>
                    <div class="card" style="max-width: 500px; margin: 0 auto; text-align: center;">
                        <h3 style="color: #16a34a; font-size: 26px; margin-bottom: 10px;" id="walletBalance">0.000 KWD</h3>
                        <p style="font-size: 13px; color: #64748b; margin-bottom: 15px;">Minimum withdrawal threshold: 50.000 KWD</p>
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
                document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
                if(btnElement) btnElement.classList.add('active');
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

                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if(res.ok) {
                    currentUserId = data.user_id;
                    updateUI(data.cash_balance, data.escrow_locked);
                    showModal("Profile Registered", `User ID: ${currentUserId}\\nDelivery Address Linked Successfully.\\nReady for Worldwide Factory Sourcing.`);
                    switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[2]);
                } else {
                    alert('Error: ' + data.detail);
                }
            }

            async function updateUI(cash, escrow) {
                document.getElementById('dashBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('walletBalance').innerText = cash.toFixed(3) + " KWD";
                document.getElementById('dashEscrow').innerText = escrow.toFixed(2) + " USD";
            }

            async function loadGlobalCatalog(category = 'All') {
                const res = await fetch(`/api/products?category=${category}`);
                const items = await res.json();
                const container = document.getElementById('productContainer');
                let html = '';
                items.forEach(i => {
                    html += `
                        <div class="prod-card">
                            <div class="prod-img-box">
                                <div class="prod-badge">${i.sold_count}</div>
                                <span>${i.image_emoji}</span>
                            </div>
                            <div class="prod-info">
                                <div class="prod-title">${i.title}</div>
                                <div class="prod-supplier">🏭 ${i.factory_name} (${i.origin})</div>
                                <div class="prod-price">💲${i.price_usd.toFixed(2)} USD</div>
                                <div class="prod-freight">📦 Weight: ${i.weight_kg} kg | ${i.moq}</div>
                                <button class="btn-orange" onclick="placeEscrowOrder('${i.id}', '${i.title}', ${i.price_usd})">Escrow Order & Ship</button>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            }

            async function filterCategory(category) {
                loadGlobalCatalog(category);
                switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[2]);
            }

            async function searchGlobalCatalog() {
                const query = document.getElementById('searchInput').value.toLowerCase();
                if(!query) { loadGlobalCatalog('All'); return; }
                const res = await fetch('/api/products?category=All');
                const items = await res.json();
                const filtered = items.filter(i => i.title.toLowerCase().includes(query) || i.origin.toLowerCase().includes(query) || i.category.toLowerCase().includes(query));
                
                const container = document.getElementById('productContainer');
                let html = '';
                if(filtered.length === 0) {
                    html = '<p style="color: #64748b; padding: 20px;">No worldwide factory products found matching your search. Try another keyword!</p>';
                } else {
                    filtered.forEach(i => {
                        html += `
                            <div class="prod-card">
                                <div class="prod-img-box">
                                    <div class="prod-badge">${i.sold_count}</div>
                                    <span>${i.image_emoji}</span>
                                </div>
                                <div class="prod-info">
                                    <div class="prod-title">${i.title}</div>
                                    <div class="prod-supplier">🏭 ${i.factory_name} (${i.origin})</div>
                                    <div class="prod-price">💲${i.price_usd.toFixed(2)} USD</div>
                                    <div class="prod-freight">📦 Weight: ${i.weight_kg} kg | ${i.moq}</div>
                                    <button class="btn-orange" onclick="placeEscrowOrder('${i.id}', '${i.title}', ${i.price_usd})">Escrow Order & Ship</button>
                                </div>
                            </div>
                        `;
                    });
                }
                container.innerHTML = html;
                switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[2]);
            }

            async function placeEscrowOrder(itemId, title, priceUsd) {
                if(!currentUserId) {
                    alert('Please complete your profile and delivery address first!');
                    switchTab('tabReg', document.querySelectorAll('.nav-btn')[0]);
                    return;
                }
                const res = await fetch('/api/order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, item_id: itemId, price_usd: priceUsd})
                });
                const data = await res.json();
                if(res.ok) {
                    updateUI(data.cash_balance, data.escrow_locked);
                    showModal("🔒 ESCROW ORDER SECURED", `Product: ${title}\\nAmount: $${priceUsd.toFixed(2)} USD\\nStatus: Funds locked in escrow. Factory dispatch to your delivery address initiated!`);
                }
            }

            async function postVendorProduct(e) {
                e.preventDefault();
                if(!currentUserId) { alert('Please register first!'); switchTab('tabReg', document.querySelectorAll('.nav-btn')[0]); return; }
                const payload = {
                    title: document.getElementById('sellTitle').value,
                    price_usd: parseFloat(document.getElementById('sellPrice').value),
                    category: document.getElementById('sellCategory').value,
                    weight_kg: parseFloat(document.getElementById('sellWeight').value),
                    description: document.getElementById('sellDesc').value,
                    seller: currentUserId
                };
                const res = await fetch('/api/sell', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(res.ok) {
                    alert('Product listed successfully to the global marketplace!');
                    loadGlobalCatalog('All');
                    switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[2]);
                }
            }

            function postAdCampaign(e) {
                e.preventDefault();
                const title = document.getElementById('adTitle').value;
                const reward = document.getElementById('adReward').value;
                document.getElementById('adList').innerHTML += `
                    <div class="prod-card" style="padding: 15px;">
                        <h3 style="font-size: 14px; color: #1e293b; margin-bottom: 5px;">🔥 ${title}</h3>
                        <p style="font-size: 12px; color: #64748b; margin-bottom: 12px;">Reward: ${reward} Tokens per view.</p>
                        <button class="btn-orange" onclick="engageAd('${title}', ${reward})">View Ad & Earn Reward</button>
                    </div>
                `;
                alert('Ad campaign published live successfully!');
            }

            function engageAd(title, reward) {
                alert(`Engaged with ad: "${title}"! Reward credited.`);
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
                chatContainer.innerHTML += `<div class="chat-msg ai">🤖 <b>AI Sourcing Advisor:</b> ${data.response}</div>`;
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            async function requestAIWithdrawal() {
                if(!currentUserId) { alert('Please register first!'); return; }
                const dest = document.getElementById('payoutDest').value;
                if(!dest) { alert('Enter payout destination.'); return; }
                const res = await fetch('/api/withdraw', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, destination: dest})
                });
                const data = await res.json();
                if(res.ok) {
                    showModal("🤖 AI AUTO-WITHDRAWAL APPROVED", `Status: APPROVED BY CONTROLLER\\nAmount: ${data.withdrawn.toFixed(3)} KWD\\nDestination: ${dest}`);
                    updateUI(data.cash_balance, data.escrow_locked);
                } else {
                    alert('Error: ' + data.detail);
                }
            }

            function showModal(title, text) {
                document.getElementById('modalTitle').innerText = title;
                document.getElementById('modalText').innerText = text.replace(/\\n/g, '\\n');
                document.getElementById('proofModal').classList.remove('hidden');
            }

            function closeModal() { document.getElementById('proofModal').classList.add('hidden'); }

            loadGlobalCatalog('All');
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
    seed_global_catalog(db)
    existing = db.query(GlobalHubUser).filter((GlobalHubUser.id == user.id) | (GlobalHubUser.identity_number == user.identity_number)).first()
    vault = db.query(PlatformVault).filter(PlatformVault.id == "vault_hub").first()
    if not vault:
        vault = PlatformVault(id="vault_hub", owner_revenue=Decimal("950.000"))
        db.add(vault)
        db.commit()

    if existing:
        existing.shipping_address = user.shipping_address
        existing.city = user.city
        existing.country = user.country
        db.commit()
        return {"user_id": existing.id, "cash_balance": float(existing.cash_balance), "escrow_locked": float(existing.escrow_locked)}
    
    new_user = GlobalHubUser(
        id=user.id, name=user.name, email=user.email, phone=user.phone,
        nationality=user.nationality, identity_number=user.identity_number,
        shipping_address=user.shipping_address, city=user.city, country=user.country,
        cash_balance=Decimal("0.000"), escrow_locked=Decimal("0.000")
    )
    db.add(new_user)
    db.commit()
    return {"user_id": new_user.id, "cash_balance": float(new_user.cash_balance), "escrow_locked": float(new_user.escrow_locked)}

@app.get("/api/products")
def get_products(category: str = "All", db: Session = Depends(get_db)):
    seed_global_catalog(db)
    query = db.query(GlobalProductItem)
    if category != "All":
        query = query.filter(GlobalProductItem.category == category)
    items = query.all()
    return [{
        "id": i.id, "title": i.title, "factory_name": i.factory_name, "origin": i.country_origin,
        "price_usd": float(i.price_usd), "weight_kg": float(i.weight_kg),
        "category": i.category, "image_emoji": i.image_emoji, "moq": i.moq, "sold_count": i.sold_count
    } for i in items]

@app.post("/api/sell")
def sell_product(data: dict, db: Session = Depends(get_db)):
    new_item = GlobalProductItem(
        id="item_" + str(datetime.now().timestamp()),
        title=data.get("title"),
        factory_name="Vendor: " + data.get("seller"),
        country_origin="Local / Global",
        price_usd=Decimal(str(data.get("price_usd"))),
        weight_kg=Decimal(str(data.get("weight_kg", 1.0))),
        category=data.get("category"),
        image_emoji="🛍️",
        moq="MOQ: 1 Unit",
        sold_count="New Listing"
    )
    db.add(new_item)
    db.commit()
    return {"status": "success"}

@app.post("/api/order")
def place_order(data: dict, db: Session = Depends(get_db)):
    user = db.query(GlobalHubUser).filter(GlobalHubUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    price = Decimal(str(data.get("price_usd")))
    user.escrow_locked += price
    db.commit()
    return {"status": "success", "cash_balance": float(user.cash_balance), "escrow_locked": float(user.escrow_locked)}

@app.post("/api/ai-consultant")
def ai_consultant(data: dict):
    prompt = data.get("prompt", "").lower()
    if "import" in prompt or "china" in prompt or "sell" in prompt:
        reply = "To successfully source and import from worldwide factories, select items with high profit margins, list them on social media (Facebook/Instagram Reels), and use our escrow and doorstep delivery system to handle fulfillment effortlessly."
    else:
        reply = f"That is a great trade question regarding '{prompt}'. SwiftBux connects you to global manufacturers instantly with automated escrow security and door-to-door cargo shipping!"
    return {"response": reply}

@app.post("/api/withdraw")
def withdraw(data: dict, db: Session = Depends(get_db)):
    user = db.query(GlobalHubUser).filter(GlobalHubUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.cash_balance < Decimal("50.000"):
        raise HTTPException(status_code=400, detail="Minimum withdrawal threshold is 50.000 KWD.")
    amt = user.cash_balance
    user.cash_balance = Decimal("0.000")
    db.commit()
    return {"status": "approved", "withdrawn": float(amt), "cash_balance": float(user.cash_balance), "escrow_locked": float(user.escrow_locked)}