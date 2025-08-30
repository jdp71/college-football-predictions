const fs = require('fs-extra');
const path = require('path');

class DataAnalyzer {
    constructor() {
        this.dataDir = path.join(__dirname, '..', 'data');
    }

    async analyze() {
        console.log('📊 Analyzing scraped data...'.green);

        const years = await this.getAvailableYears();
        console.log(`Found data for ${years.length} years: ${years.join(', ')}`);

        for (const year of years) {
            await this.analyzeYear(year);
        }

        await this.generateSummary(years);
    }

    async getAvailableYears() {
        try {
            const items = await fs.readdir(this.dataDir);
            return items
                .filter(item => {
                    const itemPath = path.join(this.dataDir, item);
                    return fs.statSync(itemPath).isDirectory() && /^\d{4}$/.test(item);
                })
                .map(year => parseInt(year))
                .sort((a, b) => a - b);
        } catch (error) {
            console.error('Error reading data directory:', error.message);
            return [];
        }
    }

    async analyzeYear(year) {
        const yearDir = path.join(this.dataDir, year.toString());
        const jsonPath = path.join(yearDir, 'teams.json');

        try {
            if (await fs.pathExists(jsonPath)) {
                const data = await fs.readJson(jsonPath);
                
                console.log(`\n📈 ${year} Analysis:`.cyan);
                console.log(`   Teams: ${data.teams.length}`);
                
                if (data.teams.length > 0) {
                    const conferences = [...new Set(data.teams.map(team => team.basic_info?.conference).filter(Boolean))];
                    console.log(`   Conferences: ${conferences.length} (${conferences.slice(0, 5).join(', ')}${conferences.length > 5 ? '...' : ''})`);
                    
                    const statCategories = Object.keys(data.teams[0].stats || {});
                    console.log(`   Stat Categories: ${statCategories.length} (${statCategories.join(', ')})`);
                    
                    // Count teams with complete data
                    const teamsWithStats = data.teams.filter(team => 
                        team.stats && Object.keys(team.stats).length > 0
                    ).length;
                    console.log(`   Teams with stats: ${teamsWithStats}/${data.teams.length}`);
                }
            } else {
                console.log(`\n❌ No data found for ${year}`);
            }
        } catch (error) {
            console.error(`Error analyzing ${year}:`, error.message);
        }
    }

    async generateSummary(years) {
        console.log('\n📋 Overall Summary:'.green);
        console.log(`Total years: ${years.length}`);
        console.log(`Date range: ${Math.min(...years)} - ${Math.max(...years)}`);
        
        let totalTeams = 0;
        let totalFiles = 0;
        
        for (const year of years) {
            const yearDir = path.join(this.dataDir, year.toString());
            const files = await fs.readdir(yearDir);
            totalFiles += files.length;
            
            const jsonPath = path.join(yearDir, 'teams.json');
            if (await fs.pathExists(jsonPath)) {
                try {
                    const data = await fs.readJson(jsonPath);
                    totalTeams += data.teams.length;
                } catch (error) {
                    console.error(`Error reading ${year} data:`, error.message);
                }
            }
        }
        
        console.log(`Total teams across all years: ${totalTeams}`);
        console.log(`Total data files: ${totalFiles}`);
        
        // Calculate data size
        const dataSize = await this.calculateDataSize();
        console.log(`Total data size: ${dataSize}`);
    }

    async calculateDataSize() {
        try {
            const size = await this.getDirectorySize(this.dataDir);
            return this.formatBytes(size);
        } catch (error) {
            return 'Unknown';
        }
    }

    async getDirectorySize(dirPath) {
        let size = 0;
        
        try {
            const items = await fs.readdir(dirPath);
            
            for (const item of items) {
                const itemPath = path.join(dirPath, item);
                const stats = await fs.stat(itemPath);
                
                if (stats.isDirectory()) {
                    size += await this.getDirectorySize(itemPath);
                } else {
                    size += stats.size;
                }
            }
        } catch (error) {
            console.error('Error calculating directory size:', error.message);
        }
        
        return size;
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async exportToCSV() {
        console.log('\n📄 Exporting combined data to CSV...'.green);
        
        const allData = [];
        const years = await this.getAvailableYears();
        
        for (const year of years) {
            const yearDir = path.join(this.dataDir, year.toString());
            const jsonPath = path.join(yearDir, 'teams.json');
            
            if (await fs.pathExists(jsonPath)) {
                try {
                    const data = await fs.readJson(jsonPath);
                    allData.push(...data.teams);
                } catch (error) {
                    console.error(`Error reading ${year} data:`, error.message);
                }
            }
        }
        
        if (allData.length > 0) {
            const csvPath = path.join(this.dataDir, 'all_teams_combined.csv');
            await this.saveAsCSV(allData, csvPath);
            console.log(`✅ Combined data exported to: ${csvPath}`);
        } else {
            console.log('❌ No data to export');
        }
    }

    async saveAsCSV(data, filePath) {
        const createCsvWriter = require('csv-writer').createObjectCsvWriter;
        
        // Flatten the data structure for CSV
        const flattenedData = data.map(team => {
            const flat = {
                name: team.name,
                year: team.year,
                conference: team.basic_info?.conference || '',
                record: team.basic_info?.record || '',
                division: team.basic_info?.division || ''
            };

            // Flatten stats
            if (team.stats) {
                Object.keys(team.stats).forEach(category => {
                    Object.keys(team.stats[category]).forEach(stat => {
                        flat[`${category}_${stat}`] = team.stats[category][stat];
                    });
                });
            }

            return flat;
        });

        if (flattenedData.length === 0) return;

        const csvWriter = createCsvWriter({
            path: filePath,
            header: Object.keys(flattenedData[0]).map(key => ({
                id: key,
                title: key
            }))
        });

        await csvWriter.writeRecords(flattenedData);
    }
}

// Run the analyzer
if (require.main === module) {
    const analyzer = new DataAnalyzer();
    
    const args = process.argv.slice(2);
    const command = args[0];
    
    if (command === 'export') {
        analyzer.exportToCSV().catch(console.error);
    } else {
        analyzer.analyze().catch(console.error);
    }
}

module.exports = DataAnalyzer; 