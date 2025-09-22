#!/usr/bin/env python3
"""
Script to extract all unique teams from the real 2025 schedule and update the teams list
"""

import re

def extract_teams_from_app_js(app_js_path):
    """Extract all unique team names from the app.js schedule"""
    teams = set()
    
    with open(app_js_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find all home and away team names
    home_pattern = r"home: '([^']*)'"
    away_pattern = r"away: '([^']*)'"
    
    home_teams = re.findall(home_pattern, content)
    away_teams = re.findall(away_pattern, content)
    
    teams.update(home_teams)
    teams.update(away_teams)
    
    # Remove empty strings and sort
    teams = sorted([team for team in teams if team.strip()])
    
    return teams

def update_teams_list_in_app_js(app_js_path, teams):
    """Update the teams list in app.js with all teams from the schedule"""
    
    with open(app_js_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create the new teams array
    teams_js = "            [\n"
    for i, team in enumerate(teams):
        teams_js += f"                '{team}'"
        if i < len(teams) - 1:
            teams_js += ","
        teams_js += "\n"
    teams_js += "            ];"
    
    # Find and replace the teams array
    pattern = r"\[\s*//.*?\];"
    new_content = re.sub(pattern, teams_js, content, flags=re.DOTALL)
    
    with open(app_js_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    return len(teams)

if __name__ == "__main__":
    app_js_file = "/Users/jeff/NCAA Stats/college-football-app/app.js"
    
    print("Extracting teams from 2025 schedule...")
    teams = extract_teams_from_app_js(app_js_file)
    
    print(f"Found {len(teams)} unique teams:")
    for team in teams:
        print(f"  - {team}")
    
    print("\nUpdating teams list in app.js...")
    team_count = update_teams_list_in_app_js(app_js_file, teams)
    
    print(f"✅ Successfully updated teams list with {team_count} teams!")
