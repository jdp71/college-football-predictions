# test_model_loading.py
# Run this script to test if your model loads correctly

import pickle
import os
import pandas as pd
import numpy as np

def test_model_loading():
    print("🔍 Testing model loading...")
    print("=" * 50)
    
    # Check for common model file names
    model_files = [
        'cfb_prediction_model.pkl',
        'model.pkl', 
        'trained_model.pkl',
        'cfb_model.pkl',
        'college_football_model.pkl'
    ]
    
    print("📁 Looking for model files:")
    for file in model_files:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"   {exists} {file}")
    
    # Try to load the first available model
    model_loaded = False
    model = None
    scaler = None
    feature_columns = []
    
    for model_file in model_files:
        if os.path.exists(model_file):
            try:
                print(f"\n🔄 Attempting to load {model_file}...")
                
                with open(model_file, 'rb') as f:
                    model_data = pickle.load(f)
                
                print(f"✅ Successfully loaded {model_file}")
                print(f"📊 Model data type: {type(model_data)}")
                
                # Handle different save formats
                if isinstance(model_data, dict):
                    print("📋 Model saved as dictionary. Keys:")
                    for key in model_data.keys():
                        print(f"   - {key}: {type(model_data[key])}")
                    
                    model = model_data.get('model')
                    scaler = model_data.get('scaler')
                    feature_columns = model_data.get('feature_columns', [])
                    
                else:
                    print("🤖 Model saved as single object")
                    model = model_data
                
                model_loaded = True
                
                # Test model properties
                if model is not None:
                    print(f"🎯 Model type: {type(model)}")
                    if hasattr(model, 'predict'):
                        print("✅ Model has predict method")
                    if hasattr(model, 'predict_proba'):
                        print("✅ Model has predict_proba method")
                    if hasattr(model, 'feature_importances_'):
                        print(f"📈 Feature importances available: {len(model.feature_importances_)} features")
                
                if scaler is not None:
                    print(f"📏 Scaler type: {type(scaler)}")
                
                if feature_columns:
                    print(f"🔢 Feature columns: {len(feature_columns)} features")
                    print(f"   First 10: {feature_columns[:10]}")
                
                break
                
            except Exception as e:
                print(f"❌ Error loading {model_file}: {e}")
                continue
    
    if not model_loaded:
        print("\n❌ No model files found or loaded successfully")
        return False
    
    # Test prediction
    print(f"\n🧪 Testing prediction...")
    try:
        # Create sample features
        if feature_columns:
            # Use actual feature columns
            sample_features = pd.DataFrame([[0] * len(feature_columns)], columns=feature_columns)
        else:
            # Create basic sample features
            sample_features = pd.DataFrame([[1, 0, 25.0, 20.0, 400, 350]], 
                                         columns=['is_home', 'is_conference_game', 'home_ppg', 'away_ppg', 'home_ypg', 'away_ypg'])
        
        print(f"📊 Sample features shape: {sample_features.shape}")
        
        # Scale if scaler available
        if scaler is not None:
            try:
                sample_features_scaled = scaler.transform(sample_features)
                print("✅ Scaling successful")
            except Exception as e:
                print(f"⚠️ Scaling failed: {e}")
                sample_features_scaled = sample_features
        else:
            sample_features_scaled = sample_features
        
        # Test prediction
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(sample_features_scaled)
            print(f"✅ Predict proba successful: {probabilities}")
            
        elif hasattr(model, 'predict'):
            prediction = model.predict(sample_features_scaled)
            print(f"✅ Predict successful: {prediction}")
        
        print("🎉 Model testing completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Prediction test failed: {e}")
        return False

def check_additional_files():
    print("\n🔍 Checking for additional files...")
    
    additional_files = [
        'scaler.pkl',
        'feature_scaler.pkl', 
        'feature_columns.pkl',
        'features.pkl',
        'team_stats.pkl',
        '2024_team_stats.pkl',
        '2025_college_football_schedules.json'
    ]
    
    for file in additional_files:
        if os.path.exists(file):
            print(f"✅ Found: {file}")
            try:
                if file.endswith('.pkl'):
                    with open(file, 'rb') as f:
                        data = pickle.load(f)
                    print(f"   Type: {type(data)}")
                    if isinstance(data, (list, dict)):
                        print(f"   Length: {len(data)}")
                elif file.endswith('.json'):
                    import json
                    with open(file, 'r') as f:
                        data = json.load(f)
                    print(f"   Type: {type(data)}, Length: {len(data)}")
            except Exception as e:
                print(f"   ❌ Error reading: {e}")
        else:
            print(f"❌ Missing: {file}")

if __name__ == "__main__":
    print("🏈 College Football Model Testing")
    print("=" * 50)
    
    # Test model loading
    success = test_model_loading()
    
    # Check additional files
    check_additional_files()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Your model should work with the updated app!")
        print("\n📋 Next steps:")
        print("1. Replace the CFBPredictionSystem class in app.py")
        print("2. Make sure your model files are in the same directory")
        print("3. Restart your Flask app")
        print("4. Test with Utah vs UCLA - should give consistent results")
    else:
        print("❌ Model loading failed. Please check:")
        print("1. Model file exists and is not corrupted")
        print("2. All required dependencies are installed")
        print("3. Model was saved correctly during training")
        
    print("\n💡 If you need help, please share:")
    print("- The exact filename of your model file")
    print("- How you saved the model during training")
    print("- Any error messages from this test")