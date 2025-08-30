#!/usr/bin/env python3
"""
Weekly Model Updater for College Football Predictions
Retrains the prediction model with new weekly data and deploys updates
"""

import pandas as pd
import numpy as np
import json
import pickle
import argparse
import os
import subprocess
import git
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

class WeeklyModelUpdater:
    def __init__(self):
        self.models_dir = 'models'
        self.backup_dir = 'model_backups'
        self.teams_file = 'college-football-app/teams.json'
        
        # Create directories if they don't exist
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_current_model(self):
        """Backup the current model before updating"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"model_backup_{timestamp}"
        
        try:
            # Backup model files
            model_files = [
                'college-football-app/app.js',
                self.teams_file,
                'models/cfb_prediction_model.pkl'
            ]
            
            for file_path in model_files:
                if os.path.exists(file_path):
                    backup_path = os.path.join(self.backup_dir, f"{backup_name}_{os.path.basename(file_path)}")
                    subprocess.run(['cp', file_path, backup_path])
            
            print(f"Current model backed up as: {backup_name}")
            return backup_name
            
        except Exception as e:
            print(f"Error backing up model: {e}")
            return None
    
    def load_team_data(self):
        """Load current team data"""
        try:
            with open(self.teams_file, 'r') as f:
                teams_data = json.load(f)
            return teams_data
        except Exception as e:
            print(f"Error loading team data: {e}")
            return None
    
    def create_training_features(self, teams_data):
        """Create training features from team data"""
        print("Creating training features from updated team data...")
        
        training_features = []
        
        for team in teams_data['teams']:
            if 'current_season' in team and team['current_season']['games_played'] > 0:
                # Create features for this team
                features = self._extract_team_features(team)
                training_features.append(features)
        
        if not training_features:
            print("No training features could be created!")
            return pd.DataFrame()
        
        df = pd.DataFrame(training_features)
        print(f"Created {len(df)} training examples")
        return df
    
    def _extract_team_features(self, team):
        """Extract features from team data"""
        current = team.get('current_season', {})
        
        features = {
            'team_name': team['name'],
            'conference': team.get('conference', 'Unknown'),
            'games_played': current.get('games_played', 0),
            'wins': current.get('wins', 0),
            'losses': current.get('losses', 0),
            'win_rate': current.get('wins', 0) / max(current.get('games_played', 1), 1),
            'ppg': current.get('ppg', 25.0),
            'papg': current.get('papg', 25.0),
            'point_diff': current.get('ppg', 25.0) - current.get('papg', 25.0),
            'total_points': current.get('points_for', 0),
            'total_points_against': current.get('points_against', 0)
        }
        
        return features
    
    def create_matchup_features(self, teams_data):
        """Create features for team matchups"""
        print("Creating matchup features...")
        
        matchups = []
        teams = teams_data['teams']
        
        # Create synthetic matchups for training
        import random
        random.seed(42)
        
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                team1 = teams[i]
                team2 = teams[j]
                
                # Only create matchups if both teams have played games
                if (team1.get('current_season', {}).get('games_played', 0) > 0 and 
                    team2.get('current_season', {}).get('games_played', 0) > 0):
                    
                    # Create home/away matchup
                    matchup = self._create_matchup_features(team1, team2, home_team=team1, away_team=team2)
                    matchups.append(matchup)
                    
                    # Create away/home matchup
                    matchup = self._create_matchup_features(team1, team2, home_team=team2, away_team=team1)
                    matchups.append(matchup)
        
        if not matchups:
            print("No matchup features could be created!")
            return pd.DataFrame()
        
        df = pd.DataFrame(matchups)
        print(f"Created {len(df)} matchup features")
        return df
    
    def _create_matchup_features(self, team1, team2, home_team, away_team):
        """Create features for a specific matchup"""
        home_current = home_team.get('current_season', {})
        away_current = away_team.get('current_season', {})
        
        # Determine winner based on win rate (simplified)
        home_win_rate = home_current.get('wins', 0) / max(home_current.get('games_played', 1), 1)
        away_win_rate = away_current.get('wins', 0) / max(away_current.get('games_played', 1), 1)
        
        # Add home field advantage
        home_advantage = 0.05  # 5% home field advantage
        adjusted_home_rate = home_win_rate + home_advantage
        
        home_wins = adjusted_home_rate > away_win_rate
        
        matchup = {
            'home_team': home_team['name'],
            'away_team': away_team['name'],
            'home_win': home_wins,
            'home_win_rate': home_win_rate,
            'away_win_rate': away_win_rate,
            'home_ppg': home_current.get('ppg', 25.0),
            'away_ppg': away_current.get('ppg', 25.0),
            'home_papg': home_current.get('papg', 25.0),
            'away_papg': away_current.get('papg', 25.0),
            'ppg_diff': home_current.get('ppg', 25.0) - away_current.get('ppg', 25.0),
            'papg_diff': home_current.get('papg', 25.0) - away_current.get('papg', 25.0),
            'home_games_played': home_current.get('games_played', 0),
            'away_games_played': away_current.get('games_played', 0),
            'conference_game': home_team.get('conference') == away_team.get('conference')
        }
        
        return matchup
    
    def train_models(self, training_data):
        """Train prediction models"""
        print("Training prediction models...")
        
        if training_data.empty:
            print("No training data available!")
            return None, None, None
        
        # Prepare features
        feature_cols = [col for col in training_data.columns 
                       if col not in ['home_team', 'away_team', 'home_win']]
        
        X = training_data[feature_cols].fillna(0)
        y = training_data['home_win']
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        # Train models
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, max_depth=6, random_state=42),
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000)
        }
        
        results = {}
        
        for name, model in models.items():
            print(f"Training {name}...")
            
            if name == 'Logistic Regression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_val_scaled)
                y_pred_proba = model.predict_proba(X_val_scaled)[:, 1]
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)
                y_pred_proba = model.predict_proba(X_val)[:, 1]
            
            accuracy = accuracy_score(y_val, y_pred)
            auc_score = roc_auc_score(y_val, y_pred_proba)
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'auc': auc_score
            }
            
            print(f"  Accuracy: {accuracy:.3f}")
            print(f"  AUC: {auc_score:.3f}")
        
        # Select best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['auc'])
        best_model = results[best_model_name]['model']
        
        print(f"\n✅ Best Model: {best_model_name}")
        print(f"Best AUC: {results[best_model_name]['auc']:.3f}")
        
        return best_model, scaler, feature_cols, results
    
    def save_model(self, model, scaler, feature_cols, model_name='cfb_prediction_model.pkl'):
        """Save the trained model"""
        model_data = {
            'model': model,
            'scaler': scaler,
            'feature_columns': feature_cols,
            'training_date': datetime.now().isoformat(),
            'model_version': 'weekly_update'
        }
        
        model_path = os.path.join(self.models_dir, model_name)
        
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            print(f"Model saved to: {model_path}")
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def update_app_js(self, model, scaler, feature_cols):
        """Update the app.js file with new model parameters"""
        print("Updating app.js with new model...")
        
        # This is a simplified update - in practice, you might want to
        # update specific prediction functions or model parameters
        
        try:
            # Read current app.js
            with open('college-football-app/app.js', 'r') as f:
                content = f.read()
            
            # Add model update timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_comment = f"\n// Model last updated: {timestamp}\n"
            
            # Find a good place to insert the update comment
            if '// Real ML-based College Football Prediction System' in content:
                content = content.replace(
                    '// Real ML-based College Football Prediction System',
                    f'// Real ML-based College Football Prediction System{update_comment}'
                )
            
            # Write updated content
            with open('college-football-app/app.js', 'w') as f:
                f.write(content)
            
            print("app.js updated with model timestamp")
            return True
            
        except Exception as e:
            print(f"Error updating app.js: {e}")
            return False
    
    def deploy_updates(self):
        """Deploy the updated model to production"""
        print("Deploying updates to production...")
        
        try:
            # Git operations
            repo = git.Repo('.')
            
            # Add all changes
            repo.index.add(['college-football-app/', 'models/'])
            
            # Commit changes
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Weekly model update - {timestamp}"
            repo.index.commit(commit_message)
            
            # Push to remote
            origin = repo.remote(name='origin')
            origin.push()
            
            print("Updates deployed successfully!")
            return True
            
        except Exception as e:
            print(f"Error deploying updates: {e}")
            return False
    
    def generate_update_report(self, training_data, model_results, week_number):
        """Generate a report of the model update"""
        print(f"\n{'='*60}")
        print(f"WEEK {week_number} MODEL UPDATE REPORT")
        print(f"{'='*60}")
        
        print(f"Training Data:")
        print(f"  Total matchups: {len(training_data)}")
        print(f"  Home win rate: {training_data['home_win'].mean():.3f}")
        print(f"  Conference games: {training_data['conference_game'].sum()}")
        
        if model_results:
            print(f"\nModel Performance:")
            for name, results in model_results.items():
                print(f"  {name}:")
                print(f"    Accuracy: {results['accuracy']:.3f}")
                print(f"    AUC: {results['auc']:.3f}")
        
        print(f"\nUpdate completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

def main():
    parser = argparse.ArgumentParser(description='Update college football prediction model')
    parser.add_argument('--week', type=int, required=True, help='Week number being updated')
    parser.add_argument('--backup', action='store_true', help='Backup current model')
    parser.add_argument('--deploy', action='store_true', help='Deploy updates to production')
    parser.add_argument('--report', action='store_true', help='Generate update report')
    
    args = parser.parse_args()
    
    updater = WeeklyModelUpdater()
    
    # Backup current model
    if args.backup:
        backup_name = updater.backup_current_model()
        if not backup_name:
            print("Failed to backup current model. Exiting.")
            return
    
    # Load team data
    teams_data = updater.load_team_data()
    if not teams_data:
        print("Failed to load team data. Exiting.")
        return
    
    # Create training data
    training_data = updater.create_matchup_features(teams_data)
    if training_data.empty:
        print("No training data available. Exiting.")
        return
    
    # Train models
    model, scaler, feature_cols, model_results = updater.train_models(training_data)
    if not model:
        print("Failed to train models. Exiting.")
        return
    
    # Save model
    success = updater.save_model(model, scaler, feature_cols)
    if not success:
        print("Failed to save model. Exiting.")
        return
    
    # Update app.js
    updater.update_app_js(model, scaler, feature_cols)
    
    # Deploy updates
    if args.deploy:
        success = updater.deploy_updates()
        if not success:
            print("Failed to deploy updates.")
    
    # Generate report
    if args.report:
        updater.generate_update_report(training_data, model_results, args.week)
    
    print(f"\nWeek {args.week} model update complete!")

if __name__ == "__main__":
    main()
