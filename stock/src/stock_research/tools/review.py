"""Objective next-session outcomes and historical memory selection."""

from stock_research.models.prediction import Outcome


def evaluate(row, snapshot):
    """Compare to the FIRST completed later bar, never a convenient later price."""
    if row.snapshot.stock != snapshot.stock or row.snapshot.date >= snapshot.date:
        return None
    original = row.snapshot.technical.bars[-1].bar_time
    if not any(b.bar_time == original for b in snapshot.technical.bars):
        return None
    later = [b for b in snapshot.technical.bars if b.bar_time > original]
    if not later:
        return None
    target = min(later, key=lambda b: b.bar_time)
    change = target.close / row.snapshot.technical.current_price - 1
    prediction = row.master.prediction
    verdict = "INCONCLUSIVE"
    if prediction != "INSUFFICIENT_EVIDENCE":
        success = (
            (prediction == "UP" and change > 0.001)
            or (prediction == "DOWN" and change < -0.001)
            or (prediction == "FLAT" and abs(change) <= 0.001)
        )
        verdict = "CORRECT" if success else "INCORRECT"
    return Outcome(
        prediction_id=row.prediction_id,
        evaluated_at=snapshot.date,
        actual_price=target.close,
        actual_return=change,
        verdict=verdict,
        target_bar_time=target.bar_time,
    )


def learning_packet(rows, stock, as_of):
    """Only evaluated historical outcomes are eligible; future feedback is excluded."""
    eligible = [
        r
        for r in rows
        if r.snapshot.stock == stock
        and r.snapshot.date < as_of
        and r.outcome
        and r.outcome.evaluated_at <= as_of
    ]
    eligible = sorted(eligible, key=lambda r: r.snapshot.date)[-30:]
    scored = [r for r in eligible if r.outcome.verdict != "INCONCLUSIVE"]
    return {
        "stock": stock,
        "evaluated_count": len(scored),
        "accuracy": sum(r.outcome.verdict == "CORRECT" for r in scored) / len(scored)
        if scored
        else None,
        "history": [
            {
                "prediction_id": str(r.prediction_id),
                "date": r.snapshot.date.isoformat(),
                "master": r.master.model_dump(),
                "outcome": r.outcome.model_dump(mode="json"),
                "critique": r.critique.model_dump(mode="json") if r.critique else None,
            }
            for r in eligible
        ],
    }
