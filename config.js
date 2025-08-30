module.exports = {
    // Scraping settings
    headless: false, // Set to true for production (no browser window)
    delayBetweenRequests: 2000, // Milliseconds between requests
    delayBetweenYears: 10000, // Milliseconds between years
    
    // Years to scrape (2005-2025)
    years: Array.from({length: 21}, (_, i) => 2005 + i),
    
    // Stat categories to scrape
    statsPages: [
        'offense',
        'defense', 
        'special-teams',
        'efficiency',
        'situational',
        'advanced-stats'
    ],
    
    // Browser settings
    browser: {
        defaultViewport: { width: 1920, height: 1080 },
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu'
        ]
    },
    
    // User agent
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    
    // HTTP headers
    headers: {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    },
    
    // Timeouts
    timeouts: {
        pageLoad: 30000,
        navigation: 15000,
        waitAfterLoad: 3000
    },
    
    // Data output settings
    output: {
        saveJson: true,
        saveCsv: true,
        saveSummary: true,
        dataDirectory: 'data'
    }
}; 