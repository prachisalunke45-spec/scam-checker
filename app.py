import streamlit as st

st.set_page_config(page_title="Internship Scam Checker", page_icon="🛡️")

st.title("🛡️ Internship Scam Checker")
st.write("Paste an internship or job message below to check if it is a scam.")

message = st.text_area("Message", height=200)

if st.button("Check karo"):
    if message.strip() == "":
        st.warning("Please paste a message first.")
    else:
        st.info("Checker coming soon...")
