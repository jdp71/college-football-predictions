# 🗓️ How to Update Model Each Week

## 📋 **Overview**
This document provides step-by-step instructions for updating your college football prediction model every Monday. The process is fully automated - you only need to run one command.

---

## 🚀 **Weekly Update Process (Every Monday)**

### **Step 1: Run the Weekly Update**
```bash
# Navigate to your project directory
cd /Users/jeff/NCAA\ Stats/college-football-app

# Run the weekly update (replace N with the week number)
python3 run_weekly_update.py --week N
```

**Examples:**
- **Week 2**: `python3 run_weekly_update.py --week 2`
- **Week 3**: `python3 run_weekly_update.py --week 3`
- **Week 4**: `python3 run_weekly_update.py --week 4`

### **Step 2: Wait for Automation to Complete**
The system will automatically:
- ✅ Collect previous week's game results
- ✅ Update team statistics with real performance data
- ✅ Retrain the prediction model
- ✅ Create backups of current data
- ✅ Deploy the updated model to production
- ✅ Generate performance reports

**Expected Time**: 5-10 minutes

---

## 🔧 **What Happens Automatically**

### **Data Collection**
- Scrapes actual game results from the previous week
- Updates team ratings based on real performance
- Creates backup of current `teams.json`
- Generates weekly data report

### **Model Update**
- Retrains prediction algorithm with new statistics
- Creates backup of current model
- Updates algorithm with timestamp
- Generates model performance report

### **Deployment**
- Commits all changes to Git
- Pushes to GitHub repository
- Deploys to GitHub Pages
- Model is live for next week's predictions

---

## 📊 **Expected Results Each Week**

### **Week 1 → Week 2**
- **Accuracy Improvement**: 49.5% → 55-65%
- **Better Team Ratings**: Based on actual performance
- **More Confident Predictions**: Less 50/50 outcomes

### **Week 2 → Week 3**
- **Further Accuracy**: 55-65% → 60-70%
- **Trend Recognition**: Model learns team patterns
- **Conference Strength**: Better understanding of divisions

### **Season Long**
- **Target Accuracy**: 65-75% by mid-season
- **Continuous Learning**: Model improves weekly
- **Performance Tracking**: Clear metrics on improvement

---

## 📁 **Generated Files Each Week**

After each update, you'll have:
```
college-football-app/
├── backups/
│   └── week_N_backup_YYYYMMDD_HHMMSS/
│       ├── app.js
│       └── teams.json
├── reports/
│   ├── week_N_report.md              # Game results & team updates
│   ├── week_N_model_report.md        # Model performance & updates
│   └── week_N_complete_summary.md    # Complete process summary
└── teams_backup_YYYYMMDD_HHMMSS.json # Backup of team data
```

---

## 🎯 **Monday Morning Checklist**

### **Before Running Update**
1. ✅ Ensure all previous week's games are completed
2. ✅ Verify you're in the correct directory
3. ✅ Check that no other processes are running

### **Run Update**
1. ✅ Execute: `python3 run_weekly_update.py --week N`
2. ✅ Monitor for any errors in terminal
3. ✅ Wait for completion message
4. ✅ Verify backup creation

### **After Update**
1. ✅ Check GitHub Pages deployment (wait 2-5 minutes)
2. ✅ Verify model accuracy improvement
3. ✅ Review generated reports
4. ✅ Test next week's predictions

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"Missing required packages"**
```bash
# Install required packages
pip install -r requirements.txt
```

#### **Git conflicts or errors**
```bash
# Check git status
git status

# If needed, reset to clean state
git reset --hard HEAD
git pull origin master
```

#### **Port already in use (for local testing)**
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
python3 -m http.server 8001
```

### **If Update Fails**
1. Check the error message in terminal
2. Review the backup files created
3. Restore from backup if needed
4. Contact support with error details

---

## 📈 **Performance Monitoring**

### **In-App Dashboard**
The app automatically shows:
- **Season Overview**: Overall accuracy and trends
- **Weekly Breakdown**: Performance by week
- **Improvement Tracking**: How accuracy increases over time
- **Game Coverage**: % of games successfully predicted

### **Key Metrics to Watch**
- **Prediction Coverage**: Should stay above 95%
- **Weekly Accuracy**: Should improve each week
- **Model Learning**: Less random predictions over time

---

## 🔄 **Automation Benefits**

### **What You Won't Have to Do**
- ❌ Manual data collection
- ❌ Manual model updates
- ❌ Manual deployment
- ❌ Manual performance tracking
- ❌ Back-and-forth troubleshooting

### **What Happens Automatically**
- ✅ Data collection from previous week
- ✅ Model retraining with new statistics
- ✅ Performance analysis and reporting
- ✅ Deployment to production
- ✅ Backup and version control

---

## 📅 **Weekly Schedule**

### **Monday Morning (Recommended)**
- Run update after all weekend games are complete
- Allows full day for any issues to be resolved
- Model ready for next week's predictions

### **Alternative Times**
- **Sunday Night**: If all games are complete
- **Monday Afternoon**: If you prefer later in the day
- **Tuesday**: As last resort (not recommended)

---

## 🎉 **Summary**

**Every Monday, you'll just need to:**
1. **Run one command**: `python3 run_weekly_update.py --week N`
2. **Wait 5-10 minutes** for automation to complete
3. **Check the results** in your app

**The system will automatically:**
- Update team statistics with real game data
- Retrain the prediction model
- Deploy the improved model
- Track performance improvements
- Generate detailed reports

**Result**: Your model gets smarter every week, and you get better predictions without any manual work! 🏈🚀

---

## 📞 **Support**

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the generated error logs
3. Check the backup files created
4. Contact support with specific error details

**Remember**: The system creates backups before every update, so your data is always safe! 🛡️
