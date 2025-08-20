// Simple College Football Prediction System
// Only handles weekly team predictions

class SimplePredictionSystem {
    constructor() {
        this.teams = [
            'Alabama', 'Auburn', 'Florida', 'Georgia', 'Kentucky', 'LSU', 'Mississippi State', 
            'Missouri', 'Ole Miss', 'South Carolina', 'Tennessee', 'Texas A&M', 'Vanderbilt',
            'Illinois', 'Indiana', 'Iowa', 'Maryland', 'Michigan', 'Michigan State', 'Minnesota',
            'Nebraska', 'Northwestern', 'Ohio State', 'Penn State', 'Purdue', 'Rutgers', 'Wisconsin',
            'Boston College', 'Clemson', 'Duke', 'Florida State', 'Georgia Tech', 'Louisville',
            'Miami', 'NC State', 'North Carolina', 'Pittsburgh', 'Syracuse', 'Virginia', 'Virginia Tech',
            'Wake Forest', 'Baylor', 'BYU', 'Cincinnati', 'Houston', 'Iowa State', 'Kansas',
            'Kansas State', 'Oklahoma', 'Oklahoma State', 'TCU', 'Texas', 'Texas Tech', 'UCF',
            'UCLA', 'Utah', 'USC', 'Washington', 'Oregon', 'Stanford', 'California', 'Arizona',
            'Arizona State', 'Colorado', 'Oregon State', 'Washington State'
        ];
        
        this.schedule = this.generateSimpleSchedule();
    }
    
    generateSimpleSchedule() {
        const schedule = {};
        
        // Week 1 games
        schedule[1] = [
            { home: 'UCLA', away: 'Utah' },
            { home: 'Georgia', away: 'UT Martin' },
            { home: 'Ohio State', away: 'Akron' },
            { home: 'Michigan', away: 'East Carolina' },
            { home: 'Texas', away: 'Colorado State' },
            { home: 'LSU', away: 'USC' },
            { home: 'Oklahoma', away: 'Temple' },
            { home: 'Oregon', away: 'Idaho' },
            { home: 'Penn State', away: 'West Virginia' },
            { home: 'Wisconsin', away: 'Western Michigan' },
            { home: 'Iowa', away: 'Illinois State' },
            { home: 'Auburn', away: 'Alabama A&M' },
            { home: 'Florida', away: 'Samford' },
            { home: 'Tennessee', away: 'Ball State' },
            { home: 'Notre Dame', away: 'Navy' },
            { home: 'Miami', away: 'Florida A&M' },
            { home: 'Clemson', away: 'Georgia Tech' },
            { home: 'BYU', away: 'Southern Illinois' },
            { home: 'Baylor', away: 'Tarleton State' },
            { home: 'TCU', away: 'Stanford' },
            { home: 'Oklahoma State', away: 'South Dakota State' },
            { home: 'Alabama', away: 'Western Kentucky' }
        ];
        
        // Week 2 games
        schedule[2] = [
            { home: 'Utah', away: 'Cal Poly' },
            { home: 'Georgia', away: 'Tennessee Tech' },
            { home: 'Ohio State', away: 'Western Michigan' },
            { home: 'Texas', away: 'Michigan' },
            { home: 'LSU', away: 'Nicholls' },
            { home: 'Oklahoma', away: 'Houston' },
            { home: 'Oregon', away: 'Boise State' },
            { home: 'Penn State', away: 'Bowling Green' },
            { home: 'Wisconsin', away: 'South Dakota' },
            { home: 'Iowa', away: 'Iowa State' },
            { home: 'Auburn', away: 'California' },
            { home: 'Florida', away: 'Samford' },
            { home: 'Tennessee', away: 'Austin Peay' },
            { home: 'Notre Dame', away: 'Northern Illinois' },
            { home: 'Miami', away: 'Florida International' },
            { home: 'Clemson', away: 'Appalachian State' },
            { home: 'BYU', away: 'Sam Houston' },
            { home: 'Baylor', away: 'Air Force' },
            { home: 'TCU', away: 'Long Island' },
            { home: 'Oklahoma State', away: 'Arkansas' },
            { home: 'Alabama', away: 'South Florida' }
        ];
        
        // Add more weeks as needed
        for (let week = 3; week <= 15; week++) {
            schedule[week] = this.generateRandomGames(week);
        }
        
        return schedule;
    }
    
