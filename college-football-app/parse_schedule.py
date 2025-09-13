#!/usr/bin/env python3
"""
Parse the 2025 college football schedule CSV and generate JavaScript schedule data
"""

import csv
import json
import sys
from collections import defaultdict
import os

def parse_schedule_csv(csv_file_path):
    """Parse the comprehensive CSV file and extract schedule data"""
    schedule_data = defaultdict(list)
    teams = set()
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                team = row['Team'].strip()
                week = int(row['Week'])
                opponent = row['Opponent'].strip()
                home_away = row['Home_Away'].strip()
                location = row['Location'].strip()
                
                # Add teams to set
                teams.add(team)
                teams.add(opponent)
                
                # Create game entry (comprehensive schedule has minimal fields)
                game = {
                    'team': team,
                    'opponent': opponent,
                    'week': week,
                    'home_away': home_away,
                    'location': location
                }
                
                schedule_data[week].append(game)
                
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_file_path}")
        return None, None
    except Exception as e:
        print(f"❌ Error parsing CSV: {e}")
        return None, None
    
    return dict(schedule_data), sorted(teams)

def parse_detailed_schedule(csv_file_path):
    """Parse the detailed CSV file with enhanced information"""
    detailed_games = {}
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                team = row['Team'].strip()
                week = int(row['Week'])
                opponent = row['Opponent'].strip()
                home_away = row['Home_Away'].strip()
                location = row['Location'].strip()
                date = row['Date'].strip()
                time_et = row['Time_ET'].strip()
                tv_network = row['TV_Network'].strip()
                conference = row['Conference'].strip()
                notes = row['Notes'].strip()
                
                # Skip bye weeks
                if opponent.lower() in ['bye', ''] or notes.lower() in ['bye', 'bye week']:
                    continue
                
                # Create detailed game info
                game_key = f"{team}_{opponent}_{week}" if home_away == 'Home' else f"{opponent}_{team}_{week}"
                detailed_games[game_key] = {
                    'date': date,
                    'time_et': time_et,
                    'tv_network': tv_network,
                    'conference': conference,
                    'notes': notes
                }
                
    except Exception as e:
        print(f"❌ Error parsing detailed CSV: {e}")
        return {}
    
    return detailed_games

def parse_detailed_schedule_primary(csv_file_path):
    """Parse the detailed CSV file as the primary schedule source"""
    schedule_data = defaultdict(list)
    teams = set()
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                team = row['Team'].strip()
                week = int(row['Week'])
                opponent = row['Opponent'].strip()
                home_away = row['Home_Away'].strip()
                location = row['Location'].strip()
                date = row['Date'].strip()
                time_et = row['Time_ET'].strip()
                tv_network = row['TV_Network'].strip()
                conference = row['Conference'].strip()
                notes = row['Notes'].strip()
                
                # Skip bye weeks
                if opponent.lower() in ['bye', ''] or notes.lower() in ['bye', 'bye week']:
                    continue
                
                # Add teams to set
                teams.add(team)
                teams.add(opponent)
                
                # Create game entry
                game = {
                    'team': team,
                    'opponent': opponent,
                    'week': week,
                    'home_away': home_away,
                    'location': location,
                    'date': date,
                    'time_et': time_et,
                    'tv_network': tv_network,
                    'conference': conference,
                    'notes': notes
                }
                
                schedule_data[week].append(game)
                
    except Exception as e:
        print(f"❌ Error parsing detailed CSV: {e}")
        return None, None
    
    return dict(schedule_data), sorted(teams)

