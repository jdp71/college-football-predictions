const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const cliProgress = require('cli-progress');
const colors = require('colors');

class NCAAStatsScraper {
    constructor(config = {}) {
        this.browser = null;
        this.page = null;
        this.baseUrl = 'https://www.teamrankings.com';
        this.dataDir = path.join(__dirname, '..', 'data');
        
        // Configurable options
        this.years = config.years || [2024]; // Default to just 2024
        this.conferences = config.conferences || []; // Empty = all conferences
        this.teams = config.teams || []; // Empty = all teams
        this.statsCategories = config.statsCategories || ['offense', 'defense']; // Default categories
        this.maxTeams = config.maxTeams || 50; // Limit for testing
        
        console.log('🎯 NCAA Stats Scraper Configuration:'.green);
        console.log(`   Years: ${this.years.join(', ')}`);
        console.log(`   Conferences: ${this.conferences.length > 0 ? this.conferences.join(', ') : 'All'}`);
        console.log(`   Teams: ${this.teams.length > 0 ? this.teams.join(', ') : 'All'}`);
        console.log(`   Stat Categories: ${this.statsCategories.join(', ')}`);
        console.log(`   Max Teams: ${this.maxTeams}`);
    }

    async init() {
        console.log('🚀 Initializing NCAA Stats Scraper...'.green);
        
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
        
        await this.page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        await this.page.setViewport({ width: 1920, height: 1080 });
        
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
            timestamp: new Date().toISOString(),
            config: {
                years: this.years,
                conferences: this.conferences,
                teams: this.teams,
                statsCategories: this.statsCategories,
                maxTeams: this.maxTeams
            }
        };

        try {
            // Navigate to NCAA football page
            const url = `${this.baseUrl}/college-football/`;
            await this.page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
            await new Promise(resolve => setTimeout(resolve, 3000));

            // Try to select the year
            await this.selectYear(year);

            // Get NCAA teams only
            const teams = await this.getNCAATeams(year);
            console.log(`Found ${teams.length} NCAA teams for ${year}`);

            // Filter teams based on configuration
            let filteredTeams = teams;
            
            if (this.conferences.length > 0) {
                const originalCount = filteredTeams.length;
                filteredTeams = filteredTeams.filter(team => 
                    this.conferences.some(conf => 
                        team.conference && team.conference.toLowerCase().includes(conf.toLowerCase())
                    )
                );
                console.log(`Filtered to ${filteredTeams.length} teams in specified conferences (from ${originalCount} total)`);
                
                // If no teams found with conference filtering, use all teams
                if (filteredTeams.length === 0) {
                    console.log('No teams found with conference filtering, using all teams');
                    filteredTeams = teams;
                }
            }

            if (this.teams.length > 0) {
                filteredTeams = filteredTeams.filter(team => 
                    this.teams.some(targetTeam => 
                        team.name.toLowerCase().includes(targetTeam.toLowerCase())
                    )
                );
                console.log(`Filtered to ${filteredTeams.length} teams matching specified names`);
            }

            // Limit teams for testing
            if (filteredTeams.length > this.maxTeams) {
                filteredTeams = filteredTeams.slice(0, this.maxTeams);
                console.log(`Limited to ${filteredTeams.length} teams for testing`);
            }

            const progressBar = new cliProgress.SingleBar({
                format: `Scraping ${year} |${colors.cyan('{bar}')}| {percentage}% | {value}/{total} teams | ETA: {eta}s`,
                barCompleteChar: '\u2588',
                barIncompleteChar: '\u2591',
                hideCursor: true
            });

            progressBar.start(filteredTeams.length, 0);

            for (let i = 0; i < filteredTeams.length; i++) {
                const team = filteredTeams[i];
                
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

            console.log(`No year selector found for ${year}, continuing with current page`);
        } catch (error) {
            console.log(`Could not select year ${year}: ${error.message}`);
        }
    }

