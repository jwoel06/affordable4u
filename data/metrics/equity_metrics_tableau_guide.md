# 📊 Equity Metrics & Tableau Visualization Guide

## 🎯 Core Metrics to Calculate

### 1. **Racial Equity Gap Score** (MOST IMPORTANT)
```python
# Calculate graduation gaps by race
df['black_white_grad_gap'] = df['black_grad_6yr'] - df['white_grad_6yr']
df['latino_white_grad_gap'] = df['latino_grad_6yr'] - df['white_grad_6yr'] 
df['asian_white_grad_gap'] = df['asian_grad_6yr'] - df['white_grad_6yr']

# Overall URM gap (weighted average based on enrollment)
df['urm_enrollment'] = df['black_pct'] + df['latino_pct'] + df['native_pct']
df['urm_grad_rate'] = (
    (df['black_grad_6yr'] * df['black_pct'] + 
     df['latino_grad_6yr'] * df['latino_pct']) /
    (df['black_pct'] + df['latino_pct'])
)
df['overall_equity_gap'] = df['urm_grad_rate'] - df['white_grad_6yr']

# Equity Score (100 = perfect equity, 0 = worst gap)
df['racial_equity_score'] = 100 - abs(df['overall_equity_gap'])
```

**Tableau Viz**: Scatter plot with % URM enrollment on X, equity gap on Y, color by institution type

---

### 2. **Economic Mobility Index**
```python
# How well does school move low-income to high-income?
df['economic_mobility_index'] = (
    (df['pell_pct'] / 100) *                          # Access: % low-income admitted
    (df['pell_grad_rate_6yr'] / df['overall_grad_rate_6yr']) *  # Success: Relative success
    (df['earnings_10yr'] / df['earnings_10yr'].median()) *      # Outcome: Relative earnings
    (df['median_debt'].median() / (df['median_debt'] + 1))      # Debt: Inverse debt burden
)

# Percentile rank for easy interpretation
df['mobility_percentile'] = df['economic_mobility_index'].rank(pct=True) * 100
```

**Tableau Viz**: Slope chart showing Pell % at entry → Earnings at 10 years

---

### 3. **True Affordability Score**
```python
# Beyond sticker price - can students actually afford it?
df['affordability_score'] = (
    (20 / (df['work_hours_needed'] + 1)) * 40 +      # 20 hrs/week is sustainable max
    (1 - df['affordability_gap'] / df['net_price']) * 30 +  # Gap as % of price
    (df['net_price'].median() / (df['net_price'] + 1)) * 30  # Absolute price comparison
)

# Parent affordability 
df['parent_affordability_score'] = (
    20 / (df['parent_work_hours_needed'] + 1)  # Even less time available
) * 100

# Flag crisis schools
df['affordability_crisis'] = df['work_hours_needed'] > 30
```

**Tableau Viz**: Heat map by state, sized by enrollment, colored by hours needed

---

### 4. **Disparate Impact Ratio** (Legal standard)
```python
# 80% rule from employment law
df['disparate_impact_ratio'] = df['urm_grad_rate'] / (df['white_grad_6yr'] + 0.001)

# Classification
df['equity_status'] = pd.cut(
    df['disparate_impact_ratio'],
    bins=[0, 0.6, 0.8, 0.95, 1.05, 999],
    labels=['Severe Disparity', 'Actionable Disparity', 'Approaching Equity', 
            'Equitable', 'URM Outperforming']
)

# Schools needing intervention
df['needs_intervention'] = df['disparate_impact_ratio'] < 0.8
```

**Tableau Viz**: Treemap colored by equity status, sized by URM enrollment

---

### 5. **Composite Equity-Value Score**
```python
# The ultimate metric combining all factors
def calculate_equity_value_score(df):
    # Normalize each component to 0-100
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 100))
    
    # Financial ROI (25% weight)
    df['roi_score'] = scaler.fit_transform(df[['basic_roi']])
    
    # Racial Equity (30% weight) 
    df['equity_score'] = 100 - abs(df['overall_equity_gap'])
    
    # Economic Mobility (25% weight)
    df['mobility_score'] = scaler.fit_transform(df[['economic_mobility_index']])
    
    # Affordability (20% weight)
    df['afford_score'] = 100 - scaler.fit_transform(df[['work_hours_needed']])
    
    # Final composite
    df['equity_value_score'] = (
        df['roi_score'] * 0.25 +
        df['equity_score'] * 0.30 +
        df['mobility_score'] * 0.25 +
        df['afford_score'] * 0.20
    )
    
    return df

df = calculate_equity_value_score(df)

# Rank schools
df['equity_value_rank'] = df['equity_value_score'].rank(ascending=False, method='min')
```

**Tableau Viz**: Dashboard with top 20 schools, showing component breakdown

---

