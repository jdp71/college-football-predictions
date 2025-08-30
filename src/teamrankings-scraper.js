const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const cliProgress = require('cli-progress');
const colors = require('colors');

class TeamRankingsScraper {
    constructor() {
        this.browser = null;
        this.page = null;
        this.baseUrl = 'https://www.teamrankings.com';
        this.dataDir = path.join(__dirname, '..', 'data');
        this.years = Array.from({length: 21}, (_, i) => 2005 + i); // 2005-2025
        this.statsPages = [
            'offense',
            'defense', 
            'special-teams',
            'efficiency',
            'situational',
            'advanced-stats'
        ];
    }

    async init() {
        console.log('🚀 Initializing TeamRankings Scraper...'.green);
        
        await fs.ensureDir(this.dataDir);
        
        this.browser = await puppeteer.launch({
            headless: false,
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
        await this.page.setViewport({ width: 1920, height: 1080 });
        
        // Set extra headers
        await this.page.setExtraHTTPHeaders({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        });
        
        console.log('✅ Browser initialized successfully'.green);
    }

    async scrapeYear(year) {
        console.log(`\n📊 Scraping data for year: ${year}`.cyan);
        
        const yearData = {
            year: year,
            teams: [],
            timestamp: new Date().toISOString()
        };

        try {
            // Start with the main NCAA football page
            const mainUrl = `${this.baseUrl}/college-football/`;
            await this.page.goto(mainUrl, { waitUntil: 'networkidle2', timeout: 30000 });
            await new Promise(resolve => setTimeout(resolve, 3000));

            // Try to find year selector and set it
            await this.selectYear(year);

            // Get all teams for this year
            const teams = await this.getTeamsForYear(year);
            console.log(`Found ${teams.length} teams for ${year}`);

            const progressBar = new cliProgress.SingleBar({
                format: `Scraping ${year} |${colors.cyan('{bar}')}| {percentage}% | {value}/{total} teams | ETA: {eta}s`,
                barCompleteChar: '\u2588',
                barIncompleteChar: '\u2591',
                hideCursor: true
            });

            progressBar.start(teams.length, 0);

            for (let i = 0; i < teams.length; i++) {
                const team = teams[i];
                
                try {
                    const teamData = await this.scrapeTeam(team, year);
                    yearData.teams.push(teamData);
                    
                    progressBar.update(i + 1);
                    
                    // Be respectful to the server
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                } catch (error) {
                    console.error(`\n❌ Error scraping team ${team.name}: ${error.message}`.red);
                    continue;
                }
            }

            progressBar.stop();
            
            await this.saveYearData(yearData, year);
            console.log(`✅ Completed scraping for ${year}`.green);
            
        } catch (error) {
            console.error(`❌ Error scraping year ${year}: ${error.message}`.red);
        }
    }

    async selectYear(year) {
        try {
            // Look for year selector dropdown
            const yearSelectors = [
                'select[name="season"]',
                'select[data-season]',
                '.season-selector select',
                '#season-selector'
            ];

            for (const selector of yearSelectors) {
                const yearSelect = await this.page.$(selector);
                if (yearSelect) {
                    await this.page.select(selector, year.toString());
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    console.log(`Selected year ${year} using selector: ${selector}`);
                    return;
                }
            }

            // If no dropdown found, try clicking on year links
            const yearLinks = await this.page.$$(`a[href*="${year}"], a:contains("${year}")`);
            if (yearLinks.length > 0) {
                await yearLinks[0].click();
                await new Promise(resolve => setTimeout(resolve, 2000));
                console.log(`Clicked year ${year} link`);
                return;
            }

            console.log(`No year selector found for ${year}, continuing with current page`);
        } catch (error) {
            console.log(`Could not select year ${year}: ${error.message}`);
        }
    }

    async getTeamsForYear(year) {
        const teams = await this.page.evaluate((year) => {
            const teamElements = document.querySelectorAll('a[href*="/college-football/team/"], .team-link, [class*="team"] a');
            const teams = [];

            teamElements.forEach(element => {
                const name = element.textContent.trim();
                const url = element.href;
                
                if (name && url && name.length > 0 && name.length < 100) {
                    teams.push({
                        name: name,
                        url: url
                    });
                }
            });

            // Remove duplicates
            const uniqueTeams = teams.filter((team, index, self) => 
                index === self.findIndex(t => t.name === team.name)
            );

            return uniqueTeams;
        }, year);

        return teams;
    }

    async scrapeTeam(team, year) {
        const teamData = {
            name: team.name,
            year: year,
            url: team.url,
            stats: {},
            basic_info: {}
        };

        try {
            await this.page.goto(team.url, { waitUntil: 'networkidle2', timeout: 30000 });
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Get basic team information
            const basicInfo = await this.page.evaluate(() => {
                const info = {};
                
                // Conference
                const conferenceSelectors = [
                    '.team-conference',
                    '.conference',
                    '[class*="conference"]',
                    '.team-info .conference'
                ];
                
                for (const selector of conferenceSelectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        info.conference = element.textContent.trim();
                        break;
                    }
                }

                // Record
                const recordSelectors = [
                    '.team-record',
                    '.record',
                    '[class*="record"]',
                    '.team-info .record'
                ];
                
                for (const selector of recordSelectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        info.record = element.textContent.trim();
                        break;
                    }
                }

                // Division
                const divisionSelectors = [
                    '.division',
                    '[class*="division"]',
                    '.team-info .division'
                ];
                
                for (const selector of divisionSelectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        info.division = element.textContent.trim();
                        break;
                    }
                }

                return info;
            });

            teamData.basic_info = basicInfo;

            // Scrape different stat categories
            for (const statPage of this.statsPages) {
                try {
                    const categoryStats = await this.scrapeStatPage(statPage);
                    teamData.stats[statPage] = categoryStats;
                } catch (error) {
                    console.error(`Error scraping ${statPage} for ${team.name}: ${error.message}`);
                }
            }

        } catch (error) {
            console.error(`Error scraping team ${team.name}: ${error.message}`);
        }

