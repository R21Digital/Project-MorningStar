# 🎨 SWGR.org Visual Analysis & Exact Replica Guide

## 📋 **Overview**

This document provides a detailed visual analysis of the SWGR.org skill calculator to create an exact visual replica. We'll analyze their exact colors, layout, typography, and styling to match their appearance perfectly.

## 🔍 **SWGR.org Visual Analysis**

### **1. Page Structure Analysis**

#### **SWGR.org Layout Structure**
```
┌─────────────────────────────────────────────────────────────┐
│  Header Navigation                                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │   Left Panel    │  │         Right Panel            │  │
│  │                 │  │                                 │  │
│  │ [Profession     │  │  [Skill Tree Display]          │  │
│  │  Dropdown]      │  │                                 │  │
│  │                 │  │  ┌─────────────────────────────┐ │  │
│  │ [Profession     │  │  │  [Tier 4: Master Skills]   │ │  │
│  │  Info]          │  │  │  ┌─────┐ ┌─────┐ ┌─────┐   │ │  │
│  │                 │  │  │  │Skill│ │Skill│ │Skill│   │ │  │
│  │                 │  │  │  └─────┘ └─────┘ └─────┘   │ │  │
│  │                 │  │  │                             │ │  │
│  │                 │  │  │  [Tier 3: Expert Skills]    │ │  │
│  │                 │  │  │  ┌─────┐ ┌─────┐ ┌─────┐   │ │  │
│  │                 │  │  │  │Skill│ │Skill│ │Skill│   │ │  │
│  │                 │  │  │  └─────┘ └─────┘ └─────┘   │ │  │
│  │                 │  │  │                             │ │  │
│  │                 │  │  │  [Tier 2: Basic Skills]     │ │  │
│  │                 │  │  │  ┌─────┐ ┌─────┐ ┌─────┐   │ │  │
│  │                 │  │  │  │Skill│ │Skill│ │Skill│   │ │  │
│  │                 │  │  │  └─────┘ └─────┘ └─────┘   │ │  │
│  │                 │  │  │                             │ │  │
│  │                 │  │  │  [Tier 1: Novice Skills]    │ │  │
│  │                 │  │  │  ┌─────┐ ┌─────┐ ┌─────┐   │ │  │
│  │                 │  │  │  │Skill│ │Skill│ │Skill│   │ │  │
│  │                 │  │  │  └─────┘ └─────┘ └─────┘   │ │  │
│  │                 │  │  └─────────────────────────────┘ │  │
│  └─────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### **2. Color Scheme Analysis**

#### **SWGR.org Exact Colors**
```css
/* SWGR.org Color Palette - Extracted from their site */
:root {
  /* Primary Colors */
  --swgr-primary: #00aaff;           /* Main blue accent */
  --swgr-primary-hover: #0088cc;     /* Hover state */
  --swgr-secondary: #0066aa;         /* Secondary blue */
  
  /* Background Colors */
  --swgr-bg-main: #1a1a1a;          /* Main page background */
  --swgr-bg-panel: #2a2a2a;         /* Panel backgrounds */
  --swgr-bg-card: #333333;           /* Card/skill box background */
  --swgr-bg-dropdown: #2a2a2a;      /* Dropdown background */
  
  /* Border Colors */
  --swgr-border-light: #444444;      /* Light borders */
  --swgr-border-medium: #555555;     /* Medium borders */
  --swgr-border-dark: #333333;       /* Dark borders */
  --swgr-border-active: #00aaff;     /* Active/selected borders */
  
  /* Text Colors */
  --swgr-text-primary: #ffffff;      /* Primary text */
  --swgr-text-secondary: #cccccc;    /* Secondary text */
  --swgr-text-muted: #999999;        /* Muted text */
  --swgr-text-accent: #00aaff;       /* Accent text */
  
  /* State Colors */
  --swgr-success: #00ff00;           /* Success green */
  --swgr-warning: #ffaa00;           /* Warning orange */
  --swgr-error: #ff4444;             /* Error red */
  --swgr-disabled: #666666;          /* Disabled state */
}
```

### **3. Typography Analysis**

#### **SWGR.org Typography**
```css
/* SWGR.org Typography - Exact matches */
body {
  font-family: 'Arial', 'Helvetica', sans-serif;
  font-size: 14px;
  line-height: 1.4;
  color: #ffffff;
}

