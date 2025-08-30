const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const cliProgress = require('cli-progress');
const colors = require('colors');

class NCAAStatsScraper {
    constructor() {
        this.browser = null;
        this.page = null;
        this.baseUrl = 'https://www.teamrankings.com';
        this.dataDir = path.join(__dirname, '..', 'data');
        this.years = Array.from({length: 21}, (_, i) => 2005 + i); // 2005-2025
        this.statsCategories = [
            'offense',
            'defense',
            'special-teams',
            'efficiency',
            'situational',
            'advanced'
        ];
    }

    async init() {
        console.log('🚀 Initializing NCAA Stats Scraper...'.green);
        
        // Create data directory
        await fs.ensureDir(this.dataDir);
        
        // Launch browser
        this.browser = await puppeteer.launch({
            headless: false, // Set to true for production
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
        });

        this.page = await this.browser.newPage();
        
        // Set user agent
        await this.page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        
        // Set viewport
        await this.page.setViewport({ width: 1920, height: 1080 });
        
        console.log('✅ Browser initialized successfully'.green);
    }

    async scrapeYear(year) {
        console.log(`\n📊 Scraping data for year: ${year}`.cyan);
        
        const yearData = {
            year: year,
            teams: [],
            stats: {}
        };

        try {
            // Navigate to the main NCAA football page for the year
            const url = `${this.baseUrl}/college-football/`;
            await this.page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
            
            // Wait for page to load
            await this.page.waitForTimeout(2000);
            
            // Check if we need to select the year
            const yearSelector = await this.page.$('select[name="season"]');
            if (yearSelector) {
                await this.page.select('select[name="season"]', year.toString());
                await this.page.waitForTimeout(2000);
            }

            // Get all team links
            const teamLinks = await this.page.evaluate(() => {
                const links = Array.from(document.querySelectorAll('a[href*="/college-football/team/"]'));
                return links.map(link => ({
                    name: link.textContent.trim(),
                    url: link.href
                })).filter(team => team.name && team.url);
            });

            console.log(`Found ${teamLinks.length} teams for ${year}`);

            // Create progress bar
            const progressBar = new cliProgress.SingleBar({
                format: `Scraping ${year} |${colors.cyan('{bar}')}| {percentage}% | {value}/{total} teams | ETA: {eta}s`,
                barCompleteChar: '\u2588',
                barIncompleteChar: '\u2591',
                hideCursor: true
            });

            progressBar.start(teamLinks.length, 0);

            for (let i = 0; i < teamLinks.length; i++) {
                const team = teamLinks[i];
                
                try {
                    const teamData = await this.scrapeTeam(team.url, team.name, year);
                    yearData.teams.push(teamData);
                    
                    progressBar.update(i + 1);
                    
                    // Add delay to be respectful to the server
                    await this.page.waitForTimeout(1000);
                    
                } catch (error) {
                    console.error(`\n❌ Error scraping team ${team.name}: ${error.message}`.red);
                    continue;
                }
            }

            progressBar.stop();
            
            // Save year data
            await this.saveYearData(yearData, year);
            
            console.log(`✅ Completed scraping for ${year}`.green);
            
        } catch (error) {
            console.error(`❌ Error scraping year ${year}: ${error.message}`.red);
        }
    }

    async scrapeTeam(teamUrl, teamName, year) {
        const teamData = {
            name: teamName,
            year: year,
            url: teamUrl,
            stats: {}
        };

        try {
            await this.page.goto(teamUrl, { waitUntil: 'networkidle2', timeout: 30000 });
            await this.page.waitForTimeout(2000);

            // Scrape basic team info
            const basicInfo = await this.page.evaluate(() => {
                const info = {};
                
                // Get conference
                const conferenceElement = document.querySelector('.team-conference, .conference');
                if (conferenceElement) {
                    info.conference = conferenceElement.textContent.trim();
                }
                
                // Get record
                const recordElement = document.querySelector('.team-record, .record');
                if (recordElement) {
                    info.record = recordElement.textContent.trim();
                }
                
                return info;
            });

            Object.assign(teamData, basicInfo);

            // Scrape different stat categories
            for (const category of this.statsCategories) {
                try {
                    const categoryStats = await this.scrapeStatCategory(category);
                    teamData.stats[category] = categoryStats;
                } catch (error) {
                    console.error(`Error scraping ${category} stats for ${teamName}: ${error.message}`);
                }
            }

        } catch (error) {
            console.error(`Error scraping team ${teamName}: ${error.message}`);
        }

        return teamData;
    }

