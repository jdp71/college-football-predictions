#!/usr/bin/env python3
"""
Master script to run the complete weekly update process
This script orchestrates data collection, model training, and deployment
"""

import argparse
import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='Run complete weekly model update')
    parser.add_argument('--week', type=int, required=True, help='Week number to update')
    parser.add_argument('--year', type=int, default=2025, help='Year (default: 2025)')
    parser.add_argument('--skip-data-collection', action='store_true', help='Skip data collection step')
    parser.add_argument('--skip-deployment', action='store_true', help='Skip deployment step')
    parser.add_argument('--api-key', type=str, help='CFBD API key (or set CFBD_API_KEY env var)')
    
    args = parser.parse_args()
    
    print(f"🏈 College Football Weekly Model Update")
    print(f"Week: {args.week}, Year: {args.year}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set API key if provided
    if args.api_key:
        os.environ['CFBD_API_KEY'] = args.api_key
    
    # Step 1: Data Collection
    if not args.skip_data_collection:
        success = run_command(
            f"python weekly_data_collector.py --week {args.week} --year {args.year} --update-teams --generate-report",
            "Step 1: Collecting Week Data and Updating Team Statistics"
        )
        if not success:
            print("❌ Data collection failed. Exiting.")
            sys.exit(1)
    else:
        print("⏭️  Skipping data collection step")
    
    # Step 2: Model Training and Update
    success = run_command(
        f"python weekly_model_updater.py --week {args.week} --backup --report",
        "Step 2: Training Updated Model"
    )
    if not success:
        print("❌ Model training failed. Exiting.")
        sys.exit(1)
    
    # Step 3: Deploy Updates
    if not args.skip_deployment:
        success = run_command(
            f"python weekly_model_updater.py --week {args.week} --deploy",
            "Step 3: Deploying Updates to Production"
        )
        if not success:
            print("❌ Deployment failed.")
            print("⚠️  Model was trained but not deployed. You can deploy manually later.")
        else:
            print("✅ All updates deployed successfully!")
    else:
        print("⏭️  Skipping deployment step")
        print("💡 To deploy later, run: python weekly_model_updater.py --week {args.week} --deploy")
    
    print(f"\n{'='*60}")
    print(f"🎉 Weekly Update Complete!")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"  Week {args.week} data collected: {'✅' if not args.skip_data_collection else '⏭️'}")
    print(f"  Model retrained: ✅")
    print(f"  Updates deployed: {'✅' if not args.skip_deployment else '⏭️'}")
    
    print(f"\n🌐 Your updated app is available at:")
    print(f"  https://jdp71.github.io/college-football-predictions/")
    
    print(f"\n📊 Next steps:")
    print(f"  1. Test the updated predictions")
    print(f"  2. Monitor model performance")
    print(f"  3. Prepare for Week {args.week + 1} update")

if __name__ == "__main__":
    main()
