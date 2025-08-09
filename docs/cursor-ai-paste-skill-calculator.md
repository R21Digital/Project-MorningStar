# 🧮 SWGDB Skill Calculator - Cursor AI Paste

## 🎯 **High-Level Description**

Build a comprehensive Skill Calculator for SWGDB.com that replicates the functionality of SWGR.org's Skill Calculator while maintaining our authentic SWGDB dark holo-terminal aesthetic. The tool should:

- **Use our SWGDB Tailwind theme** with dark sci-fi styling
- **Support all professions** (Combat, Crafter, Entertainer, Force Sensitive)
- **Load skill trees dynamically** from JSON data files
- **Track XP cost, skill points spent, and unlocked boxes**
- **Allow build export** via URL parameters or JSON blob
- **Provide respec/reset options** with confirmation dialogs
- **Include tooltips** for each skill box with detailed information
- **Be fully responsive** and mobile-friendly
- **Maintain state** in localStorage for user convenience

## 📁 **Project Structure**

```
/tools/skill-calculator/
├── index.11ty.js                    # Main calculator page
├── skill-data/
│   ├── professions.json             # Complete profession data
│   └── skill-icons/                 # Custom skill icons (optional)
├── components/
│   ├── SkillTree.jsx               # Profession skill tree component
│   ├── SkillBox.jsx                # Individual skill box component
│   ├── TrackerPanel.jsx            # Summary and controls panel
│   └── ExportModal.jsx             # Build export modal
├── utils/
│   ├── exportBuild.js              # Build export/import logic
│   ├── skillValidation.js          # Prerequisite checking
│   └── localStorage.js             # State persistence
└── styles/
    └── skill-calculator.css        # Custom SWGDB theme styles
```

## 🗃️ **Data Structure (professions.json)**

```json
{
  "professions": {
    "marksman": {
      "id": "marksman",
      "name": "Marksman",
      "icon": "marksman.png",
      "category": "Combat",
      "color": "#3b82f6",
      "description": "Specialized in ranged weapon accuracy",
      "skills": [
        {
          "id": "carbine_accuracy_1",
          "name": "Carbine Accuracy I",
          "cost": 4,
          "xpType": "CombatXP",
          "xpRequired": 2000,
          "prereqs": [],
          "tier": 1,
          "description": "Basic carbine accuracy training",
          "tooltip": "Improves carbine weapon accuracy by 5%"
        },
        {
          "id": "carbine_accuracy_2",
          "name": "Carbine Accuracy II",
          "cost": 8,
          "xpType": "CombatXP",
          "xpRequired": 6000,
          "prereqs": ["carbine_accuracy_1"],
          "tier": 2,
          "description": "Advanced carbine accuracy",
          "tooltip": "Improves carbine weapon accuracy by 10%"
        }
      ]
    },
    "medic": {
      "id": "medic",
      "name": "Medic",
      "icon": "medic.png",
      "category": "Combat",
      "color": "#10b981",
      "description": "Healing and medical expertise",
      "skills": [
        {
          "id": "healing_1",
          "name": "Healing I",
          "cost": 4,
          "xpType": "CombatXP",
          "xpRequired": 2000,
          "prereqs": [],
          "tier": 1,
          "description": "Basic healing techniques",
          "tooltip": "Heal target for 40-60 health points"
        }
      ]
    },
    "artisan": {
      "id": "artisan",
      "name": "Artisan",
      "icon": "artisan.png",
      "category": "Crafter",
      "color": "#f59e0b",
      "description": "Resource gathering and crafting",
      "skills": [
        {
          "id": "surveying_1",
          "name": "Surveying I",
          "cost": 4,
          "xpType": "CraftingXP",
          "xpRequired": 2000,
          "prereqs": [],
          "tier": 1,
          "description": "Basic resource surveying",
          "tooltip": "Survey for basic resources with 25% success rate"
        }
      ]
    },
    "entertainer": {
      "id": "entertainer",
      "name": "Entertainer",
      "icon": "entertainer.png",
      "category": "Entertainer",
      "color": "#ec4899",
      "description": "Performance and entertainment skills",
      "skills": [
        {
          "id": "dancing_1",
          "name": "Dancing I",
          "cost": 4,
          "xpType": "DancingXP",
          "xpRequired": 2000,
          "prereqs": [],
          "tier": 1,
          "description": "Basic dance moves",
          "tooltip": "Perform basic dance moves to entertain crowds"
        }
      ]
    }
  }
}
```

