import streamlit as st
import requests

API_URL = "https://yummy-carrots-marry.loca.lt/chat"

st.set_page_config(
    page_title="AutoStream AI Assistant",
    page_icon="🎬",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0f1a 100%); }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

.hero-header { text-align: center; padding: 2rem 0 1rem 0; }
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00d4ff, #7b2ff7, #ff6b6b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}
.hero-sub { color: #6b7280; font-size: 0.95rem; font-weight: 300; letter-spacing: 0.05em; }

.footer-credit {
    text-align: center;
    color: #4b5563;
    font-size: 0.75rem;
    padding: 1rem 0 0.5rem 0;
    letter-spacing: 0.05em;
}
.footer-credit span {
    background: linear-gradient(90deg, #7b2ff7, #00d4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 600;
}

.intent-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.badge-high_intent { background: #14532d; color: #4ade80; border: 1px solid #16a34a; }
.badge-product_query { background: #1e3a5f; color: #60a5fa; border: 1px solid #2563eb; }
.badge-casual_greeting { background: #3b1f5e; color: #c084fc; border: 1px solid #7c3aed; }

.lead-captured-box {
    background: linear-gradient(135deg, #052e16, #14532d);
    border: 1px solid #16a34a;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    color: #4ade80;
    font-size: 0.9rem;
}

.stTextInput > div > div > input {
    border-radius: 10px !important;
    border: 1.5px solid #2a2a3f !important;
    background: #12121f !important;
    color: #e2e8f0 !important;
}
div[data-testid="stChatMessageContent"] p { color: #e2e8f0; line-height: 1.6; }

.sidebar-section {
    background: #12121f;
    border: 1px solid #1e1e35;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.7rem;
}
.sidebar-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    color: #7b2ff7;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-header">
    <div class="hero-title">🎬 AutoStream AI</div>
    <div class="hero-sub">Your intelligent video editing assistant · Powered by Groq (gpt-oss-120b) + RAG</div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {"collecting_lead": False, "lead_data": {}, "lead_captured": False}
if "last_intent" not in st.session_state:
    st.session_state.last_intent = None

with st.sidebar:
    st.markdown('<div style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;color:#7b2ff7">🎬 AutoStream</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div class="sidebar-section"><div class="sidebar-title">📊 Session Status</div>', unsafe_allow_html=True)
    if st.session_state.last_intent:
        badge_class = f"badge-{st.session_state.last_intent}"
        st.markdown(f'<span class="intent-badge {badge_class}">{st.session_state.last_intent.replace("_", " ")}</span>', unsafe_allow_html=True)

    state = st.session_state.agent_state
    if state["lead_captured"]:
        ld = state["lead_data"]
        st.markdown(f"""
        <div class="lead-captured-box">
            ✅ <strong>Lead Captured</strong><br>
            👤 {ld.get('name','')}<br>
            📧 {ld.get('email','')}<br>
            🎥 {ld.get('platform','')}
        </div>""", unsafe_allow_html=True)
    elif state["collecting_lead"]:
        st.info("🔄 Collecting lead details...")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section"><div class="sidebar-title">💬 Try These</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="color:#9ca3af; font-size:0.82rem; line-height:1.9">
    • Hi, tell me about AutoStream<br>
    • What's the difference between Basic and Pro?<br>
    • Do you have a free trial?<br>
    • I want to sign up for the Pro plan<br>
    • What's your refund policy?
    </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_state = {"collecting_lead": False, "lead_data": {}, "lead_captured": False}
        st.session_state.last_intent = None
        st.rerun()

    st.markdown("""
    <div style="margin-top:2rem; text-align:center; color:#374151; font-size:0.72rem; line-height:1.8">
        Built by<br>
        <span style="background:linear-gradient(90deg,#7b2ff7,#00d4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700;font-size:0.85rem">Manikant</span><br>
        ML Intern Assignment<br>ServiceHive × Inflx
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("👋 Hey there! I'm AutoStream's AI assistant. I can help you with pricing, features, or get you started with a free trial. What can I help you with today?")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask me anything about AutoStream..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    history_for_api = []
    for m in st.session_state.messages[:-1]:
        history_for_api.append({"role": m["role"], "content": m["content"]})


    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(API_URL, json={
                    "message": user_input,
                    "history": history_for_api,
                    "agent_state": st.session_state.agent_state,
                }, timeout=120)
                if resp.status_code != 200:
                    raise ValueError(f"Backend error {resp.status_code}: {resp.text[:300]}")
                data = resp.json()
                bot_reply = data["response"]
                st.session_state.last_intent = data.get("intent")
                st.session_state.agent_state = {
                    "collecting_lead": data.get("collecting_lead", False),
                    "lead_data": data.get("lead_data", {}),
                    "lead_captured": data.get("lead_captured", False),
                }
            except Exception as e:
                bot_reply = f"⚠️ Could not reach the backend. Make sure `main.py` is running.\n\nError: {e}"

        st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    st.rerun()

st.markdown("""
<div class="footer-credit">
    🎬 AutoStream AI · Developed by <span>Manikant</span> · ML Intern Assignment @ ServiceHive
</div>
""", unsafe_allow_html=True)
