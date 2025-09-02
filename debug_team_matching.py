#!/usr/bin/env python3
"""
Debug Team Name Matching Issues
Identifies which teams from the Week 1 schedule are missing from teams.json
"""

import json
import re

def load_teams_data():
    """Load team statistics from teams.json"""
    try:
        with open('teams.json', 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print("Error: teams.json not found")
        return None

def get_week1_schedule():
    """Extract Week 1 schedule from app.js"""
    try:
        with open('app.js', 'r') as f:
            content = f.read()
        
        # Find the Week 1 schedule section
        start = content.find("schedule[1] = [")
        if start == -1:
            print("Error: Could not find Week 1 schedule in app.js")
            return []
        
        # Extract the array content
        start = content.find('[', start)
        end = content.find('];', start) + 1
        
        schedule_text = content[start:end]
        
        # Parse the JavaScript array into Python
        games = []
        
        # Find all game objects
        game_pattern = r'\{[^}]*home:\s*\'([^\']+)\'[^}]*away:\s*\'([^\']+)\'[^}]*\}'
        matches = re.findall(game_pattern, schedule_text)
        
        for home, away in matches:
            games.append({
                'home': home,
                'away': away
            })
        
        return games
    except Exception as e:
        print(f"Error parsing schedule: {e}")
        return []

def debug_team_matching():
    """Debug team name matching issues"""
    print("🔍 Debugging Team Name Matching Issues")
    print("=" * 50)
    
    # Load data
    teams_data = load_teams_data()
    if not teams_data:
        print("Failed to load team data")
        return
    
    schedule = get_week1_schedule()
    if not schedule:
        print("Failed to load schedule")
        return
    
    print(f"Found {len(schedule)} Week 1 games")
    print(f"Found {len(teams_data)} teams in teams.json")
    
    # Get all team names from teams.json
    available_teams = set(teams_data.keys())
    
    # Get all team names from schedule
    schedule_teams = set()
    for game in schedule:
        schedule_teams.add(game['home'])
        schedule_teams.add(game['away'])
    
    print(f"Found {len(schedule_teams)} unique teams in Week 1 schedule")
    
    # Find missing teams
    missing_teams = schedule_teams - available_teams
    extra_teams = available_teams - schedule_teams
    
    print(f"\n❌ Missing Teams ({len(missing_teams)}):")
    for team in sorted(missing_teams):
        print(f"  - {team}")
    
    print(f"\n✅ Extra Teams in teams.json ({len(extra_teams)}):")
    for team in sorted(list(extra_teams)[:20]):  # Show first 20
        print(f"  - {team}")
    
    if len(extra_teams) > 20:
        print(f"  ... and {len(extra_teams) - 20} more")
    
    # Show some examples of games that can't be predicted
    print(f"\n🚫 Games That Can't Be Predicted:")
    unpredicted_count = 0
    for game in schedule:
        if game['home'] in missing_teams or game['away'] in missing_teams:
            print(f"  - {game['home']} vs {game['away']}")
            unpredicted_count += 1
            if unpredicted_count >= 10:  # Limit output
                print(f"  ... and {len(schedule) - unpredicted_count} more games")
                break
    
    print(f"\n📊 Summary:")
    print(f"  Total Week 1 Games: {len(schedule)}")
    print(f"  Games That Can Be Predicted: {len(schedule) - unpredicted_count}")
    print(f"  Games That Cannot Be Predicted: {unpredicted_count}")
    print(f"  Prediction Coverage: {((len(schedule) - unpredicted_count) / len(schedule) * 100):.1f}%")
    
    return missing_teams

if __name__ == "__main__":
    debug_team_matching()
