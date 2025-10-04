import streamlit as st
import openai
import pandas as pd
import numpy as np
import os
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from PIL import Image
from spacy.lang.en import English
from textblob import TextBlob
from cryptography.fernet import Fernet

# ---------------------------
# OpenAI API Key
# ---------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------------------------
# Lightweight NLP
# ---------------------------
nlp = English()
nlp.add_pipe("sentencizer")

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "positive", polarity
    elif polarity < 0:
        return "negative", polarity
    else:
        return "neutral", polarity

def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return keywords[:5]

# ---------------------------
# Persistent Vault (encrypted)
# ---------------------------
KEY = os.getenv("SECRET_KEY", Fernet.generate_key())
cipher = Fernet(KEY)

def save_to_vault(data, filename="vault.enc"):
    with open(filename, "wb") as f:
        f.write(cipher.encrypt(data.encode()))

def load_from_vault(filename="vault.enc"):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return cipher.decrypt(f.read()).decode()
    return ""

# ---------------------------
# Life Timeline Storage
# ---------------------------
if "timeline" not in st.session_state:
    st.session_state.timeline = []

def add_event(event):
    st.session_state.timeline.append({"event": event, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("EchoSoul")
mode = st.sidebar.radio("Mode", ["Chat", "Chat history", "Life timeline", "Vault", "Call", "About"])

# ---------------------------
# Chat Mode
# ---------------------------
if mode == "Chat":
    st.title("💬 Chat with EchoSoul")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_area("Message", key="chat_input")
    if st.button("Send"):
        if user_input.strip():
            sentiment, score = analyze_sentiment(user_input)
            keywords = extract_keywords(user_input)

            reply = f"I heard you. Your mood seems {sentiment} (score={score:.2f}). Keywords: {', '.join(keywords)}"

            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("assistant", reply))

    for role, msg in st.session_state.chat_history:
        st.markdown(f"**{role}:** {msg}")

# ---------------------------
# Chat History
# ---------------------------
elif mode == "Chat history":
    st.title("📜 Chat History")
    if "chat_history" in st.session_state:
        for role, msg in st.session_state.chat_history:
            st.markdown(f"**{role}:** {msg}")

# ---------------------------
# Life Timeline
# ---------------------------
elif mode == "Life timeline":
    st.title("📅 Life Timeline")
    new_event = st.text_input("Add an event")
    if st.button("Save Event"):
        if new_event.strip():
            add_event(new_event)
    for ev in st.session_state.timeline:
        st.markdown(f"- {ev['time']}: {ev['event']}")

# ---------------------------
# Vault
# ---------------------------
elif mode == "Vault":
    st.title("🔒 Personal Vault")
    secret = st.text_area("Write something private")
    if st.button("Save to Vault"):
        save_to_vault(secret)
        st.success("Saved securely!")
    if st.button("Load Vault"):
        st.write(load_from_vault())

# ---------------------------
# Call Mode (WebRTC)
# ---------------------------
elif mode == "Call":
    st.title("📞 Live Call with EchoSoul")
    webrtc_streamer(key="call", mode=WebRtcMode.SENDRECV)

# ---------------------------
# About
# ---------------------------
elif mode == "About":
    st.title("ℹ️ About EchoSoul")
    st.write("""
    EchoSoul is your AI companion that remembers your past, adapts to your personality, 
    recognizes emotions, and keeps a life timeline.  
    """)
