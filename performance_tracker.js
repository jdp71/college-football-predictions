/**
 * Performance Tracker for College Football Predictions
 * Tracks prediction accuracy and game results over time
 */

class PerformanceTracker {
    constructor() {
        this.predictions = {};
        this.results = {};
        this.loadFromStorage();
    }

    // Store a prediction for a specific week
    storePrediction(week, homeTeam, awayTeam, homeWinProb, confidence) {
        if (!this.predictions[week]) {
            this.predictions[week] = {};
        }
        
        const gameKey = `${homeTeam} vs ${awayTeam}`;
        this.predictions[week][gameKey] = {
            homeTeam,
            awayTeam,
            homeWinProb,
            confidence,
            timestamp: new Date().toISOString()
        };
        
        this.saveToStorage();
    }

    // Store actual game result
    storeResult(week, homeTeam, awayTeam, homeScore, awayScore) {
        if (!this.results[week]) {
            this.results[week] = {};
        }
        
        const gameKey = `${homeTeam} vs ${awayTeam}`;
        const winner = homeScore > awayScore ? homeTeam : awayTeam;
        
        this.results[week][gameKey] = {
            homeTeam,
            awayTeam,
            homeScore: parseInt(homeScore),
            awayScore: parseInt(awayScore),
            winner,
            timestamp: new Date().toISOString()
        };
        
        this.saveToStorage();
    }

    // Calculate accuracy for a specific week
    calculateWeekAccuracy(week) {
        if (!this.predictions[week] || !this.results[week]) {
            return { total: 0, correct: 0, accuracy: 0, confidence: 0 };
        }

        let total = 0;
        let correct = 0;
        let totalConfidence = 0;

        for (const gameKey in this.predictions[week]) {
            if (this.results[week][gameKey]) {
                total++;
                const prediction = this.predictions[week][gameKey];
                const result = this.results[week][gameKey];
                
                const predictedWinner = prediction.homeWinProb > 0.5 ? prediction.homeTeam : prediction.awayTeam;
                const actualWinner = result.winner;
                
                if (predictedWinner === actualWinner) {
                    correct++;
                }
                
                totalConfidence += prediction.confidence;
            }
        }

        return {
            total,
            correct,
            accuracy: total > 0 ? Math.round((correct / total) * 100) : 0,
            confidence: total > 0 ? Math.round((totalConfidence / total) * 100) : 0
        };
    }

    // Calculate overall season performance
    calculateSeasonPerformance() {
        let totalGames = 0;
        let totalCorrect = 0;
        let totalConfidence = 0;

        for (const week in this.predictions) {
            const weekPerf = this.calculateWeekAccuracy(parseInt(week));
            totalGames += weekPerf.total;
            totalCorrect += weekPerf.correct;
            totalConfidence += weekPerf.confidence * weekPerf.total;
        }

        return {
            totalGames,
            correct: totalCorrect,
            incorrect: totalGames - totalCorrect,
            accuracy: totalGames > 0 ? Math.round((totalCorrect / totalGames) * 100) : 0,
            confidence: totalGames > 0 ? Math.round((totalConfidence / totalGames)) : 0
        };
    }

    // Get detailed results for a specific week
    getWeekResults(week) {
        if (!this.predictions[week] || !this.results[week]) {
            return [];
        }

        const results = [];
        for (const gameKey in this.predictions[week]) {
            if (this.results[week][gameKey]) {
                const prediction = this.predictions[week][gameKey];
                const result = this.results[week][gameKey];
                
                const predictedWinner = prediction.homeWinProb > 0.5 ? prediction.homeTeam : prediction.awayTeam;
                const actualWinner = result.winner;
                const isCorrect = predictedWinner === actualWinner;
                
                results.push({
                    game: gameKey,
                    predictedWinner,
                    actualWinner,
                    homeScore: result.homeScore,
                    awayScore: result.awayScore,
                    confidence: prediction.confidence,
                    correct: isCorrect
                });
            }
        }

        return results.sort((a, b) => b.confidence - a.confidence);
    }

    // Save data to localStorage
    saveToStorage() {
        try {
            localStorage.setItem('performanceTracker', JSON.stringify({
                predictions: this.predictions,
                results: this.results
            }));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    }

    // Load data from localStorage
    loadFromStorage() {
        try {
            const data = localStorage.getItem('performanceTracker');
            if (data) {
                const parsed = JSON.parse(data);
                this.predictions = parsed.predictions || {};
                this.results = parsed.results || {};
            }
        } catch (error) {
            console.error('Error loading from localStorage:', error);
            this.predictions = {};
            this.results = {};
        }
    }

    // Clear all data
    clearAllData() {
        this.predictions = {};
        this.results = {};
        this.saveToStorage();
    }

    // Initialize with test data
    initializeWithRealData() {
        console.log('Initializing performance tracker...');
        
        // Clear existing data
        this.predictions = {};
        this.results = {};
        
        // Simple test data - 3 games with 2 correct (66.7% accuracy)
        const testGames = [
            { home: 'Alabama', away: 'Florida', homeWinProb: 0.7, confidence: 0.80, correct: true },
            { home: 'Georgia', away: 'Auburn', homeWinProb: 0.6, confidence: 0.70, correct: true },
            { home: 'Ohio State', away: 'Michigan', homeWinProb: 0.8, confidence: 0.90, correct: false }
        ];

        // Add predictions and results
        testGames.forEach(game => {
            this.storePrediction(1, game.home, game.away, game.homeWinProb, game.confidence);
            
            // Create realistic scores
            let homeScore, awayScore;
            if (game.correct) {
                // If prediction was correct, use the predicted winner
                if (game.homeWinProb > 0.5) {
                    homeScore = 31;
                    awayScore = 24;
                } else {
                    homeScore = 24;
                    awayScore = 31;
                }
            } else {
                // If prediction was wrong, use the opposite
                if (game.homeWinProb > 0.5) {
                    homeScore = 24;
                    awayScore = 31;
                } else {
                    homeScore = 31;
                    awayScore = 24;
                }
            }
            
            this.storeResult(1, game.home, game.away, homeScore, awayScore);
        });

        console.log('Initialized with test data:', testGames.length, 'games');
        this.saveToStorage();
    }
}

// Initialize the performance tracker
window.performanceTracker = new PerformanceTracker();