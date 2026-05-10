CATEGORY_RULES: dict[str, list[str]] = {
    "Food & Dining":   ["ZOMATO", "SWIGGY", "RESTAURANT", "CAFE", "DOMINOS", "KFC", "MCDONALD", "PIZZA"],
    "Transport":       ["UBER", "OLA", "METRO", "RAPIDO", "PETROL", "FUEL", "AUTO", "CAB"],
    "Entertainment":   ["NETFLIX", "PRIME VIDEO", "SPOTIFY", "BOOKMYSHOW", "HOTSTAR", "DISNEY", "YOUTUBE"],
    "Shopping":        ["AMAZON", "FLIPKART", "MYNTRA", "H&M", "ZARA", "NYKAA", "MEESHO", "AJIO"],
    "Utilities":       ["ELECTRICITY", "WATER BILL", "GAS", "BROADBAND", "WIFI", "INTERNET", "AIRTEL", "JIO"],
    "Health":          ["PHARMACY", "APOLLO", "DOCTOR", "HOSPITAL", "CLINIC", "GYM", "FITNESS", "MEDPLUS"],
    "Rent/EMI":        ["RENT", "EMI", "HOME LOAN", "SOCIETY", "MAINTENANCE"],
    "Groceries":       ["BIGBASKET", "BLINKIT", "DMART", "ZEPTO", "SUPERMARKET", "GROFER", "INSTAMART"],
    "Income":          ["SALARY", "CREDIT", "NEFT RECEIVED", "IMPS RECEIVED", "FREELANCE", "PAYMENT RECEIVED"],
    "Savings":         ["FD", "RD", "MUTUAL FUND", "SIP", "INVESTMENT", "PPFAS", "PPF", "ZERODHA", "GROWW"],
}

DRS_WEIGHTS = {
    "budget_adherence":    0.23,
    "velocity_stability":  0.19,
    "savings_rate":        0.06,
    "recurring_coverage":  0.08,
    "emotional_spend":     0.19,
    "salary_gap":          0.25,
}

# Deterministic DRS tuning (component formulas — not model weights)
DRS_SAVINGS_MARGIN_TARGET = 0.27       # typical healthy monthly margin vs income → caps toward 1.0
DRS_SAVINGS_INVEST_BLEND = 0.30        # weight on Savings-category consistency vs raw margin
DRS_SAVINGS_INVEST_SCALE = 4.9         # maps investment debits / income to score contribution
DRS_SAVINGS_INVEST_CEILING = 0.62      # cap so disciplined investors rarely peg at 1.0 on this axis
DRS_VELOCITY_CV_CAP = 0.62             # cap CV when mapping to score (raw CV can explode on lumpy series)
DRS_VELOCITY_CV_SCALE = 1.12           # spending velocity coefficient-of-variation penalty
DRS_EMOTIONAL_RATIO_MULT = 2.95        # emotional debit share → score (higher mult = steeper penalty)
DRS_SALARY_GAP_PRESSURE_MULT = 5.0     # overspending pace vs month elapsed

RISK_SIGNAL_WEIGHTS = {
    "velocity_spike":   0.30,
    "salary_gap_risk":  0.25,
    "budget_overflow":  0.20,
    "emotional_spend":  0.15,
    "recurring_miss":   0.10,
}

ALERT_THRESHOLD = 0.55   # aggregate risk score that triggers alert
DRS_CHANGE_THRESHOLD = 5  # min DRS point change to generate AI explanation

ARCHETYPE_LABELS = [
    "stress_spender",
    "impulse_buyer",
    "planner",
    "social_spender",
    "anxiety_saver",
    "status_seeker",
]

URGENCY_LEVELS = ["low", "medium", "high"]

DEFAULT_BUDGET_RULES = {
    "Food & Dining":  12000,
    "Transport":       5000,
    "Entertainment":   3000,
    "Shopping":        8000,
    "Groceries":       6000,
    "Health":          3000,
}
