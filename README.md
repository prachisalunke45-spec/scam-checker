# 🛡️ Internship Scam Checker

A free web app that helps students check whether an internship or job message is a **scam**, and explains why in **English, Hindi or Marathi**.

**Live app:** https://scam-checker-prachi.streamlit.app

## Why I built this
Many students receive fake internship offers that ask for a "registration fee", promise "performance-based" stipends, or push them to pay quickly. I built this tool to spot these red flags in seconds.

## Features
- **Rule-based checker:** detects fee requests, fake stipends, pressure tactics, requests for Aadhaar/PAN/OTP, paid-course funnels and more, and gives a score out of 10.
- **AI explanation:** Gemini API explains the result in simple English, Hindi or Marathi.
- **SQL dashboard:** every check is saved in SQLite and shown as charts (results, most common red flags, languages used).
- **Sample messages:** one-click scam and safe examples for a quick demo.
- **Privacy:** only the score, verdict and red flags are saved. The message text is never stored.

## Tech stack
Python, Streamlit, Gemini API (google-genai), SQLite, Pandas, Regex

## How it works
1. The user pastes a message.
2. Regex rules find red flags and calculate a score (SCAM / BE CAREFUL / SAFE).
3. Gemini writes a short explanation in the chosen language.
4. The result is saved in SQLite and shown on the Dashboard tab.

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

Add your key in `.streamlit/secrets.toml`:

    GEMINI_API_KEY = "your_key_here"

## Future plans
- Upload a screenshot of the message
- Permanent cloud database
- Company verification checklist
- Installable mobile app (PWA)

## Author
**Prachi Salunke**, BSc Computer Science student, MIT Arts Commerce and Science College, Barshi.
