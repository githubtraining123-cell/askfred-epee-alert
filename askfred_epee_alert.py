import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os

SEARCH_URL = "https://www.askfred.net/tournaments"



KEYWORDS = [
    "epee"
]

SEEN_FILE = "seen_tournaments.json"

EMAIL_TO = [
    "mshwetha694@gmail.com"
]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]

def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f, indent=2)

def fetch_tournaments():
    api_url = "https://www.askfred.net/api/tournaments"

    params = {
        "weapon": "Epee",
        "page": 1
    }

    r = requests.get(api_url, params=params, timeout=30)
    data = r.json()

    results = []

    for t in data.get("tournaments", []):
        name = t.get("name", "").lower()
        url = "https://www.askfred.net" + t.get("url", "")

        # Age filter
        if not any(age in name for age in ["y14", "cadet", "junior"]):
            continue

        # Gender filter
        if not ("women" in name or "mixed" in name):
            continue

        results.append((name, url))

    return results
    
def send_email(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(EMAIL_TO)
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)

def main():
    seen = load_seen()
    tournaments = fetch_tournaments()

    new_events = []
    for title, link in tournaments:
        if link not in seen:
            new_events.append((title, link))
            seen.add(link)

    today = datetime.now().strftime("%Y-%m-%d")

    if new_events:
        body = "Automated email. New Épée tournaments found:\n\n"
        for t, l in new_events:
            body += f"- {t.title()}\n  {l}\n\n"
        subject = f"🗡️ New Épée Tournaments Found ({today})"
    else:
        body = "Automated email. No new Épée tournaments matching your criteria were found today."
        subject = f"ℹ️ No New Épée Tournaments ({today})"

    send_email(subject, body)
    save_seen(seen)

if __name__ == "__main__":
    main()
