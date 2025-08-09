# 🔍 SWGR.org Skill Calculator Analysis Tool

## 📋 **Overview**

This document provides a comprehensive analysis framework to help us understand and replicate the SWGR.org skill calculator more accurately. We'll use various techniques to analyze their implementation and create a superior version.

## 🎯 **Analysis Techniques**

### **1. Browser Developer Tools Analysis**

#### **Network Tab Analysis**
```javascript
// Open browser dev tools and monitor network requests
// Look for:
// - API endpoints for skill data
// - JSON responses with skill information
// - Static assets (images, CSS, JS)
```

#### **Console Analysis**
```javascript
// In browser console, run these commands to understand their data structure:

// Check for global variables
console.log(window);

// Look for skill data
console.log(window.skillData || window.professions || window.skills);

// Check for any exposed functions
console.log(Object.keys(window).filter(key => key.includes('skill') || key.includes('profession')));

// Analyze DOM structure
console.log(document.querySelector('.skill-tree')?.innerHTML);
```

#### **Elements Tab Analysis**
```html
<!-- Key elements to inspect:
1. Profession selector structure
2. Skill tree container
3. Individual skill boxes
4. Connection lines
5. Tier organization
-->
```

### **2. Data Structure Analysis**

#### **Current SWGDB Structure**
```json
{
  "professions": {
    "marksman": {
      "id": "marksman",
      "name": "Marksman",
      "category": "Combat",
      "skills": [
        {
          "id": "carbine_accuracy_1",
          "name": "Carbine Accuracy I",
          "cost": 4,
          "xpType": "CombatXP",
          "xpRequired": 2000,
          "prereqs": [],
          "tier": 1
        }
      ]
    }
  }
}
```

#### **SWGR.org Structure (Inferred)**
```json
{
  "professions": {
    "marksman": {
      "name": "Marksman",
      "category": "Combat",
      "skills": [
        {
          "id": "novice_marksman",
          "name": "Novice Marksman",
          "tier": 0,
          "prerequisites": [],
          "skillPoints": 0,
          "xpRequired": 0
        },
        {
          "id": "carbine_accuracy_1",
          "name": "Carbine Accuracy I",
          "tier": 1,
          "prerequisites": ["novice_marksman"],
          "skillPoints": 4,
          "xpRequired": 2000
        }
      ]
    }
  }
}
```

## 🔧 **Implementation Strategy**

### **Phase 1: Data Structure Enhancement**

#### **Enhanced Skill Data Structure**
```javascript
// Enhanced skill structure to match SWGR.org
const enhancedSkillStructure = {
  "professions": {
    "marksman": {
      "id": "marksman",
      "name": "Marksman",
      "category": "Combat",
      "color": "#3b82f6",
      "description": "Combat profession focused on ranged weapons",
      "skills": [
        {
          "id": "novice_marksman",
          "name": "Novice Marksman",
          "displayName": "Novice Marksman",
          "tier": 0,
          "cost": 0,
          "xpType": "CombatXP",
          "xpRequired": 0,
          "prereqs": [],
          "description": "Basic marksman training",
          "icon": "novice_marksman.png",
          "category": "Novice",
          "isNovice": true
        },
        {
          "id": "carbine_accuracy_1",
          "name": "Carbine Accuracy I",
          "displayName": "Carbine Accuracy I",
          "tier": 1,
          "cost": 4,
          "xpType": "CombatXP",
          "xpRequired": 2000,
          "prereqs": ["novice_marksman"],
          "description": "Basic carbine accuracy training",
          "icon": "carbine_accuracy_1.png",
          "category": "Carbine",
          "branch": "accuracy"
        }
      ]
    }
  }
};
```

### **Phase 2: Visual Layout Analysis**

#### **SWGR.org Layout Structure**
```css
/* SWGR.org layout analysis */
.skill-calculator-container {
  display: flex;
  min-height: 100vh;
  background: #1a1a1a;
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
  position: relative;
}

.skill-tree {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 600px;
  position: relative;
}

.skill-tier {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px 0;
  position: relative;
}

.skill-box {
  background: #333;
  border: 2px solid #555;
  border-radius: 8px;
  padding: 12px 16px;
  margin: 0 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  min-width: 200px;
  text-align: center;
}

.skill-box.selected {
  border-color: #00aaff;
  background: rgba(0, 170, 255, 0.1);
  box-shadow: 0 0 15px rgba(0, 170, 255, 0.3);
}

.skill-box.locked {
  opacity: 0.4;
  cursor: not-allowed;
  background: #222;
  border-color: #444;
}
```

### **Phase 3: Connection System**

