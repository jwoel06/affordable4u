# 🚀 Quick Tableau Implementation Guide

## Files Generated for You:
- `tableau_equity_metrics.csv` - Main dataset with all metrics
- `equity_champions.csv` - Top 50 equity champion schools  
- `crisis_schools.csv` - 50 schools needing intervention
- `top_overall.csv` - Top 100 schools by equity-value score

---

## 📊 5 Must-Have Visualizations (In Priority Order)

### 1. **Equity Gap Scatter Plot** (MOST IMPORTANT)
**Why**: Shows the core social good issue - racial disparities

**Steps**:
1. Drag `urm_pct` to Columns (X-axis)
2. Drag `overall_equity_gap` to Rows (Y-axis)
3. Drag `equity_status` to Color
4. Drag `Total Enrollment` to Size
5. Add reference line at Y=0 (perfect equity)
6. Add reference line at Y=-20 (severe gap)

**Color Scheme**:
- Equitable: Green (#2E7D32)
- Approaching: Yellow (#FDD835)
- Actionable Disparity: Orange (#F57C00)
- Severe Disparity: Red (#C62828)

**Title**: "Where Do URM Students Actually Succeed?"
**Caption**: "Only 1,972 of 21,528 schools have equitable graduation rates"

---

### 2. **Work Hours Reality Bar Chart**
**Why**: Shows affordability crisis in relatable terms

**Steps**:
1. Create bins for `work_hours_needed`: 0-10, 10-20, 20-30, 30-40, 40+
2. Count of schools in each bin
3. Color by `afford_category`
4. Add average line at 27 hours (median)

**Annotation**: "Students need 27+ hrs/week on average - that's nearly a full-time job!"

---

### 3. **Economic Mobility Slope Graph**
**Why**: Shows which schools lift low-income students

**Steps**:
1. Filter to top 20 schools by `mobility_percentile`
2. Create dual-axis chart:
   - Left: `pell_pct` (Entry)
   - Right: `earnings_10yr` (Outcome)
3. Connect with lines
4. Color by `is_msi`

**Title**: "From Poverty to Prosperity: Schools That Deliver"

---

### 4. **Geographic Equity Heat Map**
**Why**: Shows regional disparities

**Steps**:
1. Use State dimension
2. Color by average `racial_equity_score`
3. Add labels showing # of crisis schools per state
4. Size by total URM enrollment

**Insight to highlight**: "Southern states have both the most MSIs AND largest equity gaps"

---

### 5. **MSI Excellence Dashboard**
**Why**: Highlights minority-serving institutions' impact

**Create 4 charts in one dashboard**:

A. **Bar Chart**: MSI vs Non-MSI comparison
   - Metrics: Avg debt, Avg equity score, Avg work hours

B. **Scatter**: HBCU/HSI Performance
   - X: `median_debt`, Y: `earnings_10yr`
   - Shape by MSI type

C. **Top 10 Table**: Best MSIs by equity score

D. **KPI Cards**:
   - Total MSI enrollment
   - Average MSI equity score
   - MSI graduation rate

---

## 📈 Calculated Fields to Add in Tableau

### 1. Equity Status (Stoplight)
```
IF [disparate_impact_ratio] < 0.6 THEN "🔴 Severe"
ELSEIF [disparate_impact_ratio] < 0.8 THEN "🟠 Action Needed"
ELSEIF [disparate_impact_ratio] < 0.95 THEN "🟡 Approaching"
ELSE "🟢 Equitable"
END
```

### 2. Work Sustainability
```
IF [work_hours_needed] <= 20 THEN "Sustainable"
ELSEIF [work_hours_needed] <= 30 THEN "Challenging"
ELSE "Impossible"
END
```

### 3. True Annual Cost (with opportunity cost)
```
[net_price] + 
(IF [work_hours_needed] > 20 
THEN ([work_hours_needed] - 20) * 15 * 52
ELSE 0)
```

### 4. Equity-Adjusted ROI Rank
```
RANK([equity_value_score], 'desc')
```

### 5. Crisis Flag Message
```
IF [crisis_school] = 1 THEN
  IF [work_hours_needed] > 35 THEN "⚠️ Unsustainable work hours"
  ELSEIF [disparate_impact_ratio] < 0.6 THEN "⚠️ Severe racial gaps"
  ELSE "⚠️ Debt exceeds earnings"
  END
ELSE ""
END
```

---

## 🎨 Dashboard Layout Template

```
┌─────────────────────────────────────────┐
│       College Equity Navigator          │
│   "Finding Where All Students Succeed"  │
├────────────┬────────────────────────────┤
│            │                            │
│  Key Stats │    Main Scatter Plot:      │
│   Cards    │    Equity Gap vs URM %     │
│            │                            │
├────────────┼────────────────────────────┤
│            │                            │
│ Work Hours │    Geographic Heat Map     │
│    Bars    │                            │
│            │                            │
├────────────┴────────────────────────────┤
│         Top 10 Schools Table            │
│    (Filterable by category)             │
└─────────────────────────────────────────┘
```

**Filters to Include**:
- State (multi-select)
- Institution Type
- MSI Status
- Enrollment Size (slider)
- Equity Score (slider)

---

## 💡 Story Points for Presentation

### Slide 1: The Problem
**Visual**: Disparate impact treemap
**Stat**: "3,463 schools fail the legal 80% rule for equity"

### Slide 2: The Work Burden
**Visual**: Work hours distribution
**Stat**: "9,069 schools require impossible work hours"

### Slide 3: Hidden Champions  
**Visual**: Top equity champions table
**Example**: "CUNY York: 89% URM, 94% equity score, $12k debt"

### Slide 4: The Solution
**Visual**: Your dashboard demo
**Message**: "Find schools where students like you thrive"

---

## 🏃 Quick Start (If Running Out of Time)

**Bare minimum for impact**:

1. Import `tableau_equity_metrics.csv`
2. Create ONE scatter plot: `urm_pct` vs `overall_equity_gap`
3. Color by `equity_status`
4. Add table of top 10 by `equity_value_score`
5. Add filter for State
6. Publish to Tableau Public

**Time**: 30 minutes max

---

## 🎯 Winning Insights to Highlight

From your data:
- **"Only 211 schools are true equity champions"** (no gaps + affordable + high Pell)
- **"Students need 27 hours/week average"** (nearly impossible with full course load)
- **"1,348 schools have SEVERE disparate impact"** (<60% rule)
- **"MSIs need more support"** (serving the neediest but underfunded)

---

## ⚡ Tableau Shortcuts

- **Ctrl+Drag** = Duplicate a chart
- **Double-click** measure = Auto-create viz
- **Right-click → Add Reference Line** = Add equity thresholds
- **Analytics Pane → Trend Line** = Show patterns
- **Format → Shading** = Add "equity zones"

Remember: **Simple and impactful beats complex and confusing!**
