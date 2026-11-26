import re
import streamlit as st

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
st.write("Paste an internship or job message below to check if it is a scam.")

message = st.text_area("Message", height=200)

if st.button("Check karo"):
    if message.strip() == "":
        st.warning("Please paste a message first.")
    else:
        score, flags, good = check(message)
        if score >= 5:
            st.error(f"🔴 SCAM (Score: {score}/10)")
            st.write("**Kya karein:** Paise mat do, reply mat do, block karo.")
        elif score >= 2:
            st.warning(f"🟡 CAREFUL (Score: {score}/10)")
            st.write("**Kya karein:** Company ki website aur LinkedIn page khud check karo.")
        else:
            st.success(f"🟢 Looks SAFE (Score: {score}/10)")
            st.write("**Dhyan rakho:** Phir bhi fee ya OTP kabhi mat do.")
        if flags:
            st.subheader("Red flags")
            for f in flags:
                st.write("- " + f)
        if good:
            st.subheader("Good signs")
            for g in good:
                st.write("- " + g)
