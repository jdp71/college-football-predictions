# NCAA Football Stats Scraper

A comprehensive web scraper built with Puppeteer to collect NCAA football statistics from TeamRankings.com for the years 2005-2025.

## Features

- 🏈 Scrapes all NCAA football teams from TeamRankings.com
- 📊 Collects comprehensive statistics across multiple categories:
  - Offense
  - Defense
  - Special Teams
  - Efficiency
  - Situational
  - Advanced Stats
- 📅 Covers years 2005-2025 (21 seasons)
- 💾 Saves data in both JSON and CSV formats
- 🚀 Progress tracking with visual progress bars
- ⚡ Configurable delays and timeouts
- 🛡️ Respectful scraping with built-in delays

## Installation

1. **Install Node.js** (version 16 or higher)
2. **Clone or download this project**
3. **Install dependencies:**
   ```bash
   npm install
   ```

## Usage

### Quick Start

Run the scraper with default settings:

```bash
npm start
```

### Configuration

Edit `config.js` to customize scraping behavior:

- **Years to scrape**: Modify the `years` array
- **Headless mode**: Set `headless: true` for production
- **Delays**: Adjust `delayBetweenRequests` and `delayBetweenYears`
- **Stat categories**: Modify `statsPages` array

### Output

Data is saved to the `data/` directory with the following structure:

```
data/
├── 2005/
│   ├── teams.json
│   ├── teams.csv
│   └── summary.json
├── 2006/
│   ├── teams.json
│   ├── teams.csv
│   └── summary.json
└── ... (one folder per year)
```

### Data Format

#### JSON Output (`teams.json`)
```json
{
  "year": 2023,
  "teams": [
    {
      "name": "Alabama",
      "year": 2023,
      "url": "https://www.teamrankings.com/college-football/team/alabama-crimson-tide",
      "basic_info": {
        "conference": "SEC",
        "record": "12-2",
        "division": "FBS"
      },
      "stats": {
        "offense": {
          "offense_points_per_game": "35.1",
          "offense_yards_per_game": "477.1"
        },
        "defense": {
          "defense_points_allowed_per_game": "19.0",
          "defense_yards_allowed_per_game": "318.2"
        }
      }
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### CSV Output (`teams.csv`)
- Flattened data structure
- One row per team
- All statistics as columns
- Easy to import into Excel, R, Python, etc.

## Scripts

- `npm start` - Run the main scraper
- `npm run dev` - Run with debugging enabled

## Customization

### Scraping Specific Years

Edit `config.js`:

```javascript
years: [2020, 2021, 2022, 2023, 2024], // Only specific years
```

### Adding New Stat Categories

Edit `config.js`:

```javascript
statsPages: [
    'offense',
    'defense', 
    'special-teams',
    'efficiency',
    'situational',
    'advanced-stats',
    'your-new-category' // Add new categories here
],
```

### Production Settings

For production scraping, edit `config.js`:

```javascript
headless: true, // No browser window
delayBetweenRequests: 3000, // Slower, more respectful
delayBetweenYears: 15000, // Longer delays between years
```

## Troubleshooting

### Common Issues

1. **"Page not found" errors**
   - Some years may not have complete data
   - The scraper will continue with available data

2. **Slow performance**
   - Increase delays in `config.js`
   - Run in headless mode for better performance

3. **Browser crashes**
   - Reduce viewport size in config
   - Add more browser arguments

4. **Missing data**
   - Check if TeamRankings.com structure has changed
   - Verify internet connection
   - Some teams may not have complete statistics

### Debug Mode

Run with debugging:

```bash
npm run dev
```

This will open the browser in visible mode so you can see what's happening.

## Legal and Ethical Considerations

- **Respect robots.txt**: The scraper includes delays to be respectful
- **Rate limiting**: Built-in delays prevent overwhelming the server
- **Terms of service**: Review TeamRankings.com's terms before scraping
- **Data usage**: Use scraped data responsibly and in accordance with applicable laws

## Dependencies

- **puppeteer**: Browser automation
- **csv-writer**: CSV file generation
- **fs-extra**: Enhanced file system operations
- **cli-progress**: Progress bars
- **colors**: Terminal color output

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the console output for error messages
3. Verify your internet connection
4. Check if TeamRankings.com is accessible

## Data Quality Notes

- Data availability varies by year and team
- Some historical data may be incomplete
- Team names and URLs may change over time
- Conference affiliations may have changed

## Performance Tips

- Run during off-peak hours
- Use a stable internet connection
- Consider running on a server for large datasets
- Monitor system resources during scraping 