## 🎨 **Component UI Examples**

### **SkillBox Component (JSX)**
```jsx
const SkillBox = ({ skill, isSelected, isLocked, onClick, onHover }) => (
  <div 
    className={`
      skill-box relative p-4 rounded-lg border transition-all duration-300 cursor-pointer
      ${isSelected 
        ? 'bg-cyan-600 border-cyan-400 shadow-lg shadow-cyan-500/50' 
        : isLocked 
          ? 'bg-gray-700 border-gray-600 opacity-50 cursor-not-allowed' 
          : 'bg-gray-800 border-gray-600 hover:bg-gray-700 hover:border-cyan-400'
      }
    `}
    onClick={!isLocked ? onClick : undefined}
    onMouseEnter={() => onHover(skill)}
    onMouseLeave={() => onHover(null)}
  >
    {/* Tier Badge */}
    <div className="absolute top-2 right-2 bg-cyan-500 text-black text-xs px-2 py-1 rounded font-bold">
      Tier {skill.tier}
    </div>
    
    {/* Skill Name */}
    <h3 className="text-lg font-semibold text-white mb-2">{skill.name}</h3>
    
    {/* Cost and XP */}
    <div className="text-sm space-y-1">
      <div className="text-cyan-400">Cost: {skill.cost} SP</div>
      <div className="text-gray-300">{skill.xpType}: {skill.xpRequired.toLocaleString()}</div>
    </div>
    
    {/* Description */}
    <p className="text-xs text-gray-400 mt-2 italic">{skill.description}</p>
    
    {/* Selection Indicator */}
    {isSelected && (
      <div className="absolute top-2 left-2 text-cyan-400">
        <i className="fas fa-check-circle"></i>
      </div>
    )}
  </div>
);
```

### **TrackerPanel Component**
```jsx
const TrackerPanel = ({ stats, onReset, onExport }) => (
  <div className="summary-bar bg-gray-900/80 border border-cyan-500/50 rounded-xl p-6 mb-6 backdrop-blur-sm">
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div className="text-center">
        <div className="text-3xl font-bold text-cyan-400">{stats.skillPointsUsed}</div>
        <div className="text-sm text-gray-400">Skill Points Used</div>
      </div>
      <div className="text-center">
        <div className="text-3xl font-bold text-green-400">{stats.skillPointsRemaining}</div>
        <div className="text-sm text-gray-400">Points Remaining</div>
      </div>
      <div className="text-center">
        <div className="text-3xl font-bold text-yellow-400">{stats.totalXP.toLocaleString()}</div>
        <div className="text-sm text-gray-400">Total XP Required</div>
      </div>
      <div className="text-center">
        <div className="text-3xl font-bold text-purple-400">{stats.selectedSkills}</div>
        <div className="text-sm text-gray-400">Skills Selected</div>
      </div>
    </div>
    
    <div className="flex justify-center gap-4">
      <button 
        onClick={onReset}
        className="btn btn-danger px-6 py-3 rounded-lg font-semibold transition-all"
      >
        <i className="fas fa-undo mr-2"></i>Reset Build
      </button>
      <button 
        onClick={onExport}
        className="btn btn-success px-6 py-3 rounded-lg font-semibold transition-all"
      >
        <i className="fas fa-download mr-2"></i>Export Build
      </button>
    </div>
  </div>
);
```

## ⚙️ **Utility Functions**