    async getNCAATeams(year) {
        const teams = await this.page.evaluate((year) => {
            const teamElements = document.querySelectorAll('a[href*="/college-football/team/"]');
            const teams = [];

            teamElements.forEach(element => {
                const name = element.textContent.trim();
                const url = element.href;
                
                // Filter out NFL teams and other non-NCAA teams
                const nflKeywords = ['cardinals', 'falcons', 'ravens', 'bills', 'panthers', 'bears', 'bengals', 'browns', 'cowboys', 'broncos', 'lions', 'packers', 'texans', 'colts', 'jaguars', 'chiefs', 'raiders', 'chargers', 'rams', 'dolphins', 'vikings', 'patriots', 'saints', 'giants', 'jets', 'eagles', 'steelers', '49ers', 'seahawks', 'buccaneers', 'titans', 'commanders'];
                
                const isNFL = nflKeywords.some(keyword => 
                    name.toLowerCase().includes(keyword)
                );
                
                // Filter for Division I teams (FBS and FCS) - be more inclusive
                const division1Keywords = ['university', 'state', 'tech', 'college', 'institute', 'state', 'carolina', 'florida', 'texas', 'ohio', 'michigan', 'alabama', 'georgia', 'tennessee', 'kentucky', 'mississippi', 'arkansas', 'missouri', 'louisiana', 'auburn', 'vanderbilt', 'south carolina', 'clemson', 'north carolina', 'duke', 'wake forest', 'virginia', 'virginia tech', 'miami', 'florida state', 'boston college', 'syracuse', 'pittsburgh', 'rutgers', 'maryland', 'penn state', 'indiana', 'purdue', 'illinois', 'northwestern', 'wisconsin', 'minnesota', 'iowa', 'nebraska', 'michigan state', 'ohio state', 'iowa state', 'kansas', 'kansas state', 'oklahoma', 'oklahoma state', 'baylor', 'texas tech', 'tcu', 'west virginia', 'texas a&m', 'arizona', 'arizona state', 'california', 'ucla', 'usc', 'stanford', 'oregon', 'oregon state', 'washington', 'washington state', 'colorado', 'utah', 'byu', 'nevada', 'boise state', 'fresno state', 'san diego state', 'hawaii', 'new mexico', 'wyoming', 'air force', 'colorado state', 'utah state', 'nevada', 'unlv', 'san jose state', 'new mexico state', 'utep', 'rice', 'smu', 'tulsa', 'tulane', 'memphis', 'houston', 'ucf', 'south florida', 'east carolina', 'temple', 'navy', 'army', 'notre dame', 'liberty', 'connecticut', 'massachusetts', 'old dominion', 'charlotte', 'florida atlantic', 'florida international', 'middle tennessee', 'western kentucky', 'marshall', 'appalachian state', 'georgia southern', 'georgia state', 'coastal carolina', 'troy', 'south alabama', 'texas state', 'louisiana', 'louisiana monroe', 'arkansas state', 'ball state', 'bowling green', 'buffalo', 'central michigan', 'eastern michigan', 'kent state', 'miami ohio', 'northern illinois', 'ohio', 'toledo', 'western michigan', 'akron'];
                const hasDivision1Keyword = division1Keywords.some(keyword => 
                    name.toLowerCase().includes(keyword)
                );
                
                if (name && url && name.length > 0 && name.length < 100 && !isNFL) {
                    // Try to extract conference info from nearby elements
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

    async scrapeTeam(team, year) {
        const teamData = {
            name: team.name,
            year: year,
            url: team.url,
            conference: team.conference,
            stats: {},
            basic_info: {}
        };

        try {
            await this.page.goto(team.url, { waitUntil: 'networkidle2', timeout: 30000 });
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Get basic team information
            const basicInfo = await this.page.evaluate(() => {
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

            // Scrape specified stat categories
            for (const statCategory of this.statsCategories) {
                try {
                    const categoryStats = await this.scrapeStatCategory(statCategory);
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

    async scrapeStatCategory(category) {
        const stats = {};
        
        try {
            const categoryUrl = `${this.page.url()}/${category}`;
            await this.page.goto(categoryUrl, { waitUntil: 'networkidle2', timeout: 15000 });
            await new Promise(resolve => setTimeout(resolve, 2000));

            const categoryStats = await this.page.evaluate((cat) => {
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
                record: team.basic_info?.record || '',
                division: team.basic_info?.division || ''
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
            await this.init();

            console.log(`\n🎯 Starting scrape for years: ${this.years.join(', ')}`.yellow);
            
            for (const year of this.years) {
                await this.scrapeYear(year);
                
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

// Example configurations
const configs = {
    // Test with just a few teams
    test: {
        years: [2024],
        teams: ['Alabama', 'Michigan', 'Georgia'],
        statsCategories: ['offense', 'defense'],
        maxTeams: 3
    },
    
    // Power 5 conferences only
    power5: {
        years: [2024],
        conferences: ['SEC', 'Big Ten', 'ACC', 'Big 12', 'Pac-12'],
        statsCategories: ['offense', 'defense', 'special-teams'],
        maxTeams: 100
    },
    
    // Full scrape
    full: {
        years: [2024],
        statsCategories: ['offense', 'defense', 'special-teams', 'efficiency', 'situational', 'advanced-stats'],
        maxTeams: 200
    },
    
    // Division I teams 2020-2024
    division1: {
        years: [2020, 2021, 2022, 2023, 2024],
        statsCategories: ['offense', 'defense', 'special-teams', 'efficiency', 'situational', 'advanced-stats'],
        maxTeams: 1000, // High limit to get all D1 teams
        conferences: ['SEC', 'Big Ten', 'ACC', 'Big 12', 'Pac-12', 'American', 'Conference USA', 'MAC', 'Mountain West', 'Sun Belt', 'Independent']
    }
};

// Run the scraper
if (require.main === module) {
    const configName = process.argv[2] || 'test';
    const config = configs[configName] || configs.test;
    
    console.log(`Using configuration: ${configName}`.yellow);
    const scraper = new NCAAStatsScraper(config);
    scraper.run().catch(console.error);
}

module.exports = NCAAStatsScraper; 