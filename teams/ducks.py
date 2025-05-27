import requests
from datetime import datetime

def get_last_ducks_game():
    url = "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams/anaheim/scoreboard"
    res = requests.get(url)
    data = res.json()

    if "events" not in data or not data["events"]:
        raise ValueError("No Ducks games found in ESPN feed. (Out of season?)")

    for event in data["events"]:
        if event["status"]["type"]["completed"]:
            game = event
            break
    else:
        raise ValueError("No completed Ducks games found.")

    competitors = game["competitions"][0]["competitors"]
    home = next(team for team in competitors if team["homeAway"] == "home")
    away = next(team for team in competitors if team["homeAway"] == "away")

    return {
        "date": game["date"],
        "home": home["team"]["displayName"],
        "away": away["team"]["displayName"],
        "home_score": int(home["score"]),
        "away_score": int(away["score"])
    }

def run_ducks_promo():
    print("🦆 Checking Ducks promo...")

    game = get_last_ducks_game()
    is_home_game = game["home"] == "Anaheim Ducks"
    ducks_score = game["home_score"] if is_home_game else game["away_score"]

    print(f"📅 Game: {game['away']} @ {game['home']} on {game['date']}")
    print(f"🏒 Final Score: {game['away_score']} - {game['home_score']}")

    if is_home_game and ducks_score >= 5:
        print("✅ Ducks promo condition met! 5+ goals at home.")
    else:
        print("❌ No promo earned for Ducks.")
