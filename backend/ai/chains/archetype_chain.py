from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from ai.prompts.archetype import ARCHETYPE_SYSTEM, ARCHETYPE_HUMAN


class ArchetypeOutput(BaseModel):
    archetype: str = Field(description="One of the 6 behavioral archetypes")
    confidence: float = Field(ge=0.0, le=1.0)
    key_signals: list[str] = Field(min_length=1, max_length=5)


def build_archetype_chain(llm: ChatOpenAI):
    parser = JsonOutputParser(pydantic_object=ArchetypeOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", ARCHETYPE_SYSTEM),
        ("human", ARCHETYPE_HUMAN),
    ])
    return prompt | llm | parser