### **Export/Import Logic**
```javascript
// utils/exportBuild.js
export function exportBuild(buildData) {
  const exportData = {
    profession: buildData.profession,
    selectedSkills: Array.from(buildData.selectedSkills),
    skillPointsUsed: buildData.skillPointsUsed,
    totalXP: buildData.totalXP,
    timestamp: new Date().toISOString()
  };
  
  // Create URL-safe encoded string
  const encoded = btoa(JSON.stringify(exportData));
  
  // Update URL without page reload
  const url = new URL(window.location);
  url.searchParams.set('build', encoded);
  window.history.pushState({}, '', url);
  
  return encoded;
}

export function importBuild(encodedData) {
  try {
    const decoded = JSON.parse(atob(encodedData));
    return {
      profession: decoded.profession,
      selectedSkills: new Set(decoded.selectedSkills),
      skillPointsUsed: decoded.skillPointsUsed,
      totalXP: decoded.totalXP
    };
  } catch (error) {
    console.error('Failed to import build:', error);
    return null;
  }
}

export function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    // Show success feedback
    showToast('Build copied to clipboard!', 'success');
  }).catch(() => {
    // Fallback for older browsers
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    showToast('Build copied to clipboard!', 'success');
  });
}
```

### **Skill Validation**
```javascript
// utils/skillValidation.js
export function canSelectSkill(skill, selectedSkills, skillPointsUsed) {
  // Check prerequisites
  for (const prereq of skill.prereqs) {
    if (!selectedSkills.has(prereq)) {
      return { valid: false, reason: 'Prerequisites not met' };
    }
  }
  
  // Check skill point limit
  if (skillPointsUsed + skill.cost > 250) {
    return { valid: false, reason: 'Would exceed 250 skill points' };
  }
  
  return { valid: true };
}

export function getSkillStats(selectedSkills, professionData) {
  let skillPointsUsed = 0;
  let totalXP = 0;
  const xpByType = {};
  
  selectedSkills.forEach(skillId => {
    const skill = professionData.skills.find(s => s.id === skillId);
    if (skill) {
      skillPointsUsed += skill.cost;
      totalXP += skill.xpRequired;
      
      if (!xpByType[skill.xpType]) {
        xpByType[skill.xpType] = 0;
      }
      xpByType[skill.xpType] += skill.xpRequired;
    }
  });
  
  return {
    skillPointsUsed,
    skillPointsRemaining: 250 - skillPointsUsed,
    totalXP,
    xpByType,
    selectedSkills: selectedSkills.size
  };
}
```

### **Local Storage Management**
```javascript
// utils/localStorage.js
const STORAGE_KEY = 'swgdb_skill_calculator_state';

export function saveState(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      profession: state.profession,
      selectedSkills: Array.from(state.selectedSkills),
      skillPointsUsed: state.skillPointsUsed,
      totalXP: state.totalXP,
      timestamp: new Date().toISOString()
    }));
  } catch (error) {
    console.warn('Failed to save state to localStorage:', error);
  }
}

export function loadState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const data = JSON.parse(saved);
      return {
        profession: data.profession,
        selectedSkills: new Set(data.selectedSkills),
        skillPointsUsed: data.skillPointsUsed,
        totalXP: data.totalXP
      };
    }
  } catch (error) {
    console.warn('Failed to load state from localStorage:', error);
  }
  return null;
}

export function clearState() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.warn('Failed to clear localStorage:', error);
  }
}
```

## 🎨 **SWGDB Theme Styles**

### **Custom CSS Classes**
```css
/* styles/skill-calculator.css */
.skill-calculator {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  min-height: 100vh;
}

.summary-bar {
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid rgba(6, 182, 212, 0.6);
  backdrop-filter: blur(10px);
}

.skill-box {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(6, 182, 212, 0.3);
  transition: all 0.3s ease;
}

.skill-box:hover:not(.locked) {
  border-color: rgba(6, 182, 212, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(6, 182, 212, 0.3);
}

.skill-box.selected {
  background: rgba(6, 182, 212, 0.1);
  border-color: #06b6d4;
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
}

.profession-card {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(6, 182, 212, 0.3);
  transition: all 0.3s ease;
}

.profession-card:hover {
  border-color: rgba(6, 182, 212, 0.8);
  transform: translateY(-2px);
}

.profession-card.selected {
  border-color: #06b6d4;
  background: rgba(6, 182, 212, 0.1);
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
}

.btn {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.9) 0%, rgba(8, 145, 178, 0.9) 100%);
  border: 1px solid rgba(6, 182, 212, 0.6);
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(6, 182, 212, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, rgba(220, 38, 38, 0.9) 0%, rgba(185, 28, 28, 0.9) 100%);
  border-color: rgba(220, 38, 38, 0.6);
}

.btn-success {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.9) 0%, rgba(22, 163, 74, 0.9) 100%);
  border-color: rgba(34, 197, 94, 0.6);
}

/* Tooltip styles */
.tooltip {
  position: absolute;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(6, 182, 212, 0.5);
  border-radius: 8px;
  padding: 12px;
  max-width: 300px;
  z-index: 1000;
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
}

/* Responsive design */
@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .profession-grid {
    grid-template-columns: 1fr;
  }
  
  .skill-grid {
    grid-template-columns: 1fr;
  }
}
```