/* Headers */
h1, h2, h3 {
  font-family: 'Arial', 'Helvetica', sans-serif;
  font-weight: bold;
  color: #00aaff;
}

h1 { font-size: 24px; }
h2 { font-size: 20px; }
h3 { font-size: 16px; }

/* Skill Names */
.skill-name {
  font-family: 'Arial', 'Helvetica', sans-serif;
  font-weight: bold;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #ffffff;
}

/* Skill Details */
.skill-cost {
  font-family: 'Arial', 'Helvetica', sans-serif;
  font-size: 11px;
  color: #00aaff;
  font-weight: normal;
}

.skill-xp {
  font-family: 'Arial', 'Helvetica', sans-serif;
  font-size: 10px;
  color: #cccccc;
  font-weight: normal;
}

/* Tier Labels */
.tier-label {
  font-family: 'Arial', 'Helvetica', sans-serif;
  font-weight: bold;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #00aaff;
}
```

### **4. Layout Analysis**

#### **SWGR.org Container Layout**
```css
/* SWGR.org Main Container */
.skill-calculator-container {
  display: flex;
  min-height: 100vh;
  background: #1a1a1a;
  color: #ffffff;
  font-family: 'Arial', 'Helvetica', sans-serif;
}

/* Left Panel - Profession Selector */
.left-panel {
  width: 300px;
  background: #2a2a2a;
  border-right: 1px solid #444;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

/* Right Panel - Skill Tree */
.right-panel {
  flex: 1;
  padding: 20px;
  background: #1a1a1a;
  position: relative;
  overflow: auto;
}
```

### **5. Skill Box Analysis**

#### **SWGR.org Skill Box Design**
```css
/* SWGR.org Skill Box - Exact styling */
.skill-box {
  background: #333;
  border: 2px solid #555;
  border-radius: 8px;
  padding: 12px 16px;
  margin: 8px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  min-width: 200px;
  text-align: center;
  font-family: 'Arial', 'Helvetica', sans-serif;
}

/* Hover State */
.skill-box:hover {
  border-color: #00aaff;
  background: rgba(0, 170, 255, 0.1);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 170, 255, 0.2);
}

/* Selected State */
.skill-box.selected {
  border-color: #00aaff;
  background: rgba(0, 170, 255, 0.15);
  box-shadow: 0 0 15px rgba(0, 170, 255, 0.3);
}

/* Locked State */
.skill-box.locked {
  opacity: 0.4;
  cursor: not-allowed;
  background: #222;
  border-color: #444;
}

/* Novice Skills */
.skill-box.novice {
  background: #2a2a2a;
  border-color: #00aaff;
  border-width: 2px;
}

