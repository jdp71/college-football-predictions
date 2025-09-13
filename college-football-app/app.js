// College Football Predictor 2025
class CollegeFootballPredictor {
    constructor() {
        this.teams = new Map();
        this.schedule = new Map();
        this.performanceTracker = new PerformanceTracker();
        this.init();
    }

    async init() {
        console.log('🏈 Initializing College Football Predictor 2025...');
        await this.loadScheduleData();
        await this.createTeams();
        this.initializeUI();
        console.log('✅ App ready!');
    }

    async loadScheduleData() {
        try {
            console.log('📅 Loading 2025 schedule data...');
            
            // Load real schedule data
            if (typeof REAL_SCHEDULE_DATA !== 'undefined') {
                console.log('✅ Using real schedule data from CSV');
                for (const [week, games] of Object.entries(REAL_SCHEDULE_DATA)) {
                    this.schedule.set(parseInt(week), games);
                }
            } else {
                console.log('⚠️ Real schedule data not found, using generated schedule');
                this.generateSchedule();
            }
            
            console.log(`✅ Loaded schedule for ${this.schedule.size} weeks`);
        } catch (error) {
            console.error('❌ Failed to load schedule:', error);
            throw error;
        }
    }

    generateSchedule() {
        const teams = [
            'Alabama', 'Auburn', 'LSU', 'Georgia', 'Florida', 'Tennessee', 'Texas', 'Oklahoma',
            'Ohio State', 'Michigan', 'Penn State', 'USC', 'UCLA', 'Oregon', 'Washington',
            'Clemson', 'Florida State', 'Notre Dame', 'Wisconsin', 'Iowa', 'Utah', 'Arizona',
            'Baylor', 'TCU', 'Kansas State', 'Oklahoma State', 'West Virginia', 'Cincinnati',
            'Boise State', 'San Diego State', 'Fresno State', 'Air Force', 'Wyoming',
            'Memphis', 'Tulane', 'SMU', 'Navy', 'Marshall', 'Western Kentucky',
            'Appalachian State', 'Coastal Carolina', 'Troy', 'South Alabama',
            'Miami (OH)', 'Toledo', 'Northern Illinois', 'Western Michigan',
            'Army', 'Liberty', 'Connecticut', 'UMass'
        ];

        for (let week = 1; week <= 12; week++) {
            const shuffled = [...teams].sort(() => Math.random() - 0.5);
            const games = [];
            
            for (let i = 0; i < shuffled.length; i += 2) {
                if (i + 1 < shuffled.length) {
                    games.push({
                        homeTeam: shuffled[i],
                        awayTeam: shuffled[i + 1],
                        week: week,
                        date: `2025-${String(week + 8).padStart(2, '0')}-${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}`,
                        time_et: 'TBD',
                        location: 'vs',
                        tv_network: 'TBD',
                        conference: 'Unknown',
                        notes: '',
                        rivalry: false
                    });
                }
            }
            this.schedule.set(week, games);
        }
    }

    async createTeams() {
        console.log('👥 Loading team data...');
        
        try {
            // Try to load real team data first
            const response = await fetch('teams.json');
            if (response.ok) {
                const teamData = await response.json();
                console.log(`📊 Loading ${Object.keys(teamData).length} teams from teams.json`);
                
                // Load teams from JSON file
                for (const [teamName, data] of Object.entries(teamData)) {
                    this.teams.set(teamName, data);
                }
                
                console.log(`✅ Loaded ${this.teams.size} teams with real stats`);
                return;
            }
        } catch (error) {
            console.warn('⚠️ Could not load teams.json, falling back to generated data:', error);
        }
        
        // Fallback: Extract unique teams from schedule and generate data
        const teamNames = new Set();
        for (const games of this.schedule.values()) {
            games.forEach(game => {
                teamNames.add(game.homeTeam);
                teamNames.add(game.awayTeam);
            });
        }

        console.log(`📊 Found ${teamNames.size} unique teams, generating data`);

        // Create team data with realistic stats based on conference and team strength
        teamNames.forEach(name => {
            const conference = this.getConference(name);
            const baseRating = this.getBaseRating(name, conference);
            
            this.teams.set(name, {
                name: name,
                overallRating: baseRating,
                efficiencyRating: baseRating + Math.floor(Math.random() * 10) - 5,
                offenseRating: baseRating + Math.floor(Math.random() * 8) - 4,
                defenseRating: baseRating + Math.floor(Math.random() * 8) - 4,
                specialTeamsRating: Math.floor(Math.random() * 20) + 70,
                homeAdvantage: Math.random() * 0.08 + 0.03,
                recentForm: Math.random() * 0.3 - 0.15,
                strengthOfSchedule: this.getSOSRating(conference),
                conference: conference,
                coachRating: this.getCoachRating(name, conference),
                stadiumFactor: Math.random() * 0.04 + 0.02
            });
        });

        console.log(`✅ Generated data for ${this.teams.size} teams`);
    }

