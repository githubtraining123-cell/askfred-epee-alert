import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
from datetime import datetime


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
    base_url = "https://www.askfred.net"
    search_url = f"{base_url}/tournaments"

    today = datetime.today().strftime("%m/%d/%Y")  # MM/DD/YYYY

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    age_categories = ["Y14", "Cadet", "Junior"]
    tournaments = []

    seen_urls = set()  # to avoid duplicates if same tournament appears under multiple ages

    for age in age_categories:
        params = {
            "weapon": "Epee",
            "gender": "Women or Mixed",
            "age": age,
            "date_by": "on",
            "date": today
        }

        r = requests.get(search_url, params=params, headers=headers, timeout=30)
        if r.status_code != 200:
            print(f"Failed to fetch page for age {age}: {r.status_code}")
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.find_all("tr")

        for row in rows:
            link = row.find("a", href=True)
            if link and "/tournaments/" in link["href"]:
                name = link.get_text(strip=True)
                full_url = base_url + link["href"]

                # avoid duplicates
                if full_url not in seen_urls:
                    tournaments.append((name, full_url))
                    seen_urls.add(full_url)

    return tournaments
    
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
