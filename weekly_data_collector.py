#!/usr/bin/env python3
"""
Weekly Data Collector for College Football Predictions
Collects game results and updates team statistics for model retraining
"""

import json
import requests
import pandas as pd
from datetime import datetime
import argparse
import os
import sys
from typing import Dict, List, Optional

class WeeklyDataCollector:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.collegefootballdata.com"
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        
        # Load current team data
        self.teams_file = "teams.json"
        self.current_teams = self.load_current_teams()
        
    def load_current_teams(self) -> Dict:
        """Load current team data from teams.json"""
        try:
            with open(self.teams_file, 'r') as f:
                data = json.load(f)
                # Handle both array and dict formats
                if isinstance(data, dict) and "teams" in data:
                    # Convert array format to dict format for easier processing
                    teams_dict = {}
                    for team in data["teams"]:
                        teams_dict[team["name"]] = team
                    return teams_dict
                elif isinstance(data, dict):
                    return data
                else:
                    print(f"Warning: Unexpected teams.json format. Starting with empty data.")
                    return {}
        except FileNotFoundError:
            print(f"Warning: {self.teams_file} not found. Starting with empty data.")
            return {}
        except Exception as e:
            print(f"Error loading teams.json: {e}. Starting with empty data.")
            return {}
    
    def get_week_games(self, week: int, year: int = 2025) -> List[Dict]:
        """Get all games for a specific week from CFBD API"""
        if not self.api_key:
            print("Warning: No API key provided. Using sample data for Week 1.")
            return self.get_sample_week1_data()
        
        try:
            url = f"{self.base_url}/games"
            params = {
                "year": year,
                "week": week,
                "seasonType": "regular"
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            games = response.json()
            print(f"Retrieved {len(games)} games for Week {week}")
            return games
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching games: {e}")
            print("Using sample data instead.")
            return self.get_sample_week1_data()
    
    def get_sample_week1_data(self) -> List[Dict]:
        """Sample Week 1 data for testing without API key"""
        return [
            {
                "id": 1,
                "home_team": "Georgia",
                "away_team": "Marshall",
                "home_score": 38,
                "away_score": 0,
                "home_conference": "SEC",
                "away_conference": "Sun Belt",
                "season": 2025,
                "week": 1
            },
            {
                "id": 2,
                "home_team": "Penn State",
                "away_team": "Nevada",
                "home_score": 39,
                "away_score": 3,
                "home_conference": "Big Ten",
                "away_conference": "Mountain West",
                "season": 2025,
                "week": 1
            },
            {
                "id": 3,
                "home_team": "Colorado",
                "away_team": "Georgia Tech",
                "home_score": 20,
                "away_score": 27,
                "home_conference": "Big 12",
                "away_conference": "ACC",
                "season": 2025,
                "week": 1
            },
            {
                "id": 4,
                "home_team": "Texas",
                "away_team": "Ohio State",
                "home_score": 7,
                "away_score": 14,
                "home_conference": "SEC",
                "away_conference": "Big Ten",
                "season": 2025,
                "week": 1
            },
            {
                "id": 5,
                "home_team": "Tennessee",
                "away_team": "Syracuse",
                "home_score": 45,
                "away_score": 26,
                "home_conference": "SEC",
                "away_conference": "ACC",
                "season": 2025,
                "week": 1
            },
            {
                "id": 6,
                "home_team": "Mississippi State",
                "away_team": "Southern Miss",
                "home_score": 34,
                "away_score": 17,
                "home_conference": "SEC",
                "away_conference": "Sun Belt",
                "season": 2025,
                "week": 1
            },
            {
                "id": 7,
                "home_team": "Kentucky",
                "away_team": "Toledo",
                "home_score": 24,
                "away_score": 16,
                "home_conference": "SEC",
                "away_conference": "MAC",
                "season": 2025,
                "week": 1
            },
            {
                "id": 8,
                "home_team": "Maryland",
                "away_team": "Florida Atlantic",
                "home_score": 39,
                "away_score": 7,
                "home_conference": "Big Ten",
                "away_conference": "American",
                "season": 2025,
                "week": 1
            },
            {
                "id": 9,
                "home_team": "Purdue",
                "away_team": "Ball State",
                "home_score": 31,
                "away_score": 0,
                "home_conference": "Big Ten",
                "away_conference": "MAC",
                "season": 2025,
                "week": 1
            },
            {
                "id": 10,
                "home_team": "Indiana",
                "away_team": "Old Dominion",
                "home_score": 27,
                "away_score": 14,
                "home_conference": "Big Ten",
                "away_conference": "Sun Belt",
                "season": 2025,
                "week": 1
            },
            {
                "id": 11,
                "home_team": "Boston College",
                "away_team": "Fordham",
                "home_score": 66,
                "away_score": 10,
                "home_conference": "ACC",
                "away_conference": "FCS",
                "season": 2025,
                "week": 1
            },
            {
                "id": 12,
                "home_team": "UConn",
                "away_team": "Central Connecticut State",
                "home_score": 59,
                "away_score": 13,
                "home_conference": "Independent",
                "away_conference": "FCS",
                "season": 2025,
                "week": 1
            },
            {
                "id": 13,
                "home_team": "West Virginia",
                "away_team": "Robert Morris",
                "home_score": 45,
                "away_score": 3,
                "home_conference": "Big 12",
                "away_conference": "FCS",
                "season": 2025,
                "week": 1
            },
            {
                "id": 14,
                "home_team": "Pittsburgh",
                "away_team": "Duquesne",
                "home_score": 61,
                "away_score": 9,
                "home_conference": "ACC",
                "away_conference": "FCS",
                "season": 2025,
                "week": 1
            },
            {
                "id": 15,
                "home_team": "Tulane",
                "away_team": "Northwestern",
                "home_score": 23,
                "away_score": 3,
                "home_conference": "American",
                "away_conference": "Big Ten",
                "season": 2025,
                "week": 1
            },
            {
                "id": 16,
                "home_team": "Kent State",
                "away_team": "Merrimack",
                "home_score": 21,
                "away_score": 17,
                "home_conference": "MAC",
                "away_conference": "FCS",
                "season": 2025,
                "week": 1
            },
            {
                "id": 17,
                "home_team": "Navy",
                "away_team": "VMI",
                "home_score": 52,
                "away_score": 7,
                "home_conference": "American",
                "away_conference": "FCS",
                "season": 2025,
                "week": 1
            }
        ]
    
    def update_team_statistics(self, games: List[Dict]) -> Dict:
        """Update team statistics based on game results"""
        updated_teams = self.current_teams.copy()
        
        # Initialize team records if they don't exist
        for game in games:
            home_team = game["home_team"]
            away_team = game["away_team"]
            
            if home_team not in updated_teams:
                updated_teams[home_team] = self.create_default_team_stats(home_team, game.get("home_conference", "Unknown"))
            if away_team not in updated_teams:
                updated_teams[away_team] = self.create_default_team_stats(away_team, game.get("away_conference", "Unknown"))
        
        # Update statistics based on game results
        for game in games:
            home_team = game["home_team"]
            away_team = game["away_team"]
            home_score = game["home_score"]
            away_score = game["away_score"]
            
            # Update home team stats
            home_stats = updated_teams[home_team]["stats"]
            # Initialize new fields if they don't exist
            if "games_played" not in home_stats:
                home_stats["games_played"] = 0
                home_stats["wins"] = 0
                home_stats["losses"] = 0
                home_stats["home_wins"] = 0
                home_stats["home_losses"] = 0
                home_stats["away_wins"] = 0
                home_stats["away_losses"] = 0
                home_stats["points_for"] = 0
                home_stats["points_against"] = 0
                home_stats["win_percentage"] = 0.0
                home_stats["points_per_game"] = 0.0
                home_stats["points_against_per_game"] = 0.0
                home_stats["point_differential"] = 0
                home_stats["point_differential_per_game"] = 0.0
            
            home_stats["games_played"] += 1
            home_stats["points_for"] += home_score
            home_stats["points_against"] += away_score
            
            if home_score > away_score:
                home_stats["wins"] += 1
                home_stats["home_wins"] += 1
            else:
                home_stats["losses"] += 1
                home_stats["home_losses"] += 1
            
            # Update away team stats
            if away_team not in updated_teams:
                updated_teams[away_team] = self.create_default_team_stats(away_team, game.get("away_conference", "Unknown"))
            
            away_stats = updated_teams[away_team]["stats"]
            # Initialize new fields if they don't exist
            if "games_played" not in away_stats:
                away_stats["games_played"] = 0
                away_stats["wins"] = 0
                away_stats["losses"] = 0
                away_stats["home_wins"] = 0
                away_stats["home_losses"] = 0
                away_stats["away_wins"] = 0
                away_stats["away_losses"] = 0
                away_stats["points_for"] = 0
                away_stats["points_against"] = 0
                away_stats["win_percentage"] = 0.0
                away_stats["points_per_game"] = 0.0
                away_stats["points_against_per_game"] = 0.0
                away_stats["point_differential"] = 0
                away_stats["point_differential_per_game"] = 0.0
            
            away_stats["games_played"] += 1
            away_stats["points_for"] += away_score
            away_stats["points_against"] += home_score
            
            if away_score > home_score:
                away_stats["wins"] += 1
                away_stats["away_wins"] += 1
            else:
                away_stats["losses"] += 1
                away_stats["away_losses"] += 1
        
        # Recalculate derived statistics
        for team_name, team_data in updated_teams.items():
            stats = team_data["stats"]
            
            if stats.get("games_played", 0) > 0:
                try:
                    stats["win_percentage"] = stats["wins"] / (stats["wins"] + stats["losses"])
                    stats["points_per_game"] = stats["points_for"] / stats["games_played"]
                    stats["points_against_per_game"] = stats["points_against"] / stats["games_played"]
                    stats["point_differential"] = stats["points_for"] - stats["points_against"]
                    stats["point_differential_per_game"] = stats["point_differential"] / stats["games_played"]
                    
                    # Update efficiency ratings using existing fields
                    if "offensiveRating" in stats:
                        stats["offensiveRating"] = min(100, max(1, int((stats["points_per_game"] / 40) * 100)))
                    if "defensiveRating" in stats:
                        stats["defensiveRating"] = min(100, max(1, int((100 - (stats["points_against_per_game"] / 40) * 100))))
                    if "efficiencyRating" in stats:
                        stats["efficiencyRating"] = min(100, max(1, int((stats["offensiveRating"] + stats["defensiveRating"]) / 2)))
                except Exception as e:
                    print(f"Warning: Error updating stats for {team_name}: {e}")
            else:
                # Teams that haven't played yet keep their preseason ratings
                pass
        
        return updated_teams
    
    def create_default_team_stats(self, team_name: str, conference: str) -> Dict:
        """Create default team statistics structure"""
        return {
            "name": team_name,
            "conference": conference,
            "stats": {
                "offensiveRating": 50,
                "defensiveRating": 50,
                "efficiencyRating": 50,
                "advancedRating": 50,
                "pointsPerPlay": 0.35,
                "yardsPerPlay": 5.5,
                "completionRate": 0.60,
                "thirdDownRate": 0.40,
                "redZoneRate": 0.75,
                "oppPointsPerPlay": 0.35,
                "oppYardsPerPlay": 5.5,
                "oppCompletionRate": 0.60,
                "oppThirdDownRate": 0.40,
                "oppRedZoneRate": 0.75,
                # Add new fields for tracking
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
    
    def generate_weekly_report(self, games: List[Dict], week: int) -> str:
        """Generate a comprehensive weekly report"""
        report = f"# Week {week} College Football Results Report\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Game summary
        report += f"## Game Summary\n"
        report += f"- **Total Games:** {len(games)}\n"
        report += f"- **FBS vs FBS Games:** {len([g for g in games if g.get('home_conference') != 'FCS' and g.get('away_conference') != 'FCS'])}\n"
        report += f"- **FCS Games:** {len([g for g in games if g.get('home_conference') == 'FCS' or g.get('away_conference') == 'FCS'])}\n\n"
        
        # High-scoring games
        high_scoring = sorted(games, key=lambda x: x["home_score"] + x["away_score"], reverse=True)[:5]
        report += f"## Top 5 High-Scoring Games\n"
        for game in high_scoring:
            total_score = game["home_score"] + game["away_score"]
            report += f"- **{game['home_team']} {game['home_score']} - {game['away_team']} {game['away_score']}** (Total: {total_score})\n"
        report += "\n"
        
        # Close matchups (within 7 points)
        close_games = [g for g in games if abs(g["home_score"] - g["away_score"]) <= 7]
        report += f"## Close Matchups (≤7 points)\n"
        report += f"- **Total Close Games:** {len(close_games)}\n"
        for game in close_games:
            margin = abs(game["home_score"] - game["away_score"])
            report += f"- {game['home_team']} {game['home_score']} - {game['away_team']} {game['away_score']} (Margin: {margin})\n"
        report += "\n"
        
        # Conference performance
        conference_wins = {}
        for game in games:
            if game["home_score"] > game["away_score"]:
                conf = game.get("home_conference", "Unknown")
                conference_wins[conf] = conference_wins.get(conf, 0) + 1
            else:
                conf = game.get("away_conference", "Unknown")
                conference_wins[conf] = conference_wins.get(conf, 0) + 1
        
        report += f"## Conference Performance\n"
        for conf, wins in sorted(conference_wins.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{conf}:** {wins} wins\n"
        
        return report
    
    def save_updated_teams(self, updated_teams: Dict, backup: bool = True) -> None:
        """Save updated team data to teams.json"""
        if backup and os.path.exists(self.teams_file):
            backup_file = f"teams_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.rename(self.teams_file, backup_file)
            print(f"Backed up current teams.json to {backup_file}")
        
        with open(self.teams_file, 'w') as f:
            json.dump(updated_teams, f, indent=2)
        
        print(f"Updated {self.teams_file} with new statistics")
    
    def run_weekly_update(self, week: int, backup: bool = True, generate_report: bool = True) -> Dict:
        """Run the complete weekly update process"""
        print(f"Starting Week {week} data collection...")
        
        # Get games for the week
        games = self.get_week_games(week)
        
        # Update team statistics
        updated_teams = self.update_team_statistics(games)
        
        # Save updated data
        self.save_updated_teams(updated_teams, backup)
        
        # Generate report if requested
        report = None
        if generate_report:
            report = self.generate_weekly_report(games, week)
            report_file = f"week_{week}_report.md"
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"Generated weekly report: {report_file}")
        
        return {
            "week": week,
            "games_processed": len(games),
            "teams_updated": len(updated_teams),
            "report": report
        }

def main():
    parser = argparse.ArgumentParser(description="Weekly Data Collector for College Football Predictions")
    parser.add_argument("--week", type=int, required=True, help="Week number to process")
    parser.add_argument("--api-key", type=str, help="CFBD API key (optional)")
    parser.add_argument("--backup", action="store_true", default=True, help="Backup current teams.json")
    parser.add_argument("--generate-report", action="store_true", default=True, help="Generate weekly report")
    
    args = parser.parse_args()
    
    # Initialize collector
    collector = WeeklyDataCollector(api_key=args.api_key)
    
    # Run weekly update
    try:
        result = collector.run_weekly_update(
            week=args.week,
            backup=args.backup,
            generate_report=args.generate_report
        )
        
        print(f"\n✅ Week {args.week} update completed successfully!")
        print(f"📊 Games processed: {result['games_processed']}")
        print(f"🏈 Teams updated: {result['teams_updated']}")
        
        if result['report']:
            print(f"📝 Report generated: week_{args.week}_report.md")
        
    except Exception as e:
        print(f"❌ Error during weekly update: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
