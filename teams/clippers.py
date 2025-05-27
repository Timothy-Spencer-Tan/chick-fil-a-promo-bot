from nba_api.stats.endpoints import leaguegamefinder, playbyplayv2
from nba_api.stats.static import teams
import time

print("Hello! Loading Clippers' Data. Checking if we have a BOBAN")

def get_clippers_team_id():
    all_teams = teams.get_teams()
    clippers = [team for team in all_teams if team['full_name'] == 'Los Angeles Clippers']
    return clippers[0]['id']

def get_last_clippers_game_id(team_id):
    finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id, season_type_nullable='Playoffs')
    time.sleep(1)
    games = finder.get_data_frames()[0]
    latest_game = games.iloc[0]
    return latest_game['GAME_ID'], latest_game['MATCHUP'], latest_game['WL']

def check_missed_fts_in_4th(game_id, clippers_team_id, matchup):
    pbp = playbyplayv2.PlayByPlayV2(game_id=game_id)
    time.sleep(1)
    df = pbp.get_data_frames()[0]
    home_team = 'LAC' in matchup.split()[-1]

    q4 = df[df['PERIOD'] == 4]
    streak = 0
    last_player = ""
    for _, row in q4.iterrows():
        desc = row['VISITORDESCRIPTION'] if home_team else row['HOMEDESCRIPTION']
        if isinstance(desc, str) and "misses free throw" in desc.lower():
            player = desc.split(" misses")[0]
            if player == last_player:
                streak += 1
                if streak == 2:
                    print(f"🎯 {player} missed two in a row in Q4! Promo triggered.")
                    return True
            else:
                streak = 1
                last_player = player
        else:
            streak = 0
            last_player = ""
    print("🔎 No opponent missed two consecutive FTs in Q4.")
    return False

def run_clippers_promo(test_mode=False):
    print("🏀 Checking Clippers promo...")

    clippers_id = get_clippers_team_id()
    
    if test_mode:
        game_id = "0022300003"
        matchup = "DEN @ LAC"
    else:
        game_id, matchup, _ = get_last_clippers_game_id(clippers_id)

    print(f"📝 Game: {matchup} - ID: {game_id}")
    triggered = check_missed_fts_in_4th(game_id, clippers_id, matchup)

    if triggered:
        print("✅ Clippers promo condition met.")
    else:
        print("❌ No promo earned for Clippers.")
