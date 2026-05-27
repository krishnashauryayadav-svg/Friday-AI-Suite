import streamlit as st
import requests
import os
import subprocess
import webbrowser
import sounddevice as sd
from scipy.io import wavfile
import speech_recognition as sr
import pyttsx3
import gc  # RAM cleaner

# 🌐 Streamlit Page Config
st.set_page_config(page_title="Friday - Ultimate AI Core", page_icon="⚡", layout="centered")
st.title("⚡ FRIDAY: Multi-Tasking local AI")
st.caption("🚀 Optimized for 4GB RAM & i3 | Voice OS + Cybersecurity + ATS Core")
st.markdown("---")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "friday"  # Aapka quantized 3B model

# 🛠️ HELPER FUNCTION FOR TAB 2 & TAB 3
def call_local_ollama(system_instruction, user_content):
    full_prompt = f"System: {system_instruction}\nUser: {user_content}\nResponse:"
    payload = {"model": MODEL_NAME, "prompt": full_prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json().get('response', 'Bhai, model ne koi reply nahi diya.')
    except Exception as e:
        return f"⚠️ Ollama Connect Error: {str(e)}"

# 🔊 IMPROVED TEXT TO SPEECH (Sureeli Aawaaz)
def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if "zira" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 185)   
    engine.setProperty('volume', 1.0) 
    engine.say(text)
    engine.runAndWait()
    engine.stop()

# 🎙️ SOUNDDEVICE VOICE RECORDER
def listen_voice_without_pyaudio():
    fs = 16000  
    seconds = 4  
    st.toast("🎤 Listening... Boliye bhai! (4 Seconds)")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  
    st.toast("🔄 Processing your voice...")
    filename = "temp_voice.wav"
    wavfile.write(filename, fs, myrecording)
    del myrecording
    gc.collect()
    r = sr.Recognizer()
    text = None
    try:
        with sr.AudioFile(filename) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language="en-IN")
    except sr.UnknownValueError:
        st.error("Bhai, aapki aawaaz saaf nahi aayi. Dobara try karein.")
    except Exception as e:
        pass
    gc.collect()
    return text

SYSTEM_PROMPT = """
You are Friday, a voice-activated system automation AI. 
Keep your responses short, punchy, and friendly. Use Hinglish naturally.
If the user asks to open Google, search for something, or shutdown, you MUST respond in this exact format:
[CMD: command_type parameters] Your short response.

Examples:
- "search movies on google" -> [CMD: google movies] Sure bhai, searching for movies.
- "shutdown" -> [CMD: shutdown] Goodbye bhai, shutting down.
"""

# --- CREATE TABS INTERFACE ---
tab1, tab2, tab3 = st.tabs(["🎙️ Voice OS Controller", "🕵️‍♂️ Security Auditor (SAST)", "📊 ATS Resume Optimizer"])

# ==================== TAB 1: VOICE OS CONTROLLER ====================
with tab1:
    st.header("Jarvis Voice & Command Portal")
    
    # Session State for History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    col1, col2 = st.columns(2)
    with col2:
        voice_trigger = st.button("🎤 Click & Speak", use_container_width=True)

    user_input = None

    if voice_trigger:
        user_input = listen_voice_without_pyaudio()
        if user_input:
            st.success(f"🗣️ You said: {user_input}")

    text_input = st.chat_input("Type or click the Mic button...", key="voice_chat_input")
    if text_input and not user_input:
        user_input = text_input

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_prompt = f"{SYSTEM_PROMPT}\nUser: {user_input}\nFriday:"
            payload = {"model": MODEL_NAME, "prompt": full_prompt, "stream": False}
            
            try:
                response = requests.post(OLLAMA_URL, json=payload)
                ai_reply = response.json().get('response', '')
                clean_reply = ai_reply
                
                # --- COMMAND EXECUTION ---
                if "[CMD:" in ai_reply:
                    parts = ai_reply.split("]")
                    cmd_part = parts[0].replace("[CMD:", "").strip()
                    clean_reply = parts[1].strip() if len(parts) > 1 else ""
                    
                    if cmd_part.startswith("google"):
                        search_query = cmd_part.replace("google", "").strip()
                        if search_query:
                            webbrowser.open(f"https://google.com/search?q={search_query}")
                    elif cmd_part.startswith("shutdown"):
                        os.system("shutdown /s /t 10")
                
                response_placeholder.markdown(clean_reply)
                st.session_state.messages.append({"role": "assistant", "content": clean_reply})
                speak(clean_reply)
                
            except Exception as e:
                response_placeholder.markdown(f"⚠️ **Error:** {str(e)}")
        gc.collect()

# ==================== TAB 2: AI-POWERED VULNERABILITY FINDER ====================
with tab2:
    st.header("AI-Powered Vulnerability Finder (SAST)")
    uploaded_code = st.text_area("Paste your Code here (.py, .js, .sql):", height=200, key="hacker_code")
    if st.button("Scan Code for Vulnerabilities"):
        if uploaded_code:
            with st.spinner("🕵️‍♂️ Friday is auditing code layers locally..."):
                sys_prompt = "You are an elite Cybersecurity Auditor. Analyze the given code strictly for vulnerabilities like SQL Injection, Hardcoded API keys, or XSS. Provide explicit line numbers and fixes."
                reply = call_local_ollama(sys_prompt, uploaded_code)
                st.info(reply)
        else:
            st.warning("Please paste some code lines first, bhai!")

# ==================== TAB 3: ATS RESUME OPTIMIZER ====================
with tab3:
    st.header("ATS Resume Optimizer & Parser")
    resume_text = st.text_area("Paste Resume Text:", height=150, key="resume_text")
    job_desc = st.text_area("Paste Job Description (JD):", height=150, key="jd_text")
    if st.button("Match Resume with JD"):
        if resume_text and job_desc:
            with st.spinner("📊 Calculating compliance match indexes locally..."):
                sys_prompt = "You are an advanced ATS algorithm. Compare the Resume with the Job Description. Provide a match score percentage, list critical missing keywords, and suggest improvements."
                user_content = f"Resume:\n{resume_text}\n\nJD:\n{job_desc}"
                reply = call_local_ollama(sys_prompt, user_content)
                st.success(reply)
        else:
            st.warning("Both Resume and JD fields are mandatory, bhai!")

gc.collect()