    getConference(team) {
        const conferences = {
            'SEC': ['Alabama', 'Auburn', 'LSU', 'Texas A&M', 'Mississippi', 'Mississippi State', 'Arkansas', 'Missouri', 'Georgia', 'Florida', 'Tennessee', 'Kentucky', 'South Carolina', 'Vanderbilt'],
            'ACC': ['Clemson', 'Florida State', 'North Carolina', 'NC State', 'Wake Forest', 'Duke', 'Virginia Tech', 'Virginia', 'Pittsburgh', 'Boston College', 'Miami', 'Louisville', 'Syracuse', 'Georgia Tech'],
            'Big Ten': ['Ohio State', 'Michigan', 'Penn State', 'Michigan State', 'Maryland', 'Rutgers', 'Indiana', 'Purdue', 'Illinois', 'Northwestern', 'Iowa', 'Wisconsin', 'Minnesota', 'Nebraska'],
            'Big 12': ['Texas', 'Oklahoma', 'Baylor', 'TCU', 'Texas Tech', 'Oklahoma State', 'Kansas State', 'Kansas', 'Iowa State', 'West Virginia', 'Cincinnati', 'UCF', 'Houston', 'BYU', 'Utah', 'Arizona', 'Arizona State', 'Colorado'],
            'Pac-12': ['Oregon', 'Washington', 'USC', 'UCLA', 'Oregon State', 'Washington State', 'California', 'Stanford'],
            'AAC': ['Memphis', 'Tulane', 'SMU', 'Tulsa', 'Navy', 'East Carolina', 'Temple', 'South Florida'],
            'Mountain West': ['Boise State', 'San Diego State', 'Fresno State', 'Air Force', 'Wyoming', 'Utah State', 'Colorado State', 'Nevada', 'UNLV', 'New Mexico', 'San Jose State', 'Hawaii'],
            'Sun Belt': ['Appalachian State', 'Coastal Carolina', 'Georgia Southern', 'Georgia State', 'Troy', 'South Alabama', 'Louisiana', 'Louisiana-Monroe', 'Arkansas State', 'Texas State'],
            'C-USA': ['Marshall', 'Western Kentucky', 'Middle Tennessee', 'Florida Atlantic', 'Charlotte', 'FIU', 'Rice', 'North Texas', 'UTSA', 'UTEP', 'Southern Miss', 'Louisiana Tech'],
            'MAC': ['Miami (OH)', 'Toledo', 'Northern Illinois', 'Western Michigan', 'Central Michigan', 'Eastern Michigan', 'Ball State', 'Bowling Green', 'Kent State', 'Akron', 'Buffalo', 'Ohio'],
            'Independents': ['Notre Dame', 'Army', 'Liberty', 'Connecticut', 'UMass']
        };
        
        for (const [conference, teams] of Object.entries(conferences)) {
            if (teams.includes(team)) {
                return conference;
            }
        }
        return 'Unknown';
    }

    getBaseRating(teamName, conference) {
        // Power 5 teams get higher base ratings
        const power5Conferences = ['SEC', 'Big Ten', 'Big 12', 'ACC', 'Pac-12'];
        const isPower5 = power5Conferences.includes(conference);
        
        // Elite teams get highest ratings
        const eliteTeams = ['Alabama', 'Georgia', 'Ohio State', 'Michigan', 'Texas', 'Oregon', 'Penn State', 'LSU', 'Florida State', 'Clemson'];
        const isElite = eliteTeams.includes(teamName);
        
        if (isElite) return 85 + Math.floor(Math.random() * 10);
        if (isPower5) return 70 + Math.floor(Math.random() * 15);
        return 60 + Math.floor(Math.random() * 15);
    }

