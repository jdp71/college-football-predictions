#!/usr/bin/env python3
"""
Weekly Data Collector for College Football Predictions
Collects game results and updates team statistics after each week
"""

import requests
import pandas as pd
import json
import argparse
from datetime import datetime
import time
import os

class WeeklyDataCollector:
    def __init__(self):
        self.base_url = "https://api.collegefootballdata.com"
        self.api_key = os.getenv('CFBD_API_KEY', '')  # Set your API key as environment variable
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
    def collect_week_results(self, week_number, year=2025):
        """Collect all game results for a specific week"""
        print(f"Collecting Week {week_number} results for {year}...")
        
        try:
            # Get games for the week
            url = f"{self.base_url}/games"
            params = {
                'year': year,
                'week': week_number,
                'seasonType': 'regular'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            games = response.json()
            print(f"Found {len(games)} games for Week {week_number}")
            
            # Process game results
            results = []
            for game in games:
                if game.get('home_score') is not None and game.get('away_score') is not None:
                    result = {
                        'week': week_number,
                        'year': year,
                        'home_team': game['home_team'],
                        'away_team': game['away_team'],
                        'home_score': game['home_score'],
                        'away_score': game['away_score'],
                        'home_win': game['home_score'] > game['away_score'],
                        'game_id': game.get('id'),
                        'date': game.get('start_date'),
                        'venue': game.get('venue'),
                        'conference_game': game.get('conference_game', False)
                    }
                    results.append(result)
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"Error collecting Week {week_number} results: {e}")
            return pd.DataFrame()
    
    def get_team_stats(self, team_name, year=2025):
        """Get current team statistics"""
        try:
            url = f"{self.base_url}/teams/stats"
            params = {
                'year': year,
                'team': team_name
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            stats = response.json()
            return stats
            
        except Exception as e:
            print(f"Error getting stats for {team_name}: {e}")
            return {}
    
    def update_team_statistics(self, week_results, existing_teams_file='college-football-app/teams.json'):
        """Update team statistics with new game results"""
        print("Updating team statistics...")
        
        # Load existing team data
        try:
            with open(existing_teams_file, 'r') as f:
                teams_data = json.load(f)
        except FileNotFoundError:
            print(f"Teams file not found: {existing_teams_file}")
            return False
        
        # Create a mapping of team names
        team_map = {team['name']: team for team in teams_data['teams']}
        
        # Process each game result
        for _, game in week_results.iterrows():
            home_team = game['home_team']
            away_team = game['away_team']
            
            # Update home team stats
            if home_team in team_map:
                self._update_team_game_stats(team_map[home_team], game, is_home=True)
            
            # Update away team stats
            if away_team in team_map:
                self._update_team_game_stats(team_map[away_team], game, is_home=False)
        
        # Save updated team data
        try:
            with open(existing_teams_file, 'w') as f:
                json.dump(teams_data, f, indent=2)
            print(f"Updated team statistics saved to {existing_teams_file}")
            return True
        except Exception as e:
            print(f"Error saving updated team data: {e}")
            return False
    
    def _update_team_game_stats(self, team_data, game, is_home=True):
        """Update individual team statistics with game result"""
        
        # Initialize stats structure if it doesn't exist
        if 'current_season' not in team_data:
            team_data['current_season'] = {
                'games_played': 0,
                'wins': 0,
                'losses': 0,
                'points_for': 0,
                'points_against': 0,
                'total_yards': 0,
                'yards_allowed': 0,
                'turnovers': 0,
                'turnovers_forced': 0
            }
        
        # Update basic stats
        team_data['current_season']['games_played'] += 1
        
        if is_home:
            team_score = game['home_score']
            opponent_score = game['away_score']
            team_won = game['home_win']
        else:
            team_score = game['away_score']
            opponent_score = game['home_score']
            team_won = not game['home_win']
        
        # Update win/loss record
        if team_won:
            team_data['current_season']['wins'] += 1
        else:
            team_data['current_season']['losses'] += 1
        
        # Update points
        team_data['current_season']['points_for'] += team_score
        team_data['current_season']['points_against'] += opponent_score
        
        # Calculate averages
        games_played = team_data['current_season']['games_played']
        if games_played > 0:
            team_data['current_season']['ppg'] = team_data['current_season']['points_for'] / games_played
            team_data['current_season']['papg'] = team_data['current_season']['points_against'] / games_played
    
    def save_week_results(self, week_results, week_number, year=2025):
        """Save week results to a CSV file"""
        filename = f"week_{week_number}_{year}_results.csv"
        week_results.to_csv(filename, index=False)
        print(f"Week {week_number} results saved to {filename}")
        return filename
    
    def generate_weekly_report(self, week_results, week_number):
        """Generate a weekly report of results"""
        if week_results.empty:
            print("No results to report")
            return
        
        print(f"\n{'='*50}")
        print(f"WEEK {week_number} RESULTS REPORT")
        print(f"{'='*50}")
        
        # Basic stats
        total_games = len(week_results)
        home_wins = week_results['home_win'].sum()
        away_wins = total_games - home_wins
        home_win_rate = home_wins / total_games * 100
        
        print(f"Total Games: {total_games}")
        print(f"Home Wins: {home_wins} ({home_win_rate:.1f}%)")
        print(f"Away Wins: {away_wins} ({100-home_win_rate:.1f}%)")
        
        # High-scoring games
        week_results['total_points'] = week_results['home_score'] + week_results['away_score']
        high_scoring = week_results[week_results['total_points'] >= 70]
        if not high_scoring.empty:
            print(f"\nHigh-Scoring Games (70+ points):")
            for _, game in high_scoring.iterrows():
                print(f"  {game['home_team']} {game['home_score']} - {game['away_team']} {game['away_score']} ({game['total_points']} total)")
        
        # Close games
        week_results['point_diff'] = abs(week_results['home_score'] - week_results['away_score'])
        close_games = week_results[week_results['point_diff'] <= 7]
        if not close_games.empty:
            print(f"\nClose Games (7 points or less):")
            for _, game in close_games.iterrows():
                print(f"  {game['home_team']} {game['home_score']} - {game['away_team']} {game['away_score']} ({game['point_diff']} point diff)")
        
        print(f"\n{'='*50}")

def main():
    parser = argparse.ArgumentParser(description='Collect weekly college football results')
    parser.add_argument('--week', type=int, required=True, help='Week number to collect')
    parser.add_argument('--year', type=int, default=2025, help='Year (default: 2025)')
    parser.add_argument('--update-teams', action='store_true', help='Update team statistics')
    parser.add_argument('--generate-report', action='store_true', help='Generate weekly report')
    
    args = parser.parse_args()
    
    collector = WeeklyDataCollector()
    
    # Collect week results
    week_results = collector.collect_week_results(args.week, args.year)
    
    if week_results.empty:
        print("No results collected. Exiting.")
        return
    
    # Save results
    results_file = collector.save_week_results(week_results, args.week, args.year)
    
    # Update team statistics if requested
    if args.update_teams:
        success = collector.update_team_statistics(week_results)
        if success:
            print("Team statistics updated successfully!")
        else:
            print("Failed to update team statistics")
    
    # Generate report if requested
    if args.generate_report:
        collector.generate_weekly_report(week_results, args.week)
    
    print(f"\nWeek {args.week} data collection complete!")
    print(f"Results saved to: {results_file}")

if __name__ == "__main__":
    main()
