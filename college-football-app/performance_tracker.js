// Performance Tracker for College Football Predictor
class PerformanceTracker {
    constructor() {
        this.predictions = new Map();
        this.results = new Map();
        this.loadFromStorage();
        
        // Don't initialize with sample data - track real predictions only
        console.log('📊 Performance tracker initialized - will track real predictions');
    }

    initializeWithSampleData() {
        console.log('📊 Initializing with sample performance data...');
        
        // Generate sample Week 1 predictions and results
        const sampleGames = [
            { home: 'Alabama', away: 'Georgia', homeWinProb: 0.65, actual: true },
            { home: 'Ohio State', away: 'Michigan', homeWinProb: 0.58, actual: false },
            { home: 'Texas', away: 'Oklahoma', homeWinProb: 0.52, actual: true },
            { home: 'USC', away: 'UCLA', homeWinProb: 0.61, actual: false },
            { home: 'Clemson', away: 'Florida State', homeWinProb: 0.55, actual: true },
            { home: 'Oregon', away: 'Washington', homeWinProb: 0.49, actual: false },
            { home: 'Penn State', away: 'Wisconsin', homeWinProb: 0.57, actual: true },
            { home: 'LSU', away: 'Auburn', homeWinProb: 0.53, actual: false },
            { home: 'Notre Dame', away: 'Army', homeWinProb: 0.72, actual: true },
            { home: 'Utah', away: 'Arizona', homeWinProb: 0.59, actual: true }
        ];

        sampleGames.forEach((game, index) => {
            const gameKey = `${game.home} vs ${game.away}`;
            this.storePrediction(gameKey, 1, game.home, game.away, game.homeWinProb, 0.75);
            this.storeResult(gameKey, 1, game.actual);
        });

        console.log('✅ Sample data initialized');
    }

    storePrediction(gameKey, week, homeTeam, awayTeam, homeWinProb, confidence) {
        const prediction = {
            gameKey,
            week,
            homeTeam,
            awayTeam,
            homeWinProb,
            confidence,
            predictedWinner: homeWinProb > 0.5 ? homeTeam : awayTeam,
            timestamp: new Date().toISOString()
        };
        
        this.predictions.set(gameKey, prediction);
        this.saveToStorage();
        
        console.log(`📊 Stored prediction: ${gameKey} - ${(homeWinProb * 100).toFixed(1)}%`);
    }

    storeResult(gameKey, week, homeTeamWon) {
        const result = {
            gameKey,
            week,
            homeTeamWon,
            timestamp: new Date().toISOString()
        };
        
        this.results.set(gameKey, result);
        this.saveToStorage();
        
        console.log(`📊 Stored result: ${gameKey} - Home won: ${homeTeamWon}`);
    }

    calculateWeekPerformance(week) {
        const weekPredictions = Array.from(this.predictions.values()).filter(p => p.week === week);
        const weekResults = Array.from(this.results.values()).filter(r => r.week === week);
        
        let correctPredictions = 0;
        let totalPredictions = 0;
        
        weekPredictions.forEach(prediction => {
            const result = this.results.get(prediction.gameKey);
            if (result) {
                const predictedHomeWin = prediction.homeWinProb >= 0.5;
                if (predictedHomeWin === result.homeTeamWon) {
                    correctPredictions++;
                }
                totalPredictions++;
            }
        });
        
        return {
            week,
            correctPredictions,
            totalPredictions,
            accuracy: totalPredictions > 0 ? correctPredictions / totalPredictions : 0
        };
    }

    calculateSeasonPerformance() {
        let correctPredictions = 0;
        let totalPredictions = 0;
        
        this.predictions.forEach((prediction, gameKey) => {
            const result = this.results.get(gameKey);
            if (result) {
                const predictedHomeWin = prediction.homeWinProb >= 0.5;
                if (predictedHomeWin === result.homeTeamWon) {
                    correctPredictions++;
                }
                totalPredictions++;
            }
        });
        
        return {
            correctPredictions,
            totalPredictions,
            accuracy: totalPredictions > 0 ? correctPredictions / totalPredictions : 0
        };
    }

    getTotalPredictions() {
        return this.predictions.size;
    }

    clearAllData() {
        this.predictions.clear();
        this.results.clear();
        localStorage.removeItem('cfb_predictions');
        localStorage.removeItem('cfb_results');
        console.log('🗑️ All performance data cleared');
    }

    saveToStorage() {
        try {
            localStorage.setItem('cfb_predictions', JSON.stringify(Array.from(this.predictions.entries())));
            localStorage.setItem('cfb_results', JSON.stringify(Array.from(this.results.entries())));
        } catch (error) {
            console.error('❌ Failed to save to localStorage:', error);
        }
    }

    loadFromStorage() {
        try {
            const predictionsData = localStorage.getItem('cfb_predictions');
            const resultsData = localStorage.getItem('cfb_results');
            
            if (predictionsData) {
                const predictions = JSON.parse(predictionsData);
                this.predictions = new Map(predictions);
            }
            
            if (resultsData) {
                const results = JSON.parse(resultsData);
                this.results = new Map(results);
            }
        } catch (error) {
            console.error('❌ Failed to load from localStorage:', error);
        }
    }

    // Method aliases for compatibility
    calculateWeekAccuracy(week) {
        return this.calculateWeekPerformance(week);
    }

    calculateSeasonAccuracy() {
        return this.calculateSeasonPerformance();
    }

    getWeekDetails(week) {
        return this.calculateWeekPerformance(week);
    }

    // Additional methods needed by the dashboard buttons
    getSeasonAccuracy() {
        const seasonPerf = this.calculateSeasonPerformance();
        return Math.round(seasonPerf.accuracy * 100);
    }

    getWeekAccuracy(week) {
        const weekPerf = this.calculateWeekPerformance(week);
        return Math.round(weekPerf.accuracy * 100);
    }

    getPredictions(week = null) {
        if (week === null) {
            // Return all predictions
            return Array.from(this.predictions.values());
        } else {
            // Return predictions for specific week
            return Array.from(this.predictions.values()).filter(p => p.week === week);
        }
    }
}