    getSOSRating(conference) {
        const sosRatings = {
            'SEC': 0.15,
            'Big Ten': 0.12,
            'Big 12': 0.10,
            'ACC': 0.08,
            'Pac-12': 0.05,
            'Mountain West': 0.02,
            'AAC': 0.01,
            'Sun Belt': 0.0,
            'C-USA': -0.01,
            'MAC': -0.02,
            'Independents': 0.05
        };
        return sosRatings[conference] || 0.0;
    }

    getCoachRating(teamName, conference) {
        // Elite coaches get higher ratings
        const eliteCoaches = ['Alabama', 'Georgia', 'Ohio State', 'Michigan', 'Texas', 'Oregon', 'Penn State', 'LSU', 'Florida State', 'Clemson'];
        const isEliteCoach = eliteCoaches.includes(teamName);
        
        if (isEliteCoach) return 90 + Math.floor(Math.random() * 10);
        if (['SEC', 'Big Ten', 'Big 12', 'ACC', 'Pac-12'].includes(conference)) {
            return 75 + Math.floor(Math.random() * 15);
        }
        return 65 + Math.floor(Math.random() * 15);
    }

    initializeUI() {
        try {
            console.log('🎨 Initializing UI...');
            
            // Populate team dropdown
            const teamSelect = document.getElementById('teamSelect');
            if (!teamSelect) {
                console.error('❌ Team select element not found');
                return;
            }
            
            teamSelect.innerHTML = '<option value="">Select a team...</option>';
            
            const sortedTeams = Array.from(this.teams.keys()).sort();
            console.log(`📋 Adding ${sortedTeams.length} teams to dropdown`);
            
            sortedTeams.forEach(team => {
                const option = document.createElement('option');
                option.value = team;
                option.textContent = team;
                teamSelect.appendChild(option);
            });

            // Populate week dropdown
            const weekSelect = document.getElementById('weekSelect');
            if (!weekSelect) {
                console.error('❌ Week select element not found');
                return;
            }
            
            weekSelect.innerHTML = '<option value="">Select a week...</option>';
            
            const maxWeek = Math.max(...this.schedule.keys());
            const minWeek = Math.min(...this.schedule.keys());
            console.log(`📅 Adding weeks ${minWeek}-${maxWeek} to dropdown`);
            
            for (let week = minWeek; week <= maxWeek; week++) {
                const option = document.createElement('option');
                option.value = week;
                const weekLabel = week === 0 ? 'Week 0 (Preseason)' : `Week ${week}`;
                option.textContent = weekLabel;
                weekSelect.appendChild(option);
            }

            // Add event listeners
            const getPredictionsBtn = document.getElementById('getPredictions');
            const seasonOverviewBtn = document.getElementById('seasonOverview');
            const currentWeekBtn = document.getElementById('currentWeekPerformance');
            const clearDataBtn = document.getElementById('clearAllData');
            
            if (getPredictionsBtn) {
                getPredictionsBtn.addEventListener('click', () => this.handlePrediction());
            }
            if (seasonOverviewBtn) {
                seasonOverviewBtn.addEventListener('click', () => this.showSeasonOverview());
            }
            if (currentWeekBtn) {
                currentWeekBtn.addEventListener('click', () => this.showCurrentWeekPerformance());
            }
            if (clearDataBtn) {
                clearDataBtn.addEventListener('click', () => this.clearAllData());
            }
            
            console.log('✅ UI initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing UI:', error);
        }
    }

    handlePrediction() {
        const team = document.getElementById('teamSelect').value;
        const week = document.getElementById('weekSelect').value;
        
        if (!team || !week) {
            alert('Please select both a team and a week.');
            return;
        }

        const games = this.schedule.get(parseInt(week));
        const teamGames = games.filter(game => 
            game.homeTeam === team || game.awayTeam === team
        );

        if (teamGames.length === 0) {
            alert(`${team} doesn't play in Week ${week}.`);
            return;
        }

        this.displayGames(teamGames, team);
    }

