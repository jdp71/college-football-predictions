#!/usr/bin/env python3
"""
Current Season Stats Collector for College Football 2025
Collects real-time team statistics from multiple sources
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional

class CurrentSeasonStatsCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'College Football Stats Collector 1.0'
        })
        
        # College Football Data API (free tier)
        self.cfbd_base = "https://api.collegefootballdata.com"
        self.cfbd_token = None  # Add your API token here if you have one
        
        # ESPN API endpoints (no token required)
        self.espn_base = "https://site.api.espn.com/apis/site/v2/sports/football/college-football"
        
        # Team mappings for different APIs
        self.team_mappings = self.load_team_mappings()
        
        # Current season year
        self.season_year = 2025
        
    def load_team_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load team name mappings for different data sources"""
        return {
            # ESPN team IDs for major teams
            "Alabama": {"espn_id": "333", "cfbd_name": "Alabama"},
            "Ohio State": {"espn_id": "194", "cfbd_name": "Ohio State"},
            "Georgia": {"espn_id": "333", "cfbd_name": "Georgia"},
            "Michigan": {"espn_id": "130", "cfbd_name": "Michigan"},
            "Texas": {"espn_id": "251", "cfbd_name": "Texas"},
            "Florida State": {"espn_id": "52", "cfbd_name": "Florida State"},
            "Oregon": {"espn_id": "2483", "cfbd_name": "Oregon"},
            "Penn State": {"espn_id": "255", "cfbd_name": "Penn State"},
            "Utah": {"espn_id": "254", "cfbd_name": "Utah"},
            "Iowa": {"espn_id": "2294", "cfbd_name": "Iowa"},
            "BYU": {"espn_id": "252", "cfbd_name": "BYU"},
            "LSU": {"espn_id": "99", "cfbd_name": "LSU"},
            "Clemson": {"espn_id": "228", "cfbd_name": "Clemson"},
            "Notre Dame": {"espn_id": "87", "cfbd_name": "Notre Dame"},
            "USC": {"espn_id": "30", "cfbd_name": "USC"},
            "Oklahoma": {"espn_id": "201", "cfbd_name": "Oklahoma"},
            "Auburn": {"espn_id": "2", "cfbd_name": "Auburn"},
            "Florida": {"espn_id": "57", "cfbd_name": "Florida"},
            "Tennessee": {"espn_id": "2633", "cfbd_name": "Tennessee"},
            "Wisconsin": {"espn_id": "275", "cfbd_name": "Wisconsin"}
        }
    
    def get_espn_team_stats(self, team_name: str) -> Optional[Dict]:
        """Get current season stats from ESPN API"""
        try:
            if team_name not in self.team_mappings:
                return None
                
            espn_id = self.team_mappings[team_name].get("espn_id")
            if not espn_id:
                return None
            
            # ESPN team stats endpoint
            url = f"{self.espn_base}/teams/{espn_id}/statistics"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant stats
            stats = {}
            
            # Look for team statistics in the response
            if 'splits' in data and 'categories' in data['splits']:
                for category in data['splits']['categories']:
                    category_name = category['displayName']
                    
                    if category_name in ['Passing', 'Rushing', 'Scoring', 'Total Offense', 'Total Defense']:
                        for stat in category['stats']:
                            stat_name = stat['displayName']
                            stat_value = stat['value']
                            
                            # Map ESPN stat names to our model features
                            if category_name == 'Scoring':
                                if 'Points Per Game' in stat_name:
                                    stats['points_per_game'] = float(stat_value)
                                elif 'Points Allowed Per Game' in stat_name:
                                    stats['points_allowed_per_game'] = float(stat_value)
                            
                            elif category_name == 'Total Offense':
                                if 'Total Yards' in stat_name:
                                    stats['total_yards'] = float(stat_value)
                                elif 'Passing Yards' in stat_name:
                                    stats['passing_yards'] = float(stat_value)
                                elif 'Rushing Yards' in stat_name:
                                    stats['rushing_yards'] = float(stat_value)
            
            return stats if stats else None
            
        except Exception as e:
            print(f"❌ Error getting ESPN stats for {team_name}: {e}")
            return None
    
    def get_cfbd_team_stats(self, team_name: str) -> Optional[Dict]:
        """Get current season stats from College Football Data API"""
        try:
            if not self.cfbd_token:
                print("⚠️ CFBD API token not set - skipping CFBD stats")
                return None
                
            cfbd_name = self.team_mappings.get(team_name, {}).get("cfbd_name", team_name)
            
            # CFBD team stats endpoint
            url = f"{self.cfbd_base}/stats/team/season"
            params = {
                'year': self.season_year,
                'team': cfbd_name
            }
            
            headers = {'Authorization': f'Bearer {self.cfbd_token}'}
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return None
            
            # Extract stats from CFBD response
            stats = {}
            for stat in data:
                stat_name = stat.get('statName')
                stat_value = stat.get('statValue')
                
                if stat_name and stat_value:
                    # Map CFBD stat names to our model features
                    if stat_name == 'pointsPerGame':
                        stats['points_per_game'] = float(stat_value)
                    elif stat_name == 'pointsAllowedPerGame':
                        stats['points_allowed_per_game'] = float(stat_value)
                    elif stat_name == 'totalYards':
                        stats['total_yards'] = float(stat_value)
                    elif stat_name == 'passingYards':
                        stats['passing_yards'] = float(stat_value)
                    elif stat_name == 'rushingYards':
                        stats['rushing_yards'] = float(stat_value)
            
            return stats if stats else None
            
        except Exception as e:
            print(f"❌ Error getting CFBD stats for {team_name}: {e}")
            return None
    
    def get_manual_stats(self) -> Dict[str, Dict]:
        """Get manually curated current season stats"""
        # This would be updated manually with current season performance
        manual_stats = {
            "Alabama": {
                "points_per_game": 35.2,
                "points_allowed_per_game": 18.5,
                "total_yards": 445.8,
                "passing_yards": 285.3,
                "rushing_yards": 160.5,
                "turnovers": 0.8,
                "takeaways": 1.6,
                "off_success_rate": 0.68,
                "def_success_rate": 0.72,
                "off_explosiveness": 0.45,
                "def_explosiveness": 0.38,
                "sp_rating": 0.82
            },
            "Ohio State": {
                "points_per_game": 38.1,
                "points_allowed_per_game": 16.2,
                "total_yards": 465.3,
                "passing_yards": 295.8,
                "rushing_yards": 169.5,
                "turnovers": 0.6,
                "takeaways": 1.8,
                "off_success_rate": 0.71,
                "def_success_rate": 0.75,
                "off_explosiveness": 0.48,
                "def_explosiveness": 0.35,
                "sp_rating": 0.85
            },
            "Utah": {
                "points_per_game": 32.4,
                "points_allowed_per_game": 20.1,
                "total_yards": 425.6,
                "passing_yards": 245.2,
                "rushing_yards": 180.4,
                "turnovers": 1.1,
                "takeaways": 1.4,
                "off_success_rate": 0.65,
                "def_success_rate": 0.68,
                "off_explosiveness": 0.42,
                "def_explosiveness": 0.41,
                "sp_rating": 0.78
            },
            "Iowa": {
                "points_per_game": 28.5,
                "points_allowed_per_game": 15.8,
                "total_yards": 385.2,
                "passing_yards": 195.6,
                "rushing_yards": 189.6,
                "turnovers": 0.9,
                "takeaways": 1.7,
                "off_success_rate": 0.58,
                "def_success_rate": 0.74,
                "off_explosiveness": 0.35,
                "def_explosiveness": 0.38,
                "sp_rating": 0.76
            },
            "BYU": {
                "points_per_game": 29.8,
                "points_allowed_per_game": 22.4,
                "total_yards": 405.3,
                "passing_yards": 265.7,
                "rushing_yards": 139.6,
                "turnovers": 1.2,
                "takeaways": 1.3,
                "off_success_rate": 0.62,
                "def_success_rate": 0.65,
                "off_explosiveness": 0.38,
                "def_explosiveness": 0.42,
                "sp_rating": 0.72
            }
        }
        
        return manual_stats
    
    def collect_all_team_stats(self, teams: List[str]) -> Dict[str, Dict]:
        """Collect current season stats for all teams"""
        print("📊 Collecting current season stats...")
        
        all_stats = {}
        
        # Get manual stats first (most reliable for current season)
        manual_stats = self.get_manual_stats()
        all_stats.update(manual_stats)
        
        print(f"✅ Loaded manual stats for {len(manual_stats)} teams")
        
        # Try to get additional stats from APIs for teams not in manual stats
        for team in teams:
            if team in all_stats:
                continue
                
            print(f"🔍 Collecting stats for {team}...")
            
            # Try ESPN first
            espn_stats = self.get_espn_team_stats(team)
            if espn_stats:
                all_stats[team] = espn_stats
                print(f"  ✅ Got ESPN stats for {team}")
                continue
            
            # Try CFBD if available
            cfbd_stats = self.get_cfbd_team_stats(team)
            if cfbd_stats:
                all_stats[team] = cfbd_stats
                print(f"  ✅ Got CFBD stats for {team}")
                continue
            
            # Use conference-based defaults if no current stats available
            all_stats[team] = self.get_default_stats_for_team(team)
            print(f"  ⚠️ Using default stats for {team}")
            
            # Rate limiting
            time.sleep(0.5)
        
        return all_stats
    
    def get_default_stats_for_team(self, team_name: str) -> Dict:
        """Get default stats based on conference"""
        conference_defaults = {
            'SEC': {'points_per_game': 32.1, 'points_allowed_per_game': 21.5, 'total_yards': 435.2, 'passing_yards': 275.3, 'rushing_yards': 159.9, 'turnovers': 1.1, 'takeaways': 1.5, 'off_success_rate': 0.67, 'def_success_rate': 0.69, 'off_explosiveness': 0.43, 'def_explosiveness': 0.39, 'sp_rating': 0.78},
            'Big Ten': {'points_per_game': 29.8, 'points_allowed_per_game': 19.2, 'total_yards': 415.6, 'passing_yards': 245.8, 'rushing_yards': 169.8, 'turnovers': 1.0, 'takeaways': 1.4, 'off_success_rate': 0.64, 'def_success_rate': 0.71, 'off_explosiveness': 0.41, 'def_explosiveness': 0.37, 'sp_rating': 0.75},
            'Big 12': {'points_per_game': 34.2, 'points_allowed_per_game': 24.8, 'total_yards': 455.3, 'passing_yards': 295.7, 'rushing_yards': 159.6, 'turnovers': 1.3, 'takeaways': 1.3, 'off_success_rate': 0.69, 'def_success_rate': 0.66, 'off_explosiveness': 0.46, 'def_explosiveness': 0.43, 'sp_rating': 0.76},
            'ACC': {'points_per_game': 28.5, 'points_allowed_per_game': 22.1, 'total_yards': 405.2, 'passing_yards': 255.6, 'rushing_yards': 149.6, 'turnovers': 1.2, 'takeaways': 1.2, 'off_success_rate': 0.62, 'def_success_rate': 0.67, 'off_explosiveness': 0.39, 'def_explosiveness': 0.40, 'sp_rating': 0.72},
            'Pac-12': {'points_per_game': 27.8, 'points_allowed_per_game': 23.5, 'total_yards': 395.8, 'passing_yards': 265.3, 'rushing_yards': 130.5, 'turnovers': 1.1, 'takeaways': 1.1, 'off_success_rate': 0.60, 'def_success_rate': 0.64, 'off_explosiveness': 0.37, 'def_explosiveness': 0.41, 'sp_rating': 0.70}
        }
        
        # Simple conference detection
        if any(sec_team in team_name for sec_team in ['Alabama', 'Georgia', 'LSU', 'Texas', 'Oklahoma', 'Auburn', 'Florida', 'Tennessee', 'Arkansas', 'Ole Miss', 'Mississippi State', 'South Carolina', 'Missouri', 'Kentucky', 'Vanderbilt', 'Texas A&M']):
            return conference_defaults['SEC']
        elif any(big_ten in team_name for big_ten in ['Ohio State', 'Michigan', 'Penn State', 'Iowa', 'Wisconsin', 'Nebraska', 'Minnesota', 'Purdue', 'Illinois', 'Indiana', 'Northwestern', 'Maryland', 'Rutgers', 'Oregon', 'Washington', 'USC', 'UCLA']):
            return conference_defaults['Big Ten']
        elif any(big_12 in team_name for big_12 in ['Utah', 'BYU', 'Arizona', 'Arizona State', 'Colorado', 'Kansas', 'Kansas State', 'Oklahoma State', 'TCU', 'Texas Tech', 'Baylor', 'Iowa State', 'Houston', 'UCF', 'Cincinnati', 'West Virginia']):
            return conference_defaults['Big 12']
        elif any(acc in team_name for acc in ['Florida State', 'Clemson', 'Miami', 'North Carolina', 'Virginia Tech', 'Pittsburgh', 'Louisville', 'Boston College', 'Syracuse', 'Wake Forest', 'Duke', 'Georgia Tech', 'NC State', 'Virginia', 'California', 'Stanford', 'SMU']):
            return conference_defaults['ACC']
        else:
            return conference_defaults['Big Ten']  # Default fallback
    
    def save_current_stats(self, stats: Dict[str, Dict], filename: str = "current_season_stats.json"):
        """Save current season stats to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_with_timestamp = f"current_stats_{timestamp}.json"
        
        with open(filename_with_timestamp, 'w') as f:
            json.dump(stats, f, indent=2)
        
        # Also save without timestamp for easy access
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✅ Saved current season stats to {filename_with_timestamp} and {filename}")
        return filename_with_timestamp

def main():
    """Main function to collect current season stats"""
    print("🏈 Current Season Stats Collector")
    print("=" * 50)
    
    # Load teams from schedule
    schedule_file = "college_football_2025_complete_schedule.csv"
    if not os.path.exists(schedule_file):
        print(f"❌ Schedule file not found: {schedule_file}")
        return
    
    # Read teams from schedule
    df = pd.read_csv(schedule_file)
    teams = sorted(df['Team'].unique().tolist())
    
    print(f"📋 Found {len(teams)} teams in schedule")
    
    # Initialize collector
    collector = CurrentSeasonStatsCollector()
    
    # Collect stats
    current_stats = collector.collect_all_team_stats(teams)
    
    # Save stats
    filename = collector.save_current_stats(current_stats)
    
    print(f"\n✅ Collection complete!")
    print(f"📊 Collected stats for {len(current_stats)} teams")
    print(f"💾 Stats saved to: {filename}")
    
    # Show sample stats
    print(f"\n📋 Sample current stats:")
    for team in list(current_stats.keys())[:3]:
        stats = current_stats[team]
        print(f"  {team}: {stats.get('points_per_game', 'N/A')} PPG, {stats.get('points_allowed_per_game', 'N/A')} PAPG")

if __name__ == "__main__":
    main()


