# rule_engine.py
import re

TAG_RE = re.compile(r"<[^>]+>")

def sanitize_text(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", s)
    s = TAG_RE.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def compute_score(payload):
    breakdown = []
    score = 0

    annual_turnover = float(payload.get("annualTurnover", 0) or 0)
    net_profit = float(payload.get("netProfit", 0) or 0)
    loan_amount = float(payload.get("loanAmount", 0) or 0)

    profit_margin_pct = (net_profit / annual_turnover * 100) if annual_turnover > 0 else 0
    loan_to_turnover_pct = (loan_amount / annual_turnover * 100) if annual_turnover > 0 else 0

    # Udyam registration
    udyam = payload.get("udyamRegistration", False)
    if isinstance(udyam, str):
        udyam = udyam.strip().lower() in ("yes", "true", "1")
    if udyam:
        score += 2
        breakdown.append({"reason": "Udyam registration", "points": 2})

    # Profit margin points
    pm_points = 0
    if profit_margin_pct >= 10:
        pm_points = 3
    elif profit_margin_pct >= 5:
        pm_points = 2
    elif profit_margin_pct >= 2:
        pm_points = 1
    score += pm_points
    breakdown.append({"reason": f"Profit margin {profit_margin_pct:.1f}%", "points": pm_points})

    # Loan-to-turnover points
    lt_points = 0
    if loan_to_turnover_pct <= 10:
        lt_points = 2
    elif loan_to_turnover_pct <= 20:
        lt_points = 1
    elif loan_to_turnover_pct > 30:
        lt_points = -1
    score += lt_points
    breakdown.append({"reason": f"Loan-to-turnover {loan_to_turnover_pct:.1f}%", "points": lt_points})

    # Industry points
    industry = (payload.get("industryType") or "").strip().lower()
    ind_points = 1 if industry in ("manufacturing", "services") else 0
    score += ind_points
    breakdown.append({"reason": f"Industry ({industry})", "points": ind_points})

    # Business plan heuristics
    plan = sanitize_text(payload.get("businessPlan", "") or "")
    words = plan.split()
    plan_points = 0
    if len(words) >= 150:
        plan_points += 1
        breakdown.append({"reason": "Business plan length >=150 words", "points": 1})
    else:
        breakdown.append({"reason": "Business plan length <150 words", "points": 0})

    keywords = ["repay", "repayment", "cash flow", "cashflow", "forecast", "projection", "revenue", "repayment strategy"]
    if any(kw in plan.lower() for kw in keywords):
        plan_points += 1
        breakdown.append({"reason": "Mentions repayment/cash-flow/forecast keywords", "points": 1})
    else:
        breakdown.append({"reason": "No repayment/cash-flow/forecast keywords found", "points": 0})

    score += plan_points

    score = max(0, min(10, score))
    band = "red" if score <= 3 else "amber" if score <= 6 else "green" if score <= 8 else "emerald"

    return {
        "score0to10": score,
        "band": band,
        "breakdown": breakdown,
        "derived": {
            "profit_margin_pct": round(profit_margin_pct, 2),
            "loan_to_turnover_pct": round(loan_to_turnover_pct, 2),
        }
    }