    displayGames(games, team) {
        const section = document.getElementById('predictionsSection');
        const gamesList = document.getElementById('gamesList');
        
        section.style.display = 'block';
        gamesList.innerHTML = '';

        games.forEach(game => {
            const homeData = this.teams.get(game.homeTeam);
            const awayData = this.teams.get(game.awayTeam);
            
            const prediction = this.predictGame(homeData, awayData, true);
            const winProb = prediction.homeWinProb;
            
            const gameCard = document.createElement('div');
            gameCard.className = 'game-card';
            const weekLabel = game.week === 0 ? 'Week 0 (Preseason)' : `Week ${game.week}`;
            gameCard.innerHTML = `
                <div class="game-header">
                    <div class="game-title">${game.homeTeam} vs ${game.awayTeam}</div>
                    <div class="game-week">${weekLabel}</div>
                </div>
                <div class="game-details">
                    <div class="team">
                        <div class="team-name">${game.homeTeam}</div>
                        <div class="team-record">Rating: ${homeData.overallRating}</div>
                    </div>
                    <div class="vs-divider">VS</div>
                    <div class="team">
                        <div class="team-name">${game.awayTeam}</div>
                        <div class="team-record">Rating: ${awayData.overallRating}</div>
                    </div>
                </div>
                <div class="prediction">
                    <div class="prediction-result">
                        <strong>${winProb > 0.5 ? game.homeTeam : game.awayTeam}</strong> 
                        ${Math.round(Math.max(winProb, 1 - winProb) * 100)}% 
                        (Confidence: ${Math.round(prediction.confidence * 100)}%)
                    </div>
                    <div class="game-info">
                        <strong>Date:</strong> ${game.date || 'TBD'}<br>
                        <strong>Time:</strong> ${game.time_et || 'TBD'}<br>
                        <strong>TV:</strong> ${game.tv_network || 'TBD'}<br>
                        ${game.notes ? `<strong>Notes:</strong> ${game.notes}` : ''}
                    </div>
                </div>
            `;
            
            gamesList.appendChild(gameCard);
        });
    }

    predictGame(homeData, awayData, isHomeGame) {
        // Advanced prediction algorithm using multiple factors
        const homeRating = homeData.overallRating;
        const awayRating = awayData.overallRating;
        
        // Base rating difference (0-100 scale)
        const ratingDiff = (homeRating - awayRating) / 100;
        
        // Conference strength multiplier
        const homeConfBoost = this.getConferenceBoost(homeData.conference);
        const awayConfBoost = this.getConferenceBoost(awayData.conference);
        const confAdvantage = (homeConfBoost - awayConfBoost) * 0.1;
        
        // Coach rating difference
        const coachDiff = (homeData.coachRating - awayData.coachRating) / 1000;
        
        // Recent form and momentum
        const formAdvantage = homeData.recentForm - awayData.recentForm;
        
        // Strength of schedule adjustment
        const sosAdvantage = (homeData.strengthOfSchedule - awayData.strengthOfSchedule) * 0.1;
        
        // Home field advantage
        const homeAdvantage = isHomeGame ? 0.05 : -0.05;
        
        // Stadium factor
        const stadiumAdvantage = isHomeGame ? homeData.stadiumFactor : -homeData.stadiumFactor;
        
        // Combine all factors
        const totalAdvantage = ratingDiff + confAdvantage + coachDiff + formAdvantage + sosAdvantage + homeAdvantage + stadiumAdvantage;
        
        // Add some randomness for realism
        const randomFactor = (Math.random() - 0.5) * 0.1;
        let homeWinProb = 0.5 + totalAdvantage + randomFactor;
        
        // Ensure probability is within realistic bounds
        homeWinProb = Math.max(0.1, Math.min(0.9, homeWinProb));
        
        // Calculate confidence based on rating difference
        const confidence = Math.min(0.95, Math.max(0.5, 0.5 + Math.abs(totalAdvantage) * 2));
        
        return {
            homeWinProb: homeWinProb,
            awayWinProb: 1 - homeWinProb,
            confidence: confidence
        };
    }

    getConferenceBoost(conference) {
        const conferenceStrength = {
            'SEC': 1.15,
            'Big Ten': 1.12,
            'Big 12': 1.10,
            'ACC': 1.08,
            'Pac-12': 0.98,
            'Mountain West': 0.85,
            'AAC': 0.80,
            'Sun Belt': 0.75,
            'C-USA': 0.70,
            'MAC': 0.65,
            'Independents': 0.90
        };
        return conferenceStrength[conference] || 0.75;
    }

    showSeasonOverview() {
        console.log('📊 Showing season overview...');
        // Implementation for season overview
    }

    showCurrentWeekPerformance() {
        console.log('📈 Showing current week performance...');
        // Implementation for current week performance
    }

    clearAllData() {
        console.log('🗑️ Clearing all data...');
        // Implementation for clearing data
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CollegeFootballPredictor();
});