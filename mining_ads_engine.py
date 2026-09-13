from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class UserMiningState(Base):
    __tablename__ = "user_mining_states"
    user_id = Column(String, primary_key=True, index=True)
    mining_active = Column(String, default="false") # "true" or "false"
    mining_start_time = Column(DateTime, nullable=True)
    mined_balance = Column(Numeric(10, 3), default=Decimal("0.000"))
    last_daily_claim = Column(DateTime, nullable=True)

class AdCampaignRecord(Base):
    __tablename__ = "ad_campaign_records"
    id = Column(String, primary_key=True, index=True)
    advertiser_id = Column(String)
    title = Column(String)
    target_link = Column(String)
    reward_amount = Column(Numeric(10, 3))
    views_count = Column(Numeric(10, 0), default=Decimal("0"))

class MiningAdsEngineController:
    """Autonomous controller handling 24-hour mining, daily reward claims, and ad network promotion."""
    
    @staticmethod
    def start_mining_session(user_id: str, state: UserMiningState):
        now = datetime.now(timezone.utc)
        if state.mining_active == "true":
            # Check if 24 hours have elapsed
            if state.mining_start_time and (now - state.mining_start_time) >= timedelta(hours=24):
                state.mined_balance += Decimal("12.500") # 24-hour yield reward
                state.mining_start_time = now
                return {"status": "completed_and_restarted", "mined_balance": float(state.mined_balance)}
            else:
                remaining = 24 - ((now - state.mining_start_time).total_seconds() / 3600)
                return {"status": "already_mining", "hours_remaining": round(remaining, 1)}
        else:
            state.mining_active = "true"
            state.mining_start_time = now
            return {"status": "started", "mined_balance": float(state.mined_balance)}

    @staticmethod
    def claim_daily_reward(user_id: str, state: UserMiningState):
        now = datetime.now(timezone.utc)
        if state.last_daily_claim:
            last_claim_date = state.last_daily_claim.date()
            if last_claim_date == now.date():
                return {"status": "already_claimed", "message": "Daily reward already claimed today. Come back tomorrow!"}
        
        state.last_daily_claim = now
        daily_bonus = Decimal("5.000")
        state.mined_balance += daily_bonus
        return {"status": "success", "reward": float(daily_bonus), "mined_balance": float(state.mined_balance)}

    @staticmethod
    def get_whitepaper_text():
        return """
        SWIFTBUX GLOBAL AUTONOMOUS WHITE PAPER (v3.0)
        ------------------------------------------------------------------
        1. EXECUTIVE SUMMARY:
        SwiftBux is a pioneering decentralized cross-border trade, mining, and advertising ecosystem. It bridges global manufacturing hubs in China (1688), USA, and India directly with emerging consumer markets in Nigeria and worldwide.
        
        2. 24-HOUR MINING & REWARD MECHANISM:
        Users participate in daily platform activities, initiating 24-hour automated mining cycles that reward engagement while driving network liquidity and ad impressions.
        
        3. AUTONOMOUS MIDDLEMAN & ESCROW:
        The platform acts as a secure middleman, holding user funds in an automated escrow ledger until foreign factories confirm inspection and cargo dispatch to the registered doorstep address.
        
        4. ADVERTISING & PROMOTION PROTOCOL:
        Merchants publish ad campaigns across social networks. Users view promotions to earn rewards, creating a viral marketing loop backed by the autonomous AI controller.
        """