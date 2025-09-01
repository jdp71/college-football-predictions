// Performance Tracker for College Football Predictions
// Tracks prediction accuracy against actual game results

class PerformanceTracker {
    constructor() {
        this.predictions = {};
        this.actualResults = {};
        this.performanceMetrics = {};
        this.loadStoredData();
    }
    
    // Store a prediction for tracking
    storePrediction(week, homeTeam, awayTeam, homeWinProbability, confidence) {
        const gameKey = this.getGameKey(homeTeam, awayTeam, week);
        
        if (!this.predictions[week]) {
            this.predictions[week] = {};
        }
        
        this.predictions[week][gameKey] = {
            homeTeam,
            awayTeam,
            homeWinProbability,
            confidence,
            predictedWinner: homeWinProbability > 0.5 ? homeTeam : awayTeam,
            timestamp: new Date().toISOString()
        };
        
        this.saveToStorage();
    }
    
    // Record actual game result
    recordGameResult(week, homeTeam, awayTeam, homeScore, awayScore) {
        const gameKey = this.getGameKey(homeTeam, awayTeam, week);
        
        if (!this.actualResults[week]) {
            this.actualResults[week] = {};
        }
        
        this.actualResults[week][gameKey] = {
            homeTeam,
            awayTeam,
            homeScore: parseInt(homeScore),
            awayScore: parseInt(awayScore),
            actualWinner: homeScore > awayScore ? homeTeam : awayTeam,
            margin: Math.abs(homeScore - awayScore),
            timestamp: new Date().toISOString()
        };
        
        this.saveToStorage();
    }
    
    // Calculate performance metrics for a specific week
    calculateWeekPerformance(week) {
        const weekPredictions = this.predictions[week] || {};
        const weekResults = this.actualResults[week] || {};
        
        let totalGames = 0;
        let correctPredictions = 0;
        let totalConfidence = 0;
        let gamesWithResults = 0;
        let gamesWithPredictions = 0;
        
        const gameResults = [];
        
        // First, process games with both predictions and results
        Object.keys(weekPredictions).forEach(gameKey => {
            const prediction = weekPredictions[gameKey];
            const result = weekResults[gameKey];
            
            if (result) {
                totalGames++;
                gamesWithResults++;
                gamesWithPredictions++;
                
                const isCorrect = prediction.predictedWinner === result.actualWinner;
                if (isCorrect) {
                    correctPredictions++;
                }
                
                totalConfidence += prediction.confidence;
                
                gameResults.push({
                    game: `${prediction.homeTeam} vs ${prediction.awayTeam}`,
                    prediction: `${prediction.predictedWinner} (${(prediction.homeWinProbability * 100).toFixed(1)}%)`,
                    actual: `${result.actualWinner} (${result.homeScore}-${result.awayScore})`,
                    correct: isCorrect,
                    confidence: prediction.confidence,
                    margin: result.margin,
                    hasPrediction: true
                });
            }
        });
        
        // Then, add games that only have results (no predictions)
        Object.keys(weekResults).forEach(gameKey => {
            const result = weekResults[gameKey];
            const prediction = weekPredictions[gameKey];
            
            if (!prediction) {
                totalGames++;
                gamesWithResults++;
                
                gameResults.push({
                    game: `${result.homeTeam} vs ${result.awayTeam}`,
                    prediction: 'No prediction made',
                    actual: `${result.actualWinner} (${result.homeScore}-${result.awayScore})`,
                    correct: null,
                    confidence: 0,
                    margin: result.margin,
                    hasPrediction: false
                });
            }
        });
        
        const accuracy = gamesWithPredictions > 0 ? (correctPredictions / gamesWithPredictions * 100) : 0;
        const averageConfidence = gamesWithPredictions > 0 ? (totalConfidence / gamesWithPredictions) : 0;
        
        this.performanceMetrics[week] = {
            totalGames,
            correctPredictions,
            incorrectPredictions: gamesWithPredictions - correctPredictions,
            gamesWithPredictions,
            gamesWithResults,
            accuracy: accuracy.toFixed(1),
            averageConfidence: averageConfidence.toFixed(3),
            gameResults,
            lastUpdated: new Date().toISOString()
        };
        
        return this.performanceMetrics[week];
    }
    
