from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_temu_style.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TemuUser(Base):
    __tablename__ = "temu_users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    shipping_address = Column(String)
    city = Column(String)
    country = Column(String)
    earned_balance = Column(Numeric(10, 3), default=Decimal("0.000"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class TemuProduct(Base):
    __tablename__ = "temu_products"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    factory_source = Column(String)
    origin = Column(String)
    price_usd = Column(Numeric(10, 2))
    colors_json = Column(String) # e.g. "Red, Blue, Black"
    sizes_json = Column(String)  # e.g. "Small, Medium, Large"
    category = Column(String)
    image_emoji = Column(String)
    sold_count = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwiftBux Global E-Commerce & Earning Platform")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_temu_catalog(db: Session):
    if db.query(TemuProduct).count() == 0:
        items = [
            TemuProduct(id="p1", title="Industrial 5G Smartphone Global Edition", factory_source="Shenzhen Semiconductor Factory", origin="China", price_usd=65.00, colors_json="Black, Silver, Gold", sizes_json="128GB, 256GB", category="Electronics", image_emoji="📱", sold_count="15K+ sold"),
            TemuProduct(id="p2", title="All-Terrain Mountain Bike 21-Speed", factory_source="Hangzhou Bicycle Works", origin="China", price_usd=45.00, colors_json="Red, Blue, Matte Black", sizes_json="Standard 26-inch", category="Automotive", image_emoji="🚲", sold_count="6.2K+ sold"),
            TemuProduct(id="p3", title="USA Branded Smart Fitness Watch Pro V2", factory_source="California Tech Solutions", origin="United States", price_usd=32.00, colors_json="Black, White, Rose Gold", sizes_json="Adjustable", category="Electronics", image_emoji="⌚", sold_count="9.1K+ sold"),
            TemuProduct(id="p4", title="Genuine Handcrafted Leather Briefcase", factory_source="New Delhi Export Artisans", origin="India", price_usd=28.00, colors_json="Brown, Dark Tan, Black", sizes_json="Standard", category="Fashion", image_emoji="💼", sold_count="4.5K+ sold"),
            TemuProduct(id="p5", title="Luxury Ankara Traditional Fabric (10 Yards)", factory_source="Lagos Textile Manufacturers", origin="Nigeria", price_usd=18.00, colors_json="Multi-color Print", sizes_json="10 Yards", category="Fashion", image_emoji="🧵", sold_count="18K+ sold"),
            TemuProduct(id="p6", title="Heavy Duty Solar Power Generator 5kW", factory_source="Berlin Clean Energy Works", origin="Germany", price_usd=320.00, colors_json="Industrial Gray", sizes_json="5kW Unit", category="Industrial", image_emoji="⚡", sold_count="1.4K+ sold")
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
        <title>SwiftBux Global E-Commerce & Earning Hub</title>
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
            .prod-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: 0.2s; cursor: pointer; }
            .prod-card:hover { box-shadow: 0 8px 20px rgba(0,0,0,0.08); transform: translateY(-2px); }
            .prod-img-box { background: #f8fafc; height: 160px; display: flex; align-items: center; justify-content: center; font-size: 55px; position: relative; }
            .prod-badge { position: absolute; top: 10px; left: 10px; background: #ff5000; color: white; font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
            .prod-info { padding: 15px; }
            .prod-title { font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
            .prod-supplier { font-size: 12px; color: #64748b; margin-bottom: 8px; }
            .prod-price { font-size: 18px; font-weight: bold; color: #ff5000; margin-bottom: 15px; }

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
            .modal-box { background: white; padding: 30px; border-radius: 12px; width: 480px; text-align: center; max-height: 90vh; overflow-y: auto; }
        </style>
    </head>
    <body>

        <div class="top-nav-bar">
            <div class="top-tabs">
                <span class="active" onclick="switchTab('tabGlobal', this)">🛍️ Marketplace (Temu Style)</span>
                <span onclick="switchTab('tabMining', this)">⛏️ Mining & Claims</span>
                <span onclick="switchTab('tabGames', this)">🎮 Play Games</span>
                <span onclick="switchTab('tabAds', this)">📺 Watch Videos</span>
                <span onclick="switchTab('tabLogin', this)">🔐 Login / Register</span>
                <span style="margin-left: auto; font-size: 13px; background: rgba(255,255,255,0.15); padding: 5px 14px; border-radius: 20px;" id="authStatusBadge">Guest Mode</span>
            </div>
            <div class="search-container">
                <span style="color: #ff5000; font-size: 18px;">🔍</span>
                <input type="text" id="searchInput" placeholder="Search clothes, bicycles, machines, electronics from worldwide factories...">
                <button class="search-btn" onclick="searchCatalog()">SEARCH</button>
            </div>
        </div>

        <div class="category-grid">
            <div class="cat-item" onclick="filterCategory('All')">
                <div class="cat-icon">🌍</div>
                <span>All Worldwide</span>
            </div>
            <div class="cat-item" onclick="filterCategory('Electronics')">
                <div class="cat-icon">📱</div>
                <span>Electronics</span>
            </div>
            <div class="cat-item" onclick="filterCategory('Automotive')">
                <div class="cat-icon">🚲</div>
                <span>Automotive & Bikes</span>
            </div>
            <div class="cat-item" onclick="filterCategory('Fashion')">
                <div class="cat-icon">👔</div>
                <span>Clothes & Fashion</span>
            </div>
            <div class="cat-item" onclick="filterCategory('Industrial')">
                <div class="cat-icon">⚡</div>
                <span>Machines & Power</span>
            </div>
            <div class="cat-item" onclick="switchTab('tabSell', document.querySelectorAll('.nav-btn')[5])">
                <div class="cat-icon">📦</div>
                <span>Sell Product</span>
            </div>
        </div>

        <div class="main-layout">
            <div class="sidebar">
                <button class="nav-btn active" onclick="switchTab('tabGlobal', this)">🛍️ Worldwide Marketplace</button>
                <button class="nav-btn" onclick="switchTab('tabMining', this)">⛏️ 24H Mining & Daily Claim</button>
                <button class="nav-btn" onclick="switchTab('tabGames', this)">🎮 Play Games & Earn</button>
                <button class="nav-btn" onclick="switchTab('tabAds', this)">📺 Watch Videos & Earn</button>
                <button class="nav-btn" onclick="switchTab('tabWallet', this)">💰 My Earnings & Wallet</button>
                <button class="nav-btn" onclick="switchTab('tabLogin', this)">🔐 Login / Register Profile</button>
                <button class="nav-btn" onclick="switchTab('tabSell', this)">🛒 List & Sell Product</button>
            </div>

            <div class="content-area">
                <!-- TAB 1: MARKETPLACE -->
                <div id="tabGlobal" class="tab-pane active">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Worldwide Factory Direct Marketplace</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Browse clothes, bicycles, electronics, and machines from China, US, and worldwide factories. Click any item to select colors, options, and buy!</p>
                    <div id="productContainer" class="prod-grid"></div>
                </div>

                <!-- TAB 2: MINING & EARNINGS -->
                <div id="tabMining" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">24-Hour Mining & Daily Claim Rewards</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Earn money for yourself by mining every 24 hours and claiming your daily rewards. Use your earnings to buy goods!</p>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div class="card" style="text-align: center;">
                            <h3 style="color: #ff5000; margin-bottom: 10px;">⛏️ 24H Cloud Miner</h3>
                            <p style="font-size: 14px; color: #64748b; margin-bottom: 15px;">Earned Balance: <span id="miningBalanceDisplay" style="font-weight: bold; color: #16a34a;">0.000</span> Tokens</p>
                            <button class="btn-orange" onclick="startMining()">Start / Check 24H Mining</button>
                        </div>
                        <div class="card" style="text-align: center;">
                            <h3 style="color: #16a34a; margin-bottom: 10px;">🎁 Daily Reward Claim</h3>
                            <p style="font-size: 14px; color: #64748b; margin-bottom: 15px;">Claim your free daily streak bonus (+5.0 Tokens).</p>
                            <button class="btn-orange" style="background: #16a34a;" onclick="claimDaily()">Claim Daily Reward</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 3: PLAY GAMES -->
                <div id="tabGames" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Play Mini-Games & Earn Cash</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Play our rewards game to stack up your earnings for shopping.</p>
                    
                    <div class="card" style="text-align: center; max-width: 500px; margin: 0 auto;">
                        <h3 style="color: #ff5000; margin-bottom: 10px;">🎮 Tap-to-Earn Coin Game</h3>
                        <p style="font-size: 14px; color: #64748b; margin-bottom: 20px;">Tap the coin to earn +1.0 Token per tap!</p>
                        <div style="font-size: 70px; cursor: pointer; margin-bottom: 20px;" onclick="playGameReward()">🪙</div>
                        <p style="font-weight: bold; font-size: 16px;">Total Earned: <span id="gameScore" style="color: #16a34a;">0.000</span> Tokens</p>
                    </div>
                </div>

                <!-- TAB 4: WATCH VIDEOS -->
                <div id="tabAds" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Watch Videos & Earn Money</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Watch promotional videos to earn cash rewards directly to your account.</p>
                    
                    <div class="prod-grid">
                        <div class="prod-card" style="padding: 15px;">
                            <h3 style="font-size: 15px; color: #1e293b; margin-bottom: 8px;">📺 Global Factory Promo Video #1</h3>
                            <p style="font-size: 12px; color: #64748b; margin-bottom: 15px;">Reward: +3.0 Tokens upon completion.</p>
                            <button class="btn-orange" onclick="watchVideoReward('Global Factory Promo #1', 3.0)">Watch Video & Earn</button>
                        </div>
                        <div class="prod-card" style="padding: 15px;">
                            <h3 style="font-size: 15px; color: #1e293b; margin-bottom: 8px;">📺 International Sourcing Showcase #2</h3>
                            <p style="font-size: 12px; color: #64748b; margin-bottom: 15px;">Reward: +3.0 Tokens upon completion.</p>
                            <button class="btn-orange" onclick="watchVideoReward('International Sourcing Showcase #2', 3.0)">Watch Video & Earn</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 5: WALLET & EARNINGS -->
                <div id="tabWallet" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">My Earnings & Wallet</h2>
                    <div class="card" style="max-width: 500px; margin: 0 auto; text-align: center;">
                        <h3 style="color: #16a34a; font-size: 28px; margin-bottom: 10px;" id="walletBalance">0.000 Tokens</h3>
                        <p style="font-size: 14px; color: #64748b; margin-bottom: 20px;">Use your earned tokens directly when buying goods, or keep playing games and mining to earn more!</p>
                        <button class="btn-orange" onclick="switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[0])">Go Shopping Now</button>
                    </div>
                </div>

                <!-- TAB 6: LOGIN / REGISTER -->
                <div id="tabLogin" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">Account Login & Registration</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Log back in instantly using your User ID, or register a new account.</p>

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
                                <div class="form-group full">
                                    <label>Delivery Street Address</label>
                                    <input type="text" id="regAddress" placeholder="Street Address / City" required>
                                </div>
                                <button type="submit" class="btn-orange" style="margin-top: 15px;">Register Account</button>
                            </form>
                        </div>
                    </div>
                </div>

                <!-- TAB 7: SELL PRODUCT -->
                <div id="tabSell" class="tab-pane">
                    <h2 style="color: #1e293b; margin-bottom: 8px;">List & Sell Your Products</h2>
                    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Sell clothes, bicycles, machines, or items to worldwide buyers.</p>
                    <form onsubmit="postVendorProduct(event)" class="card">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Product Title</label>
                                <input type="text" id="sellTitle" placeholder="e.g. Electric Power Machine" required>
                            </div>
                            <div class="form-group">
                                <label>Price (USD)</label>
                                <input type="number" step="0.01" id="sellPrice" placeholder="50.00" required>
                            </div>
                            <div class="form-group">
                                <label>Category</label>
                                <select id="sellCategory">
                                    <option value="Automotive">Automotive & Bikes</option>
                                    <option value="Electronics">Electronics</option>
                                    <option value="Fashion">Fashion & Clothes</option>
                                    <option value="Industrial">Machines & Industrial</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Available Colors (comma separated)</label>
                                <input type="text" id="sellColors" placeholder="Red, Blue, Black" required>
                            </div>
                            <div class="form-group full">
                                <label>Available Sizes / Specs</label>
                                <input type="text" id="sellSizes" placeholder="Small, Medium, Large or Standard" required>
                            </div>
                        </div>
                        <button type="submit" class="btn-orange" style="margin-top: 15px;">Publish Product</button>
                    </form>
                </div>
            </div>
        </div>

        <!-- TEMU STYLE PRODUCT DETAIL & CHECKOUT MODAL -->
        <div id="productModal" class="modal-overlay">
            <div class="modal-box">
                <div id="modalEmoji" style="font-size: 60px; margin-bottom: 10px;">🛍️</div>
                <h3 id="modalTitle" style="color: #1e293b; margin-bottom: 6px; font-size: 18px;"></h3>
                <p id="modalSource" style="font-size: 12px; color: #64748b; margin-bottom: 10px;"></p>
                <div id="modalPrice" style="font-size: 20px; font-weight: bold; color: #ff5000; margin-bottom: 15px;"></div>

                <!-- Color Selection -->
                <div class="form-group" style="text-align: left;">
                    <label>Select Color / Style:</label>
                    <select id="selectColor"></select>
                </div>

                <!-- Size Selection -->
                <div class="form-group" style="text-align: left;">
                    <label>Select Size / Option:</label>
                    <select id="selectSize"></select>
                </div>

                <!-- Payment Method Choice -->
                <div class="form-group" style="text-align: left; margin-top: 10px;">
                    <label>Choose Payment Method:</label>
                    <select id="selectPaymentMethod">
                        <option value="bank_card">Pay with Bank Card / Backup Card</option>
                        <option value="earned_balance">Pay with Earned Tokens / Balance</option>
                    </select>
                </div>

                <!-- Bank Card Input (Shown only if bank card selected) -->
                <div class="form-group" id="bankCardGroup" style="text-align: left;">
                    <label>Enter Bank Card Number:</label>
                    <input type="text" id="modalBankCard" placeholder="4123 4567 8901 2345">
                </div>

                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <button class="btn-orange" style="background: #16a34a;" onclick="submitOrder()">Confirm & Buy Now</button>
                    <button class="btn-orange" style="background: #64748b;" onclick="closeModal()">Cancel</button>
                </div>
            </div>
        </div>

        <script>
            let currentUserId = localStorage.getItem('swiftbux_user_id') || null;
            let activeProduct = null;

            function checkAuth() {
                if(currentUserId) {
                    document.getElementById('authStatusBadge').innerText = "Logged In: " + currentUserId;
                    fetchUserData();
                } else {
                    document.getElementById('authStatusBadge').innerText = "Guest Mode (Mining & Earning Enabled)";
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
                    shipping_address: document.getElementById('regAddress').value,
                    city: "Lagos",
                    country: "Nigeria"
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
                    alert('Account created successfully! You received 10 free starting tokens.');
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
                    document.getElementById('walletBalance').innerText = data.earned_balance.toFixed(3) + " Tokens";
                    document.getElementById('miningBalanceDisplay').innerText = data.earned_balance.toFixed(3);
                    document.getElementById('gameScore').innerText = data.earned_balance.toFixed(3);
                }
            }

            async function loadCatalog(category = 'All') {
                const res = await fetch(`/api/products?category=${category}`);
                const items = await res.json();
                let html = '';
                items.forEach(i => {
                    html += `
                        <div class="prod-card" onclick='openProductModal(${JSON.stringify(i)})'>
                            <div class="prod-img-box">
                                <div class="prod-badge">${i.sold_count}</div>
                                <span>${i.image_emoji}</span>
                            </div>
                            <div class="prod-info">
                                <div class="prod-title">${i.title}</div>
                                <div class="prod-supplier">🏭 ${i.factory_source} (${i.origin})</div>
                                <div class="prod-price">💲${i.price_usd.toFixed(2)} USD</div>
                                <button class="btn-orange">Select Options & Buy</button>
                            </div>
                        </div>
                    `;
                });
                document.getElementById('productContainer').innerHTML = html;
            }

            function filterCategory(category) {
                loadCatalog(category);
                switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[0]);
            }

            async function searchCatalog() {
                const query = document.getElementById('searchInput').value.toLowerCase();
                if(!query) { loadCatalog('All'); return; }
                const res = await fetch('/api/products?category=All');
                const items = await res.json();
                const filtered = items.filter(i => i.title.toLowerCase().includes(query) || i.origin.toLowerCase().includes(query) || i.category.toLowerCase().includes(query));
                
                let html = '';
                filtered.forEach(i => {
                    html += `
                        <div class="prod-card" onclick='openProductModal(${JSON.stringify(i)})'>
                            <div class="prod-img-box">
                                <div class="prod-badge">${i.sold_count}</div>
                                <span>${i.image_emoji}</span>
                            </div>
                            <div class="prod-info">
                                <div class="prod-title">${i.title}</div>
                                <div class="prod-supplier">🏭 ${i.factory_source} (${i.origin})</div>
                                <div class="prod-price">💲${i.price_usd.toFixed(2)} USD</div>
                                <button class="btn-orange">Select Options & Buy</button>
                            </div>
                        </div>
                    `;
                });
                document.getElementById('productContainer').innerHTML = html || '<p style="padding:20px; color:#64748b;">No products found.</p>';
            }

            function openProductModal(item) {
                activeProduct = item;
                document.getElementById('modalEmoji').innerText = item.image_emoji;
                document.getElementById('modalTitle').innerText = item.title;
                document.getElementById('modalSource').innerText = `Source: ${item.factory_source} (${item.origin})`;
                document.getElementById('modalPrice').innerText = `$${item.price_usd.toFixed(2)} USD`;

                // Populate colors
                const colorSelect = document.getElementById('selectColor');
                colorSelect.innerHTML = '';
                item.colors.split(',').forEach(c => {
                    colorSelect.innerHTML += `<option value="${c.trim()}">${c.trim()}</option>`;
                });

                // Populate sizes
                const sizeSelect = document.getElementById('selectSize');
                sizeSelect.innerHTML = '';
                item.sizes.split(',').forEach(s => {
                    sizeSelect.innerHTML += `<option value="${s.trim()}">${s.trim()}</option>`;
                });

                document.getElementById('productModal').style.display = 'flex';
            }

            function closeModal() {
                document.getElementById('productModal').style.display = 'none';
            }

            async function submitOrder() {
                if(!currentUserId) {
                    alert('Please log in or register first to place your order!');
                    closeModal();
                    switchTab('tabLogin', document.querySelectorAll('.nav-btn')[5]);
                    return;
                }

                const color = document.getElementById('selectColor').value;
                const size = document.getElementById('selectSize').value;
                const paymentMethod = document.getElementById('selectPaymentMethod').value;
                const card = document.getElementById('modalBankCard').value;

                if(paymentMethod === 'bank_card' && !card) {
                    alert('Please enter your bank card or backup card number.');
                    return;
                }

                const res = await fetch('/api/buy-goods', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        user_id: currentUserId,
                        item_id: activeProduct.id,
                        color: color,
                        size: size,
                        payment_method: paymentMethod,
                        bank_card: card
                    })
                });
                const data = await res.json();
                if(res.ok) {
                    alert(`✅ Order Successful!\\nItem: ${activeProduct.title}\\nColor: ${color}, Size: ${size}\\nPaid via: ${paymentMethod === 'bank_card' ? 'Bank Card' : 'Earned Tokens'}\\nDoorstep delivery initiated.`);
                    closeModal();
                    fetchUserData();
                } else {
                    alert('Order Error: ' + data.detail);
                }
            }

            async function startMining() {
                if(!currentUserId) { alert('Please log in first!'); switchTab('tabLogin', document.querySelectorAll('.nav-btn')[5]); return; }
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
                if(!currentUserId) { alert('Please log in first!'); switchTab('tabLogin', document.querySelectorAll('.nav-btn')[5]); return; }
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
                if(!currentUserId) { alert('Please log in first!'); switchTab('tabLogin', document.querySelectorAll('.nav-btn')[5]); return; }
                const res = await fetch('/api/earn/game', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId})
                });
                const data = await res.json();
                fetchUserData();
            }

            async function watchVideoReward(title, reward) {
                if(!currentUserId) { alert('Please log in first!'); switchTab('tabLogin', document.querySelectorAll('.nav-btn')[5]); return; }
                const res = await fetch('/api/earn/video', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, reward: reward})
                });
                const data = await res.json();
                fetchUserData();
                alert(`📺 Watched "${title}"! Earned +${reward} Tokens.`);
            }

            async function postVendorProduct(e) {
                e.preventDefault();
                if(!currentUserId) { alert('Please log in first!'); switchTab('tabLogin', document.querySelectorAll('.nav-btn')[5]); return; }
                const payload = {
                    title: document.getElementById('sellTitle').value,
                    price_usd: parseFloat(document.getElementById('sellPrice').value),
                    category: document.getElementById('sellCategory').value,
                    colors: document.getElementById('sellColors').value,
                    sizes: document.getElementById('sellSizes').value,
                    seller: currentUserId
                };
                const res = await fetch('/api/sell', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(res.ok) {
                    alert('Product listed successfully to worldwide marketplace!');
                    loadCatalog('All');
                    switchTab('tabGlobal', document.querySelectorAll('.nav-btn')[0]);
                }
            }

            checkAuth();
            loadCatalog('All');
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
    shipping_address: str
    city: str
    country: str

@app.post("/api/register")
def register_user(user: UserReg, db: Session = Depends(get_db)):
    seed_temu_catalog(db)
    existing = db.query(TemuUser).filter(TemuUser.id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User ID already exists.")
    
    new_user = TemuUser(
        id=user.id, name=user.name, email=user.email, phone=user.phone,
        shipping_address=user.shipping_address, city=user.city, country=user.country,
        earned_balance=Decimal("15.000") # Starting bonus tokens
    )
    db.add(new_user)
    db.commit()
    return {"user_id": new_user.id}

@app.get("/api/login")
def login_user(user_id: str, db: Session = Depends(get_db)):
    seed_temu_catalog(db)
    user = db.query(TemuUser).filter(TemuUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"user_id": user.id}

@app.get("/api/user")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(TemuUser).filter(TemuUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"earned_balance": float(user.earned_balance)}

@app.get("/api/products")
def get_products(category: str = "All", db: Session = Depends(get_db)):
    seed_temu_catalog(db)
    query = db.query(TemuProduct)
    if category != "All":
        query = query.filter(TemuProduct.category == category)
    items = query.all()
    return [{
        "id": i.id, "title": i.title, "factory_source": i.factory_source, "origin": i.origin,
        "price_usd": float(i.price_usd), "colors": i.colors_json, "sizes": i.sizes_json,
        "category": i.category, "image_emoji": i.image_emoji, "sold_count": i.sold_count
    } for i in items]

@app.post("/api/buy-goods")
def buy_goods(data: dict, db: Session = Depends(get_db)):
    user = db.query(TemuUser).filter(TemuUser.id == data.get("user_id")).first()
    product = db.query(TemuProduct).filter(TemuProduct.id == data.get("item_id")).first()
    if not user or not product:
        raise HTTPException(status_code=404, detail="User or Product not found.")
    
    if data.get("payment_method") == "earned_balance":
        if user.earned_balance < product.price_usd:
            raise HTTPException(status_code=400, detail="Insufficient earned balance! Play games, mine, or watch videos to earn more, or pay with your bank card.")
        user.earned_balance -= product.price_usd
        db.commit()
    
    return {"status": "success"}

@app.post("/api/earn/mining")
def earn_mining(data: dict, db: Session = Depends(get_db)):
    user = db.query(TemuUser).filter(TemuUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.earned_balance += Decimal("12.500")
    db.commit()
    return {"message": "⛏️ 24H Mining reward claimed (+12.5 Tokens)!"}

@app.post("/api/earn/daily-claim")
def earn_daily(data: dict, db: Session = Depends(get_db)):
    user = db.query(TemuUser).filter(TemuUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.earned_balance += Decimal("5.000")
    db.commit()
    return {"message": "🎁 Daily reward successfully claimed (+5.0 Tokens)!"}

@app.post("/api/earn/game")
def earn_game(data: dict, db: Session = Depends(get_db)):
    user = db.query(TemuUser).filter(TemuUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.earned_balance += Decimal("1.000")
    db.commit()
    return {"status": "success"}

@app.post("/api/earn/video")
def earn_video(data: dict, db: Session = Depends(get_db)):
    user = db.query(TemuUser).filter(TemuUser.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    reward = Decimal(str(data.get("reward", 3.0)))
    user.earned_balance += reward
    db.commit()
    return {"status": "success"}

@app.post("/api/sell")
def sell_product(data: dict, db: Session = Depends(get_db)):
    new_item = TemuProduct(
        id="item_" + str(datetime.now().timestamp()),
        title=data.get("title"),
        factory_source="Vendor: " + data.get("seller"),
        origin="Global",
        price_usd=Decimal(str(data.get("price_usd"))),
        colors_json=data.get("colors", "Standard"),
        sizes_json=data.get("sizes", "Standard"),
        category=data.get("category"),
        image_emoji="🛍️",
        sold_count="New Listing"
    )
    db.add(new_item)
    db.commit()
    return {"status": "success"}