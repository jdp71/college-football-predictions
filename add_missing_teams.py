#!/usr/bin/env python3
"""
Add Missing Teams to teams.json
Adds teams that are in the Week 1 schedule but missing from teams.json
"""

import json
import copy
import re # Added missing import for re

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

def create_default_team_stats(team_name, is_fcs=False):
    """Create default stats for a new team"""
    if is_fcs:
        # FCS teams get lower ratings
        base_rating = 30
        offensive_rating = base_rating + (hash(team_name) % 20) - 10
        defensive_rating = base_rating + (hash(team_name + "def") % 20) - 10
    else:
        # FBS teams get higher ratings
        base_rating = 60
        offensive_rating = base_rating + (hash(team_name) % 30) - 15
        defensive_rating = base_rating + (hash(team_name + "def") % 30) - 15
    
    # Ensure ratings are within reasonable bounds
    offensive_rating = max(1, min(100, offensive_rating))
    defensive_rating = max(1, min(100, defensive_rating))
    overall_rating = (offensive_rating + defensive_rating) // 2
    
    return {
        "name": team_name,
        "conference": "FCS" if is_fcs else "Independent",
        "stats": {
            "offensiveRating": offensive_rating,
            "defensiveRating": defensive_rating,
            "efficiencyRating": overall_rating,
            "advancedRating": overall_rating,
            "pointsPerPlay": 0.3 + (hash(team_name) % 20) / 100,
            "yardsPerPlay": 4.5 + (hash(team_name) % 30) / 10,
            "completionRate": 0.55 + (hash(team_name) % 20) / 100,
            "thirdDownRate": 0.35 + (hash(team_name) % 20) / 100,
            "redZoneRate": 0.65 + (hash(team_name) % 25) / 100,
            "oppPointsPerPlay": 0.4 + (hash(team_name) % 25) / 100,
            "oppYardsPerPlay": 5.5 + (hash(team_name) % 30) / 10,
            "oppCompletionRate": 0.6 + (hash(team_name) % 20) / 100,
            "oppThirdDownRate": 0.45 + (hash(team_name) % 20) / 100,
            "oppRedZoneRate": 0.75 + (hash(team_name) % 25) / 100,
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "home_wins": 0,
            "home_losses": 0,
            "away_wins": 0,
            "away_losses": 0,
            "points_for": 0,
            "points_against": 0,
            "win_percentage": 0.0,
            "points_per_game": 0.0,
            "points_against_per_game": 0.0,
            "point_differential": 0,
            "point_differential_per_game": 0.0
        }
    }

def add_missing_teams():
    """Add missing teams to teams.json"""
    print("🔧 Adding Missing Teams to teams.json")
    print("=" * 50)
    
    # Load current teams
    teams_data = load_teams_data()
    if not teams_data:
        print("Failed to load team data")
        return
    
    # Get schedule to find missing teams
    schedule = get_week1_schedule()
    if not schedule:
        print("Failed to load schedule")
        return
    
    # Get all team names from schedule
    schedule_teams = set()
    for game in schedule:
        schedule_teams.add(game['home'])
        schedule_teams.add(game['away'])
    
    # Find missing teams
    available_teams = set(teams_data.keys())
    missing_teams = schedule_teams - available_teams
    
    print(f"Found {len(missing_teams)} missing teams")
    
    # Define which teams are FCS vs FBS
    fcs_teams = {
        'Abilene Christian', 'Alabama A&M', 'Alabama State', 'App State', 
        'Arkansas-Pine Bluff', 'Austin Peay', 'Bethune-Cookman', 'Bryant',
        'Bucknell', 'Central Arkansas', 'Central Connecticut', 'Charleston Southern',
        'Chattanooga', 'East Texas A&M', 'Eastern Kentucky', 'Elon', 'Holy Cross',
        'Idaho State', 'Illinois State', 'Kennesaw State', 'Lafayette', 'Lamar',
        'Long Island University', 'Maine', 'Massachusetts', 'Mississippi',
        'Missouri State', 'Montana State', 'Morgan State', 'Nicholls',
        'Northern Arizona', 'Portland State', 'SE Louisiana', 'Saint Francis',
        'San José State', 'Southeast Missouri State', 'Stephen F. Austin',
        'Stony Brook', 'Tarleton State', 'UAlbany', 'UT Martin', 'Weber State',
        'Western Illinois'
    }
    
    # Add missing teams
    added_count = 0
    for team_name in sorted(missing_teams):
        is_fcs = team_name in fcs_teams
        new_team = create_default_team_stats(team_name, is_fcs)
        teams_data[team_name] = new_team
        added_count += 1
        print(f"  + Added {team_name} ({'FCS' if is_fcs else 'FBS'})")
    
    # Save updated teams.json
    with open('teams.json', 'w') as f:
        json.dump(teams_data, f, indent=2)
    
    print(f"\n✅ Successfully added {added_count} teams to teams.json")
    print(f"Total teams now: {len(teams_data)}")
    
    return teams_data

if __name__ == "__main__":
    add_missing_teams()
