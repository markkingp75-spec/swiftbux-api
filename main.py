from fastapi import FastAPI, HTTPException, Depends
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftbux_secure.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBUser(Base):
    __tablename__ = "secure_users"
    id = Column(String, primary_key=True, index=True)
    balance = Column(Numeric(10, 2), default=Decimal("117.00"))
    currency = Column(String, default="NGN")
    referral_code = Column(String, unique=True, index=True)
    referred_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

# --- FASTAPI APP INITIALIZATION ---
app = FastAPI(title="SwiftBux API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES ---
@app.get("/")
def read_root():
    return {"message": "SwiftBux API is live and secure!"}

@app.post("/tasks/claim-reward")
async def claim_task_reward(
    user_id: str,
    task_id: str,
    base_ad_revenue: float,
    db: Session = Depends(get_db)
):
    try:
        base_value = Decimal(str(base_ad_revenue))
        
        # Simple balance lookup or creation
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if not user:
            user = DBUser(id=user_id, balance=Decimal("0.00"))
            db.add(user)
            db.commit()
            db.refresh(user)

        user.balance += base_value
        db.commit()
        
        return {
            "status": "success",
            "user_id": user_id,
            "new_balance": float(user.balance)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))