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

async def validate_business_plan_with_ai(business_plan: str) -> dict:
    """Validate business plan using OpenAI AI for intelligent scoring"""
    import json
    from lightrag.llm.openai import gpt_4o_mini_complete
    
    # Basic validation for obvious issues
    if not business_plan or len(business_plan.strip()) < 50:
        return {"is_valid": False, "score": 0, "reason": "Business plan is too short (minimum 50 characters required)"}
    
    # Check for PII patterns (keep this for security)
    pii_patterns = [
        r'\b\d{10}\b',  # 10-digit numbers (phone numbers)
        r'\b\d{12}\b',  # 12-digit numbers (Aadhaar)
        r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card numbers
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
    ]
    
    for pattern in pii_patterns:
        if re.search(pattern, business_plan):
            return {"is_valid": False, "score": 0, "reason": "Business plan contains personal information (phone numbers, emails, etc.)"}
    
    # Let AI handle all content validation - no keyword filtering
    
    # AI-powered validation
    try:
        prompt = f"""
You are a business plan validator for MSME loan applications. 

Rate this business plan on a scale of 0-5:
- 0: Not a business plan (personal content, irrelevant topics, inappropriate content)
- 1: Very poor business plan (vague, no financial details, unrealistic)
- 2: Poor business plan (basic idea, minimal planning, lacks details)
- 3: Acceptable business plan (clear business concept, some financial details, basic planning)
- 4: Good business plan (detailed planning, financial projections, clear strategy)
- 5: Excellent business plan (comprehensive, realistic projections, clear strategy, market analysis)

Business Plan: "{business_plan}"

Respond in JSON format only:
{{
    "score": number (0-5),
    "reason": "brief explanation of the score",
    "isValid": boolean (true if score >= 3)
}}
"""
        
        # Call OpenAI API
        response = await gpt_4o_mini_complete([prompt])
        
        # Parse the response
        try:
            result = json.loads(response)
            return {
                "is_valid": result.get("isValid", False),
                "score": result.get("score", 0),
                "reason": result.get("reason", "AI validation failed")
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {"is_valid": True, "score": 3, "reason": "Business plan appears valid"}
            
    except Exception as e:
        # Fallback in case of API errors
        return {"is_valid": True, "score": 3, "reason": f"AI validation unavailable: {str(e)}"}

async def compute_score(payload):
    breakdown = []
    score = 0

    annual_turnover = float(payload.get("annualTurnover", 0) or 0)
    net_profit = float(payload.get("netProfit", 0) or 0)
    loan_amount = float(payload.get("loanAmount", 0) or 0)

    profit_margin_pct = (net_profit / annual_turnover * 100) if annual_turnover > 0 else 0
    loan_to_turnover_pct = (loan_amount / annual_turnover * 100) if annual_turnover > 0 else 0

    # Validate business plan first using AI
    business_plan = payload.get("businessPlan", "") or ""
    business_plan_validation = await validate_business_plan_with_ai(business_plan)
    
    if not business_plan_validation["is_valid"]:
        return {
            "score0to10": 0,
            "band": "red",
            "breakdown": [{"reason": "Invalid business plan", "points": 0}],
            "derived": {
                "profit_margin_pct": round(profit_margin_pct, 2),
                "loan_to_turnover_pct": round(loan_to_turnover_pct, 2),
            },
            "error": "Sorry, please provide valid business plan",
            "validation_error": business_plan_validation["reason"],
            "ai_score": business_plan_validation["score"]
        }

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

    # Business plan scoring using AI validation
    ai_score = business_plan_validation["score"]
    plan_points = 0
    
    # Convert AI score (0-5) to points (0-2)
    if ai_score >= 5:
        plan_points = 2
        breakdown.append({"reason": f"Excellent business plan (AI score: {ai_score}/5)", "points": 2})
    elif ai_score >= 4:
        plan_points = 2
        breakdown.append({"reason": f"Good business plan (AI score: {ai_score}/5)", "points": 2})
    elif ai_score >= 3:
        plan_points = 1
        breakdown.append({"reason": f"Acceptable business plan (AI score: {ai_score}/5)", "points": 1})
    else:
        plan_points = 0
        breakdown.append({"reason": f"Poor business plan (AI score: {ai_score}/5)", "points": 0})

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
        },
        "ai_score": ai_score
    }