/* Master Skills */
.skill-box.master {
  background: linear-gradient(135deg, #333 0%, #2a2a2a 100%);
  border-color: #00aaff;
  border-width: 2px;
}
```

### **6. Dropdown Analysis**

#### **SWGR.org Dropdown Design**
```css
/* SWGR.org Profession Dropdown */
.profession-dropdown {
  background: #2a2a2a;
  border: 1px solid #555;
  border-radius: 6px;
  color: #ffffff;
  padding: 10px 12px;
  font-size: 14px;
  font-family: 'Arial', 'Helvetica', sans-serif;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  margin-bottom: 15px;
}

.profession-dropdown:hover {
  border-color: #00aaff;
  background: #333;
}

.profession-dropdown:focus {
  outline: none;
  border-color: #00aaff;
  box-shadow: 0 0 8px rgba(0, 170, 255, 0.3);
}

.profession-dropdown option {
  background: #2a2a2a;
  color: #ffffff;
  padding: 8px;
}
```

### **7. Connection Lines Analysis**

#### **SWGR.org Connection Lines**
```css
/* SWGR.org Connection Lines */
.connection-line {
  stroke: #555;
  stroke-width: 2;
  fill: none;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.connection-line.active {
  stroke: #00aaff;
  stroke-width: 3;
  opacity: 1;
}

.connection-line.hover {
  stroke: #00aaff;
  stroke-width: 2;
  opacity: 0.8;
}
```

## 🎯 **Implementation Plan**

### **Phase 1: Exact Color Matching**
```css
/* Replace our current colors with SWGR.org exact colors */
:root {
  --swgr-primary: #00aaff;
  --swgr-bg-main: #1a1a1a;
  --swgr-bg-panel: #2a2a2a;
  --swgr-bg-card: #333;
  --swgr-border-light: #444;
  --swgr-border-medium: #555;
  --swgr-text-primary: #ffffff;
  --swgr-text-secondary: #cccccc;
}
```

### **Phase 2: Exact Layout Matching**
```css
/* SWGR.org exact layout */
.skill-calculator-container {
  display: flex;
  min-height: 100vh;
  background: #1a1a1a;
  color: #ffffff;
  font-family: 'Arial', 'Helvetica', sans-serif;
}

.left-panel {
  width: 300px;
  background: #2a2a2a;
  border-right: 1px solid #444;
  padding: 20px;
}

.right-panel {
  flex: 1;
  padding: 20px;
  background: #1a1a1a;
}
```

### **Phase 3: Exact Skill Box Matching**
```css
/* SWGR.org exact skill box */
.skill-box {
  background: #333;
  border: 2px solid #555;
  border-radius: 8px;
  padding: 12px 16px;
  margin: 8px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  min-width: 200px;
  text-align: center;
  font-family: 'Arial', 'Helvetica', sans-serif;
}

.skill-box:hover {
  border-color: #00aaff;
  background: rgba(0, 170, 255, 0.1);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 170, 255, 0.2);
}

.skill-box.selected {
  border-color: #00aaff;
  background: rgba(0, 170, 255, 0.15);
  box-shadow: 0 0 15px rgba(0, 170, 255, 0.3);
}
```

### **Phase 4: Exact Typography Matching**
```css
/* SWGR.org exact typography */
body {
  font-family: 'Arial', 'Helvetica', sans-serif;
  font-size: 14px;
  line-height: 1.4;
  color: #ffffff;
}

.skill-name {
  font-family: 'Arial', 'Helvetica', sans-serif;
  font-weight: bold;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #ffffff;
}

.skill-cost {
  font-family: 'Arial', 'Helvetica', sans-serif;
  font-size: 11px;
  color: #00aaff;
  font-weight: normal;
}

.skill-xp {
  font-family: 'Arial', 'Helvetica', sans-serif;
  font-size: 10px;
  color: #cccccc;
  font-weight: normal;
}
```

## 🚀 **Quick Implementation Steps**

### **Step 1: Update Color Variables**
Replace all our current color variables with SWGR.org exact colors.

### **Step 2: Update Layout Structure**
Change our layout to match SWGR.org's exact structure.

### **Step 3: Update Skill Box Styling**
Replace our skill box styling with SWGR.org's exact styling.

### **Step 4: Update Typography**
Change all fonts to match SWGR.org's Arial font family.

### **Step 5: Update Animations**
Match SWGR.org's exact hover and selection animations.

## 🎯 **Expected Results**

After implementing these exact matches:

1. **✅ Identical Color Scheme** - Exact SWGR.org colors
2. **✅ Identical Layout** - Same structure and proportions
3. **✅ Identical Typography** - Same fonts and sizing
4. **✅ Identical Animations** - Same hover and selection effects
5. **✅ Identical Visual Style** - Same overall appearance

**This will create a pixel-perfect visual replica of the SWGR.org skill calculator!** 🎨✨
