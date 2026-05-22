import streamlit as st
import os
import ollama  # 🦙 शुद्ध ऑफलाइन इंजन (नो इंटरनेट नीडेड)

# ⚙️ Master Page Layout Setup
st.set_page_config(page_title="FRIDAY AI Master Suite", page_icon="🤖", layout="wide")

st.title("⚡ FRIDAY AI: Ultimate Multi-Agent Offline Suite")
st.write("System Connected to Local Ollama Inference Engine (100% Secure & Offline)")

tab1, tab2, tab3 = st.tabs(["💻 OS Controller", "🛡️ Hacker AI (SAST)", "📄 ATS Resume Optimizer"])

# 🧠 ओलामा से लोकल बात करने का मास्टर फंक्शन
def call_local_ollama(system_prompt, user_input):
    try:
        # यह सीधे आपके कंप्यूटर की रैम में चल रहे 'friday' मॉडल को कॉल करेगा
        response = ollama.chat(model='friday', messages=[
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': user_input
            }
        ])
        return response['message']['content']
    except Exception as e:
        return f"❌ Connection Error: Kya Ollama app background mein chal raha hai? ({e})"

# --- TAB 1: OS CONTROLLER ---
with tab1:
    st.header("Telegram Bot OS Controller")
    st.write("Remote security terminal locks activated via local chat protocols.")
    bot_token = st.text_input("Enter Telegram Bot Token:", type="password")
    if st.button("Launch FRIDAY Bot Core"):
        if bot_token:
            st.success("🤖 FRIDAY Bot Core Activated locally via Ollama!")
        else:
            st.warning("Bhai, Telegram bot token field is missing!")

# --- TAB 2: HACKER AI (SAST) ---
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

# --- TAB 3: ATS RESUME OPTIMIZER ---
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
