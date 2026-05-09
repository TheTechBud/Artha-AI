from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ai.prompts.narrative import NARRATIVE_SYSTEM, NARRATIVE_HUMAN


def build_narrative_chain(llm: ChatOpenAI):
    prompt = ChatPromptTemplate.from_messages([
        ("system", NARRATIVE_SYSTEM),
        ("human", NARRATIVE_HUMAN),
    ])
    # Narrative is plain text, no JSON parsing needed
    return prompt | llm | StrOutputParser()