    // Calculate overall season performance
    calculateSeasonPerformance() {
        const weeks = Object.keys(this.actualResults).map(Number).sort((a, b) => a - b);
        let totalGames = 0;
        let totalCorrect = 0;
        let totalConfidence = 0;
        let weekAccuracies = [];
        
        weeks.forEach(week => {
            const weekPerf = this.calculateWeekPerformance(week);
            totalGames += weekPerf.totalGames;
            totalCorrect += weekPerf.correctPredictions;
            totalConfidence += weekPerf.averageConfidence * weekPerf.gamesWithPredictions;
            weekAccuracies.push({
                week,
                accuracy: parseFloat(weekPerf.accuracy),
                games: weekPerf.totalGames
            });
        });
        
        const overallAccuracy = totalGames > 0 ? (totalCorrect / totalGames * 100) : 0;
        const overallConfidence = totalGames > 0 ? (totalConfidence / totalGames) : 0;
        
        return {
            totalWeeks: weeks.length,
            totalGames,
            totalCorrect,
            totalIncorrect: totalGames - totalCorrect,
            overallAccuracy: overallAccuracy.toFixed(1),
            overallConfidence: overallConfidence.toFixed(3),
            weekAccuracies,
            lastUpdated: new Date().toISOString()
        };
    }
    
    // Get performance summary for display
    getPerformanceSummary() {
        const seasonPerf = this.calculateSeasonPerformance();
        const currentWeek = this.getCurrentWeek();
        const currentWeekPerf = this.performanceMetrics[currentWeek] || {};
        
        return {
            season: seasonPerf,
            currentWeek: currentWeekPerf,
            currentWeekNumber: currentWeek
        };
    }
    
    // Helper methods
    getGameKey(homeTeam, awayTeam, week) {
        return `${week}_${homeTeam}_${awayTeam}`.replace(/\s+/g, '_');
    }
    
    getCurrentWeek() {
        // Calculate current week based on date (Week 1 starts Aug 30, 2025)
        const startDate = new Date('2025-08-30');
        const today = new Date();
        const diffTime = Math.abs(today - startDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const currentWeek = Math.ceil(diffDays / 7);
        return Math.max(1, Math.min(15, currentWeek)); // Clamp between 1-15
    }
    
    // Storage methods
    saveToStorage() {
        try {
            localStorage.setItem('cfb_predictions', JSON.stringify(this.predictions));
            localStorage.setItem('cfb_results', JSON.stringify(this.actualResults));
            localStorage.setItem('cfb_metrics', JSON.stringify(this.performanceMetrics));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    }
    
    loadStoredData() {
        try {
            const storedPredictions = localStorage.getItem('cfb_predictions');
            const storedResults = localStorage.getItem('cfb_results');
            const storedMetrics = localStorage.getItem('cfb_metrics');
            
            if (storedPredictions) this.predictions = JSON.parse(storedPredictions);
            if (storedResults) this.actualResults = JSON.parse(storedResults);
            if (storedMetrics) this.performanceMetrics = JSON.parse(storedMetrics);
        } catch (error) {
            console.error('Error loading from localStorage:', error);
        }
    }
    
    // Clear all data
    clearAllData() {
        this.predictions = {};
        this.actualResults = {};
        this.performanceMetrics = {};
        localStorage.removeItem('cfb_predictions');
        localStorage.removeItem('cfb_results');
        localStorage.removeItem('cfb_metrics');
    }
}

// Global instance
window.performanceTracker = new PerformanceTracker();
