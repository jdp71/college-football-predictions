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
        this.saveToStorage();
        
        // Simple test data - 5 games with 3 correct (60% accuracy)
        const testPredictions = [
            { home: 'Team A', away: 'Team B', homeWinProb: 0.6, confidence: 0.70, correct: true },
            { home: 'Team C', away: 'Team D', homeWinProb: 0.7, confidence: 0.80, correct: true },
            { home: 'Team E', away: 'Team F', homeWinProb: 0.4, confidence: 0.60, correct: true },
            { home: 'Team G', away: 'Team H', homeWinProb: 0.8, confidence: 0.90, correct: false },
            { home: 'Team I', away: 'Team J', homeWinProb: 0.3, confidence: 0.50, correct: false }
        ];

        // Add predictions
        testPredictions.forEach(pred => {
            this.storePrediction(1, pred.home, pred.away, pred.homeWinProb, pred.confidence);
        });

        // Add corresponding results
        testPredictions.forEach(pred => {
            let homeScore, awayScore;
            if (pred.correct) {
                // If prediction was correct, use the predicted winner
                if (pred.homeWinProb > 0.5) {
                    homeScore = 28;
                    awayScore = 21;
                } else {
                    homeScore = 21;
                    awayScore = 28;
                }
            } else {
                // If prediction was wrong, use the opposite
                if (pred.homeWinProb > 0.5) {
                    homeScore = 21;
                    awayScore = 28;
                } else {
                    homeScore = 28;
                    awayScore = 21;
                }
            }
            
            this.storeResult(1, pred.home, pred.away, homeScore, awayScore);
        });

        console.log('Initialized with test data:', testPredictions.length, 'games');
        this.saveToStorage();
    }
}

// Initialize the performance tracker
window.performanceTracker = new PerformanceTracker();