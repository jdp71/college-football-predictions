#!/usr/bin/env python3
"""
Model Retraining Script with Current Season Data
Retrains the college football prediction model using current 2025 season stats
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

class ModelRetrainer:
    def __init__(self):
        self.current_stats_file = "current_season_stats.json"
        self.original_model_file = "cfb_prediction_model.pkl"
        self.output_model_file = "cfb_prediction_model_2025_updated.pkl"
        
        # Load current stats
        self.current_stats = self.load_current_stats()
        
        # Feature columns from original model
        self.feature_columns = [
            'home_points_per_game', 'home_total_yards', 'home_passing_yards', 'home_rushing_yards',
            'home_turnovers', 'home_off_success_rate', 'home_off_explosiveness', 'home_def_success_rate',
            'home_def_explosiveness', 'home_sp_rating', 'away_points_per_game', 'away_total_yards',
            'away_passing_yards', 'away_rushing_yards', 'away_turnovers', 'away_off_success_rate',
            'away_off_explosiveness', 'away_def_success_rate', 'away_def_explosiveness', 'away_sp_rating',
            'ppg_diff', 'papg_diff', 'ypg_diff', 'yapg_diff', 'turnovers_diff', 'takeaways_diff',
            'week', 'is_home', 'is_conference_game', 'home_conf_SEC', 'home_conf_Big Ten', 'home_conf_Big 12',
            'home_conf_ACC', 'home_conf_Pac-12', 'home_conf_Mountain West', 'home_conf_American',
            'home_conf_Conference USA', 'home_conf_MAC', 'home_conf_Sun Belt', 'home_conf_Independents',
            'away_conf_SEC', 'away_conf_Big Ten', 'away_conf_Big 12', 'away_conf_ACC'
        ]
    
    def load_current_stats(self):
        """Load current season stats"""
        if not os.path.exists(self.current_stats_file):
            print(f"❌ Current stats file not found: {self.current_stats_file}")
            print("Run collect_current_stats.py first to collect current season data")
            return {}
        
        with open(self.current_stats_file, 'r') as f:
            stats = json.load(f)
        
        print(f"✅ Loaded current stats for {len(stats)} teams")
        return stats
    
    def generate_training_data(self, num_games=1000):
        """Generate training data using current season stats"""
        print("🎯 Generating training data with current season stats...")
        
        teams = list(self.current_stats.keys())
        training_data = []
        
        for _ in range(num_games):
            # Randomly select two teams
            home_team = np.random.choice(teams)
            away_team = np.random.choice([t for t in teams if t != home_team])
            
            # Get stats for both teams
            home_stats = self.current_stats[home_team]
            away_stats = self.current_stats[away_team]
            
            # Create feature vector
            features = {}
            
            # Basic stats
            features['home_points_per_game'] = home_stats.get('points_per_game', 25.0)
            features['home_total_yards'] = home_stats.get('total_yards', 400.0)
            features['home_passing_yards'] = home_stats.get('passing_yards', 250.0)
            features['home_rushing_yards'] = home_stats.get('rushing_yards', 150.0)
            features['home_turnovers'] = home_stats.get('turnovers', 1.2)
            features['home_off_success_rate'] = home_stats.get('off_success_rate', 0.6)
            features['home_off_explosiveness'] = home_stats.get('off_explosiveness', 0.4)
            features['home_def_success_rate'] = home_stats.get('def_success_rate', 0.6)
            features['home_def_explosiveness'] = home_stats.get('def_explosiveness', 0.4)
            features['home_sp_rating'] = home_stats.get('sp_rating', 0.7)
            
            features['away_points_per_game'] = away_stats.get('points_per_game', 25.0)
            features['away_total_yards'] = away_stats.get('total_yards', 400.0)
            features['away_passing_yards'] = away_stats.get('passing_yards', 250.0)
            features['away_rushing_yards'] = away_stats.get('rushing_yards', 150.0)
            features['away_turnovers'] = away_stats.get('turnovers', 1.2)
            features['away_off_success_rate'] = away_stats.get('off_success_rate', 0.6)
            features['away_off_explosiveness'] = away_stats.get('off_explosiveness', 0.4)
            features['away_def_success_rate'] = away_stats.get('def_success_rate', 0.6)
            features['away_def_explosiveness'] = away_stats.get('def_explosiveness', 0.4)
            features['away_sp_rating'] = away_stats.get('sp_rating', 0.7)
            
            # Differential features
            features['ppg_diff'] = features['home_points_per_game'] - features['away_points_per_game']
            features['papg_diff'] = features['away_points_per_game'] - features['home_points_per_game']  # Points allowed diff
            features['ypg_diff'] = features['home_total_yards'] - features['away_total_yards']
            features['yapg_diff'] = features['away_total_yards'] - features['home_total_yards']  # Yards allowed diff
            features['turnovers_diff'] = features['away_turnovers'] - features['home_turnovers']  # Home advantage in turnovers
            features['takeaways_diff'] = home_stats.get('takeaways', 1.3) - away_stats.get('takeaways', 1.3)
            
            # Game context features
            features['week'] = np.random.randint(1, 13)  # Random week 1-12
            features['is_home'] = 1  # Always home team perspective
            features['is_conference_game'] = 1 if np.random.random() > 0.6 else 0  # 40% conference games
            
            # Conference features (simplified)
            home_conf = self.get_team_conference(home_team)
            away_conf = self.get_team_conference(away_team)
            
            for conf in ['SEC', 'Big Ten', 'Big 12', 'ACC', 'Pac-12', 'Mountain West', 'American', 'Conference USA', 'MAC', 'Sun Belt', 'Independents']:
                features[f'home_conf_{conf}'] = 1 if home_conf == conf else 0
                features[f'away_conf_{conf}'] = 1 if away_conf == conf else 0
            
            # Determine outcome based on stats (realistic simulation)
            home_advantage = 0.05  # 5% home field advantage
            stat_advantage = self.calculate_stat_advantage(home_stats, away_stats)
            
            # Add some randomness
            random_factor = np.random.normal(0, 0.1)
            
            home_win_prob = 0.5 + home_advantage + stat_advantage + random_factor
            home_win_prob = np.clip(home_win_prob, 0.1, 0.9)  # Keep probabilities realistic
            
            # Create label (1 if home team wins, 0 if away team wins)
            label = 1 if np.random.random() < home_win_prob else 0
            
            training_data.append({
                'features': features,
                'label': label,
                'home_team': home_team,
                'away_team': away_team,
                'home_win_prob': home_win_prob
            })
        
        return training_data
    
    def calculate_stat_advantage(self, home_stats, away_stats):
        """Calculate statistical advantage for home team"""
        # Points per game advantage
        ppg_adv = (home_stats.get('points_per_game', 25) - away_stats.get('points_per_game', 25)) / 100
        
        # Defense advantage (lower points allowed is better)
        def_adv = (away_stats.get('points_allowed_per_game', 25) - home_stats.get('points_allowed_per_game', 25)) / 100
        
        # Total yards advantage
        ypg_adv = (home_stats.get('total_yards', 400) - away_stats.get('total_yards', 400)) / 1000
        
        # Success rate advantage
        off_sr_adv = home_stats.get('off_success_rate', 0.6) - away_stats.get('off_success_rate', 0.6)
        def_sr_adv = home_stats.get('def_success_rate', 0.6) - away_stats.get('def_success_rate', 0.6)
        
        # Combine advantages
        total_advantage = (ppg_adv + def_adv + ypg_adv + off_sr_adv + def_sr_adv) / 5
        
        return np.clip(total_advantage, -0.3, 0.3)  # Limit to reasonable range
    
    def get_team_conference(self, team_name):
        """Get conference for a team"""
        conferences = {
            'SEC': ['Alabama', 'Georgia', 'LSU', 'Texas', 'Oklahoma', 'Auburn', 'Florida', 'Tennessee', 'Arkansas', 'Ole Miss', 'Mississippi State', 'South Carolina', 'Missouri', 'Kentucky', 'Vanderbilt', 'Texas A&M'],
            'Big Ten': ['Ohio State', 'Michigan', 'Penn State', 'Iowa', 'Wisconsin', 'Nebraska', 'Minnesota', 'Purdue', 'Illinois', 'Indiana', 'Northwestern', 'Maryland', 'Rutgers', 'Oregon', 'Washington', 'USC', 'UCLA'],
            'Big 12': ['Utah', 'BYU', 'Arizona', 'Arizona State', 'Colorado', 'Kansas', 'Kansas State', 'Oklahoma State', 'TCU', 'Texas Tech', 'Baylor', 'Iowa State', 'Houston', 'UCF', 'Cincinnati', 'West Virginia'],
            'ACC': ['Florida State', 'Clemson', 'Miami', 'North Carolina', 'Virginia Tech', 'Pittsburgh', 'Louisville', 'Boston College', 'Syracuse', 'Wake Forest', 'Duke', 'Georgia Tech', 'NC State', 'Virginia', 'California', 'Stanford', 'SMU']
        }
        
        for conf, teams in conferences.items():
            if team_name in teams:
                return conf
        return 'Other'
    
    def retrain_model(self):
        """Retrain the model with current season data"""
        if not self.current_stats:
            print("❌ No current stats available for retraining")
            return False
        
        print("🔄 Retraining model with current season data...")
        
        # Generate training data
        training_data = self.generate_training_data(num_games=2000)
        
        # Convert to DataFrame
        df_features = []
        df_labels = []
        
        for data_point in training_data:
            features = data_point['features']
            label = data_point['label']
            
            # Ensure all required features are present
            feature_vector = []
            for col in self.feature_columns:
                feature_vector.append(features.get(col, 0))
            
            df_features.append(feature_vector)
            df_labels.append(label)
        
        X = np.array(df_features)
        y = np.array(df_labels)
        
        print(f"📊 Generated {len(X)} training samples")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        
        best_model = None
        best_score = 0
        best_model_name = None
        
        for name, model in models.items():
            print(f"🎯 Training {name}...")
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            
            print(f"  📈 Train Accuracy: {train_score:.3f}")
            print(f"  📈 Test Accuracy: {test_score:.3f}")
            print(f"  📈 CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
            
            if test_score > best_score:
                best_score = test_score
                best_model = model
                best_model_name = name
        
        # Save the best model
        model_data = {
            'model': best_model,
            'scaler': scaler,
            'feature_columns': self.feature_columns,
            'model_name': best_model_name,
            'training_timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'model_results': {
                'train_accuracy': best_model.score(X_train_scaled, y_train),
                'test_accuracy': best_score,
                'cv_accuracy_mean': cross_val_score(best_model, X_train_scaled, y_train, cv=5).mean(),
                'training_samples': len(X),
                'features_count': len(self.feature_columns)
            },
            'current_stats_summary': {
                'teams_count': len(self.current_stats),
                'stats_collected_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # Save model
        with open(self.output_model_file, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n✅ Model retraining complete!")
        print(f"🏆 Best model: {best_model_name} (Accuracy: {best_score:.3f})")
        print(f"💾 Saved to: {self.output_model_file}")
        
        # Show feature importance if available
        if hasattr(best_model, 'feature_importances_'):
            print(f"\n📊 Top 10 Most Important Features:")
            feature_importance = list(zip(self.feature_columns, best_model.feature_importances_))
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            
            for i, (feature, importance) in enumerate(feature_importance[:10]):
                print(f"  {i+1:2d}. {feature}: {importance:.3f}")
        
        return True
    
    def compare_models(self):
        """Compare original and retrained models"""
        print("\n🔄 Comparing original and retrained models...")
        
        # Load original model
        if os.path.exists(self.original_model_file):
            with open(self.original_model_file, 'rb') as f:
                original_data = pickle.load(f)
            print(f"📅 Original model trained: {original_data.get('training_timestamp', 'Unknown')}")
            print(f"🎯 Original model accuracy: {original_data.get('model_results', {}).get('test_accuracy', 'Unknown')}")
        else:
            print("❌ Original model file not found")
        
        # Load retrained model
        if os.path.exists(self.output_model_file):
            with open(self.output_model_file, 'rb') as f:
                retrained_data = pickle.load(f)
            print(f"📅 Retrained model trained: {retrained_data.get('training_timestamp', 'Unknown')}")
            print(f"🎯 Retrained model accuracy: {retrained_data.get('model_results', {}).get('test_accuracy', 'Unknown')}")
            print(f"📊 Teams in current stats: {retrained_data.get('current_stats_summary', {}).get('teams_count', 'Unknown')}")
        else:
            print("❌ Retrained model file not found")

def main():
    """Main function to retrain the model"""
    print("🏈 College Football Model Retrainer")
    print("=" * 50)
    
    retrainer = ModelRetrainer()
    
    # Check if current stats are available
    if not retrainer.current_stats:
        print("❌ No current season stats found!")
        print("Please run collect_current_stats.py first to collect current season data")
        return
    
    # Retrain model
    success = retrainer.retrain_model()
    
    if success:
        # Compare models
        retrainer.compare_models()
        
        print(f"\n🎉 Retraining complete!")
        print(f"📋 Next steps:")
        print(f"1. Test the new model: {retrainer.output_model_file}")
        print(f"2. Update the web app to use the retrained model")
        print(f"3. Run predictions with current season data")
    else:
        print("❌ Retraining failed")

if __name__ == "__main__":
    main()


