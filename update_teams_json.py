#!/usr/bin/env python3
"""
Script to update teams.json with the 2025 teams from the schedule
"""

import json
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

def create_teams_json(teams, output_path):
    """Create a new teams.json file with the 2025 teams"""
    
    # Create a simple structure with just team names
    teams_data = {
        "year": 2025,
        "teams": []
    }
    
    for team in teams:
        teams_data["teams"].append({
            "name": team,
            "year": 2025,
            "conference": "",
            "stats": {
                "offense": {},
                "defense": {},
                "special_teams": {}
            }
        })
    
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(teams_data, file, indent=2)
    
    return len(teams)

if __name__ == "__main__":
    app_js_file = "/Users/jeff/NCAA Stats/college-football-app/app.js"
    teams_json_file = "/Users/jeff/NCAA Stats/college-football-app/teams.json"
    
    print("Extracting teams from 2025 schedule...")
    teams = extract_teams_from_app_js(app_js_file)
    
    print(f"Found {len(teams)} unique teams")
    
    print("Creating new teams.json...")
    team_count = create_teams_json(teams, teams_json_file)
    
    print(f"✅ Successfully created teams.json with {team_count} teams!")
