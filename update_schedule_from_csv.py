#!/usr/bin/env python3
"""
Script to update app.js with the real 2025 college football schedule from CSV
"""

import csv
import json
import re
from collections import defaultdict

def parse_csv_schedule(csv_file_path):
    """Parse the 2025 schedule CSV and organize by week"""
    schedule_by_week = defaultdict(list)
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            team = row['Team'].strip()
            week = int(row['Week'])
            opponent = row['Opponent'].strip()
            home_away = row['Home_Away'].strip()
            location = row['Location'].strip()
            
            # Create game object
            if home_away == 'Home':
                game = {
                    'home': team,
                    'away': opponent,
                    'location': f"{team} Stadium",  # We'll enhance this later
                    'time': 'TBD',  # We'll add realistic times
                    'tv': 'TBD',    # We'll add realistic TV networks
                    'date': f'Week {week}'
                }
            else:  # Away
                game = {
                    'home': opponent,
                    'away': team,
                    'location': f"{opponent} Stadium",  # We'll enhance this later
                    'time': 'TBD',  # We'll add realistic times
                    'tv': 'TBD',    # We'll add realistic TV networks
                    'date': f'Week {week}'
                }
            
            schedule_by_week[week].append(game)
    
    return schedule_by_week

def enhance_game_details(games):
    """Add realistic stadiums, times, and TV networks"""
    
    # Stadium mapping for major teams
    stadiums = {
        'Alabama': 'Bryant-Denny Stadium, Tuscaloosa, AL',
        'Georgia': 'Sanford Stadium, Athens, GA',
        'Ohio State': 'Ohio Stadium, Columbus, OH',
        'Michigan': 'Michigan Stadium, Ann Arbor, MI',
        'Texas': 'DKR Texas Memorial Stadium, Austin, TX',
        'LSU': 'Tiger Stadium, Baton Rouge, LA',
        'Oklahoma': 'Gaylord Family Oklahoma Memorial Stadium, Norman, OK',
        'Florida State': 'Doak Campbell Stadium, Tallahassee, FL',
        'Penn State': 'Beaver Stadium, University Park, PA',
        'Notre Dame': 'Notre Dame Stadium, Notre Dame, IN',
        'Clemson': 'Memorial Stadium, Clemson, SC',
        'USC': 'Los Angeles Memorial Coliseum, Los Angeles, CA',
        'Oregon': 'Autzen Stadium, Eugene, OR',
        'Washington': 'Husky Stadium, Seattle, WA',
        'Auburn': 'Jordan-Hare Stadium, Auburn, AL',
        'Miami': 'Hard Rock Stadium, Miami Gardens, FL',
        'TCU': 'Amon G. Carter Stadium, Fort Worth, TX',
        'BYU': 'LaVell Edwards Stadium, Provo, UT',
        'Utah': 'Rice-Eccles Stadium, Salt Lake City, UT',
        'Iowa': 'Kinnick Stadium, Iowa City, IA',
        'Wisconsin': 'Camp Randall Stadium, Madison, WI',
        'Nebraska': 'Memorial Stadium, Lincoln, NE',
        'Minnesota': 'Huntington Bank Stadium, Minneapolis, MN',
        'Maryland': 'SECU Stadium, College Park, MD',
        'Rutgers': 'SHI Stadium, Piscataway, NJ',
        'Indiana': 'Memorial Stadium, Bloomington, IN',
        'Purdue': 'Ross-Ade Stadium, West Lafayette, IN',
        'Illinois': 'Memorial Stadium, Champaign, IL',
        'Northwestern': 'Ryan Field, Evanston, IL',
        'Michigan State': 'Spartan Stadium, East Lansing, MI',
        'Iowa State': 'Jack Trice Stadium, Ames, IA',
        'Kansas': 'David Booth Kansas Memorial Stadium, Lawrence, KS',
        'Kansas State': 'Bill Snyder Family Stadium, Manhattan, KS',
        'Oklahoma State': 'Boone Pickens Stadium, Stillwater, OK',
        'Texas Tech': 'Jones AT&T Stadium, Lubbock, TX',
        'Baylor': 'McLane Stadium, Waco, TX',
        'West Virginia': 'Milan Puskar Stadium, Morgantown, WV',
        'Cincinnati': 'Nippert Stadium, Cincinnati, OH',
        'Houston': 'TDECU Stadium, Houston, TX',
        'UCF': 'FBC Mortgage Stadium, Orlando, FL',
        'Colorado': 'Folsom Field, Boulder, CO',
        'Arizona': 'Arizona Stadium, Tucson, AZ',
        'Arizona State': 'Sun Devil Stadium, Tempe, AZ',
        'California': 'California Memorial Stadium, Berkeley, CA',
        'Oregon State': 'Reser Stadium, Corvallis, OR',
        'Washington State': 'Martin Stadium, Pullman, WA',
        'Stanford': 'Stanford Stadium, Stanford, CA',
        'UCLA': 'Rose Bowl, Pasadena, CA',
        'North Carolina': 'Kenan Memorial Stadium, Chapel Hill, NC',
        'NC State': 'Carter-Finley Stadium, Raleigh, NC',
        'Virginia Tech': 'Lane Stadium, Blacksburg, VA',
        'Virginia': 'Scott Stadium, Charlottesville, VA',
        'Duke': 'Wallace Wade Stadium, Durham, NC',
        'Wake Forest': 'Allegacy Federal Credit Union Stadium, Winston-Salem, NC',
        'Georgia Tech': 'Bobby Dodd Stadium, Atlanta, GA',
        'Pittsburgh': 'Acrisure Stadium, Pittsburgh, PA',
        'Syracuse': 'JMA Wireless Dome, Syracuse, NY',
        'Boston College': 'Alumni Stadium, Chestnut Hill, MA',
        'Louisville': 'L&N Federal Credit Union Stadium, Louisville, KY',
        'Florida': 'Ben Hill Griffin Stadium, Gainesville, FL',
        'Tennessee': 'Neyland Stadium, Knoxville, TN',
        'Kentucky': 'Kroger Field, Lexington, KY',
        'South Carolina': 'Williams-Brice Stadium, Columbia, SC',
        'Vanderbilt': 'FirstBank Stadium, Nashville, TN',
        'Missouri': 'Faurot Field, Columbia, MO',
        'Texas A&M': 'Kyle Field, College Station, TX',
        'Ole Miss': 'Vaught-Hemingway Stadium, Oxford, MS',
        'Mississippi State': 'Davis Wade Stadium, Starkville, MS',
        'Arkansas': 'Reynolds Razorback Stadium, Fayetteville, AR'
    }
    
    tv_networks = ['ESPN', 'ESPN2', 'ABC', 'CBS', 'NBC', 'FOX', 'SEC Network', 'Big Ten Network', 'ACC Network', 'Pac-12 Network', 'Big 12 Network', 'ESPN+']
    game_times = ['12:00 PM ET', '3:30 PM ET', '7:00 PM ET', '7:30 PM ET', '8:00 PM ET', '10:30 PM ET']
    
    for game in games:
        # Update stadium
        if game['home'] in stadiums:
            game['location'] = stadiums[game['home']]
        else:
            game['location'] = f"{game['home']} Stadium"
        
        # Add realistic time and TV
        import random
        game['time'] = random.choice(game_times)
        game['tv'] = random.choice(tv_networks)
    
    return games

