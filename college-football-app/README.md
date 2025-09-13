# College Football Predictor 2025

A modern, web-based college football prediction system built with vanilla JavaScript, featuring:

## Features

- **Real 2025 Schedule**: Complete schedule with 234 teams across 12 weeks (1,560 total games)
- **Advanced Predictions**: ML-powered predictions using team ratings and statistics
- **Performance Tracking**: Track prediction accuracy over time
- **Modern UI**: Beautiful, responsive design with dark theme
- **PWA Support**: Progressive Web App with offline capabilities

## Files

- `index.html` - Main application interface
- `app.js` - Core prediction logic and UI management
- `performance_tracker.js` - Performance tracking system
- `schedule_data.js` - Auto-generated from CSV (1,560 games)
- `teams.json` - Team data with ratings and statistics
- `styles.css` - Modern, responsive styling
- `manifest.json` - PWA configuration
- `sw.js` - Service worker for offline support
- `parse_schedule.py` - Script to parse CSV and generate data files

## Usage

1. Open `index.html` in a web browser
2. Select a team from the dropdown
3. Choose a week (1-12)
4. Click "Get Predictions" to see game predictions
5. Use Performance Dashboard to track accuracy

## Data Source

The app uses real 2025 college football schedule data from `2025_college_football_schedules.csv`, including:
- 234 FBS teams
- 12 weeks of games
- Conference affiliations
- Home/away designations

## Technical Details

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Data**: JSON-based team and schedule data
- **Storage**: LocalStorage for performance tracking
- **Architecture**: Class-based JavaScript with modular design
- **Responsive**: Mobile-friendly design
- **PWA**: Service worker for offline functionality

## Development

To regenerate data files from CSV:
```bash
python3 parse_schedule.py
```

This will create:
- `schedule_data.js` - JavaScript schedule data
- `teams.json` - Team statistics and ratings

## Browser Support

- Chrome/Edge 80+
- Firefox 75+
- Safari 13+
- Mobile browsers with ES6 support

Built with ❤️ for college football fans.