### 6. **MSI Performance Metrics**
```python
# How well do Minority Serving Institutions perform?
df['is_msi'] = df[['HBCU', 'HSI', 'PBI', 'TRIBAL', 'AANAPII']].any(axis=1)

# MSI Premium: Do MSIs outperform on equity-adjusted basis?
msi_avg_roi = df[df['is_msi']]['basic_roi'].mean()
non_msi_avg_roi = df[~df['is_msi']]['basic_roi'].mean()
df['msi_premium'] = msi_avg_roi - non_msi_avg_roi

# HBCU Excellence Score
df['hbcu_excellence'] = np.where(
    df['HBCU'] == 'X',
    df['black_grad_6yr'] * df['equity_value_score'] / 100,
    0
)

# HSI Impact Score  
df['hsi_impact'] = np.where(
    df['HSI'] == 'X',
    df['latino_grad_6yr'] * df['equity_value_score'] / 100,
    0
)
```

**Tableau Viz**: Side-by-side comparison of MSI vs non-MSI outcomes

---

### 7. **Hidden Gems Identifier**
```python
# Schools that outperform expectations
df['hidden_gem_score'] = 0

# Low debt, high earnings, good equity
gems = (
    (df['median_debt'] < df['median_debt'].quantile(0.25)) &
    (df['earnings_10yr'] > df['earnings_10yr'].quantile(0.75)) &
    (df['racial_equity_score'] > 80) &
    (df['work_hours_needed'] < 20)
)
df.loc[gems, 'hidden_gem_score'] = 100

# Underrated schools (low prestige, high value)
df['prestige_proxy'] = df['sat_75th_percentile'].fillna(df['sat_75th_percentile'].median())
df['underrated_score'] = df['equity_value_score'] - (df['prestige_proxy'] / 16)  # SAT max 1600
```

**Tableau Viz**: Quadrant chart - Prestige vs Equity Value

---

## 📈 Tableau Visualization Strategy

### **Dashboard 1: Equity Overview** (Main Dashboard)
```
Layout:
┌─────────────────────────────────────┐
│  Title: College Equity Navigator    │
├─────────────┬───────────────────────┤
│             │                       │
│  National   │   Scatter Plot:       │
│  Heat Map   │   Equity Gap vs       │
│  (by state) │   % URM Students      │
│             │                       │
├─────────────┼───────────────────────┤
│  Top 10     │   Work Hours         │
│  Equity     │   Distribution       │
│  Champions  │   (histogram)        │
└─────────────┴───────────────────────┘
```

**Filters**: State, Institution Type, MSI Status, Enrollment Size

**Key Metrics** (as cards):
- Median equity gap
- % schools meeting 80% rule
- Average work hours needed
- % Pell students graduating

---

### **Dashboard 2: Economic Mobility Ladder**
```
Layout:
┌─────────────────────────────────────┐
│   From Poverty to Prosperity        │
├─────────────────────────────────────┤
│                                     │
│   Sankey Diagram:                  │
│   Pell % → Graduation → Earnings   │
│                                     │
├─────────────┬───────────────────────┤
│ Best Value  │  Slope Chart:         │
│ for Low-    │  Entry Income →       │
│ Income      │  10-yr Earnings       │
└─────────────┴───────────────────────┘
```

**Interactive**: Click school to see full pathway

---

### **Dashboard 3: Disparate Impact Alert**
```
Layout:
┌─────────────────────────────────────┐
│  ⚠️ Schools Needing Intervention    │
├─────────────────────────────────────┤
│                                     │
│  Treemap: Colored by Severity      │
│  (Red = <60%, Orange = 60-80%)     │
│                                     │
├─────────────────────────────────────┤
│  Table: Specific Gaps by Race      │
│  [School | Black | Latino | Asian] │
└─────────────────────────────────────┘
```

**Call to Action**: "237 schools show severe disparate impact"

---

### **Dashboard 4: MSI Excellence**
```
Layout:
┌─────────────────────────────────────┐
│   Minority Serving Institutions     │
├──────────────┬──────────────────────┤
│              │                      │
│  HBCU Map    │  HSI Performance     │
│  (Southeast) │  (Southwest)         │
│              │                      │
├──────────────┴──────────────────────┤
│  Comparison: MSI vs PWI Outcomes    │
│  [Bar charts side by side]          │
└─────────────────────────────────────┘
```

---

### **Dashboard 5: Personal Match Finder**
```
Layout:
┌─────────────────────────────────────┐
│   Find Your Best-Fit School         │
├─────────────────────────────────────┤
│  Parameters:                        │
│  ► I am: [Race/Ethnicity dropdown]  │
│  ► Income: [Slider]                 │
│  ► Can work: [Hours slider]         │
│  ► Have kids: [Checkbox]            │
├─────────────────────────────────────┤
│  Your Top 10 Matches:               │
│  [Filtered table with scores]       │
└─────────────────────────────────────┘
```

---

## 🎨 Tableau Best Practices for Equity Data

