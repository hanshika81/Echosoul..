import streamlit as st
import openai
import os
import json
import datetime
import pandas as pd
from textblob import TextBlob
from gtts import gTTS
from io import BytesIO
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
from dotenv import load_dotenv

# ==============================
# SETUP
# ==============================
load_dotenv()
st.set_page_config(page_title="EchoSoul", layout="wide")

if "memory" not in st.session_state:
    st.session_state.memory = []
if "timeline" not in st.session_state:
    st.session_state.timeline = []
if "mode" not in st.session_state:
    st.session_state.mode = "Chat"

# Load API key
openai.api_key = st.session_state.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# ==============================
# UTILITY FUNCTIONS
# ==============================
def analyze_emotion(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.2:
        emotion = "positive"
    elif polarity < -0.2:
        emotion = "negative"
    else:
        emotion = "neutral"
    return emotion, round(polarity, 2)

def save_to_memory(user_input, response):
    st.session_state.memory.append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_input,
        "assistant": response
    })

def add_to_timeline(event):
    st.session_state.timeline.append({
        "event": event,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def generate_response(prompt):
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"[Error: {e}]"

def speak_text(text):
    tts = gTTS(text)
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    st.audio(audio_bytes.getvalue(), format="audio/mp3")

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("EchoSoul")
st.sidebar.caption("Adaptive personal companion — chat, call, remember.")

mode = st.sidebar.radio(
    "Mode",
    ["Chat", "Chat history", "Life timeline", "Vault", "Call", "About"]
)
st.session_state.mode = mode

st.sidebar.subheader("Settings")
st.sidebar.text_input("OpenAI API Key (session only)", key="OPENAI_API_KEY", type="password")

if st.sidebar.button("Clear chat history"):
    st.session_state.memory = []

# ==============================
# MAIN INTERFACE
# ==============================
st.title("🧠 Chat with EchoSoul")

if mode == "Chat":
    user_input = st.text_area("Message", placeholder="Say something...")

    if st.button("Send"):
        if user_input.strip():
            emotion, score = analyze_emotion(user_input)
            response = generate_response(
                f"You are EchoSoul, a compassionate AI companion. The user feels {emotion}. Respond warmly to this: {user_input}"
            )
            save_to_memory(user_input, response)
            add_to_timeline(f"User expressed a {emotion} message: '{user_input}'")

            st.markdown(f"**user:** {user_input}")
            st.markdown(f"**assistant:** {response}")
            st.markdown(f"_Emotion detected: {emotion} (score={score})_")
            speak_text(response)

elif mode == "Chat history":
    st.subheader("🗂️ Chat History")
    if st.session_state.memory:
        for m in st.session_state.memory:
            st.markdown(f"**{m['timestamp']}** — 👤 *You:* {m['user']}")
            st.markdown(f"🤖 *EchoSoul:* {m['assistant']}")
            st.divider()
    else:
        st.info("No chat history yet.")

elif mode == "Life timeline":
    st.subheader("📜 Life Timeline")
    if st.session_state.timeline:
        df = pd.DataFrame(st.session_state.timeline)
        st.table(df)
    else:
        st.info("No life events recorded yet.")

elif mode == "Vault":
    st.subheader("🔐 Memory Vault")
    if st.session_state.memory:
        json_data = json.dumps(st.session_state.memory, indent=4)
        st.download_button("Export Memory", json_data, "echosoul_memory.json")
    else:
        st.info("Nothing to export yet.")

elif mode == "Call":
    st.subheader("📞 EchoSoul Voice (Agora/VoIP placeholder)")
    st.write("This section enables real-time VoIP. For now, it uses Streamlit WebRTC.")

    rtc_config = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    webrtc_streamer(
        key="call",
        mode="sendonly",
        rtc_configuration=rtc_config,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True
    )
    st.success("Voice streaming active (prototype mode).")

elif mode == "About":
    st.markdown("""
    ### About EchoSoul
    EchoSoul is your adaptive AI companion built to:
    - Remember your past interactions
    - Adapt tone & style over time
    - Understand emotional context
    - Create a life timeline of memories
    - Offer real-time voice (VoIP-ready)
    """)
