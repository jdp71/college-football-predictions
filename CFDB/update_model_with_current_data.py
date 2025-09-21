#!/usr/bin/env python3
"""
Master Script: Update Model with Current Season Data
Runs the complete process of collecting current stats and retraining the model
"""

import os
import sys
import subprocess
from datetime import datetime

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n🔄 {description}...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            if result.stdout:
                print("Standard output:")
                print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Main function to run the complete update process"""
    print("🏈 College Football Model Update System")
    print("=" * 60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Collect current season stats
    print("\n📊 STEP 1: Collecting Current Season Stats")
    if not run_script("collect_current_stats.py", "Collecting current season stats"):
        print("❌ Failed to collect current stats. Cannot proceed.")
        return False
    
    # Step 2: Retrain model with current data
    print("\n🎯 STEP 2: Retraining Model with Current Data")
    if not run_script("retrain_model_with_current_data.py", "Retraining model with current season data"):
        print("❌ Failed to retrain model. Cannot proceed.")
        return False
    
    # Step 3: Update web app
    print("\n🌐 STEP 3: Updating Web App")
    if not run_script("update_web_app_model.py", "Updating web app with retrained model"):
        print("❌ Failed to update web app.")
        return False
    
    # Success!
    print("\n" + "=" * 60)
    print("🎉 MODEL UPDATE COMPLETE!")
    print("=" * 60)
    
    print("\n✅ What was accomplished:")
    print("1. 📊 Collected current 2025 season stats for all teams")
    print("2. 🎯 Retrained the prediction model with current data")
    print("3. 🌐 Updated the web app to use the retrained model")
    
    print("\n🚀 Your prediction system now has:")
    print("- ✅ Real current season performance data")
    print("- ✅ Updated team ratings based on 2025 performance")
    print("- ✅ More accurate predictions for Utah vs Wyoming and all games")
    print("- ✅ Model trained on actual current season stats")
    
    print("\n📋 Next steps:")
    print("1. 🔄 Refresh your web app at http://localhost:8002")
    print("2. 🧪 Test predictions with current season data")
    print("3. 📈 Check that Utah vs Wyoming shows realistic predictions")
    print("4. 🎯 Run predictions for upcoming games")
    
    print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n❌ Update process failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n🎊 All done! Your prediction system is now up-to-date with current season data!")