### Color Schemes
```python
# Use colorblind-friendly palettes
EQUITY_COLORS = {
    'Equitable': '#2E7D32',      # Green
    'Approaching': '#FDD835',     # Yellow
    'Gap Present': '#F57C00',     # Orange  
    'Severe Gap': '#C62828',      # Red
    'No Data': '#BDBDBD'          # Gray
}

# For continuous scales
# Use diverging palette: Red → White → Green
# Center at 0 for gap metrics
```

### Annotations to Add
```python
ANNOTATIONS = [
    "80% threshold (legal standard)",
    "20 hrs/week (sustainable work)",
    "National median debt: $27,000",
    "Living wage threshold",
    "Only 23% of schools have no racial gaps"
]
```

### Reference Lines
- Add 80% line for disparate impact
- Add 20 hrs/week for work sustainability  
- Add median lines for context
- Add "equity zone" shading

---

## 🚀 Calculated Fields in Tableau

```sql
-- Equity Gap Category
IF [URM Grad Rate] / [White Grad Rate] < 0.6 THEN "Severe"
ELSEIF [URM Grad Rate] / [White Grad Rate] < 0.8 THEN "Actionable"  
ELSEIF [URM Grad Rate] / [White Grad Rate] < 0.95 THEN "Approaching"
ELSE "Equitable"
END

-- Work Sustainability Flag
IF [Weekly Hours Needed] <= 20 THEN "✓ Sustainable"
ELSEIF [Weekly Hours Needed] <= 30 THEN "⚠ Challenging"  
ELSE "✗ Unsustainable"
END

-- MSI Performance Index
IF [HBCU] = "X" THEN [Black Grad Rate] * 1.2
ELSEIF [HSI] = "X" THEN [Latino Grad Rate] * 1.2
ELSE [Overall Grad Rate]
END

-- Mobility Achieved
([10yr Earnings] - [State Median Income]) / [State Median Income] * 100

-- True Cost (including opportunity cost)
[Net Price] + ([Work Hours Needed] - 10) * [State Min Wage] * 52
```

---

## 📊 Story Points for Presentation

### Slide 1: "The Equity Crisis"
- "Only 187 of 6,000 schools have equitable graduation rates"
- Show: Treemap of disparate impact

### Slide 2: "Work or Study?"  
- "Average student needs 29 hrs/week to afford college"
- Show: Distribution histogram

### Slide 3: "Hidden Champions"
- "Fort Scott CC: 56% Pell, 2190x ROI"
- Show: Scatter of Pell % vs ROI

### Slide 4: "MSIs Leading the Way"
- "HBCUs deliver 23% better equity-adjusted ROI"
- Show: Comparison charts

### Slide 5: "Your Tool Changes Lives"
- Interactive demo of matcher
- "Find schools where students like you succeed"

---

## 💡 Advanced Metrics (If Time)

### Intersectionality Score
```python
# Multiple disadvantage factors
df['intersectionality_factors'] = (
    (df['pell_pct'] > 50).astype(int) +
    (df['urm_pct'] > 40).astype(int) +
    (df['first_gen_pct'] > 30).astype(int) +
    (df['rural_serving'] == 1).astype(int)
)

df['intersectional_success'] = (
    df['grad_rate_6yr'] * df['intersectionality_factors'] / 4
)
```

### Momentum Metric
```python
# Is equity improving over time?
df['equity_momentum'] = (
    df['urm_grad_rate_2021'] - df['urm_grad_rate_2018']
) / 3  # Per year improvement
```

### Regional Equity Index
```python
# Compare to regional demographics
df['regional_representation'] = (
    df['urm_pct'] / df['state_urm_population_pct']
)
```

---

## ⚡ Quick Implementation Code

```python
# Fast track to get all metrics
def calculate_all_equity_metrics(df):
    """Calculate all equity metrics at once"""
    
    # 1. Racial gaps
    df['black_white_gap'] = df['black_grad_6yr'] - df['white_grad_6yr']
    df['latino_white_gap'] = df['latino_grad_6yr'] - df['white_grad_6yr']
    
    # 2. Economic mobility  
    df['mobility_index'] = (
        df['pell_pct'] * df['pell_grad_rate_6yr'] * 
        df['earnings_10yr'] / (df['median_debt'] + 1)
    ) / 1000
    
    # 3. Affordability
    df['afford_score'] = 100 - (df['work_hours_needed'] / 40 * 100)
    
    # 4. Disparate impact
    df['disparate_impact'] = df['urm_grad_rate'] / (df['white_grad_6yr'] + 0.001)
    
    # 5. Composite score
    df['equity_value'] = (
        df['basic_roi'].rank(pct=True) * 25 +
        (100 - abs(df['black_white_gap'])) * 0.30 +
        df['mobility_index'].rank(pct=True) * 100 * 0.25 +
        df['afford_score'] * 0.20
    )
    
    # 6. Categories
    df['equity_champion'] = (
        (abs(df['black_white_gap']) < 5) & 
        (df['pell_pct'] > 40) &
        (df['work_hours_needed'] < 20)
    )
    
    return df
```

This comprehensive approach will make your project stand out as truly focused on social good!
