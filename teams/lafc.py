from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
from datetime import datetime, timedelta

CHROMEDRIVER_PATH = r"C:\Users\timot\OneDrive\Documents\Python Projects\chromedriver-win64\chromedriver.exe"
load_dotenv()

EMAIL_LOG_FILE = "sent_emails.log"

# Optional: Call this function to clear the log manually
def reset_email_log():
    open(EMAIL_LOG_FILE, 'w', encoding='utf-8').close()
    print("🔄 Email log has been reset.")

def launch_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    service = Service(CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)

def send_email(subject, body):
    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT", "timothytan997@gmail.com")

    # Prevent redundant emails by checking log
    if os.path.exists(EMAIL_LOG_FILE):
        with open(EMAIL_LOG_FILE, "r", encoding="utf-8") as f:
            sent_subjects = [line.split(" — ", 1)[-1].strip() for line in f if " — " in line]
            if subject.strip() in sent_subjects:
                print("📭 Email already sent — skipping.")
                return

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)
        print(f"📧 Email sent to {recipient}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(EMAIL_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} — {subject.strip()}\n")

def should_run_now(next_game_info):
    if not next_game_info:
        return True  # no upcoming game info available, always run
    try:
        date_str, teams_str = next_game_info.split(" — ")
        date_parts = date_str.split("/")
        game_time_str = "19:30"  # default kickoff if unknown
        parts = teams_str.split()
        kickoff_display = "7:30pm PDT"  # default for output if nothing found
        for i, part in enumerate(parts):
            if ":" in part and "pm" in part.lower():
                kickoff_display = part.upper().replace("PM", "pm PDT")
                game_time_str = part.lower().replace("pm", "").strip()
                break
        game_datetime = datetime.strptime(f"2025-{int(date_parts[0]):02d}-{int(date_parts[1]):02d} {game_time_str}", "%Y-%m-%d %H:%M")
        readable_date = game_datetime.strftime("%B %d, %Y")
        readable_time = game_datetime.strftime("%I:%M %p PDT").lstrip("0")
        formatted_line = f"🔜 Next Scheduled Home Game: {readable_date} | {readable_time} Kickoff | {teams_str}"
        print(formatted_line)
        return datetime.now() >= game_datetime + timedelta(hours=3)
    except Exception as e:
        print(f"⚠️ Failed to parse game time: {e}")
        return True
    

def run_lafc_promo():
    print("⚽ Checking LAFC promo (via Selenium)...")
    driver = launch_browser()
    try:
        driver.get("https://www.lafc.com/schedule")
        time.sleep(6)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        text = driver.find_element(By.TAG_NAME, "body").text
        lines = text.strip().split("\n")

        completed_home_games = []
        next_home_game = None

        for i in range(len(lines)):
            if lines[i] == "Final" and i + 5 < len(lines):
                comp = lines[i + 1]
                home_team = lines[i + 2].strip()
                try:
                    home_score = int(lines[i + 3].strip())
                    away_score = int(lines[i + 4].strip())
                except ValueError:
                    continue
                away_team = lines[i + 5].strip()

                if home_team == "LAFC":
                    completed_home_games.append({
                        "home_team": home_team,
                        "away_team": away_team,
                        "home_score": home_score,
                        "away_score": away_score,
                        "competition": comp,
                        "result": (
                            "win" if home_score > away_score else
                            "loss" if home_score < away_score else
                            "draw"
                        )
                    })

        # Updated next home game logic to match real structure: [Date], [Title], [Home], [Time], [Away], ...
        for i in range(len(lines) - 5):
            if any(m in lines[i] for m in ["/", "pm", "TBD"]):
                maybe_home = lines[i + 2].strip()
                maybe_away = lines[i + 4].strip()
                if maybe_home == "LAFC":
                    next_home_game = f"{lines[i]} — {maybe_home} vs {maybe_away}"
                    break

        if completed_home_games:
            last_game = completed_home_games[-1]
            print(f"\n📅 Last Home Game: {last_game['away_team']} @ {last_game['home_team']}")
            print(f"🏁 Final Score: {last_game['home_score']} - {last_game['away_score']}")
            if last_game["result"] == "win":
                print("✅ LAFC won at home! Chick-fil-A reward likely available.")
                subject = f"🏆 LAFC Won at Home — {last_game['away_team']} @ LAFC {last_game['home_score']}-{last_game['away_score']}"
                body = (
                    f"LAFC won their last home game!\n\n"
                    f"Final Score: {last_game['away_team']} {last_game['away_score']} @ LAFC {last_game['home_score']}\n\n"
                    f"Time to check the Chick-fil-A app for your reward."
                )
                if next_home_game:
                    body += f"\n\nNext Home Game: {next_home_game}"
                send_email(subject, body)
            elif last_game["result"] == "draw":
                print("🤝 It was a draw. No promo.")
            else:
                print("❌ LAFC did not win at home. No promo.")
        else:
            print("❌ No completed LAFC home games found.")

        if next_home_game:
            should_run_now(next_home_game)
            #print(f"\n🔜 Next Scheduled Home Game: {next_home_game}")

    except Exception as e:
        print("⚠️ Error:", e)
    finally:
        driver.quit()

