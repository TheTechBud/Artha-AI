import os
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from ai.chains.archetype_chain import build_archetype_chain
from ai.chains.narrative_chain import build_narrative_chain
from ai.chains.intervention_chain import build_intervention_chain
from ai.prompts.explainability import EXPLAIN_SYSTEM, EXPLAIN_HUMAN
from observability.logger import get_logger

logger = get_logger("ai.orchestrator")

FALLBACK_ARCHETYPE = {
    "archetype": "stress_spender",
    "confidence": 0.5,
    "key_signals": ["High weekend spend", "Food & Dining spike", "Late night transactions"],
}

FALLBACK_INTERVENTION = {
    "title": "Review weekend spending patterns",
    "action": "Set a ₹2,000 limit on Zomato/Swiggy orders for the next 7 days",
    "reason": "Your spending spikes on weekends, often driven by stress or social pressure rather than hunger",
    "urgency": "medium",
    "savings_potential": 3000.0,
}


class AIOrchestrator:
    def __init__(self):
        model = os.getenv("OPENAI_MODEL", "gpt-4o")
        model_fast = os.getenv("OPENAI_MODEL_FAST", "gpt-4o-mini")
        api_key = os.getenv("OPENAI_API_KEY")
        self.ai_enabled = bool(api_key and api_key.strip())

        self.llm = None
        self.llm_narrative = None
        self.llm_fast = None
        self.openai_async = None
        self.chains = {}

        if not self.ai_enabled:
            logger.warning(
                "OPENAI_API_KEY is missing. AI features are running in fallback mode; "
                "deterministic analytics remain fully enabled."
            )
            return

        self.llm = ChatOpenAI(model=model, temperature=0.3)
        self.llm_narrative = ChatOpenAI(model=model, temperature=0.7)
        self.llm_fast = ChatOpenAI(model=model_fast, temperature=0.2)
        self.openai_async = AsyncOpenAI()

        self.chains = {
            "archetype": build_archetype_chain(self.llm_fast),      # cheaper model for classification
            "narrative": build_narrative_chain(self.llm_narrative),  # creative model for narrative
            "intervention": build_intervention_chain(self.llm),      # balanced for interventions
        }

    async def classify_archetype(self, context: dict) -> dict:
        if not self.ai_enabled:
            logger.warning("AI disabled: using deterministic fallback archetype classification")
            return self._deterministic_archetype(context)
        try:
            result = await self.chains["archetype"].ainvoke(context)
            logger.info(f"Archetype classified: {result.get('archetype')}")
            return result
        except Exception as e:
            logger.error(f"Archetype classification failed: {e}")
            return FALLBACK_ARCHETYPE

    async def generate_narrative(self, context: dict) -> str:
        if not self.ai_enabled:
            logger.warning("AI disabled: using narrative template fallback")
            return self._fallback_narrative(context)
        try:
            result = await self.chains["narrative"].ainvoke(context)
            logger.info("Narrative generated successfully")
            return result
        except Exception as e:
            logger.error(f"Narrative generation failed: {e}")
            return (
                "We weren't able to generate your personalized narrative right now. "
                "Your financial data looks active — check back shortly for your weekly summary."
            )

    async def generate_intervention(self, context: dict) -> dict:
        if not self.ai_enabled:
            logger.warning("AI disabled: using fallback intervention text")
            return self._fallback_intervention(context)
        try:
            result = await self.chains["intervention"].ainvoke(context)
            logger.info(f"Intervention generated: urgency={result.get('urgency')}")
            return result
        except Exception as e:
            logger.error(f"Intervention generation failed: {e}")
            return FALLBACK_INTERVENTION

    async def explain_drs(self, name: str, prev_score: float, current_score: float, components: dict) -> str:
        """Direct OpenAI call — no chain needed for this simple task."""
        delta = current_score - prev_score
        components_str = ", ".join(f"{k}: {v:.2f}" for k, v in components.items())
        if not self.ai_enabled:
            logger.warning("AI disabled: using deterministic DRS explanation fallback")
            direction = "improved" if delta > 0 else "dropped"
            return (
                f"Your Decision Readiness Score {direction} by {abs(delta):.0f} points. "
                f"Biggest signals now are: {components_str}."
            )
        try:
            response = await self.openai_async.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                messages=[
                    {"role": "system", "content": EXPLAIN_SYSTEM},
                    {"role": "user", "content": EXPLAIN_HUMAN.format(
                        name=name,
                        prev_score=prev_score,
                        current_score=current_score,
                        delta=delta,
                        components=components_str,
                    )},
                ],
                max_tokens=150,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"DRS explanation failed: {e}")
            direction = "improved" if delta > 0 else "dropped"
            return f"Your Decision Readiness Score {direction} by {abs(delta):.0f} points since last calculation."

    def _deterministic_archetype(self, context: dict) -> dict:
        emotional_ratio = float(context.get("emotional_ratio", 0) or 0)
        food_pct = float(context.get("food_pct", 0) or 0)
        velocity_spike = str(context.get("velocity_spike", "No")).strip().lower() == "yes"

        archetype = "planner"
        key_signals = [
            "Deterministic fallback mode active",
            "Pattern inferred from rule-based analytics",
        ]

        if emotional_ratio >= 30 or (velocity_spike and food_pct >= 25):
            archetype = "stress_spender"
            key_signals = ["High emotional spend ratio", "Food/velocity spikes detected"]
        elif food_pct >= 35:
            archetype = "social_spender"
            key_signals = ["Food & dining concentration is high", "Weekend-linked spending pattern"]
        elif velocity_spike:
            archetype = "impulse_buyer"
            key_signals = ["Spending velocity volatility detected", "Recent pace exceeds baseline"]

        return {
            "archetype": archetype,
            "confidence": 0.6,
            "key_signals": key_signals,
        }

    def _fallback_narrative(self, context: dict) -> str:
        name = context.get("name", "there")
        drs_score = context.get("drs_score", "N/A")
        drs_label = context.get("drs_label", "Current")
        top_categories = context.get("top_categories", "No category data yet")
        risk_flags = context.get("risk_flags", "No critical risk flags")
        return (
            f"{name}, your current Decision Readiness Score is {drs_score} ({drs_label}). "
            f"Your spending is currently concentrated in: {top_categories}.\n\n"
            f"Risk view: {risk_flags}. Keep your spending pace steady and prioritize planned expenses first.\n\n"
            "Next step for this week: choose one controllable category and set a hard spending cap before weekend spending starts."
        )

    def _fallback_intervention(self, context: dict) -> dict:
        risk_type = str(context.get("risk_type", "spending_risk")).replace("_", " ")
        return {
            "title": f"Take control of {risk_type}",
            "action": "Set a 7-day cap for your top spending category and track every debit above ₹500.",
            "reason": "Your recent deterministic risk signals show elevated pressure in current spending behavior.",
            "urgency": "medium",
            "savings_potential": 2500.0,
        }
