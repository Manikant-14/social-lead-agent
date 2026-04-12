import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.environ.get("GROQ_API_KEY")
)

INTENT_SYSTEM_PROMPT = """You are an intent classifier for a SaaS product chatbot.

Classify the user message into EXACTLY one of these three intents:
- casual_greeting     : small talk, hello, how are you
- product_query       : questions about features, pricing, policies, or how something works
- high_intent         : user wants to buy, sign up, start a trial, book a demo, or is clearly ready to convert

Respond with ONLY the intent label. No explanation. No punctuation."""

def classify_intent(user_message: str) -> str:
    messages = [
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]
    response = llm.invoke(messages)
    intent = response.content.strip().lower()
    valid_intents = {"casual_greeting", "product_query", "high_intent"}
    return intent if intent in valid_intents else "product_query"
