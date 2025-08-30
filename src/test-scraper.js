const TeamRankingsScraper = require('./teamrankings-scraper');

class TestScraper extends TeamRankingsScraper {
    constructor() {
        super();
        // Override years to only test with 2024
        this.years = [2024];
        // Override stats pages to only test with offense
        this.statsPages = ['offense'];
    }

    async run() {
        try {
            await this.init();

            console.log('\n🧪 Running test scrape for 2024 (offense stats only)'.yellow);
            
            for (const year of this.years) {
                await this.scrapeYear(year);
            }

            console.log('\n✅ Test completed successfully!'.green);
            console.log('📁 Check the data/2024/ directory for results'.cyan);

        } catch (error) {
            console.error('❌ Test failed:', error.message);
        } finally {
            if (this.browser) {
                await this.browser.close();
            }
        }
    }
}

// Run the test
if (require.main === module) {
    const testScraper = new TestScraper();
    testScraper.run().catch(console.error);
}

module.exports = TestScraper; 