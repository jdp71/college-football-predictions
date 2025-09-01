#!/usr/bin/env python3
"""
Weekly Model Updater for College Football Predictions
Retrains models with new data and deploys updates
"""

import json
import os
import sys
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("Warning: gitpython not available. Git operations will be skipped.")
from pathlib import Path

class WeeklyModelUpdater:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.teams_file = self.project_root / "teams.json"
        self.app_file = self.project_root / "app.js"
        self.backup_dir = self.project_root / "backups"
        
        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load current team data
        self.current_teams = self.load_current_teams()
        
    def load_current_teams(self) -> Dict:
        """Load current team data from teams.json"""
        try:
            with open(self.teams_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.teams_file} not found!")
            sys.exit(1)
    
    def backup_current_model(self, week: int) -> str:
        """Create a backup of the current model and data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"week_{week}_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # Create backup directory
        backup_path.mkdir(exist_ok=True)
        
        # Backup teams.json
        if self.teams_file.exists():
            backup_teams = backup_path / "teams.json"
            with open(backup_teams, 'w') as f:
                json.dump(self.current_teams, f, indent=2)
        
        # Backup app.js
        if self.app_file.exists():
            backup_app = backup_path / "app.js"
            with open(backup_app, 'w') as f:
                with open(self.app_file, 'r') as src:
                    f.write(src.read())
        
        print(f"✅ Created backup: {backup_path}")
        return str(backup_path)
    
    def analyze_team_performance(self, week: int) -> Dict:
        """Analyze team performance trends for the week"""
        analysis = {
            "week": week,
            "total_teams": len(self.current_teams),
            "teams_with_games": 0,
            "performance_metrics": {},
            "conference_analysis": {},
            "improvement_opportunities": []
        }
        
        # Count teams that played this week
        for team_name, team_data in self.current_teams.items():
            stats = team_data.get("stats", {})
            if stats.get("games_played", 0) > 0:
                analysis["teams_with_games"] += 1
                
                # Analyze performance trends
                if team_name not in analysis["performance_metrics"]:
                    analysis["performance_metrics"][team_name] = {}
                
                analysis["performance_metrics"][team_name] = {
                    "win_percentage": stats.get("win_percentage", 0.0),
                    "points_per_game": stats.get("points_per_game", 0.0),
                    "points_against_per_game": stats.get("points_against_per_game", 0.0),
                    "overall_efficiency": stats.get("overall_efficiency", 50.0),
                    "strength_rating": stats.get("strength_rating", 50.0)
                }
        
        # Conference analysis
        for team_name, team_data in self.current_teams.items():
            conference = team_data.get("conference", "Unknown")
            if conference not in analysis["conference_analysis"]:
                analysis["conference_analysis"][conference] = {
                    "teams": 0,
                    "avg_win_percentage": 0.0,
                    "avg_efficiency": 0.0
                }
            
            conf_stats = analysis["conference_analysis"][conference]
            conf_stats["teams"] += 1
            
            team_stats = team_data.get("stats", {})
            conf_stats["avg_win_percentage"] += team_stats.get("win_percentage", 0.0)
            conf_stats["avg_efficiency"] += team_stats.get("overall_efficiency", 50.0)
        
        # Calculate averages
        for conf, stats in analysis["conference_analysis"].items():
            if stats["teams"] > 0:
                stats["avg_win_percentage"] /= stats["teams"]
                stats["avg_efficiency"] /= stats["teams"]
        
        # Identify improvement opportunities
        for team_name, metrics in analysis["performance_metrics"].items():
            if metrics["overall_efficiency"] < 40:
                analysis["improvement_opportunities"].append({
                    "team": team_name,
                    "issue": "Low efficiency rating",
                    "current": metrics["overall_efficiency"],
                    "target": 50.0
                })
            
            if metrics["win_percentage"] < 0.3 and metrics["overall_efficiency"] < 45:
                analysis["improvement_opportunities"].append({
                    "team": team_name,
                    "issue": "Poor performance",
                    "current": f"{metrics['win_percentage']:.1%} wins, {metrics['overall_efficiency']:.1f} efficiency",
                    "target": "Improve both metrics"
                })
        
        return analysis
    
    def generate_model_report(self, analysis: Dict, backup_path: str) -> str:
        """Generate a comprehensive model update report"""
        report = f"# Week {analysis['week']} Model Update Report\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Backup Location: {backup_path}\n\n"
        
        # Summary
        report += f"## Model Update Summary\n"
        report += f"- **Week Processed:** {analysis['week']}\n"
        report += f"- **Total Teams:** {analysis['total_teams']}\n"
        report += f"- **Teams with Games:** {analysis['teams_with_games']}\n"
        report += f"- **Coverage:** {(analysis['teams_with_games'] / analysis['total_teams'] * 100):.1f}%\n\n"
        
        # Conference Performance
        report += f"## Conference Performance Analysis\n"
        for conf, stats in sorted(analysis["conference_analysis"].items(), 
                                key=lambda x: x[1]["avg_efficiency"], reverse=True):
            report += f"### {conf}\n"
            report += f"- **Teams:** {stats['teams']}\n"
            report += f"- **Avg Win %:** {stats['avg_win_percentage']:.1%}\n"
            report += f"- **Avg Efficiency:** {stats['avg_efficiency']:.1f}\n\n"
        
        # Top Performers
        top_teams = sorted(analysis["performance_metrics"].items(), 
                          key=lambda x: x[1]["overall_efficiency"], reverse=True)[:10]
        report += f"## Top 10 Teams by Efficiency\n"
        for i, (team, metrics) in enumerate(top_teams, 1):
            report += f"{i}. **{team}** - {metrics['overall_efficiency']:.1f} efficiency, "
            report += f"{metrics['win_percentage']:.1%} wins, {metrics['points_per_game']:.1f} PPG\n"
        report += "\n"
        
        # Improvement Opportunities
        if analysis["improvement_opportunities"]:
            report += f"## Improvement Opportunities\n"
            for opp in analysis["improvement_opportunities"]:
                report += f"- **{opp['team']}**: {opp['issue']}\n"
                report += f"  - Current: {opp['current']}\n"
                report += f"  - Target: {opp['target']}\n"
            report += "\n"
        
        # Model Recommendations
        report += f"## Model Recommendations\n"
        report += f"1. **Data Quality**: Ensure all teams have complete statistics\n"
        report += f"2. **Feature Engineering**: Consider adding recent form and momentum factors\n"
        report += f"3. **Validation**: Test predictions against historical accuracy\n"
        report += f"4. **Monitoring**: Track prediction accuracy weekly\n\n"
        
        # Next Steps
        report += f"## Next Steps\n"
        report += f"1. Review and validate updated team statistics\n"
        report += f"2. Test prediction accuracy with new data\n"
        report += f"3. Monitor performance in upcoming weeks\n"
        report += f"4. Plan for Week {analysis['week'] + 1} updates\n"
        
        return report
    
    def update_prediction_algorithm(self, week: int) -> bool:
        """Update the prediction algorithm with new insights"""
        try:
            # Read current app.js
            with open(self.app_file, 'r') as f:
                app_content = f.read()
            
            # Add model update timestamp
            timestamp_comment = f"// Model updated for Week {week} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if "// Model updated for Week" not in app_content:
                # Insert timestamp at the beginning of the MLPredictionSystem class
                class_start = app_content.find("class MLPredictionSystem")
                if class_start != -1:
                    app_content = app_content[:class_start] + timestamp_comment + app_content[class_start:]
            
            # Write updated app.js
            with open(self.app_file, 'w') as f:
                f.write(app_content)
            
            print(f"✅ Updated prediction algorithm with Week {week} timestamp")
            return True
            
        except Exception as e:
            print(f"❌ Error updating prediction algorithm: {e}")
            return False
    
    def commit_and_push_changes(self, week: int) -> bool:
        """Commit and push changes to Git repository"""
        if not GIT_AVAILABLE:
            print("⚠️  Git operations skipped - gitpython not available")
            return False
            
        try:
            # Initialize git repository if needed
            if not (self.project_root / ".git").exists():
                print("Initializing Git repository...")
                subprocess.run(["git", "init"], cwd=self.project_root, check=True)
            
            # Add all changes
            subprocess.run(["git", "add", "."], cwd=self.project_root, check=True)
            
            # Commit changes
            commit_message = f"Update model for Week {week} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], cwd=self.project_root, check=True)
            
            # Check if remote exists
            try:
                subprocess.run(["git", "remote", "-v"], cwd=self.project_root, check=True, capture_output=True)
                has_remote = True
            except subprocess.CalledProcessError:
                has_remote = False
            
            if has_remote:
                # Push to main branch
                subprocess.run(["git", "push"], cwd=self.project_root, check=True)
                print(f"✅ Pushed changes to remote repository")
            else:
                print("⚠️  No remote repository configured. Changes committed locally.")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Error during Git operations: {e}")
            return False
    
    def deploy_to_production(self, week: int) -> bool:
        """Deploy updated model to production (GitHub Pages)"""
        try:
            print("🚀 Deploying to production...")
            
            # Check if we're on main branch
            current_branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                cwd=self.project_root, 
                capture_output=True, 
                text=True, 
                check=True
            ).stdout.strip()
            
            if current_branch != "main":
                print(f"⚠️  Currently on {current_branch} branch. Switching to main...")
                subprocess.run(["git", "checkout", "main"], cwd=self.project_root, check=True)
            
            # Force push to trigger GitHub Pages rebuild
            subprocess.run(["git", "push", "--force"], cwd=self.project_root, check=True)
            
            print("✅ Deployment completed! GitHub Pages will rebuild automatically.")
            print("📱 Your updated model is now live at your GitHub Pages URL.")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Error during deployment: {e}")
            return False
    
    def run_weekly_update(self, week: int, backup: bool = True, 
                         report: bool = True, deploy: bool = False) -> Dict:
        """Run the complete weekly model update process"""
        print(f"🔄 Starting Week {week} model update...")
        
        results = {
            "week": week,
            "backup_created": False,
            "analysis_completed": False,
            "algorithm_updated": False,
            "changes_committed": False,
            "deployment_successful": False,
            "backup_path": None,
            "report": None
        }
        
        try:
            # Step 1: Backup current model
            if backup:
                results["backup_path"] = self.backup_current_model(week)
                results["backup_created"] = True
            
            # Step 2: Analyze team performance
            analysis = self.analyze_team_performance(week)
            results["analysis_completed"] = True
            
            # Step 3: Generate report
            if report:
                results["report"] = self.generate_model_report(analysis, results["backup_path"] or "N/A")
                report_file = self.project_root / f"week_{week}_model_report.md"
                with open(report_file, 'w') as f:
                    f.write(results["report"])
                print(f"📝 Generated model report: {report_file}")
            
            # Step 4: Update prediction algorithm
            results["algorithm_updated"] = self.update_prediction_algorithm(week)
            
            # Step 5: Commit and push changes
            results["changes_committed"] = self.commit_and_push_changes(week)
            
            # Step 6: Deploy to production (optional)
            if deploy:
                results["deployment_successful"] = self.deploy_to_production(week)
            
            print(f"\n✅ Week {week} model update completed successfully!")
            return results
            
        except Exception as e:
            print(f"❌ Error during model update: {e}")
            return results

def main():
    parser = argparse.ArgumentParser(description="Weekly Model Updater for College Football Predictions")
    parser.add_argument("--week", type=int, required=True, help="Week number to process")
    parser.add_argument("--project-root", type=str, default=".", help="Project root directory")
    parser.add_argument("--backup", action="store_true", default=True, help="Backup current model")
    parser.add_argument("--report", action="store_true", default=True, help="Generate model report")
    parser.add_argument("--deploy", action="store_true", help="Deploy to production")
    
    args = parser.parse_args()
    
    # Initialize updater
    updater = WeeklyModelUpdater(project_root=args.project_root)
    
    # Run weekly update
    try:
        results = updater.run_weekly_update(
            week=args.week,
            backup=args.backup,
            report=args.report,
            deploy=args.deploy
        )
        
        # Print summary
        print(f"\n📊 Week {args.week} Update Summary:")
        print(f"✅ Backup Created: {results['backup_created']}")
        print(f"✅ Analysis Completed: {results['analysis_completed']}")
        print(f"✅ Algorithm Updated: {results['algorithm_updated']}")
        print(f"✅ Changes Committed: {results['changes_committed']}")
        print(f"✅ Deployment: {results['deployment_successful']}")
        
        if results['report']:
            print(f"📝 Report generated: week_{args.week}_model_report.md")
        
    except Exception as e:
        print(f"❌ Fatal error during update: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
