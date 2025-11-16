# 🎯 Essential Columns for Equity-Focused ROI Calculator

## Core Philosophy
**"Which schools actually help underserved students succeed?"**

---

## 📊 MUST-HAVE Columns for Social Good Focus

### From College Results Dataset

```python
EQUITY_ESSENTIAL_COLUMNS = {
    # ========== INSTITUTIONAL IDENTITY ==========
    'Institution Name': 'Primary key for merging',
    'Institution Type': 'Public/Private/For-Profit matters for equity',
    'State of Institution': 'Geographic equity disparities',
    
    # ========== RACIAL/ETHNIC COMPOSITION (CRITICAL) ==========
    'Percent of Black or African American Undergraduates': 'URM representation',
    'Percent of Latino Undergraduates': 'URM representation', 
    'Percent of American Indian or Alaska Native Undergraduates': 'URM representation',
    'Percent of Asian Undergraduates': 'Minority representation',
    'Percent of White Undergraduates': 'For comparison/gap analysis',
    'Percent of Two or More Races Undergraduates': 'Growing demographic',
    
    # ========== GRADUATION RATES BY RACE (MOST IMPORTANT) ==========
    "Bachelor's Degree Graduation Rate Within 6 Years - Black, Non-Latino": 'Equity outcome',
    "Bachelor's Degree Graduation Rate Within 6 Years - Latino": 'Equity outcome',
    "Bachelor's Degree Graduation Rate Within 6 Years - White Non-Latino": 'Comparison baseline',
    "Bachelor's Degree Graduation Rate Within 6 Years - Asian": 'Additional equity metric',
    "Bachelor's Degree Graduation Rate Bachelor Degree Within 6 Years - Total": 'Overall baseline',
    
    # ========== ECONOMIC EQUITY INDICATORS ==========
    'Percent of First-Time, Full-Time Undergraduates Awarded Pell Grants': 'Low-income access',
    'Number of First-Time, Full-Time Undergraduates Awarded Pell Grants': 'Scale of impact',
    'Percent Full-time, First-time, Pell Grant Recipients Receiving an Award - 6 Years': 'Low-income success',
    
    # ========== FINANCIAL OUTCOMES ==========
    'Median Earnings of Students Working and Not Enrolled 10 Years After Entry': 'Economic outcome',
    'Median Earnings of Dependent Students Working and Not Enrolled 10 Years After Entry': 'Traditional students',
    'Median Earnings of Independent Students Working and Not Enrolled 10 Years After Entry': 'Non-traditional',
    
    # ========== DEBT BURDEN (IMPACTS MINORITIES MORE) ==========
    'Median Debt of Completers': 'Overall debt burden',
    'Median Debt for Dependent Students': 'Traditional student debt',
    'Median Debt for Independent Students': 'Non-traditional debt',
    
    # ========== COST BARRIERS ==========
    'Average Net Price for Low-Income Students, 2020-21': 'Actual cost for neediest',
    'Average Net Price After Grants, 2020-21': 'Real cost after aid',
    'Cost of Attendance for In-State Students Living on Campus': 'Sticker price',
    
    # ========== RETENTION (EARLY INDICATOR) ==========
    'First-Time, Full-Time Retention Rate': 'Do students stay?',
    
    # ========== SIZE/SCALE ==========
    'Total Enrollment': 'How many students impacted',
    'Number of Undergraduates Enrolled': 'Undergrad focus'
}
```

### From Affordability Gap Dataset

```python
AFFORDABILITY_EQUITY_COLUMNS = {
    # ========== IDENTIFIERS ==========
    'Institution Name': 'Merge key',
    'State Abbreviation': 'State code',
    
    # ========== MINORITY SERVING INSTITUTION STATUS (CRUCIAL) ==========
    'MSI Status': 'Is this a Minority Serving Institution?',
    'HBCU': 'Historically Black College/University',
    'HSI': 'Hispanic Serving Institution',
    'PBI': 'Predominantly Black Institution',
    'TRIBAL': 'Tribal College',
    'AANAPII': 'Asian American Native American Pacific Islander Institution',
    'ANNHI': 'Alaska Native Native Hawaiian Institution',
    
    # ========== WORK-STUDY REALITY (EQUITY ISSUE) ==========
    'Net Price': 'What students actually pay',
    'Affordability Gap (net price minus income earned working 10 hrs at min wage)': 'THE KEY METRIC',
    'Weekly Hours to Close Gap': 'Work burden on students',
    
    # ========== PARENT STUDENT CHALLENGES ==========
    'Student Parent Affordability Gap: Center-Based Care': 'Parent student burden',
    'Student Parent Affordability Gap: Home-Based Care': 'Alternative childcare burden',
    'Weekly Hours to Close Gap: Center-Based Care': 'Parent work hours needed',
    
    # ========== STATE CONTEXT ==========
    'State Minimum Wage': 'Local economic reality',
    "Income Earned from Working 10 Hours a Week at State's Minimum Wage": 'Work-study potential',
    
    # ========== INSTITUTIONAL CONTROL ==========
    'Control of Institution': '1=Public, 2=Private nonprofit, 3=For-profit',
    'Sector Name': 'Detailed institution type'
}
```

---

## 🧮 Calculated Equity Metrics You'll Create

