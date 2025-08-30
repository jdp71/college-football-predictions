const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const cliProgress = require('cli-progress');
const colors = require('colors');

class RobustNCAAScraper {
    constructor(config = {}) {
        this.baseUrl = 'https://www.teamrankings.com';
        this.dataDir = path.join(__dirname, '..', 'data');
        
        // Configurable options
        this.years = config.years || [2024];
        this.statsCategories = config.statsCategories || ['offense', 'defense'];
        this.maxTeams = config.maxTeams || 200;
        this.delayBetweenTeams = config.delayBetweenTeams || 3000;
        this.delayBetweenYears = config.delayBetweenYears || 15000;
        
        console.log('🎯 Robust NCAA Stats Scraper Configuration:'.green);
        console.log(`   Years: ${this.years.join(', ')}`);
        console.log(`   Stat Categories: ${this.statsCategories.join(', ')}`);
        console.log(`   Max Teams: ${this.maxTeams}`);
        console.log(`   Delay between teams: ${this.delayBetweenTeams}ms`);
        console.log(`   Delay between years: ${this.delayBetweenYears}ms`);
    }

    async initBrowser() {
        console.log('🚀 Initializing browser...'.green);
        
        const browser = await puppeteer.launch({
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

        const page = await browser.newPage();
        
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        await page.setViewport({ width: 1920, height: 1080 });
        
        await page.setExtraHTTPHeaders({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        });
        
        console.log('✅ Browser initialized successfully'.green);
        return { browser, page };
    }

    async scrapeYear(year) {
        console.log(`\n📊 Scraping data for year: ${year}`.cyan);
        
        const { browser, page } = await this.initBrowser();
        
        const yearData = {
            year: year,
            teams: [],
            timestamp: new Date().toISOString(),
            config: {
                years: this.years,
                statsCategories: this.statsCategories,
                maxTeams: this.maxTeams
            }
        };

        try {
            // Navigate to NCAA football page
            const url = `${this.baseUrl}/college-football/`;
            await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
            await new Promise(resolve => setTimeout(resolve, 3000));

            // Try to select the year
            await this.selectYear(page, year);

            // Get NCAA teams
            const teams = await this.getNCAATeams(page, year);
            console.log(`Found ${teams.length} NCAA teams for ${year}`);

            // Limit teams if needed
            let teamsToScrape = teams;
            if (teamsToScrape.length > this.maxTeams) {
                teamsToScrape = teamsToScrape.slice(0, this.maxTeams);
                console.log(`Limited to ${teamsToScrape.length} teams for scraping`);
            }

            const progressBar = new cliProgress.SingleBar({
                format: `Scraping ${year} |${colors.cyan('{bar}')}| {percentage}% | {value}/{total} teams | ETA: {eta}s`,
                barCompleteChar: '\u2588',
                barIncompleteChar: '\u2591',
                hideCursor: true
            });

            progressBar.start(teamsToScrape.length, 0);

            for (let i = 0; i < teamsToScrape.length; i++) {
                const team = teamsToScrape[i];
                
                try {
                    const teamData = await this.scrapeTeam(page, team, year);
                    yearData.teams.push(teamData);
                    
                    progressBar.update(i + 1);
                    
                    // Be respectful to the server
                    await new Promise(resolve => setTimeout(resolve, this.delayBetweenTeams));
                    
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
        } finally {
            await browser.close();
        }
    }

    async selectYear(page, year) {
        try {
            const yearSelectors = [
                'select[name="season"]',
                'select[data-season]',
                '.season-selector select',
                '#season-selector'
            ];

            for (const selector of yearSelectors) {
                const yearSelect = await page.$(selector);
                if (yearSelect) {
                    await page.select(selector, year.toString());
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    console.log(`Selected year ${year} using selector: ${selector}`);
                    return;
                }
            }

            console.log(`No year selector found for ${year}, continuing with current page`);
        } catch (error) {
            console.log(`Could not select year ${year}: ${error.message}`);
        }
    }

    async getNCAATeams(page, year) {
        const teams = await page.evaluate((year) => {
            const teamElements = document.querySelectorAll('a[href*="/college-football/team/"]');
            const teams = [];

            teamElements.forEach(element => {
                const name = element.textContent.trim();
                const url = element.href;
                
                // Filter out NFL teams
                const nflKeywords = ['cardinals', 'falcons', 'ravens', 'bills', 'panthers', 'bears', 'bengals', 'browns', 'cowboys', 'broncos', 'lions', 'packers', 'texans', 'colts', 'jaguars', 'chiefs', 'raiders', 'chargers', 'rams', 'dolphins', 'vikings', 'patriots', 'saints', 'giants', 'jets', 'eagles', 'steelers', '49ers', 'seahawks', 'buccaneers', 'titans', 'commanders'];
                
                const isNFL = nflKeywords.some(keyword => 
                    name.toLowerCase().includes(keyword)
                );
                
                if (name && url && name.length > 0 && name.length < 100 && !isNFL) {
                    // Try to extract conference info
                    let conference = '';
                    const parentElement = element.closest('tr, .team-row, .team-item');
                    if (parentElement) {
                        const conferenceElement = parentElement.querySelector('.conference, [class*="conference"], .conf');
                        if (conferenceElement) {
                            conference = conferenceElement.textContent.trim();
                        }
                    }
                    
                    teams.push({
                        name: name,
                        url: url,
                        conference: conference
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

    async scrapeTeam(page, team, year) {
        const teamData = {
            name: team.name,
            year: year,
            url: team.url,
            conference: team.conference,
            stats: {},
            basic_info: {}
        };

        try {
            await page.goto(team.url, { waitUntil: 'networkidle2', timeout: 30000 });
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Get basic team information
            const basicInfo = await page.evaluate(() => {
                const info = {};
                
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

                return info;
            });

            teamData.basic_info = basicInfo;

            // Scrape specified stat categories
            for (const statCategory of this.statsCategories) {
                try {
                    const categoryStats = await this.scrapeStatCategory(page, statCategory);
                    teamData.stats[statCategory] = categoryStats;
                } catch (error) {
                    console.error(`Error scraping ${statCategory} for ${team.name}: ${error.message}`);
                }
            }

        } catch (error) {
            console.error(`Error scraping team ${team.name}: ${error.message}`);
        }

        return teamData;
    }

    async scrapeStatCategory(page, category) {
        const stats = {};
        
        try {
            const categoryUrl = `${page.url()}/${category}`;
            await page.goto(categoryUrl, { waitUntil: 'networkidle2', timeout: 15000 });
            await new Promise(resolve => setTimeout(resolve, 2000));

            const categoryStats = await page.evaluate((cat) => {
                const stats = {};
                
                // Look for data tables
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
                                stats[`${cat}_${cleanName}`] = statValue;
                            }
                        }
                    });
                });

                // Look for stat cards/divs
                const statElements = document.querySelectorAll('.stat-card, .stat-item, [class*="stat"], .metric');
                statElements.forEach((element, index) => {
                    const statName = element.querySelector('.stat-name, .stat-label, .metric-name')?.textContent?.trim();
                    const statValue = element.querySelector('.stat-value, .stat-number, .metric-value')?.textContent?.trim();
                    
                    if (statName && statValue) {
                        const cleanName = statName.replace(/[^\w\s]/g, '').replace(/\s+/g, '_').toLowerCase();
                        stats[`${cat}_${cleanName}`] = statValue;
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

        const jsonPath = path.join(yearDir, 'teams.json');
        await fs.writeJson(jsonPath, yearData, { spaces: 2 });

        const csvPath = path.join(yearDir, 'teams.csv');
        await this.saveAsCSV(yearData.teams, csvPath);

        const summaryPath = path.join(yearDir, 'summary.json');
        const summary = {
            year: year,
            total_teams: yearData.teams.length,
            timestamp: yearData.timestamp,
            config: yearData.config,
            data_files: ['teams.json', 'teams.csv']
        };
        await fs.writeJson(summaryPath, summary, { spaces: 2 });

        console.log(`💾 Saved data for ${year} to ${yearDir}`.green);
    }

    async saveAsCSV(data, filePath) {
        if (data.length === 0) return;

        const flattenedData = data.map(team => {
            const flat = {
                name: team.name,
                year: team.year,
                conference: team.conference || team.basic_info?.conference || '',
                record: team.basic_info?.record || ''
            };

            if (team.stats) {
                Object.keys(team.stats).forEach(category => {
                    Object.keys(team.stats[category]).forEach(stat => {
                        flat[`${category}_${stat}`] = team.stats[category][stat];
                    });
                });
            }

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
            console.log(`\n🎯 Starting robust scrape for years: ${this.years.join(', ')}`.yellow);
            
            for (const year of this.years) {
                await this.scrapeYear(year);
                
                // Add delay between years
                if (year !== this.years[this.years.length - 1]) {
                    console.log(`\n⏳ Waiting ${this.delayBetweenYears/1000} seconds before next year...`.yellow);
                    await new Promise(resolve => setTimeout(resolve, this.delayBetweenYears));
                }
            }

            console.log('\n🎉 Scraping completed successfully!'.green);
            console.log(`📁 Data saved to: ${this.dataDir}`.cyan);

        } catch (error) {
            console.error('❌ Scraping failed:', error.message);
        }
    }
}

// Example configurations
const configs = {
    // Test with just 2024
    test: {
        years: [2024],
        statsCategories: ['offense', 'defense'],
        maxTeams: 10,
        delayBetweenTeams: 2000,
        delayBetweenYears: 5000
    },
    
    // Division I teams 2020-2024
    division1: {
        years: [2020, 2021, 2022, 2023, 2024],
        statsCategories: ['offense', 'defense', 'special-teams', 'efficiency', 'situational', 'advanced-stats'],
        maxTeams: 200,
        delayBetweenTeams: 3000,
        delayBetweenYears: 15000
    }
};

// Run the scraper
if (require.main === module) {
    const configName = process.argv[2] || 'test';
    const config = configs[configName] || configs.test;
    
    console.log(`Using configuration: ${configName}`.yellow);
    const scraper = new RobustNCAAScraper(config);
    scraper.run().catch(console.error);
}

module.exports = RobustNCAAScraper; 