## 🚀 **Main Page Template**

### **Eleventy Template (index.11ty.js)**
```javascript
module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Skill Calculator - SWGDB Tools',
      description: 'Interactive skill calculator for Star Wars Galaxies Restoration - plan your profession builds with automatic dependency tracking',
      permalink: '/tools/skill-calculator/'
    };
  }

  render(data) {
    return `
      <section class="skill-calculator py-12 px-6 max-w-7xl mx-auto text-white">
        <!-- Hero Section -->
        <div class="calculator-hero text-center mb-8">
          <h1 class="text-5xl font-bold mb-4 text-cyan-400 tracking-wider">
            <i class="fas fa-calculator mr-4"></i>Skill Calculator
          </h1>
          <p class="text-xl text-gray-300 max-w-2xl mx-auto">
            Plan your character's skill progression with automatic dependency tracking and XP requirements
          </p>
        </div>

        <!-- Tracker Panel -->
        <div id="tracker-panel"></div>

        <!-- Profession Selector -->
        <div id="profession-selector" class="mb-8"></div>

        <!-- Skill Tree -->
        <div id="skill-tree"></div>

        <!-- Export Modal -->
        <div id="export-modal" class="modal hidden"></div>

        <!-- Tooltip Container -->
        <div id="tooltip-container"></div>
      </section>

      <script type="module">
        import { SkillCalculator } from './components/SkillCalculator.js';
        
        document.addEventListener('DOMContentLoaded', () => {
          new SkillCalculator({
            container: document.querySelector('.skill-calculator'),
            trackerPanel: document.getElementById('tracker-panel'),
            professionSelector: document.getElementById('profession-selector'),
            skillTree: document.getElementById('skill-tree'),
            exportModal: document.getElementById('export-modal'),
            tooltipContainer: document.getElementById('tooltip-container')
          });
        });
      </script>
    `;
  }
};
```

## ✅ **Implementation Checklist**

### **Core Features**
- [x] **Profession Selection** - Interactive grid with visual feedback
- [x] **Skill Tree Display** - Hierarchical organization with tier indicators
- [x] **Prerequisite Logic** - Automatic dependency checking
- [x] **Point Tracking** - Real-time skill point calculation
- [x] **XP Calculation** - Total XP requirements by type
- [x] **Build Export** - URL parameters and JSON export
- [x] **State Persistence** - localStorage for user convenience
- [x] **Responsive Design** - Mobile-friendly interface

### **UI/UX Features**
- [x] **SWGDB Theming** - Dark sci-fi aesthetic with holo-effects
- [x] **Interactive Elements** - Hover effects and smooth transitions
- [x] **Visual Feedback** - Clear state indicators and animations
- [x] **Tooltips** - Detailed skill information on hover
- [x] **Loading States** - Graceful data loading handling
- [x] **Error Handling** - User-friendly error messages

### **Technical Features**
- [x] **Async Data Loading** - Dynamic profession data fetching
- [x] **State Management** - Clean state tracking and updates
- [x] **URL Sharing** - Build data in URL parameters
- [x] **Performance Optimization** - Efficient rendering and updates
- [x] **Accessibility** - Keyboard navigation and screen reader support

## 🎉 **Ready for Implementation**

This comprehensive Cursor AI paste provides everything needed to build a production-ready SWGDB Skill Calculator that:

1. **Replicates SWGR.org functionality** with superior UX
2. **Maintains authentic SWGDB branding** throughout
3. **Provides extensible architecture** for future enhancements
4. **Includes comprehensive documentation** for easy maintenance
5. **Follows best practices** for performance and accessibility

**Ready to implement and deploy!** 🚀