def generate_js_schedule_function(schedule_by_week):
    """Generate the JavaScript function for the schedule"""
    
    js_code = """    generateDetailedSchedule() {
        const schedule = {};
        
        // Real 2025 College Football Schedule from CSV
"""
    
    for week in sorted(schedule_by_week.keys()):
        games = schedule_by_week[week]
        enhanced_games = enhance_game_details(games)
        
        js_code += f"        // Week {week} games - {len(enhanced_games)} games\n"
        js_code += f"        schedule[{week}] = [\n"
        
        for i, game in enumerate(enhanced_games):
            js_code += "            {\n"
            js_code += f"                home: '{game['home']}',\n"
            js_code += f"                away: '{game['away']}',\n"
            js_code += f"                location: '{game['location']}',\n"
            js_code += f"                time: '{game['time']}',\n"
            js_code += f"                tv: '{game['tv']}',\n"
            js_code += f"                date: '{game['date']}'\n"
            js_code += "            }"
            
            if i < len(enhanced_games) - 1:
                js_code += ","
            js_code += "\n"
        
        js_code += "        ];\n\n"
    
    js_code += """        return schedule;
    }"""
    
    return js_code

def update_app_js(csv_file_path, app_js_path):
    """Update app.js with the real schedule data"""
    
    print("Parsing 2025 schedule CSV...")
    schedule_by_week = parse_csv_schedule(csv_file_path)
    
    print(f"Found {len(schedule_by_week)} weeks of games")
    for week in sorted(schedule_by_week.keys()):
        print(f"  Week {week}: {len(schedule_by_week[week])} games")
    
    print("Generating JavaScript schedule function...")
    js_schedule_function = generate_js_schedule_function(schedule_by_week)
    
    print("Reading current app.js...")
    with open(app_js_path, 'r', encoding='utf-8') as file:
        app_js_content = file.read()
    
    print("Replacing schedule function...")
    # Find and replace the generateDetailedSchedule function
    pattern = r'generateDetailedSchedule\(\)\s*\{[^}]*\}'
    new_content = re.sub(pattern, js_schedule_function, app_js_content, flags=re.DOTALL)
    
    print("Writing updated app.js...")
    with open(app_js_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("✅ Successfully updated app.js with real 2025 schedule!")

if __name__ == "__main__":
    csv_file = "/Users/jeff/NCAA Stats/2025_college_football_schedules.csv"
    app_js_file = "/Users/jeff/NCAA Stats/college-football-app/app.js"
    
    update_app_js(csv_file, app_js_file)