    async scrapeStatCategory(category) {
        const stats = {};
        
        try {
            // Navigate to specific stat category if needed
            const categoryUrl = `${this.page.url()}/${category}`;
            await this.page.goto(categoryUrl, { waitUntil: 'networkidle2', timeout: 15000 });
            await this.page.waitForTimeout(1000);

            // Extract stats from the page
            const categoryStats = await this.page.evaluate((cat) => {
                const stats = {};
                
                // Look for stat tables
                const tables = document.querySelectorAll('table');
                tables.forEach((table, tableIndex) => {
                    const rows = table.querySelectorAll('tr');
                    rows.forEach((row, rowIndex) => {
                        const cells = row.querySelectorAll('td, th');
                        if (cells.length >= 2) {
                            const statName = cells[0]?.textContent?.trim();
                            const statValue = cells[1]?.textContent?.trim();
                            
                            if (statName && statValue) {
                                stats[`${cat}_${statName.replace(/\s+/g, '_').toLowerCase()}`] = statValue;
                            }
                        }
                    });
                });

                // Also look for stat cards or divs
                const statElements = document.querySelectorAll('.stat-card, .stat-item, [class*="stat"]');
                statElements.forEach((element, index) => {
                    const statName = element.querySelector('.stat-name, .stat-label')?.textContent?.trim();
                    const statValue = element.querySelector('.stat-value, .stat-number')?.textContent?.trim();
                    
                    if (statName && statValue) {
                        stats[`${cat}_${statName.replace(/\s+/g, '_').toLowerCase()}`] = statValue;
                    }
                });

                return stats;
            }, category);

            Object.assign(stats, categoryStats);

        } catch (error) {
            console.error(`Error scraping ${category} category: ${error.message}`);
        }

        return stats;
    }

    async saveYearData(yearData, year) {
        const yearDir = path.join(this.dataDir, year.toString());
        await fs.ensureDir(yearDir);

        // Save as JSON
        const jsonPath = path.join(yearDir, 'teams.json');
        await fs.writeJson(jsonPath, yearData, { spaces: 2 });

        // Save as CSV
        const csvPath = path.join(yearDir, 'teams.csv');
        await this.saveAsCSV(yearData.teams, csvPath);

        console.log(`💾 Saved data for ${year} to ${yearDir}`.green);
    }

    async saveAsCSV(data, filePath) {
        if (data.length === 0) return;

        // Flatten the data structure for CSV
        const flattenedData = data.map(team => {
            const flat = {
                name: team.name,
                year: team.year,
                conference: team.conference || '',
                record: team.record || ''
            };

            // Flatten stats
            Object.keys(team.stats).forEach(category => {
                Object.keys(team.stats[category]).forEach(stat => {
                    flat[`${category}_${stat}`] = team.stats[category][stat];
                });
            });

            return flat;
        });

        const csvWriter = createCsvWriter({
            path: filePath,
            header: Object.keys(flattenedData[0]).map(key => ({
                id: key,
                title: key
            }))
        });

        await csvWriter.writeRecords(flattenedData);
    }

    async run() {
        try {
            await this.init();

            console.log(`\n🎯 Starting scrape for years: ${this.years.join(', ')}`.yellow);
            
            for (const year of this.years) {
                await this.scrapeYear(year);
                
                // Add delay between years
                if (year !== this.years[this.years.length - 1]) {
                    console.log('\n⏳ Waiting 5 seconds before next year...'.yellow);
                    await new Promise(resolve => setTimeout(resolve, 5000));
                }
            }

            console.log('\n🎉 Scraping completed successfully!'.green);
            console.log(`📁 Data saved to: ${this.dataDir}`.cyan);

        } catch (error) {
            console.error('❌ Scraping failed:', error.message);
        } finally {
            if (this.browser) {
                await this.browser.close();
            }
        }
    }
}

// Run the scraper
if (require.main === module) {
    const scraper = new NCAAStatsScraper();
    scraper.run().catch(console.error);
}

module.exports = NCAAStatsScraper; 