import re
import time
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
from google import genai

MODEL = "gemini-3.5-flash-lite"
DB_FILE = "checks.db"

st.set_page_config(page_title="Internship Scam Checker", page_icon="🛡️")

# (pattern, points, reason)
RULES = [
    (r"registration fee|security deposit|refundable|processing fee|pay\s*(rs|₹|inr)?\s*\d+|₹\s*\d+\s*(fee|only)|training fee|kit fee",
     4, "Fee / payment is being asked (real companies never charge for a job or internship)"),
    (r"performance[- ]based|up to\s*(rs|₹|inr)?\s*[\d,]+|incentive based",
     2, "Stipend is 'up to' or 'performance-based' (not a fixed amount)"),
    (r"welcome letter|offer letter.*(pay|fee)|enrol+ment|enroll|program fee|course fee|bootcamp",
     3, "Looks like a paid course / program funnel, not a real internship"),
    (r"whatsapp|telegram|dm me|contact on|call us",
     2, "Asks you to move to WhatsApp / Telegram / phone"),
    (r"limited seats|hurry|last date today|urgent|immediately|confirm your seat",
     2, "Pressure tactics (hurry, limited seats)"),
    (r"aadhaar|aadhar|\bpan\b|otp|bank account|password|card number",
     4, "Asks for sensitive details (Aadhaar / PAN / OTP / bank)"),
    (r"congratulations.*selected|you are selected|you have been selected",
     1, "'You are selected' message without any interview"),
    (r"guaranteed (job|placement)|100% placement|earn\s*(rs|₹)?\s*\d+.*(per day|daily|weekly)",
     3, "Unrealistic promise (guaranteed job / easy daily earning)"),
]
SAFE = [
    (r"fixed stipend|careers\.|official website|interview",
     "Mentions an interview / official site / fixed stipend (good sign)"),
]

def ai_explain(text, score, flags, language):
    prompt = (
        "You help Indian college students spot fake internship/job messages. "
        f"Our rule checker gave this message a scam score of {score}/10 with red flags: {flags}. "
        f"Read the message and explain in simple {language} (max 5 short bullet points) "
        "why it is or is not safe, and what the student should do. "
        "Never ask for personal data. Message:\n" + text
    )
    for attempt in range(2):
        try:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            resp = client.models.generate_content(model=MODEL, contents=prompt)
            return resp.text
        except Exception:
            time.sleep(1.5)
    return None

# ---------- Database (SQLite) ----------
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS checks ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "created_at TEXT, verdict TEXT, score INTEGER, language TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS flag_hits ("
        "check_id INTEGER, flag TEXT)"
    )
    return conn

def verdict_of(score):
    if score >= 5:
        return "SCAM"
    if score >= 2:
        return "BE CAREFUL"
    return "SAFE"

def save_check(score, flags, language):
    # Only the result is saved, never the message text (privacy)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO checks (created_at, verdict, score, language) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M"), verdict_of(score), score, language),
    )
    for f in flags:
        conn.execute("INSERT INTO flag_hits (check_id, flag) VALUES (?, ?)", (cur.lastrowid, f))
    conn.commit()
    conn.close()

def check(text):
    t = text.lower()
    score, flags, good = 0, [], []
    for pat, pts, why in RULES:
        if re.search(pat, t):
            score += pts
            flags.append(why)
    for pat, why in SAFE:
        if re.search(pat, t):
            good.append(why)
    return min(score, 10), flags, good

st.title("🛡️ Internship Scam Checker")

tab_check, tab_dash = st.tabs(["Checker", "Dashboard"])

with tab_check:
    st.write("Paste an internship or job message below to check if it is a scam.")

    language = st.selectbox("Explain in", ["English", "Hindi", "Marathi"])

    message = st.text_area("Message", height=200)

    if st.button("Check Message"):
        if message.strip() == "":
            st.warning("Please paste a message first.")
        else:
            score, flags, good = check(message)
            save_check(score, flags, language)
            if score >= 5:
                st.error(f"🔴 SCAM (Score: {score}/10)")
                st.write("**What to do:** Do not pay, do not reply, and block the sender.")
            elif score >= 2:
                st.warning(f"🟡 BE CAREFUL (Score: {score}/10)")
                st.write("**What to do:** Check the company's website and LinkedIn page yourself.")
            else:
                st.success(f"🟢 Looks SAFE (Score: {score}/10)")
                st.write("**Remember:** Never pay any fee or share an OTP, even if it looks safe.")
            if flags:
                st.subheader("Red flags")
                for f in flags:
                    st.write("- " + f)
            if good:
                st.subheader("Good signs")
                for g in good:
                    st.write("- " + g)

            with st.spinner("AI is explaining..."):
                explanation = ai_explain(message, score, flags, language)
            st.subheader("AI explanation")
            if explanation:
                st.write(explanation)
            else:
                st.write("AI explanation is not available right now. Please use the red flags above.")

with tab_dash:
    st.write("Live statistics of all checks done in this app.")
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM checks").fetchone()[0]
    if total == 0:
        st.info("No checks yet. Check a message first!")
    else:
        st.metric("Total checks", total)
        verdicts = pd.read_sql_query(
            "SELECT verdict, COUNT(*) AS count FROM checks GROUP BY verdict ORDER BY count DESC", conn)
        st.subheader("Results")
        st.bar_chart(verdicts, x="verdict", y="count")
        top_flags = pd.read_sql_query(
            "SELECT flag, COUNT(*) AS count FROM flag_hits GROUP BY flag ORDER BY count DESC LIMIT 5", conn)
        if not top_flags.empty:
            st.subheader("Most common red flags")
            st.dataframe(top_flags, hide_index=True)
        langs = pd.read_sql_query(
            "SELECT language, COUNT(*) AS count FROM checks GROUP BY language", conn)
        st.subheader("Languages used")
        st.bar_chart(langs, x="language", y="count")
    conn.close()
