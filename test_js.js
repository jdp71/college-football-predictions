// Simple test to check if the JavaScript files can be loaded
const fs = require('fs');

console.log('Testing JavaScript files...');

try {
    // Test performance_tracker.js
    console.log('Testing performance_tracker.js...');
    const perfTrackerCode = fs.readFileSync('performance_tracker.js', 'utf8');
    console.log('✅ performance_tracker.js loaded successfully');
    
    // Test app.js
    console.log('Testing app.js...');
    const appCode = fs.readFileSync('app.js', 'utf8');
    console.log('✅ app.js loaded successfully');
    
    // Check for basic syntax
    console.log('Checking for PerformanceTracker class...');
    if (perfTrackerCode.includes('class PerformanceTracker')) {
        console.log('✅ PerformanceTracker class found');
    } else {
        console.log('❌ PerformanceTracker class NOT found');
    }
    
    console.log('Checking for MLPredictionSystem class...');
    if (appCode.includes('class MLPredictionSystem')) {
        console.log('✅ MLPredictionSystem class found');
    } else {
        console.log('❌ MLPredictionSystem class NOT found');
    }
    
    console.log('Checking for performance tracker initialization...');
    if (appCode.includes('window.performanceTracker = new PerformanceTracker()')) {
        console.log('✅ Performance tracker initialization found');
    } else {
        console.log('❌ Performance tracker initialization NOT found');
    }
    
    console.log('Checking for teams.json loading...');
    if (appCode.includes('fetch(\'./teams.json\')')) {
        console.log('✅ teams.json loading found');
    } else {
        console.log('❌ teams.json loading NOT found');
    }
    
} catch (error) {
    console.error('❌ Error:', error.message);
}
