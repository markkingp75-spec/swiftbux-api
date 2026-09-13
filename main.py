from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_complete_hub.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CompleteUser(Base):
    __tablename__ = "complete_users"
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
    mined_balance = Column(Numeric(10, 3), default=Decimal("0.000"))
    mining_active = Column(String, default="false")
    mining_start_time = Column(DateTime, nullable=True)
    last_daily_claim = Column(DateTime, nullable=True)
    bank_card_number = Column(String, default="")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class CompleteProduct(Base):
    __tablename__ = "complete_products"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    factory_name = Column(String)
    origin = Column(String)
    price_usd = Column(Numeric(10, 2))
    weight_kg = Column(Numeric(5, 2))
    category = Column(String)
    image_emoji = Column(String)
    moq = Column(String)
    sold_count = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwiftBux Complete Global Marketplace & Earning Hub")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_catalog(db: Session):
    if db.query(CompleteProduct).count() == 0:
        items = [
            CompleteProduct(id="c1", title="Industrial 5G Smartphone Global Edition", factory_name="Shenzhen Semiconductor Works", origin="China", price_usd=65.00, weight_kg=0.4, category="Electronics", image_emoji="📱", moq="MOQ: 1 Unit", sold_count="15K+ sold"),
            CompleteProduct(id="c2", title="All-Terrain Mountain Bike 21-Speed", factory_name="Hangzhou Industrial Assembly", origin="China", price_usd=45.00, weight_kg=14.0, category="Automotive", image_emoji="🚲", sold_count="6.2K+ sold"),
            CompleteProduct(id="c3", title="USA Branded Smart Fitness Watch Pro V2", factory_name="California Tech Solutions", origin="United States", price_usd=32.00, weight_kg=0.2, category="Electronics", image_emoji="⌚", sold_count="9.1K+ sold"),
            CompleteProduct(id="c4", title="Genuine Handcrafted Leather Briefcase", factory_name="New Delhi Export Artisans", origin="India", price_usd=28.00, weight_kg=1.5, category="Fashion", image_emoji="💼", sold_count="4.5K+ sold"),
            CompleteProduct(id="c5", title="Luxury Ankara Traditional Fabric Bundle", factory_name="Lagos Textile Manufacturers", origin="Nigeria", price_usd=18.00, weight_kg=1.0, category="Fashion", image_emoji="🧵", sold_count="18K+ sold"),
            CompleteProduct(id="c6", title="Heavy Duty Solar Power Generator 5kW", factory_name="Berlin Clean Energy Works", origin="Germany", price_usd=320.00, weight_kg=22.0, category="Industrial", image_emoji="⚡", sold_count="1.4K+ sold")
        ]
        db.add_all(items)
        db.commit()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwiftBux Global Marketplace & Earning Hub</title>
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
            .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; display: none; }
            .modal-box { background: white; padding: 30px; border-radius: 12px; width: 450px; text-align: center; }
        </style>
    </head>
    <body>

        <div class="top-nav-bar">
            <div class="top-tabs">
                <span class="active" onclick="switchTab('tabGlobal', this)">🌐 Marketplace & Shopping</span>
                <span onclick="switchTab('tabMining', this)">⛏️ Mining & Daily Claims</span>
                <span onclick="switchTab('tabGames', this)">🎮 Play & Earn Games</span>
                <span onclick="switchTab('tabAds', this)">📺 Watch Videos & Earn</span>
                <span onclick="switchTab('tabLogin', this)">🔐 Login / Register</span>
                <span style="margin-left: auto; font-size: 13px; background: rgba(255,255,255,0.15); padding: 5px 14px; border-radius: 20px;" id="authStatusBadge">Guest Mode</span>
            </div>
            <div class="search-container">
                <span style="color: #ff5000; font-size: 18px;">🔍</span>
                <input type="text" id="searchInput" placeholder="Search products to buy with your bank card...">
                <button class="search-btn" onclick="searchCatalog()">SEARCH</button>
            </div>
        </div>

        <div class="category-grid">
            <div class="cat-item" onclick="switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[0])">
                <div class="cat-icon">🛒</div>
                <span>Buy Goods</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabMining', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">⛏️</div>
                <span>24H Mining</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabMining', document.querySelectorAll('.nav-btn')[2])">
                <div class="cat-icon">🎁</div>
                <span>Daily Claim</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabGames', document.querySelectorAll('.nav-btn')[3])">
                <div class="cat-icon">🎮</div>
                <span>Play Games</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabAds', document.querySelectorAll('.nav-btn')[4])">
                <div class="cat-icon">📺</div>
                <span>Watch & Earn</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabWallet', document.querySelectorAll('.nav-btn')[6])">
                <div class="cat-icon">💳</div>
                <span>Bank Card / Wallet</span>
            </div>
        </div>

        <div class="main-layout">
            <div class="sidebar">
                <button class="nav-btn active" onclick="switchTab('tabGlobal', this)">🌐 Marketplace (Buy Goods)</button>
                <button class="nav-btn" onclick="switchTab('tabLogin', this)">🔐 Login / Register Profile</button>
                <button class="nav-btn" onclick="switchTab('tabMining', this)">⛏️ 24H Mining & Daily Claims</button>
                <button class="nav-btn" onclick="switchTab('tabGames', this)">🎮 Play & Earn Games</button>
                <button class="nav-btn" onclick="switchTab('tabAds', this)">📺 Watch Videos & Earn</button>
                <button class="nav-btn" onclick="switchTab('tabWallet', this)">💳 Bank Card & Wallet</button>
                <button class="nav-btn" onclick="switchTab('tabSell', this)">🛒 List & Sell Product</button>
            </div>

            <div class="content-area">
                <!-- TAB 1: MARKETPLACE & BUYING -->
                <div id="tabGlobal" class="tab-pane active">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Worldwide Factory Marketplace</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Browse and buy goods directly. When you click buy, you can securely pay using your saved bank card or backup payment method.</p>
                    <div id="productContainer" class="prod-grid"></div>
                </div>

                <!-- TAB 2: LOGIN / REGISTER -->
                <div id="tabLogin" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Account Login & Registration</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Log in with your User ID, or create a new account to save your earnings and bank card.</p>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                        <div class="card">
                            <h3 style="color: #ff5000; margin-bottom: 15px;">Quick Login</h3>
                            <form onsubmit="handleLogin(event)">
                                <div class="form-group">
                                    <label>Your Username / ID</label>
                                    <input type="text" id="loginId" placeholder="e.g. user123" required>
                                </div>
                                <button type="submit" class="btn-orange" style="margin-top: 10px;">Log In</button>
                            </form>
                        </div>

                        <div class="card">
                            <h3 style="color: #1e293b; margin-bottom: 15px;">Register New Account</h3>
                            <form onsubmit="handleRegistration(event)">
                                <div class="form-group">
                                    <label>Full Legal Name</label>
                                    <input type="text" id="regName" required>
                                </div>
                                <div class="form-group">
                                    <label>Choose Username / ID</label>
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
                                    <label>Bank Card Number (for buying goods)</label>
                                    <input type="text" id="regCard" placeholder="4123 4567 8901 2345" required>
                                </div>
                                <div class="form-group">
                                    <label>Destination Country</label>
                                    <select id="regNationality">
                                        <option value="Nigeria">Nigeria (Doorstep Cargo)</option>
                                        <option value="Kuwait">Kuwait</option>
                                        <option value="International">International</option>
                                    </select>
                                </div>
                                <div class="form-group full">
                                    <label>Delivery Address</label>
                                    <input type="text" id="regAddress" placeholder="Street Address / City" required>
                                </div>
                                <button type="submit" class="btn-orange" style="margin-top: 15px;">Register Account</button>
                            </form>
                        </div>
                    </div>
                </div>

                <!-- TAB 3: MINING & DAILY CLAIMS (EARNINGS) -->
                <div id="tabMining" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">24-Hour Mining & Daily Reward Claims</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Earn free tokens daily by starting your 24-hour mining cycle and claiming daily rewards!</p>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div class="card" style="text-align: center;">
                            <h3 style="color: #ff5000; margin-bottom: 10px;">⛏️ 24-Hour Cloud Miner</h3>
                            <p style="font-size: 14px; color: #64748b; margin-bottom: 15px;">Mined Earnings: <span id="minedBalanceDisplay" style="font-weight: bold; color: #16a34a;">0.000</span> Tokens</p>
                            <button class="btn-orange" onclick="startMining()">Start / Check 24H Mining</button>
                        </div>

                        <div class="card" style="text-align: center;">
                            <h3 style="color: #16a34a; margin-bottom: 10px;">🎁 Daily Reward Claim</h3>
                            <p style="font-size: 14px; color: #64748b; margin-bottom: 15px;">Claim your free daily streak bonus of +5.0 Tokens.</p>
                            <button class="btn-orange" style="background: #16a34a;" onclick="claimDaily()">Claim Daily Reward</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 4: PLAY & EARN GAMES -->
                <div id="tabGames" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Play & Earn Mini-Games</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Play our interactive rewards game to boost your token balance instantly.</p>
                    
                    <div class="card" style="text-align: center; max-width: 500px; margin: 0 auto;">
                        <h3 style="color: #ff5000; margin-bottom: 10px;">🎮 Tap-to-Earn Coin Game</h3>
                        <p style="font-size: 14px; color: #64748b; margin-bottom: 20px;">Tap the coin below to earn +1.0 Token per tap!</p>
                        <div style="font-size: 70px; cursor: pointer; margin-bottom: 20px;" onclick="playGameReward()">🪙</div>
                        <p style="font-weight: bold; font-size: 16px;">Game Score / Earned: <span id="gameScore" style="color: #16a34a;">0.000</span> Tokens</p>
                    </div>
                </div>

                <!-- TAB 5: WATCH VIDEOS & EARN -->
                <div id="tabAds" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Watch Videos & Ads to Earn</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Watch sponsored promotional videos and ad campaigns to earn rewards straight to your wallet.</p>
                    
                    <div class="prod-grid">
                        <div class="prod-card" style="padding: 15px;">
                            <h3 style="font-size: 15px; color: #1e293b; margin-bottom: 8px;">📺 Global Factory Promo Video #1</h3>
                            <p style="font-size: 12px; color: #64748b; margin-bottom: 15px;">Reward: +3.0 Tokens upon completion.</p>
                            <button class="btn-orange" onclick="watchAdReward('Global Factory Promo #1', 3.0)">Watch Video & Earn</button>
                        </div>
                        <div class="prod-card" style="padding: 15px;">
                            <h3 style="font-size: 15px; color: #1e293b; margin-bottom: 8px;">📺 International Sourcing Showcase #2</h3>
                            <p style="font-size: 12px; color: #64748b; margin-bottom: 15px;">Reward: +3.0 Tokens upon completion.</p>
                            <button class="btn-orange" onclick="watchAdReward('International Sourcing Showcase #2', 3.0)">Watch Video & Earn</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 6: BANK CARD & WALLET -->
                <div id="tabWallet" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Bank Card & Wallet Management</h2>
                    <div class="card" style="max-width: 500px; margin: 0 auto;">
                        <h3 style="color: #16a34a; font-size: 24px; margin-bottom: 10px;" id="walletBalance">0.000 Tokens / KWD</h3>
                        <p style="font-size: 13px; color: #64748b; margin-bottom: 15px;">Your saved bank card is used when buying goods from the marketplace.</p>
                        <div class="form-group">
                            <label>Saved Bank Card / Payment Backup</label>
                            <input type="text" id="userBankCard" placeholder="Card Number on file">
                        </div>
                        <button class="btn-orange" onclick="updateBankCard()">Update Bank Card Backup</button>
                    </div>
                </div>

                <!-- TAB 7: SELL PRODUCT -->
                <div id="tabSell" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">List & Sell Your Products Worldwide</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">List your products on the marketplace.</p>
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
                                    <option value="Fashion">Fashion</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Weight (kg)</label>
                                <input type="number" step="0.1" id="sellWeight" placeholder="1.0" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-orange" style="margin-top: 15px;">Publish Product</button>
                    </form>
                </div>
            </div>
        </div>

        <!-- PAYMENT CHECKOUT MODAL -->
        <div id="checkoutModal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="color: #1e293b; margin-bottom: 10px;">💳 Secure Bank Card Checkout</h3>
                <p id="checkoutItemText" style="font-size: 13px; color: #64748b; margin-bottom: 15px;"></p>
                <div class="form-group">
                    <label>Confirm Bank Card / Backup Payment</label>
                    <input type="text" id="checkoutCardInput" placeholder="Enter card number to pay">
                </div>
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <button class="btn-orange" style="background: #16a34a;" onclick="confirmPurchase()">Pay Now & Order</button>
                    <button class="btn-orange" style="background: #64748b;" onclick="closeModal()">Cancel</button>
                </div>
            </div>
        </div>

        <script>
            let currentUserId = localStorage.getItem('swiftbux_user_id') || null;
            let currentSelectedItem = null;
            let currentItemPrice = 0;

            function checkAuth() {
                if(currentUserId) {
                    document.getElementById('authStatusBadge').innerText = "Logged In: " + currentUserId;
                    fetchUserData();
                } else {
                    document.getElementById('authStatusBadge').innerText = "Guest Mode";
                }
            }

            function switchTab(tabId, btnElement) {
                document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
                if(btnElement) btnElement.classList.add('active');
            }

            async function handleLogin(e) {
                e.preventDefault();
                const userId = document.getElementById('loginId').value.trim();
                const res = await fetch(`/api/login?user_id=${userId}`);
                const data = await res.json();
                if(res.ok) {
                    currentUserId = data.user_id;
                    localStorage.setItem('swiftbux_user_id', currentUserId);
                    checkAuth();
                    alert('Login successful!');
                    switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[0]);
                } else {
                    alert('Login Error: ' + data.detail);
                }
            }

            async function handleRegistration(e) {
                e.preventDefault();
                const payload = {
                    id: document.getElementById('regId').value,
                    name: document.getElementById('regName').value,
                    email: document.getElementById('regEmail').value,
                    phone: document.getElementById('regPhone').value,
                    bank_card_number: document.getElementById('regCard').value,
                    nationality: document.getElementById('regNationality').value,
                    identity_number: "NIN_" + Math.random(),
                    shipping_address: document.getElementById('regAddress').value,
                    city: "Lagos",
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
                    localStorage.setItem('swiftbux_user_id', currentUserId);
                    checkAuth();
                    alert('Account created successfully!');
                    switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[0]);
                } else {
                    alert('Error: ' + data.detail);
                }
            }

            async function fetchUserData() {
                if(!currentUserId) return;
                const res = await fetch(`/api/user?user_id=${currentUserId}`);
                const data = await res.json();
                if(res.ok) {
                    document.getElementById('walletBalance').innerText = data.mined_balance.toFixed(3) + " Tokens";
                    document.getElementById('minedBalanceDisplay').innerText = data.mined_balance.toFixed(3);
                    document.getElementById('gameScore').innerText = data.mined_balance.toFixed(3);
                    if(data.bank_card) document.getElementById('userBankCard').value = data.bank_card;
                }
            }

            async function loadCatalog() {
                const res = await fetch('/api/products');
                const items = await res.json();
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
                                <button class="btn-orange" onclick="openCheckout('${i.title}', ${i.price_usd})">Buy with Bank Card</button>
                            </div>
                        </div>
                    `;
                });
                document.getElementById('productContainer').innerHTML = html;
            }

            function openCheckout(title, price) {
                if(!currentUserId) {
                    alert('Please log in or register first before purchasing!');
                    switchTab('tabLogin', document.querySelectorAll('.nav-btn')[1]);
                    return;
                }
                currentSelectedItem = title;
                currentItemPrice = price;
                document.getElementById('checkoutItemText').innerText = `Item: ${title}\\nPrice: $${price.toFixed(2)} USD\\nPayment method will charge your saved bank card/backup.`;
                document.getElementById('checkoutModal').style.display = 'flex';
            }

            function closeModal() {
                document.getElementById('checkoutModal').style.display = 'none';
            }

            async function confirmPurchase() {
                const card = document.getElementById('checkoutCardInput').value;
                const res = await fetch('/api/buy-goods', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, item: currentSelectedItem, price: currentItemPrice, card: card})
                });
                const data = await res.json();
                if(res.ok) {
                    alert(`✅ Payment successful using bank card! Your order for "${currentSelectedItem}" has been placed.`);
                    closeModal();
                } else {
                    alert('Payment Error: ' + data.detail);
                }
            }

            async function startMining() {
                if(!currentUserId) { alert('Please log in first!'); switchTab('tabLogin', document.querySelectorAll('.nav-btn')[1]); return; }
                const res = await fetch('/api/earn/mining', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId})
                });
                const data = await res.json();
                fetchUserData();
                alert(data.message);
            }

            async function claimDaily() {
                if(!currentUserId) { alert('Please log in first!'); switchTab('tabLogin', document.querySelectorAll('.nav-btn')[1]); return; }
                const res = await fetch('/api/earn/daily-claim', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId})
                });
                const data = await res.json();
                fetchUserData();
                alert(data.message);
            }

            async function playGameReward() {
                if(!currentUserId) { alert('Please log in first!'); switchTab('tabLogin', document.querySelectorAll('.nav-btn')[1]); return; }
                const res = await fetch('/api/earn/game', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId})
                });
                const data = await res.json();
                fetchUserData();
            }

            async function watchAdReward(title, reward) {
                if(!currentUserId) { alert('Please log in first!'); switchTab('tabLogin', document.querySelectorAll('.nav-btn')[1]); return; }
                const res = await fetch('/api/earn/ad', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, reward: reward})
                });
                const data = await res.json();
                fetchUserData();
                alert(`📺 Watched "${title}" successfully! Earned +${reward} Tokens.`);
            }

            async function updateBankCard() {
                if(!currentUserId) { alert('Please log in first!'); return; }
                const card = document.getElementById('userBankCard').value;
                const res = await fetch('/api/update-card', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, card: card})
                });
                alert('Bank card backup updated successfully!');
            }

            async function postVendorProduct(e) {
                e.preventDefault();
                if(!currentUserId) { alert('Please log in first!'); return; }
                const payload = {
                    title: document.getElementById('sellTitle').value,
                    price_usd: parseFloat(document.getElementById('sellPrice').value),
                    category: document.getElementById('sellCategory').value,
                    weight_kg: parseFloat(document.getElementById('sellWeight').value),
                    seller: currentUserId
                };
                const res = await fetch('/api/sell', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(res.ok) {
                    alert('Product listed successfully!');
                    loadCatalog();
                    switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[0]);
                }
            }

            checkAuth();
            loadCatalog();
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
    bank_card_number: str

@app.post("/api/register")
def register_user(user: UserReg, db: Session = Depends(get_db)):
    seed_catalog(db)
    existing = db.query(CompleteUser).filter(CompleteUser.id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User ID already exists.")
    
    new_user = CompleteUser(
        id=user.id, name=user.name, email=user.email, phone=user.phone,
        nationality=user.nationality, identity_number=user.identity_number,
        shipping_address=user.shipping_address, city=user.city, country=user.country,
        bank_card_number=user.bank_card_number, mined_balance=Decimal("10.000")
    )
    db.add(new_user)
    db.commit()
    return {"user_id": new_user.id}

@app.get("/api/login")
def login_user(user_id: str, db: Session = Depends(get_db)):
    seed_catalog(db)
    user = db.query(CompleteUser).filter(CompleteUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"user_id": user.id}

@app.get("/api/user")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(CompleteUser).filter(CompleteUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"mined_balance": float(user.mined_balance), "bank_card": user.bank_card_number}

@app.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    seed_catalog(db)
    items = db.query(CompleteProduct).all()
    return [{
        "id": i.id, "title": i.title, "factory_name": i.factory_name, "origin": i.origin,
        "price_usd": float(i.price_usd), "image_emoji": i.image_emoji, "sold_count": i.sold_count
    } for i in items]

@app.post("/api/buy-goods")
def buy_goods(data: dict, db: Session = Depends(get_db)):
    user = db.query(CompleteUser).filter(CompleteUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"status": "success"}

@app.post("/api/earn/mining")
def earn_mining(data: dict, db: Session = Depends(get_db)):
    user = db.query(CompleteUser).filter(CompleteUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.mined_balance += Decimal("12.500")
    db.commit()
    return {"message": "⛏️ 24H Mining reward claimed (+12.5 Tokens)!"}

@app.post("/api/earn/daily-claim")
def earn_daily(data: dict, db: Session = Depends(get_db)):
    user = db.query(CompleteUser).filter(CompleteUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.mined_balance += Decimal("5.000")
    db.commit()
    return {"message": "🎁 Daily reward successfully claimed (+5.0 Tokens)!"}

@app.post("/api/earn/game")
def earn_game(data: dict, db: Session = Depends(get_db)):
    user = db.query(CompleteUser).filter(CompleteUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.mined_balance += Decimal("1.000")
    db.commit()
    return {"status": "success"}

@app.post("/api/earn/ad")
def earn_ad(data: dict, db: Session = Depends(get_db)):
    user = db.query(CompleteUser).filter(CompleteUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    reward = Decimal(str(data.get("reward", 3.0)))
    user.mined_balance += reward
    db.commit()
    return {"status": "success"}

@app.post("/api/update-card")
def update_card(data: dict, db: Session = Depends(get_db)):
    user = db.query(CompleteUser).filter(CompleteUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.bank_card_number = data.get("card", "")
    db.commit()
    return {"status": "success"}

@app.post("/api/sell")
def sell_product(data: dict, db: Session = Depends(get_db)):
    new_item = CompleteProduct(
        id="item_" + str(datetime.now().timestamp()),
        title=data.get("title"),
        factory_name="Vendor: " + data.get("seller"),
        origin="Global",
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