    generateRandomGames(week) {
        const games = [];
        const shuffledTeams = [...this.teams].sort(() => Math.random() - 0.5);
        
        for (let i = 0; i < Math.min(20, Math.floor(shuffledTeams.length / 2)); i++) {
            const homeTeam = shuffledTeams[i * 2];
            const awayTeam = shuffledTeams[i * 2 + 1];
            if (homeTeam && awayTeam) {
                games.push({ home: homeTeam, away: awayTeam });
            }
        }
        
        return games;
    }
    
    findTeamGame(team, week) {
        const weekGames = this.schedule[week] || [];
        return weekGames.find(game => game.home === team || game.away === team);
    }
    
    predictGame(homeTeam, awayTeam, week) {
        // Simple deterministic prediction based on team names and week
        const gameKey = `${homeTeam}_${awayTeam}_${week}`;
        
        // Simple hash function
        let hash = 0;
        for (let i = 0; i < gameKey.length; i++) {
            const char = gameKey.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        
        // Use hash to create a deterministic probability
        const randomValue = Math.abs(hash) % 1000 / 1000;
        
        // Base probability starts at 50%
        let homeProb = 0.50;
        
        // Add home field advantage
        homeProb += 0.05;
        
        // Add variation based on hash
        homeProb += (randomValue - 0.5) * 0.30;
        
        // Keep it reasonable
        homeProb = Math.max(0.25, Math.min(0.75, homeProb));
        const awayProb = 1 - homeProb;
        
        const winner = homeProb > awayProb ? homeTeam : awayTeam;
        const confidence = Math.max(homeProb, awayProb);
        const spreadEstimate = (homeProb - 0.5) * 28;
        
        console.log(`PREDICTION: ${homeTeam} vs ${awayTeam} (Week ${week})`);
        console.log(`Key: ${gameKey}, Hash: ${hash}, Value: ${randomValue.toFixed(3)}`);
        console.log(`Result: ${(homeProb * 100).toFixed(1)}% home win`);
        
        return {
            home_team: homeTeam,
            away_team: awayTeam,
            winner: winner,
            home_win_probability: homeProb,
            away_win_probability: awayProb,
            confidence: confidence,
            spread_estimate: spreadEstimate
        };
    }
}

// Initialize the prediction system
const predictor = new SimplePredictionSystem();

// DOM elements
const weekSelect = document.getElementById('singleWeek');
const teamSelect = document.getElementById('teamSelect');
const matchupDisplay = document.getElementById('matchupDisplay');
const matchupText = document.getElementById('matchupText');
const singleGameForm = document.getElementById('singleGameForm');
const singleLoading = document.getElementById('singleLoading');
const singleResult = document.getElementById('singleResult');

// Populate team dropdown
function populateTeamDropdown() {
    teamSelect.innerHTML = '<option value="">Select a Team</option>';
    predictor.teams.forEach(team => {
        const option = document.createElement('option');
        option.value = team;
        option.textContent = team;
        teamSelect.appendChild(option);
    });
}

// Find team's opponent for selected week
function findTeamOpponent(selectedTeam, week) {
    const game = predictor.findTeamGame(selectedTeam, week);
    
    if (game) {
        const isHome = game.home === selectedTeam;
        const opponent = isHome ? game.away : game.home;
        const homeTeam = game.home;
        const awayTeam = game.away;
        
        // Show the matchup with the selected team highlighted
        const displayText = isHome ? 
            `<strong>${homeTeam}</strong> vs ${awayTeam}` : 
            `${homeTeam} vs <strong>${awayTeam}</strong>`;
        
        matchupText.innerHTML = displayText;
        matchupDisplay.style.display = 'block';
        
        // Store the game data
        window.currentGame = game;
        
        console.log(`Found game: ${homeTeam} vs ${awayTeam} (Week ${week})`);
    } else {
        matchupText.innerHTML = `<em>No scheduled game found for ${selectedTeam} in Week ${week}</em>`;
        matchupDisplay.style.display = 'block';
        window.currentGame = null;
        
        console.log(`No game found for ${selectedTeam} in Week ${week}`);
    }
}

// Handle form submission
async function handlePrediction(e) {
    e.preventDefault();
    
    const selectedTeam = teamSelect.value;
    const week = weekSelect.value;
    
    if (!selectedTeam || !week) {
        alert('Please select both a week and a team');
        return;
    }
    
    if (!window.currentGame) {
        alert('No scheduled game found for this team in the selected week');
        return;
    }
    
    // Show loading
    singleLoading.style.display = 'block';
    singleResult.style.display = 'none';
    
    try {
        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Make prediction
        const prediction = predictor.predictGame(
            window.currentGame.home, 
            window.currentGame.away, 
            parseInt(week)
        );
        
        // Show result
        showResult(prediction);
    } catch (error) {
        console.error('Prediction error:', error);
        showError('An error occurred while making the prediction');
    }
    
    // Hide loading
    singleLoading.style.display = 'none';
}

// Show prediction result
function showResult(prediction) {
    const confidence = getConfidenceClass(prediction.confidence);
    
    singleResult.innerHTML = `
        <div class="game-result ${confidence}">
            <div class="row align-items-center">
                <div class="col-8">
                    <strong>${prediction.home_team}</strong> vs <strong>${prediction.away_team}</strong>
                    <br>
                    <span class="winner">Winner: ${prediction.winner}</span>
                </div>
                <div class="col-4 text-end">
                    <div style="font-size: 1.2rem; font-weight: bold;">
                        ${(prediction.confidence * 100).toFixed(1)}%
                    </div>
                    <small>Confidence</small>
                </div>
            </div>
            <div class="mt-2">
                <small>
                    ${prediction.home_team}: ${(prediction.home_win_probability * 100).toFixed(1)}% | 
                    ${prediction.away_team}: ${(prediction.away_win_probability * 100).toFixed(1)}%
                    <br>
                    Spread: ${prediction.home_team} ${prediction.spread_estimate > 0 ? '+' : ''}${prediction.spread_estimate.toFixed(1)}
                </small>
            </div>
        </div>
    `;
    
    singleResult.style.display = 'block';
}

// Show error
function showError(message) {
    singleResult.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    singleResult.style.display = 'block';
}

// Get confidence class
function getConfidenceClass(confidence) {
    if (confidence > 0.75) return 'confidence-high';
    if (confidence > 0.6) return 'confidence-medium';
    return 'confidence-low';
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Populate team dropdown
    populateTeamDropdown();
    
    // Week change handler
    weekSelect.addEventListener('change', function() {
        teamSelect.value = '';
        matchupDisplay.style.display = 'none';
    });
    
    // Team change handler
    teamSelect.addEventListener('change', function() {
        const selectedTeam = this.value;
        const week = weekSelect.value;
        
        if (selectedTeam && week) {
            findTeamOpponent(selectedTeam, parseInt(week));
        } else {
            matchupDisplay.style.display = 'none';
        }
    });
    
    // Form submission handler
    singleGameForm.addEventListener('submit', handlePrediction);
    
    console.log('Simple College Football Prediction System loaded');
    console.log(`Loaded ${predictor.teams.length} teams`);
    console.log(`Week 1 has ${predictor.schedule[1].length} games`);
});

