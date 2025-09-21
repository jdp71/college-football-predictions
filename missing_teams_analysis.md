# Missing Teams Analysis - August 30, 2025

## Overview
- **Total Games Today**: 47
- **Games Algorithm Could Predict**: 17
- **Games Algorithm Could NOT Predict**: 30
- **Missing Coverage**: 63.8%

## 🔍 **Why Only 17 Games Could Be Predicted**

### **Team Coverage Issues**

#### **FCS Teams (Not in teams.json)**
These teams are outside the scope of your FBS-focused algorithm:
- **Tarleton State** (vs Army)
- **Bethune-Cookman** (vs FIU)
- **Kennesaw State** (vs Wake Forest)
- **Western Illinois** (vs Illinois)
- **Wagner** (vs Kansas)
- **Central Arkansas** (vs Missouri)
- **SFA/Stephen F. Austin** (vs Houston)
- **Stony Brook** (vs San Diego State)
- **Saint Francis** (vs ULM)
- **Jacksonville State** (vs UCF)
- **UT Martin** (vs Oklahoma State)
- **Elon** (vs Duke)
- **Delaware State** (vs Delaware)
- **Lafayette** (vs Bowling Green)
- **Idaho State** (vs UNLV)
- **Sam Houston** (vs UNLV)
- **VMI** (vs Navy)
- **Merrimack** (vs Kent State)
- **Central Connecticut State** (vs UConn)
- **Robert Morris** (vs West Virginia)
- **Duquesne** (vs Pittsburgh)
- **Northwestern** (vs Tulane)
- **Fordham** (vs Boston College)
- **Holy Cross** (vs Northern Illinois)
- **South Dakota** (vs Iowa State)
- **Bucknell** (vs Air Force)
- **Maine** (vs Liberty)
- **Eastern Kentucky** (vs Louisville)
- **Weber State** (vs James Madison)
- **Coastal Carolina** (vs Virginia)
- **Illinois State** (vs Oklahoma)
- **Albany** (vs Iowa)
- **North Dakota** (vs Kansas State)
- **Charleston Southern** (vs Vanderbilt)
- **Austin Peay** (vs Middle Tennessee)
- **UTSA** (vs Texas A&M)
- **North Alabama** (vs Western Kentucky)
- **Southeast Missouri State** (vs Arkansas State)
- **Morgan State** (vs South Alabama)
- **Nicholls State** (vs Troy)
- **Long Island** (vs Florida)
- **Southeastern Louisiana** (vs Louisiana Tech)
- **Missouri State** (vs Southern California)
- **New Mexico** (vs Michigan)
- **Arkansas-Pine Bluff** (vs Texas Tech)
- **Northern Arizona** (vs Arizona State)
- **Idaho** (vs Washington State)
- **California** (vs Oregon State)
- **Hawaii** (vs Arizona)
- **Colorado State** (vs Washington)
- **Utah** (vs UCLA)

#### **FBS Teams Missing from teams.json**
These teams should be in your 128-team list but appear to be missing:
- **App State** (Appalachian State)
- **NIU** (Northern Illinois)
- **FIU** (Florida International)
- **Charlotte**
- **ULM** (Louisiana-Monroe)
- **UCF** (Central Florida)
- **Akron**
- **Wyoming**
- **UNLV**
- **Fresno State**
- **Western Kentucky**
- **Sam Houston State**
- **Hawaii**
- **Stanford**
- **South Florida**
- **Boise State**
- **Rutgers**
- **Ohio**
- **Bowling Green**
- **Delaware**
- **NC State**
- **East Carolina**
- **UAB**
- **Alabama State**
- **Wisconsin**
- **Miami (OH)**
- **Cincinnati**
- **Nebraska**
- **San Diego State**
- **Army**
- **Charlotte**
- **App State**
- **FIU**
- **Bethune-Cookman**
- **Wake Forest**
- **Michigan State**
- **Illinois**
- **Kansas**
- **Baylor**
- **Sam Houston**
- **San Jose State**
- **Central Michigan**

## 🎯 **Root Cause Analysis**

### **1. FCS Team Coverage**
- **Problem**: Your algorithm is designed for FBS teams only
- **Impact**: ~25 games involve FCS teams that can't be predicted
- **Solution**: Either expand to FCS or focus on FBS-only games

### **2. Team Naming Mismatches**
- **Problem**: Some teams have different names in NCAA data vs teams.json
- **Examples**: 
  - "App State" vs "Appalachian State"
  - "NIU" vs "Northern Illinois"
  - "FIU" vs "Florida International"
- **Impact**: Algorithm can't match team names
- **Solution**: Standardize team naming conventions

### **3. Missing FBS Teams**
- **Problem**: Some FBS teams appear to be missing from teams.json
- **Impact**: Reduced coverage of FBS games
- **Solution**: Verify all 130 FBS teams are included

## 📊 **Coverage Breakdown**

### **Games by Team Type**
- **FBS vs FBS**: 25 games (53%)
- **FBS vs FCS**: 18 games (38%)
- **FCS vs FCS**: 4 games (9%)

### **Algorithm Coverage by Type**
- **FBS vs FBS**: 17/25 (68%)
- **FBS vs FCS**: 0/18 (0%)
- **FCS vs FCS**: 0/4 (0%)

## 🚀 **Immediate Actions Needed**

### **1. Fix Team Naming**
- Standardize team names between NCAA data and teams.json
- Handle abbreviations (App State → Appalachian State)
- Handle special characters (Alabama A&M)

### **2. Verify FBS Coverage**
- Ensure all 130 FBS teams are in teams.json
- Add any missing FBS teams
- Remove any non-FBS teams

### **3. Expand Coverage Options**
- **Option A**: Focus on FBS vs FBS games only (target: 25 games)
- **Option B**: Add FCS teams for full coverage (target: 47 games)
- **Option C**: Hybrid approach with FBS priority

## 📈 **Expected Results After Fixes**

### **With FBS vs FBS Focus**
- **Coverage**: 25/47 games (53%)
- **Expected Accuracy**: 75-80%
- **Predictable Games**: All major conference matchups

### **With Full FCS Coverage**
- **Coverage**: 47/47 games (100%)
- **Expected Accuracy**: 70-75%
- **Predictable Games**: All games, including FCS upsets

## 🎯 **Recommendation**

**Focus on FBS vs FBS games first** (25 games) to achieve:
- **Higher accuracy** (75-80%)
- **Better data quality** (FBS teams have more reliable stats)
- **Faster implementation** (fix naming issues only)

Then expand to FCS coverage if desired for complete Week 1 coverage.
