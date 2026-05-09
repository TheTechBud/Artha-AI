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
    "Savings":         ["FD", "RD", "MUTUAL FUND", "SIP", "INVESTMENT", "PPFAS", "ZERODHA"],
}

DRS_WEIGHTS = {
    "budget_adherence":    0.25,
    "velocity_stability":  0.20,
    "savings_rate":        0.20,
    "recurring_coverage":  0.15,
    "emotional_spend":     0.10,
    "salary_gap":          0.10,
}

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
