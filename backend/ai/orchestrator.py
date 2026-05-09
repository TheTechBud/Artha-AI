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
        try:
            result = await self.chains["archetype"].ainvoke(context)
            logger.info(f"Archetype classified: {result.get('archetype')}")
            return result
        except Exception as e:
            logger.error(f"Archetype classification failed: {e}")
            return FALLBACK_ARCHETYPE

    async def generate_narrative(self, context: dict) -> str:
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
