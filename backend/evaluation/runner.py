"""
Evaluation runner — tests AI prompt accuracy against a golden dataset.

Usage:
    cd backend
    python evaluation/runner.py
"""

import sys, os, asyncio, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from ai.orchestrator import AIOrchestrator

GOLDEN_DATASET = [
    {
        "id": "arch_001",
        "task": "archetype",
        "input": {
            "name": "Riya",
            "monthly_income": 85000,
            "top_categories": "Food & Dining, Shopping, Entertainment",
            "emotional_ratio": 38.0,
            "weekend_ratio": "2.1x weekday average",
            "cv": "0.61",
            "food_pct": 34.0,
            "velocity_spike": "Yes",
            "net_savings": "₹12,000",
        },
        "expected_archetype": "stress_spender",
        "acceptable": ["stress_spender", "social_spender"],
    },
    {
        "id": "arch_002",
        "task": "archetype",
        "input": {
            "name": "Priya",
            "monthly_income": 95000,
            "top_categories": "Groceries, Utilities, Health",
            "emotional_ratio": 4.0,
            "weekend_ratio": "0.9x weekday average",
            "cv": "0.12",
            "food_pct": 12.0,
            "velocity_spike": "No",
            "net_savings": "₹24,000",
        },
        "expected_archetype": "planner",
        "acceptable": ["planner", "anxiety_saver"],
    },
    {
        "id": "intv_001",
        "task": "intervention",
        "input": {
            "name": "Riya",
            "archetype": "stress_spender",
            "risk_type": "velocity_spike",
            "risk_score": 0.82,
            "drs_score": 38,
            "context": "Spending velocity 2.3x above average over last 7 days",
            "top_categories": "Food & Dining (₹9,200), Shopping (₹6,800), Entertainment (₹2,400)",
            "recent_pattern": "Emotional spend: ₹12,000, Top category: Food & Dining",
        },
        "must_have": ["urgency", "action", "reason", "savings_potential"],
        "expected_urgency": "high",
    },
]


async def run_evals():
    orchestrator = AIOrchestrator()
    results = []
    passed = 0

    for case in GOLDEN_DATASET:
        print(f"\n[{case['id']}] Running {case['task']} eval…")
        try:
            if case["task"] == "archetype":
                output = await orchestrator.classify_archetype(case["input"])
                got = output.get("archetype", "")
                ok = got in case["acceptable"]
                results.append({
                    "id": case["id"],
                    "passed": ok,
                    "expected": case["expected_archetype"],
                    "got": got,
                    "confidence": output.get("confidence", 0),
                })
                status = "✅ PASS" if ok else "❌ FAIL"
                print(f"  {status} — expected: {case['expected_archetype']}, got: {got}")

            elif case["task"] == "intervention":
                output = await orchestrator.generate_intervention(case["input"])
                missing = [k for k in case["must_have"] if k not in output or not output[k]]
                urgency_ok = output.get("urgency") == case.get("expected_urgency")
                ok = len(missing) == 0 and urgency_ok
                results.append({
                    "id": case["id"],
                    "passed": ok,
                    "missing_fields": missing,
                    "urgency_match": urgency_ok,
                    "title": output.get("title", ""),
                })
                status = "✅ PASS" if ok else "❌ FAIL"
                print(f"  {status} — urgency: {output.get('urgency')}, title: {output.get('title', '')[:50]}")

            if ok:
                passed += 1

        except Exception as e:
            print(f"  💥 ERROR: {e}")
            results.append({"id": case["id"], "passed": False, "error": str(e)})

    total = len(GOLDEN_DATASET)
    accuracy = round(passed / total * 100, 1) if total > 0 else 0

    print(f"\n{'─'*50}")
    print(f"EVALUATION COMPLETE: {passed}/{total} passed ({accuracy}%)")
    print(f"{'─'*50}\n")

    with open("evaluation/results.json", "w") as f:
        json.dump({"passed": passed, "total": total, "accuracy": accuracy, "results": results}, f, indent=2)

    return accuracy


if __name__ == "__main__":
    asyncio.run(run_evals())