#### **SVG Connection Lines**
```javascript
// Enhanced connection system
function drawSkillConnections() {
  const connectionsSvg = document.getElementById('skillConnections');
  connectionsSvg.innerHTML = '';
  
  // Set SVG dimensions
  const container = document.getElementById('skillTree');
  const rect = container.getBoundingClientRect();
  connectionsSvg.setAttribute('width', rect.width);
  connectionsSvg.setAttribute('height', rect.height);
  
  // Draw connections for each skill
  currentProfession.skills.forEach(skill => {
    if (skill.prereqs && skill.prereqs.length > 0) {
      skill.prereqs.forEach(prereqId => {
        const fromSkill = document.getElementById(`skill-${prereqId}`);
        const toSkill = document.getElementById(`skill-${skill.id}`);
        
        if (fromSkill && toSkill) {
          const fromRect = fromSkill.getBoundingClientRect();
          const toRect = toSkill.getBoundingClientRect();
          const containerRect = container.getBoundingClientRect();
          
          const fromX = fromRect.left + fromRect.width / 2 - containerRect.left;
          const fromY = fromRect.top + fromRect.height - containerRect.top;
          const toX = toRect.left + toRect.width / 2 - containerRect.left;
          const toY = toRect.top - containerRect.top;
          
          // Create curved path
          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          const controlPoint1X = fromX;
          const controlPoint1Y = fromY + (toY - fromY) / 2;
          const controlPoint2X = toX;
          const controlPoint2Y = toY - (toY - fromY) / 2;
          
          path.setAttribute('d', `M ${fromX} ${fromY} C ${controlPoint1X} ${controlPoint1Y} ${controlPoint2X} ${controlPoint2Y} ${toX} ${toY}`);
          path.setAttribute('class', 'connection-line');
          
          // Active state for selected skills
          if (selectedSkills.has(prereqId) && selectedSkills.has(skill.id)) {
            path.classList.add('active');
          }
          
          connectionsSvg.appendChild(path);
        }
      });
    }
  });
}
```

## 🎨 **Visual Enhancement Plan**

### **1. Color Scheme Analysis**
```css
/* SWGR.org color scheme */
:root {
  --swgr-primary: #00aaff;
  --swgr-secondary: #0088cc;
  --swgr-background: #1a1a1a;
  --swgr-panel: #2a2a2a;
  --swgr-border: #444;
  --swgr-text: #ffffff;
  --swgr-text-secondary: #cccccc;
  --swgr-success: #00ff00;
  --swgr-warning: #ffaa00;
  --swgr-error: #ff4444;
}
```

### **2. Typography Analysis**
```css
/* SWGR.org typography */
.skill-calculator {
  font-family: 'Arial', sans-serif;
  font-size: 14px;
  line-height: 1.4;
}

.skill-name {
  font-weight: bold;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tier-label {
  font-weight: bold;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--swgr-primary);
}
```

## 🚀 **Implementation Roadmap**

### **Phase 1: Foundation (Week 1)**
- [ ] Analyze SWGR.org data structure
- [ ] Enhance our skill data format
- [ ] Implement basic SWGR-style layout
- [ ] Add profession dropdown selector

### **Phase 2: Visual Design (Week 2)**
- [ ] Implement SWGR-style skill boxes
- [ ] Add tier-based organization
- [ ] Create connection line system
- [ ] Match color scheme and typography

### **Phase 3: Functionality (Week 3)**
- [ ] Implement skill selection logic
- [ ] Add prerequisite checking
- [ ] Create skill point tracking
- [ ] Add build export functionality

### **Phase 4: Enhancement (Week 4)**
- [ ] Add animations and transitions
- [ ] Implement responsive design
- [ ] Add accessibility features
- [ ] Create comprehensive testing

## 🔍 **Analysis Tools**

### **Browser Extension for Analysis**
```javascript
// Create a browser extension to analyze SWGR.org
// This will help us understand their exact implementation

const analysisScript = `
// Inject this script into SWGR.org to analyze their structure
(function() {
  console.log('=== SWGR.org Analysis ===');
  
  // Analyze skill data
  const skillData = window.skillData || window.professions || {};
  console.log('Skill Data:', skillData);
  
  // Analyze DOM structure
  const skillTree = document.querySelector('.skill-tree');
  console.log('Skill Tree Structure:', skillTree?.innerHTML);
  
  // Analyze CSS classes
  const skillBoxes = document.querySelectorAll('.skill-box');
  console.log('Skill Box Classes:', Array.from(skillBoxes).map(box => box.className));
  
  // Analyze JavaScript functions
  const functions = Object.keys(window).filter(key => 
    typeof window[key] === 'function' && 
    (key.includes('skill') || key.includes('profession'))
  );
  console.log('Relevant Functions:', functions);
})();
`;
```

## 📊 **Comparison Matrix**

| Feature | SWGR.org | Current SWGDB | Target SWGDB |
|---------|----------|---------------|--------------|
| **Layout** | Vertical tree | ✅ Vertical tree | ✅ Enhanced vertical |
| **Profession Selection** | Dropdown | ✅ Dropdown | ✅ Enhanced dropdown |
| **Skill Connections** | Lines | ✅ SVG lines | ✅ Curved SVG lines |
| **Tier Organization** | Clear tiers | ✅ Tier labels | ✅ Enhanced tiers |
| **Visual Design** | Dark theme | ✅ SWGDB theme | ✅ SWGR-style theme |
| **Animations** | Smooth | ✅ Basic | ✅ Enhanced |
| **Responsive** | Limited | ✅ Full | ✅ Enhanced |
| **Export System** | Basic | ✅ Advanced | ✅ Superior |

## 🎯 **Next Steps**

1. **Analyze SWGR.org in detail** using browser dev tools
2. **Enhance our data structure** to match their format
3. **Implement SWGR-style visual design** with our branding
4. **Add advanced features** beyond what SWGR.org offers
5. **Test and refine** the implementation

**This analysis tool will help us create a truly superior skill calculator that matches and exceeds the SWGR.org implementation!** 🎨✨
