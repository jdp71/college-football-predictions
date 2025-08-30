#!/usr/bin/env python3
import json
import re

def load_complete_schedule():
    """Load the complete schedule from JSON"""
    with open('complete_schedule.json', 'r') as f:
        return json.load(f)

def format_week_schedule(week_games):
    """Format a week's games into JavaScript array format"""
    if not week_games:
        return "[]"
    
    formatted_games = []
    for game in week_games:
        formatted_game = f"""            {{ 
                home: '{game['home']}', 
                away: '{game['away']}', 
                location: '{game['location']}',
                time: '{game['time']}',
                tv: '{game['tv']}',
                date: '{game['date']}'
            }}"""
        formatted_games.append(formatted_game)
    
    return "[\n" + ",\n".join(formatted_games) + "\n        ]"

def update_app_js():
    """Update the app.js file with complete schedule"""
    schedule = load_complete_schedule()
    
    # Read the current app.js file
    with open('../college-football-app/app.js', 'r') as f:
        content = f.read()
    
    # Find the generateSimpleSchedule function
    pattern = r'generateSimpleSchedule\(\)\s*\{[^}]*schedule\s*=\s*\{\};[^}]*schedule\[1\]\s*=\s*\[[^\]]*\];[^}]*// Add more weeks with basic info[^}]*for\s*\(let week = 2; week <= 15; week\+\+\)\s*\{[^}]*schedule\[week\]\s*=\s*this\.generateRandomGames\(week\);[^}]*\}[^}]*return schedule;[^}]*\}'
    
    # Create the new schedule content
    new_schedule_content = """    generateSimpleSchedule() {
        const schedule = {};
        
        // Complete schedule for all weeks from actual data
        schedule[1] = """ + format_week_schedule(schedule['1']) + """;
        
        schedule[2] = """ + format_week_schedule(schedule['2']) + """;
        
        schedule[3] = """ + format_week_schedule(schedule['3']) + """;
        
        schedule[4] = """ + format_week_schedule(schedule['4']) + """;
        
        schedule[5] = """ + format_week_schedule(schedule['5']) + """;
        
        schedule[6] = """ + format_week_schedule(schedule['6']) + """;
        
        schedule[7] = """ + format_week_schedule(schedule['7']) + """;
        
        schedule[8] = """ + format_week_schedule(schedule['8']) + """;
        
        schedule[9] = """ + format_week_schedule(schedule['9']) + """;
        
        schedule[10] = """ + format_week_schedule(schedule['10']) + """;
        
        schedule[11] = """ + format_week_schedule(schedule['11']) + """;
        
        schedule[12] = """ + format_week_schedule(schedule['12']) + """;
        
        schedule[13] = """ + format_week_schedule(schedule['13']) + """;
        
        schedule[14] = """ + format_week_schedule(schedule['14']) + """;
        
        schedule[15] = """ + format_week_schedule(schedule['15']) + """;
        
        return schedule;
    }"""
    
    # Replace the function
    new_content = re.sub(pattern, new_schedule_content, content, flags=re.DOTALL)
    
    # Write the updated content back to app.js
    with open('../college-football-app/app.js', 'w') as f:
        f.write(new_content)
    
    print("✅ Successfully updated app.js with complete schedule data")
    print(f"📊 Schedule summary:")
    for week in range(1, 16):
        game_count = len(schedule[str(week)])
        print(f"   Week {week}: {game_count} games")
    print(f"🎯 Total games: {sum(len(games) for games in schedule.values())}")

if __name__ == "__main__":
    update_app_js()