def add_missing_teams(detailed_data, comprehensive_data, detailed_teams):
    """Add games from comprehensive schedule for teams not in detailed schedule, but respect bye weeks"""
    detailed_teams_set = set(detailed_teams)
    
    # First, collect all teams that have bye weeks in the detailed schedule
    teams_with_byes = set()
    detailed_csv_path = '../CFDB/college_football_2025_complete_schedule.csv'
    
    try:
        with open(detailed_csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                team = row['Team'].strip()
                week = int(row['Week'])
                notes = row['Notes'].strip()
                if 'bye' in notes.lower():
                    teams_with_byes.add(f"{team}_{week}")
    except:
        pass  # If we can't read the detailed CSV, continue without bye week protection
    
    for week, games in comprehensive_data.items():
        if week not in detailed_data:
            detailed_data[week] = []
        
        for game in games:
            team = game['team']
            opponent = game['opponent']
            
            # Skip if this team has a bye week in the detailed schedule
            if f"{team}_{week}" in teams_with_byes or f"{opponent}_{week}" in teams_with_byes:
                continue
            
            # Add game if either team is missing from detailed schedule
            if team not in detailed_teams_set or opponent not in detailed_teams_set:
                # Check if this game already exists in detailed data
                game_exists = any(
                    (g['team'] == team and g['opponent'] == opponent) or 
                    (g['team'] == opponent and g['opponent'] == team)
                    for g in detailed_data[week]
                )
                
                if not game_exists:
                    detailed_data[week].append({
                        'team': team,
                        'opponent': opponent,
                        'week': week,
                        'home_away': game['home_away'],
                        'location': game['location'],
                        'date': get_date_for_week(week),
                        'time_et': 'TBD',
                        'tv_network': 'TBD',
                        'conference': get_conference(team),
                        'notes': ''
                    })
    
    return detailed_data

def merge_schedules(comprehensive_data, detailed_data):
    """Merge comprehensive schedule with detailed enhancements, prioritizing detailed schedule for conflicts"""
    merged_data = {}
    
    # First, collect all teams that have bye weeks in the detailed schedule
    teams_with_byes = set()
    for game_key, details in detailed_data.items():
        if 'bye' in details.get('notes', '').lower() or details.get('opponent', '').lower() in ['bye', '']:
            # Extract team name from game_key
            parts = game_key.split('_')
            if len(parts) >= 2:
                teams_with_byes.add(parts[0])
    
    for week, games in comprehensive_data.items():
        merged_games = []
        
        for game in games:
            team = game['team']
            opponent = game['opponent']
            
            # Create lookup key for detailed info
            game_key = f"{team}_{opponent}_{week}" if game['home_away'] == 'Home' else f"{opponent}_{team}_{week}"
            
            # Check if this team has a bye week in the detailed schedule
            if team in teams_with_byes:
                # Check if this specific game is a bye in detailed schedule
                bye_key = f"{team}_BYE_{week}"
                if bye_key in detailed_data or any(key.startswith(f"{team}_") and key.endswith(f"_{week}") and 'bye' in detailed_data[key].get('notes', '').lower() for key in detailed_data.keys()):
                    # This is a bye week - skip adding this game
                    continue
            
            # Start with comprehensive game data
            merged_game = {
                'team': team,
                'opponent': opponent,
                'week': week,
                'home_away': game['home_away'],
                'location': game['location'],
                'date': get_date_for_week(week),  # Default date
                'time_et': 'TBD',  # Default time
                'tv_network': 'TBD',  # Default network
                'conference': get_conference(team),  # Default conference
                'notes': ''  # Default notes
            }
            
            # Add detailed info if available
            if game_key in detailed_data:
                detailed_info = detailed_data[game_key]
                merged_game.update({
                    'date': detailed_info['date'],
                    'time_et': detailed_info['time_et'],
                    'tv_network': detailed_info['tv_network'],
                    'conference': detailed_info['conference'],
                    'notes': detailed_info['notes']
                })
            
            merged_games.append(merged_game)
        
        merged_data[week] = merged_games
    
    return merged_data

def generate_team_data(teams):
    """Generate team data with realistic stats"""
    team_data = {}
    
    for team in teams:
        team_data[team] = {
            'name': team,
            'overallRating': generate_rating(),
            'efficiencyRating': generate_rating(),
            'offenseRating': generate_rating(),
            'defenseRating': generate_rating(),
            'specialTeamsRating': generate_rating(),
            'homeAdvantage': generate_home_advantage(),
            'recentForm': generate_recent_form(),
            'strengthOfSchedule': generate_sos(),
            'conference': get_conference(team),
            'coachRating': generate_rating(),
            'stadiumFactor': generate_stadium_factor()
        }
    
    return team_data

def generate_rating():
    """Generate realistic team rating (60-100)"""
    import random
    return random.randint(60, 100)

def generate_home_advantage():
    """Generate home advantage (2-12%)"""
    import random
    return random.uniform(0.02, 0.12)

def generate_recent_form():
    """Generate recent form (-20% to +20%)"""
    import random
    return random.uniform(-0.2, 0.2)

def generate_sos():
    """Generate strength of schedule (-15% to +15%)"""
    import random
    return random.uniform(-0.15, 0.15)

def generate_stadium_factor():
    """Generate stadium factor (1-6%)"""
    import random
    return random.uniform(0.01, 0.06)

def get_conference(team):
    """Determine conference for team"""
    conferences = {
        'SEC': ['Alabama', 'Auburn', 'LSU', 'Texas A&M', 'Mississippi', 'Mississippi State', 'Arkansas', 'Missouri', 'Georgia', 'Florida', 'Tennessee', 'Kentucky', 'South Carolina', 'Vanderbilt'],
        'ACC': ['Clemson', 'Florida State', 'North Carolina', 'NC State', 'Wake Forest', 'Duke', 'Virginia Tech', 'Virginia', 'Pittsburgh', 'Boston College', 'Miami', 'Louisville', 'Syracuse', 'Georgia Tech'],
        'Big Ten': ['Ohio State', 'Michigan', 'Penn State', 'Michigan State', 'Maryland', 'Rutgers', 'Indiana', 'Purdue', 'Illinois', 'Northwestern', 'Iowa', 'Wisconsin', 'Minnesota', 'Nebraska'],
        'Pac-12': ['Oregon', 'Washington', 'USC', 'UCLA', 'Utah', 'Arizona State', 'Arizona', 'California', 'Stanford', 'Oregon State', 'Washington State', 'Colorado'],
        'Big 12': ['Texas', 'Oklahoma', 'Baylor', 'TCU', 'Texas Tech', 'Oklahoma State', 'Kansas State', 'Kansas', 'Iowa State', 'West Virginia', 'Cincinnati', 'UCF', 'Houston', 'BYU'],
        'AAC': ['Memphis', 'Tulane', 'SMU', 'Tulsa', 'Navy', 'East Carolina', 'Temple', 'South Florida'],
        'Mountain West': ['Boise State', 'San Diego State', 'Fresno State', 'Air Force', 'Wyoming', 'Utah State', 'Colorado State', 'Nevada', 'UNLV', 'New Mexico', 'San Jose State', 'Hawaii'],
        'Sun Belt': ['Appalachian State', 'Coastal Carolina', 'Georgia Southern', 'Georgia State', 'Troy', 'South Alabama', 'Louisiana', 'Louisiana-Monroe', 'Arkansas State', 'Texas State'],
        'C-USA': ['Marshall', 'Western Kentucky', 'Middle Tennessee', 'Florida Atlantic', 'Charlotte', 'FIU', 'Rice', 'North Texas', 'UTSA', 'UTEP', 'Southern Miss', 'Louisiana Tech'],
        'MAC': ['Miami (OH)', 'Toledo', 'Northern Illinois', 'Western Michigan', 'Central Michigan', 'Eastern Michigan', 'Ball State', 'Bowling Green', 'Kent State', 'Akron', 'Buffalo', 'Ohio'],
        'Independent': ['Notre Dame', 'Army', 'Liberty', 'UMass', 'New Mexico State', 'Connecticut', 'James Madison', 'Old Dominion']
    }
    
    for conference, teams in conferences.items():
        if team in teams:
            return conference
    
    return 'Independent'

def create_javascript_schedule(schedule_data, teams):
    """Create JavaScript code for the schedule"""
    
    js_code = f"""// Auto-generated schedule from CSV data
const REAL_SCHEDULE_DATA = {{
"""
    
    for week in sorted(schedule_data.keys()):
        games = schedule_data[week]
        js_code += f"    {week}: [\n"
        
        for game in games:
            js_code += f"""        {{
            homeTeam: "{game['team'] if game['home_away'] == 'Home' else game['opponent']}",
            awayTeam: "{game['opponent'] if game['home_away'] == 'Home' else game['team']}",
            week: {week},
            date: "{game['date']}",
            time_et: "{game['time_et']}",
            location: "{game['location']}",
            tv_network: "{game['tv_network']}",
            conference: "{game['conference']}",
            notes: "{game['notes']}",
            rivalry: {str(is_rivalry_game(game['team'], game['opponent'])).lower()}
        }},\n"""
        
        js_code += "    ],\n"
    
    js_code += "};\n\n"
    js_code += f"const REAL_TEAMS_DATA = {json.dumps(teams, indent=4)};\n"
    
    return js_code

def get_date_for_week(week):
    """Generate date for week"""
    from datetime import datetime, timedelta
    base_date = datetime(2025, 8, 30)  # Start of season
    week_date = base_date + timedelta(weeks=week-1)
    return week_date.strftime('%Y-%m-%d')

def is_rivalry_game(team1, team2):
    """Check if teams are rivals"""
    rivalries = [
        ['Alabama', 'Auburn'], ['Michigan', 'Ohio State'], ['USC', 'UCLA'], ['Texas', 'Oklahoma'],
        ['Florida', 'Georgia'], ['Notre Dame', 'USC'], ['Army', 'Navy'], ['Oregon', 'Oregon State'],
        ['Arizona', 'Arizona State'], ['Colorado', 'Colorado State']
    ]
    
    for rivalry in rivalries:
        if team1 in rivalry and team2 in rivalry:
            return True
    return False

def main():
    # Use the comprehensive schedule for all teams, enhanced with detailed schedule
    comprehensive_csv = '../2025_college_football_schedules.csv'
    detailed_csv = '../CFDB/college_football_2025_complete_schedule.csv'
    
    if not os.path.exists(comprehensive_csv):
        print(f"❌ Comprehensive CSV file not found at {comprehensive_csv}")
        return
    
    if not os.path.exists(detailed_csv):
        print(f"❌ Detailed CSV file not found at {detailed_csv}")
        return
    
    print("📅 Parsing detailed schedule as primary source...")
    
    # Use the detailed schedule as primary source
    schedule_data, teams = parse_detailed_schedule_primary(detailed_csv)
    
    # Add missing teams from comprehensive schedule
    comprehensive_data, comprehensive_teams = parse_schedule_csv(comprehensive_csv)
    schedule_data = add_missing_teams(schedule_data, comprehensive_data, teams)
    teams = list(set(teams + comprehensive_teams))
    
    if schedule_data is None:
        return
    
    print(f"✅ Found {len(teams)} teams across {len(schedule_data)} weeks")
    
    # Generate team data
    team_data = generate_team_data(teams)
    
    # Create JavaScript files
    js_schedule = create_javascript_schedule(schedule_data, team_data)
    
    # Write to files
    with open('schedule_data.js', 'w') as f:
        f.write(js_schedule)
    
    with open('teams.json', 'w') as f:
        json.dump(team_data, f, indent=2)
    
    print("✅ Generated schedule_data.js and teams.json")
    print(f"📊 Schedule covers {len(schedule_data)} weeks with {sum(len(games) for games in schedule_data.values())} total games")
    
    # Show sample data
    print("\n📋 Sample Week 1 games:")
    if 1 in schedule_data:
        for i, game in enumerate(schedule_data[1][:5]):
            print(f"  {i+1}. {game['team']} vs {game['opponent']} ({game['home_away']})")

if __name__ == "__main__":
    main()
