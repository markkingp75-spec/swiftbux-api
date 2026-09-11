@app.post("/tasks/claim-reward")
async def claim_task_reward(
    user_id: uuid.UUID, 
    task_id: str, 
    base_ad_revenue: float, # What the ad network paid you for this view
    db: AsyncSession = Depends(get_db)
):
    try:
        base_value = Decimal(str(base_ad_revenue))
        
        # Calculate dynamic payout based on user's age/status
        user_payout, platform_cut = await calculate_task_payout(db, user_id, base_value)

        # Idempotency check & Ledger insertion
        # (Using the atomic ledger design from our previous setup)
        user_entry = LedgerEntry(
            user_id=user_id,
            amount=user_payout,
            type=TransactionType.EARN_TASK,
            reference_id=f"task_{task_id}"
        )
        
        db.add(user_entry)
        await db.commit()

        return {
            "status": "success", 
            "earned": float(user_payout),
            "promo_active": user_payout > (base_value * Decimal("0.40")) # Tell frontend if they are still boosted
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))