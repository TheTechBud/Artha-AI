from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from ai.prompts.intervention import INTERVENTION_SYSTEM, INTERVENTION_HUMAN


class InterventionOutput(BaseModel):
    title: str
    action: str
    reason: str
    urgency: str = Field(pattern="^(low|medium|high)$")
    savings_potential: float = Field(ge=0)


def build_intervention_chain(llm: ChatOpenAI):
    parser = JsonOutputParser(pydantic_object=InterventionOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", INTERVENTION_SYSTEM),
        ("human", INTERVENTION_HUMAN),
    ])
    return prompt | llm | parser