```python
# RACIAL EQUITY GAPS (Critical for social good)
df['urm_percentage'] = df['black_pct'] + df['latino_pct'] + df['native_pct']
df['black_white_grad_gap'] = df['black_grad_rate'] - df['white_grad_rate']
df['latino_white_grad_gap'] = df['latino_grad_rate'] - df['white_grad_rate']
df['overall_urm_grad_gap'] = df[['black_grad_rate', 'latino_grad_rate']].mean(axis=1) - df['white_grad_rate']

# ECONOMIC MOBILITY SCORE
df['economic_mobility_score'] = (
    df['pell_pct'] *                    # Access for low-income
    df['pell_graduation_rate'] *        # Success for low-income
    df['earnings_10yr'] /                # Economic outcomes
    df['median_debt']                   # Debt burden
)

# EQUITY-ADJUSTED ROI
df['equity_roi'] = (
    df['basic_roi'] * 
    (1 + df['urm_pct']/100) *           # Bonus for serving URM
    (1 + df['pell_pct']/100) *          # Bonus for serving low-income
    (2 - abs(df['urm_grad_gap'])/100)   # Penalty for graduation gaps
)

# AFFORDABILITY STRESS INDEX
df['afford_stress'] = df['work_hours_needed'] / 20  # >1 means unsustainable
df['parent_afford_stress'] = df['parent_work_hours'] / 20

# DISPARATE IMPACT RATIO (Legal threshold = 0.8)
df['disparate_impact'] = df['urm_grad_rate'] / df['white_grad_rate']
df['needs_intervention'] = df['disparate_impact'] < 0.8
```

---

## 🎯 The 20 Columns You ABSOLUTELY Need

If you're pressed for time, these are the bare minimum for an equity-focused project:

```python
BARE_MINIMUM_EQUITY = [
    # Identity
    'Institution Name',
    'State',
    
    # Racial composition
    'Percent of Black or African American Undergraduates',
    'Percent of Latino Undergraduates', 
    'Percent of White Undergraduates',
    
    # Graduation equity
    "Bachelor's Degree Graduation Rate Within 6 Years - Black, Non-Latino",
    "Bachelor's Degree Graduation Rate Within 6 Years - Latino",
    "Bachelor's Degree Graduation Rate Within 6 Years - White Non-Latino",
    
    # Economic access
    'Percent of First-Time, Full-Time Undergraduates Awarded Pell Grants',
    'Median Earnings of Students Working and Not Enrolled 10 Years After Entry',
    'Median Debt of Completers',
    
    # Affordability reality
    'Net Price',
    'Weekly Hours to Close Gap',
    
    # MSI Status
    'HBCU',
    'HSI',
    'MSI Status'
]
```

---

## 📈 Visualizations That Show Social Impact

1. **Graduation Gap Scatter Plot**
   - X-axis: % URM students
   - Y-axis: URM-White graduation gap
   - Color: MSI status
   - Size: Total enrollment
   - **Shows**: Which schools serve AND succeed with URM students

2. **Economic Mobility Ladder**
   - X-axis: % Pell recipients
   - Y-axis: 10-year earnings
   - Color: Median debt
   - **Shows**: Schools that lift low-income students

3. **Work Hours Heat Map**
   - Geographic map
   - Color intensity: Weekly hours needed
   - Overlay: % URM students
   - **Shows**: Where education is actually accessible

4. **Disparate Impact Dashboard**
   - Bar chart of schools below 80% threshold
   - Table of interventions needed
   - **Shows**: Where systemic change is needed

---

## 🚨 Critical Equity Insights to Highlight

Your analysis should answer:

1. **"Where do students like me actually succeed?"**
   - Not just get in, but graduate
   - Not just graduate, but earn well
   - Not just earn, but without crushing debt

2. **"Which schools close racial gaps?"**
   - Schools where Black/Latino students graduate at similar rates to White students
   - Schools actively addressing disparate impact

3. **"Where can I afford to go without working full-time?"**
   - Schools where <20 hours/week covers costs
   - Parent-friendly schools with childcare considerations

4. **"Which MSIs provide best value?"**
   - HBCUs with strong ROI
   - HSIs with low debt burden
   - Tribal colleges with good outcomes

---

## 🎓 Sample Queries for Your Tool

```python
# Find schools with equity AND value
"Show me schools where Black students graduate at 70%+ rate with <$20k debt"

# Economic mobility focus  
"Which schools have 40%+ Pell students earning $40k+ after graduation?"

# Parent student friendly
"Find schools where I can afford tuition working less than 15 hours/week with childcare"

# MSI excellence
"Best HBCUs for STEM with high graduation rates"

# No gaps allowed
"Schools with less than 5% racial graduation gap"
```

---

## ⚠️ Ethical Considerations to Address

1. **ROI can perpetuate inequality** - High-earning fields are often less diverse
2. **Debt impacts communities differently** - $20k debt means different things to different families
3. **Graduation rates reflect support systems** - Not just student capability
4. **Geographic disparities** - Cost of living varies dramatically
5. **Hidden costs** - Childcare, transportation, family obligations

---

## 💡 Your Unique Value Proposition

**"We don't just show ROI - we show EQUITABLE ROI"**

Traditional calculators optimize for money.
Yours optimizes for social mobility and justice.

This wins datathons for social good.
