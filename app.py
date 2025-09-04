import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from db import init_db, save_message, get_history, clear_history

# ✅ Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Initialize DB
init_db()

# Choose a Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="🏗️ Construction Chatbot", layout="centered")
st.title("🏗️ Construction Chatbot ")
st.write("Ask me anything about **construction**. I will only answer construction-related queries.")

# Sidebar controls
if st.sidebar.button("🗑️ Clear Chat History"):
    clear_history()
    st.session_state.messages = [
    {
        "role": "system",
        "content": (
            "You are ConstructBot, an expert AI assistant specializing exclusively in construction, building, "
            "architecture, engineering, and related fields.\n\n"
            "IMPORTANT RESTRICTIONS:\n"
            "- You ONLY answer questions related to construction, building, architecture, civil engineering, "
            "structural engineering, construction materials, building codes, safety protocols, project management "
            "in construction, tools, equipment, and similar topics.\n"
            "- If asked about anything unrelated to construction (like cooking, sports, general knowledge, etc.), "
            "politely decline and redirect to construction topics.\n"
            "- Always provide practical, accurate, and safety-conscious advice.\n"
            "- Include relevant building codes and safety considerations when applicable.\n"
            "- Be helpful and detailed in your construction-related responses.\n\n"
            "Response format: Provide clear, actionable advice with safety considerations prominently featured."
        )
    }
]

st.rerun()


# ✅ Load messages from DB if session_state is empty
if "messages" not in st.session_state:
    db_history = get_history()
    if db_history:
        st.session_state.messages = [{"role": role, "content": msg} for role, msg, _ in db_history]
    else:
        st.session_state.messages = [
            {"role": "system", "content": "You are a construction-domain assistant. Only answer questions related to construction (materials, BOQ, codes, contracts, safety, methods, etc.). If the question is outside construction, reply strictly with: 'I can answer only construction-related queries.'"}
        ]

# ✅ Show chat history
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# ✅ Chat input
if user_input := st.chat_input("Type your construction query..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message("user", user_input)  # Save to DB
    st.chat_message("user").markdown(user_input)

    # Format history for Gemini
    conversation = "\n".join(
        [f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages]
    )

    response = model.generate_content(conversation)
    reply = response.text

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_message("assistant", reply)  # Save to DB
    st.chat_message("assistant").markdown(reply)
