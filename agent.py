from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os

from intent_classifier import classify_intent
from rag import retrieve_context
from tools import mock_lead_capture

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.environ.get("GROQ_API_KEY")
)

class AgentState(TypedDict):
    messages: List[dict]
    intent: str
    collecting_lead: bool
    lead_data: dict
    lead_captured: bool
    response: str

SYSTEM_PROMPT = """You are an AI sales assistant for AutoStream, an AI-powered video editing SaaS for content creators.
Be friendly, helpful, and concise. When answering product questions, use the context provided.
When a user shows high buying intent, warmly acknowledge it and help collect their details.
Never ask for all fields at once — collect them one at a time in a natural conversation."""

def build_lc_messages(state: AgentState):
    lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in state["messages"]:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
    return lc_messages

def classify_node(state: AgentState) -> AgentState:
    last_user_msg = next(
        (m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), ""
    )
    intent = classify_intent(last_user_msg)
    return {**state, "intent": intent}

def respond_greeting(state: AgentState) -> AgentState:
    messages = build_lc_messages(state)
    response = llm.invoke(messages)
    return {**state, "response": response.content}

def respond_product_query(state: AgentState) -> AgentState:
    last_user_msg = next(
        (m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), ""
    )
    context = retrieve_context(last_user_msg)
    messages = [SystemMessage(content=SYSTEM_PROMPT + f"\n\nRelevant knowledge base context:\n{context}")]
    for msg in state["messages"]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    response = llm.invoke(messages)
    return {**state, "response": response.content}

def handle_lead_collection(state: AgentState) -> AgentState:
    lead = state.get("lead_data", {})
    last_user_msg = next(
        (m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), ""
    )
    if not state.get("collecting_lead") and state["intent"] == "high_intent":
        return {
            **state,
            "collecting_lead": True,
            "lead_data": lead,
            "response": "That's awesome! I'd love to get you set up. Could I grab your name first?"
        }
    if "name" not in lead:
        lead["name"] = last_user_msg.strip()
        return {**state, "lead_data": lead, "response": "Thanks! What's your email address?"}
    if "email" not in lead:
        lead["email"] = last_user_msg.strip()
        return {
            **state,
            "lead_data": lead,
            "response": "Perfect! Which creator platform do you mainly use? (e.g., YouTube, Instagram, TikTok)"
        }
    if "platform" not in lead:
        lead["platform"] = last_user_msg.strip()
        mock_lead_capture(lead["name"], lead["email"], lead["platform"])
        return {
            **state,
            "lead_data": lead,
            "lead_captured": True,
            "collecting_lead": False,
            "response": f"You're all set, {lead['name']}! Our team will reach out shortly. Anything else I can help with?"
        }
    return {**state, "response": "We already have your details! Anything else I can help with?"}

def router(state: AgentState) -> str:
    if state.get("collecting_lead"):
        return "lead_collection"
    intent = state.get("intent", "product_query")
    if intent == "casual_greeting":
        return "greeting"
    if intent == "high_intent":
        return "lead_collection"
    return "product_query"

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_node)
    graph.add_node("greeting", respond_greeting)
    graph.add_node("product_query", respond_product_query)
    graph.add_node("lead_collection", handle_lead_collection)
    graph.set_entry_point("classify")
    graph.add_conditional_edges("classify", router, {
        "greeting": "greeting",
        "product_query": "product_query",
        "lead_collection": "lead_collection",
    })
    graph.add_edge("greeting", END)
    graph.add_edge("product_query", END)
    graph.add_edge("lead_collection", END)
    return graph.compile()

agent_graph = build_graph()

def run_agent(user_message: str, conversation_history: List[dict]) -> dict:
    messages = conversation_history + [{"role": "user", "content": user_message}]
    collecting_lead = False
    lead_data = {}
    lead_captured = False
    for msg in conversation_history:
        if msg.get("role") == "_state":
            collecting_lead = msg.get("collecting_lead", False)
            lead_data = msg.get("lead_data", {})
            lead_captured = msg.get("lead_captured", False)
    state: AgentState = {
        "messages": [m for m in messages if m.get("role") != "_state"],
        "intent": "",
        "collecting_lead": collecting_lead,
        "lead_data": lead_data,
        "lead_captured": lead_captured,
        "response": "",
    }
    result = agent_graph.invoke(state)
    return {
        "response": result["response"],
        "intent": result["intent"],
        "collecting_lead": result["collecting_lead"],
        "lead_data": result["lead_data"],
        "lead_captured": result["lead_captured"],
    }
