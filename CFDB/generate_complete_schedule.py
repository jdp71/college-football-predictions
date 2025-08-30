#!/usr/bin/env python3
import csv
import json
from datetime import datetime, timedelta

def parse_csv_schedule():
    """Parse the CSV file and organize games by week"""
    schedule = {}
    
    with open('2025_college_football_schedules.csv', 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            team = row['Team']
            week = int(row['Week'])
            opponent = row['Opponent']
            home_away = row['Home_Away']
            
            if week not in schedule:
                schedule[week] = []
            
            # Determine home and away teams
            if home_away == 'Home':
                home_team = team
                away_team = opponent
            else:  # Away
                home_team = opponent
                away_team = team
            
            # Check if this game is already added (avoid duplicates)
            game_exists = any(
                (g['home'] == home_team and g['away'] == away_team) or
                (g['home'] == away_team and g['away'] == home_team)
                for g in schedule[week]
            )
            
            if not game_exists:
                # Generate game details
                game = {
                    'home': home_team,
                    'away': away_team,
                    'location': f'{home_team} Stadium',
                    'time': 'TBD',
                    'tv': 'TBD',
                    'date': f'Saturday, Week {week}, 2025'
                }
                schedule[week].append(game)
    
    return schedule

def generate_stadium_names():
    """Generate realistic stadium names for teams"""
    stadiums = {
        'Air Force': 'Falcon Stadium, Colorado Springs, CO',
        'Akron': 'InfoCision Stadium, Akron, OH',
        'Alabama': 'Bryant-Denny Stadium, Tuscaloosa, AL',
        'Appalachian State': 'Kidd Brewer Stadium, Boone, NC',
        'Arizona': 'Arizona Stadium, Tucson, AZ',
        'Arizona State': 'Sun Devil Stadium, Tempe, AZ',
        'Arkansas': 'Donald W. Reynolds Razorback Stadium, Fayetteville, AR',
        'Arkansas State': 'Centennial Bank Stadium, Jonesboro, AR',
        'Army': 'Michie Stadium, West Point, NY',
        'Auburn': 'Jordan-Hare Stadium, Auburn, AL',
        'BYU': 'LaVell Edwards Stadium, Provo, UT',
        'Ball State': 'Scheumann Stadium, Muncie, IN',
        'Baylor': 'McLane Stadium, Waco, TX',
        'Boise State': 'Albertsons Stadium, Boise, ID',
        'Boston College': 'Alumni Stadium, Chestnut Hill, MA',
        'Bowling Green': 'Doyt Perry Stadium, Bowling Green, OH',
        'Buffalo': 'UB Stadium, Buffalo, NY',
        'California': 'California Memorial Stadium, Berkeley, CA',
        'Central Michigan': 'Kelly/Shorts Stadium, Mount Pleasant, MI',
        'Charlotte': 'Jerry Richardson Stadium, Charlotte, NC',
        'Cincinnati': 'Nippert Stadium, Cincinnati, OH',
        'Clemson': 'Memorial Stadium, Clemson, SC',
        'Coastal Carolina': 'Brooks Stadium, Conway, SC',
        'Colorado': 'Folsom Field, Boulder, CO',
        'Colorado State': 'Canvas Stadium, Fort Collins, CO',
        'Duke': 'Wallace Wade Stadium, Durham, NC',
        'East Carolina': 'Dowdy-Ficklen Stadium, Greenville, NC',
        'Eastern Michigan': 'Rynearson Stadium, Ypsilanti, MI',
        'Florida': 'Ben Hill Griffin Stadium, Gainesville, FL',
        'Florida Atlantic': 'FAU Stadium, Boca Raton, FL',
        'Florida International': 'Riccardo Silva Stadium, Miami, FL',
        'Florida State': 'Doak Campbell Stadium, Tallahassee, FL',
        'Fresno State': 'Valley Children\'s Stadium, Fresno, CA',
        'Georgia': 'Sanford Stadium, Athens, GA',
        'Georgia Southern': 'Paulson Stadium, Statesboro, GA',
        'Georgia State': 'Center Parc Stadium, Atlanta, GA',
        'Georgia Tech': 'Bobby Dodd Stadium, Atlanta, GA',
        'Hawaii': 'Clarence T.C. Ching Athletics Complex, Honolulu, HI',
        'Houston': 'TDECU Stadium, Houston, TX',
        'Illinois': 'Memorial Stadium, Champaign, IL',
        'Indiana': 'Memorial Stadium, Bloomington, IN',
        'Iowa': 'Kinnick Stadium, Iowa City, IA',
        'Iowa State': 'Jack Trice Stadium, Ames, IA',
        'Jacksonville State': 'Burgess-Snow Field, Jacksonville, AL',
        'James Madison': 'Bridgeforth Stadium, Harrisonburg, VA',
        'Kansas': 'David Booth Kansas Memorial Stadium, Lawrence, KS',
        'Kansas State': 'Bill Snyder Family Stadium, Manhattan, KS',
        'Kent State': 'Dix Stadium, Kent, OH',
        'Kentucky': 'Kroger Field, Lexington, KY',
        'LSU': 'Tiger Stadium, Baton Rouge, LA',
        'Liberty': 'Williams Stadium, Lynchburg, VA',
        'Louisiana': 'Cajun Field, Lafayette, LA',
        'Louisiana Monroe': 'Malone Stadium, Monroe, LA',
        'Louisiana Tech': 'Joe Aillet Stadium, Ruston, LA',
        'Louisville': 'L&N Federal Credit Union Stadium, Louisville, KY',
        'Marshall': 'Joan C. Edwards Stadium, Huntington, WV',
        'Maryland': 'SECU Stadium, College Park, MD',
        'Memphis': 'Simmons Bank Liberty Stadium, Memphis, TN',
        'Miami': 'Hard Rock Stadium, Miami Gardens, FL',
        'Miami (OH)': 'Yager Stadium, Oxford, OH',
        'Michigan': 'Michigan Stadium, Ann Arbor, MI',
        'Michigan State': 'Spartan Stadium, East Lansing, MI',
        'Middle Tennessee': 'Johnny "Red" Floyd Stadium, Murfreesboro, TN',
        'Minnesota': 'Huntington Bank Stadium, Minneapolis, MN',
        'Mississippi': 'Vaught-Hemingway Stadium, Oxford, MS',
        'Mississippi State': 'Davis Wade Stadium, Starkville, MS',
        'Missouri': 'Memorial Stadium, Columbia, MO',
        'NC State': 'Carter-Finley Stadium, Raleigh, NC',
        'Navy': 'Navy-Marine Corps Memorial Stadium, Annapolis, MD',
        'Nebraska': 'Memorial Stadium, Lincoln, NE',
        'Nevada': 'Mackay Stadium, Reno, NV',
        'New Mexico': 'University Stadium, Albuquerque, NM',
        'New Mexico State': 'Aggie Memorial Stadium, Las Cruces, NM',
        'North Carolina': 'Kenan Memorial Stadium, Chapel Hill, NC',
        'North Texas': 'Apogee Stadium, Denton, TX',
        'Northern Illinois': 'Huskie Stadium, DeKalb, IL',
        'Northwestern': 'Ryan Field, Evanston, IL',
        'Notre Dame': 'Notre Dame Stadium, Notre Dame, IN',
        'Ohio': 'Peden Stadium, Athens, OH',
        'Ohio State': 'Ohio Stadium, Columbus, OH',
        'Oklahoma': 'Gaylord Family Oklahoma Memorial Stadium, Norman, OK',
        'Oklahoma State': 'Boone Pickens Stadium, Stillwater, OK',
        'Old Dominion': 'S.B. Ballard Stadium, Norfolk, VA',
        'Oregon': 'Autzen Stadium, Eugene, OR',
        'Penn State': 'Beaver Stadium, University Park, PA',
        'Pittsburgh': 'Acrisure Stadium, Pittsburgh, PA',
        'Purdue': 'Ross-Ade Stadium, West Lafayette, IN',
        'Rice': 'Rice Stadium, Houston, TX',
        'Rutgers': 'SHI Stadium, Piscataway, NJ',
        'SMU': 'Gerald J. Ford Stadium, Dallas, TX',
        'Sam Houston': 'Bowers Stadium, Huntsville, TX',
        'San Diego State': 'Snapdragon Stadium, San Diego, CA',
        'San Jose State': 'CEFCU Stadium, San Jose, CA',
        'South Alabama': 'Hancock Whitney Stadium, Mobile, AL',
        'South Carolina': 'Williams-Brice Stadium, Columbia, SC',
        'South Florida': 'Raymond James Stadium, Tampa, FL',
        'Stanford': 'Stanford Stadium, Stanford, CA',
        'Syracuse': 'JMA Wireless Dome, Syracuse, NY',
        'TCU': 'Amon G. Carter Stadium, Fort Worth, TX',
        'Temple': 'Lincoln Financial Field, Philadelphia, PA',
        'Tennessee': 'Neyland Stadium, Knoxville, TN',
        'Texas': 'DKR Texas Memorial Stadium, Austin, TX',
        'Texas A&M': 'Kyle Field, College Station, TX',
        'Texas State': 'Bobcat Stadium, San Marcos, TX',
        'Texas Tech': 'Jones AT&T Stadium, Lubbock, TX',
        'Toledo': 'Glass Bowl, Toledo, OH',
        'Troy': 'Veterans Memorial Stadium, Troy, AL',
        'Tulane': 'Yulman Stadium, New Orleans, LA',
        'Tulsa': 'H.A. Chapman Stadium, Tulsa, OK',
        'UAB': 'Protective Stadium, Birmingham, AL',
        'UCF': 'FBC Mortgage Stadium, Orlando, FL',
        'UCLA': 'Rose Bowl, Pasadena, CA',
        'UConn': 'Pratt & Whitney Stadium, East Hartford, CT',
        'UMass': 'McGuirk Alumni Stadium, Amherst, MA',
        'UNLV': 'Allegiant Stadium, Las Vegas, NV',
        'USC': 'Los Angeles Memorial Coliseum, Los Angeles, CA',
        'UTEP': 'Sun Bowl, El Paso, TX',
        'UTSA': 'Alamodome, San Antonio, TX',
        'Utah': 'Rice-Eccles Stadium, Salt Lake City, UT',
        'Utah State': 'Maverik Stadium, Logan, UT',
        'Vanderbilt': 'FirstBank Stadium, Nashville, TN',
        'Virginia': 'Scott Stadium, Charlottesville, VA',
        'Virginia Tech': 'Lane Stadium, Blacksburg, VA',
        'Wake Forest': 'Truist Field, Winston-Salem, NC',
        'Washington': 'Husky Stadium, Seattle, WA',
        'West Virginia': 'Milan Puskar Stadium, Morgantown, WV',
        'Western Kentucky': 'Houchens Industries-L.T. Smith Stadium, Bowling Green, KY',
        'Western Michigan': 'Waldo Stadium, Kalamazoo, MI',
        'Wisconsin': 'Camp Randall Stadium, Madison, WI',
        'Wyoming': 'War Memorial Stadium, Laramie, WY'
    }
    return stadiums

def generate_times_and_tv():
    """Generate realistic times and TV networks"""
    times = [
        '12:00 PM ET', '12:30 PM ET', '1:00 PM ET', '2:00 PM ET', '3:30 PM ET',
        '4:00 PM ET', '6:00 PM ET', '7:00 PM ET', '7:30 PM ET', '8:00 PM ET',
        '10:30 PM ET', '11:00 PM ET'
    ]
    
    tv_networks = [
        'ABC', 'CBS', 'FOX', 'NBC', 'ESPN', 'ESPN2', 'ESPN+', 'SEC Network',
        'Big Ten Network', 'ACC Network', 'Pac-12 Network', 'Big 12 Network',
        'CBS Sports Network', 'Mountain West Network'
    ]
    
    return times, tv_networks

def generate_complete_schedule():
    """Generate the complete schedule for all weeks"""
    schedule = parse_csv_schedule()
    stadiums = generate_stadium_names()
    times, tv_networks = generate_times_and_tv()
    
    import random
    random.seed(42)  # For consistent results
    
    # Base date for Week 1 (August 30, 2025)
    base_date = datetime(2025, 8, 30)
    
    complete_schedule = {}
    
    for week in range(1, 16):
        if week in schedule:
            week_games = []
            for game in schedule[week]:
                # Get stadium name
                stadium = stadiums.get(game['home'], f'{game["home"]} Stadium')
                
                # Generate realistic time and TV
                time = random.choice(times)
                tv = random.choice(tv_networks)
                
                # Calculate date for this week
                game_date = base_date + timedelta(weeks=week-1)
                date_str = game_date.strftime('%A, %B %d, %Y')
                
                week_games.append({
                    'home': game['home'],
                    'away': game['away'],
                    'location': stadium,
                    'time': time,
                    'tv': tv,
                    'date': date_str
                })
            
            complete_schedule[week] = week_games
        else:
            complete_schedule[week] = []
    
    return complete_schedule

if __name__ == "__main__":
    schedule = generate_complete_schedule()
    
    # Print summary
    for week in range(1, 16):
        game_count = len(schedule[week])
        print(f"Week {week}: {game_count} games")
    
    # Save to JSON for reference
    with open('complete_schedule.json', 'w') as f:
        json.dump(schedule, f, indent=2)
    
    print(f"\nComplete schedule saved to complete_schedule.json")
    print(f"Total games across all weeks: {sum(len(games) for games in schedule.values())}")