        return teamData;
    }

    async scrapeStatPage(statPage) {
        const stats = {};
        
        try {
            // Navigate to the specific stat page
            const statUrl = `${this.page.url()}/${statPage}`;
            await this.page.goto(statUrl, { waitUntil: 'networkidle2', timeout: 15000 });
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Extract stats from the page
            const pageStats = await this.page.evaluate((pageName) => {
                const stats = {};
                
                // Method 1: Look for data tables
                const tables = document.querySelectorAll('table');
                tables.forEach((table, tableIndex) => {
                    const rows = table.querySelectorAll('tr');
                    rows.forEach((row, rowIndex) => {
                        const cells = row.querySelectorAll('td, th');
                        if (cells.length >= 2) {
                            const statName = cells[0]?.textContent?.trim();
                            const statValue = cells[1]?.textContent?.trim();
                            
                            if (statName && statValue && statName.length > 0) {
                                const cleanName = statName.replace(/[^\w\s]/g, '').replace(/\s+/g, '_').toLowerCase();
                                stats[`${pageName}_${cleanName}`] = statValue;
                            }
                        }
                    });
                });

                // Method 2: Look for stat cards/divs
                const statElements = document.querySelectorAll('.stat-card, .stat-item, [class*="stat"], .metric');
                statElements.forEach((element, index) => {
                    const statName = element.querySelector('.stat-name, .stat-label, .metric-name')?.textContent?.trim();
                    const statValue = element.querySelector('.stat-value, .stat-number, .metric-value')?.textContent?.trim();
                    
                    if (statName && statValue) {
                        const cleanName = statName.replace(/[^\w\s]/g, '').replace(/\s+/g, '_').toLowerCase();
                        stats[`${pageName}_${cleanName}`] = statValue;
                    }
                });

                // Method 3: Look for any divs with data attributes
                const dataElements = document.querySelectorAll('[data-stat], [data-metric], [data-value]');
                dataElements.forEach((element, index) => {
                    const statName = element.getAttribute('data-stat') || element.getAttribute('data-metric') || element.textContent.trim();
                    const statValue = element.getAttribute('data-value') || element.textContent.trim();
                    
                    if (statName && statValue && statName !== statValue) {
                        const cleanName = statName.replace(/[^\w\s]/g, '').replace(/\s+/g, '_').toLowerCase();
                        stats[`${pageName}_${cleanName}`] = statValue;
                    }
                });

                return stats;
            }, statPage);

            Object.assign(stats, pageStats);

        } catch (error) {
            console.error(`Error scraping ${statPage} page: ${error.message}`);
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

        // Save summary
        const summaryPath = path.join(yearDir, 'summary.json');
        const summary = {
            year: year,
            total_teams: yearData.teams.length,
            timestamp: yearData.timestamp,
            data_files: ['teams.json', 'teams.csv']
        };
        await fs.writeJson(summaryPath, summary, { spaces: 2 });

        console.log(`💾 Saved data for ${year} to ${yearDir}`.green);
    }

    async saveAsCSV(data, filePath) {
        if (data.length === 0) return;

        // Flatten the data structure for CSV
        const flattenedData = data.map(team => {
            const flat = {
                name: team.name,
                year: team.year,
                conference: team.basic_info.conference || '',
                record: team.basic_info.record || '',
                division: team.basic_info.division || ''
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
                    console.log('\n⏳ Waiting 10 seconds before next year...'.yellow);
                    await new Promise(resolve => setTimeout(resolve, 10000));
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
    const scraper = new TeamRankingsScraper();
    scraper.run().catch(console.error);
}

module.exports = TeamRankingsScraper; 