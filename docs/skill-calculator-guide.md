# 🧮 SWGDB Skill Calculator - Complete Guide

## 🌟 Overview

The **SWGDB Skill Calculator** is a comprehensive, interactive tool that replicates the functionality of the SWGR.org skill calculator while maintaining the authentic SWGDB dark holo-terminal aesthetic. This tool allows players to plan their character builds with automatic dependency tracking, XP requirements, and build export functionality.

## ✨ Key Features

### 🎯 **Core Functionality**
- **Profession Selection** - Choose from Combat, Crafter, and Entertainer professions
- **Skill Tree Visualization** - Hierarchical skill display with tier indicators
- **Automatic Prerequisites** - Skills are locked until prerequisites are met
- **Real-time Tracking** - Live updates of skill points and XP requirements
- **Build Export** - Share builds via JSON export

### 🎨 **SWGDB Theming**
- **Dark Sci-fi Interface** - Authentic Star Wars Galaxies aesthetic
- **Holo-terminal Effects** - Glowing borders and animated elements
- **Responsive Design** - Works on desktop and mobile devices
- **Professional Icons** - FontAwesome icons for each profession category

### 📊 **Smart Tracking**
- **Skill Points** - Tracks usage against 250-point limit
- **XP Requirements** - Calculates total XP needed for selected skills
- **Dependency Validation** - Prevents selecting skills without prerequisites
- **Visual Feedback** - Clear indicators for locked/unlocked states

## 🏗️ Technical Architecture

### 📁 **File Structure**
```
src/pages/tools/skill-calculator.11ty.js    # Main calculator component
data/skills/professions.json                # Profession and skill data
public/data/skills/professions.json         # Public data for JavaScript
```

### 🗃️ **Data Structure**
```json
{
  "professions": {
    "marksman": {
      "id": "marksman",
      "name": "Marksman",
      "icon": "marksman.png",
      "category": "Combat",
      "color": "#3b82f6",
      "skills": [
        {
          "id": "carbine_accuracy_1",
          "name": "Carbine Accuracy I",
          "cost": 4,
          "xpType": "CombatXP",
          "xpRequired": 2000,
          "prereqs": [],
          "tier": 1,
          "description": "Basic carbine accuracy training"
        }
      ]
    }
  }
}
```

### ⚙️ **JavaScript Features**
- **Async Data Loading** - Fetches profession data from JSON
- **State Management** - Tracks selected skills and calculations
- **Event Handling** - Manages skill selection and UI updates
- **Modal System** - Export functionality with copy-to-clipboard

## 🎮 **User Interface**

### 📱 **Summary Bar**
- **Skill Points Used** - Current skill point consumption
- **Skill Points Remaining** - Available points (250 max)
- **Total XP Required** - Cumulative XP for selected skills
- **Skills Selected** - Count of active skill selections

### 🎯 **Profession Selection**
- **Visual Cards** - Each profession displayed as an interactive card
- **Category Icons** - FontAwesome icons for Combat, Crafter, Entertainer
- **Hover Effects** - Smooth animations and visual feedback
- **Selection State** - Clear indication of selected profession

### 🌳 **Skill Tree Display**
- **Grouped Skills** - Skills organized by base name (e.g., "Carbine Accuracy")
- **Tier Indicators** - Visual tier badges (Tier 1, 2, 3, 4)
- **Locked/Unlocked States** - Grayed out skills that can't be selected
- **Selection Feedback** - Highlighted selected skills

### 📋 **Skill Box Information**
- **Skill Name** - Clear, readable skill titles
- **Cost Display** - Skill point cost prominently shown
- **XP Requirements** - XP type and amount required
- **Description** - Helpful skill descriptions
- **Tier Badge** - Visual tier indicator

## 🔧 **Functionality Details**

### 🎯 **Skill Selection Logic**
```javascript
function toggleSkill(skillId) {
    const skill = currentProfession.skills.find(s => s.id === skillId);
    
    if (selectedSkills.has(skillId)) {
        // Deselect skill
        selectedSkills.delete(skillId);
        skillPointsUsed -= skill.cost;
        totalXP -= skill.xpRequired;
    } else {
        // Check prerequisites and point limit
        if (canSelectSkill(skill) && skillPointsUsed + skill.cost <= 250) {
            selectedSkills.add(skillId);
            skillPointsUsed += skill.cost;
            totalXP += skill.xpRequired;
        }
    }
    
    updateUI();
    renderSkillTree();
}
```

### 🔒 **Prerequisite Checking**
```javascript
function canSelectSkill(skill) {
    for (const prereq of skill.prereqs) {
        if (!selectedSkills.has(prereq)) {
            return false;
        }
    }
    return true;
}
```

### 📤 **Build Export**
```javascript
function exportBuild() {
    const buildData = {
        profession: currentProfession.name,
        selectedSkills: Array.from(selectedSkills),
        skillPointsUsed: skillPointsUsed,
        totalXP: totalXP,
        timestamp: new Date().toISOString()
    };
    
    // Display in modal for copying
    document.getElementById('exportData').value = JSON.stringify(buildData, null, 2);
    document.getElementById('exportModal').classList.add('show');
}
```

## 🎨 **Styling Features**

### 🌌 **SWGDB Theme Elements**
- **Dark Background** - Deep space gradient with starfield animation
- **Cyan Accents** - Primary color (#06b6d4) for highlights
- **Holo-glow Effects** - Animated glowing borders
- **Backdrop Blur** - Modern glass-morphism effects

### 📱 **Responsive Design**
```css
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

### 🎭 **Interactive Elements**
- **Hover Effects** - Smooth transitions on all interactive elements
- **Selection States** - Clear visual feedback for selected items
- **Loading States** - Graceful handling of data loading
- **Error Handling** - User-friendly error messages

## 🚀 **Usage Instructions**

### 📖 **Getting Started**
1. **Navigate** to `/tools/skill-calculator/`
2. **Select** a profession from the grid
3. **Choose** skills by clicking on skill boxes
4. **Monitor** your skill points and XP requirements
5. **Export** your build when finished

### 🎯 **Skill Selection Tips**
- **Start with Tier 1** - Select basic skills first
- **Watch Prerequisites** - Higher tiers require lower tiers
- **Monitor Points** - Stay under 250 skill points
- **Plan Ahead** - Consider XP requirements for your build

### 📤 **Build Export**
1. **Click** "Export Build" button
2. **Copy** the JSON data from the modal
3. **Share** with others or save for later
4. **Import** into other tools (future feature)

## 🔮 **Future Enhancements**

### 📈 **Planned Features**
- **Build Import** - Load saved builds from JSON
- **Multiple Professions** - Plan hybrid builds
- **XP Calculator** - Estimate time to earn required XP
- **Build Templates** - Pre-made popular builds
- **Community Sharing** - Share builds with other players

### 🎨 **UI Improvements**
- **Skill Icons** - Custom icons for each skill
- **Animation Effects** - More sophisticated animations
- **Sound Effects** - Optional audio feedback
- **Dark/Light Mode** - Theme switching option

### 🔧 **Technical Enhancements**
- **Local Storage** - Auto-save builds to browser
- **URL Sharing** - Build data in URL parameters
- **Progressive Web App** - Offline functionality
- **Performance Optimization** - Faster loading and rendering

## 🛠️ **Development Notes**

### 🔧 **Building the Calculator**
```bash
# Build the site
npx @11ty/eleventy

# The skill calculator will be available at:
# _site/tools/skill-calculator/index.html
```

### 📊 **Data Management**
- **Profession Data** - Stored in `data/skills/professions.json`
- **Public Access** - Copied to `public/data/skills/` for JavaScript
- **Schema Validation** - Ensures data integrity
- **Extensible Structure** - Easy to add new professions

### 🎯 **Key Implementation Details**
- **Eleventy Integration** - Uses 11ty.js template format
- **Tailwind CSS** - Utility-first styling approach
- **Vanilla JavaScript** - No framework dependencies
- **FontAwesome Icons** - Consistent iconography

## ✅ **Success Metrics**

### 🎯 **Functionality**
- ✅ **Profession Selection** - All 4 professions working
- ✅ **Skill Tree Display** - Hierarchical skill organization
- ✅ **Prerequisite Logic** - Proper dependency checking
- ✅ **Point Tracking** - Accurate skill point calculation
- ✅ **XP Calculation** - Total XP requirements
- ✅ **Build Export** - JSON export functionality

### 🎨 **Design**
- ✅ **SWGDB Theming** - Authentic dark sci-fi aesthetic
- ✅ **Responsive Layout** - Works on all screen sizes
- ✅ **Interactive Elements** - Smooth hover and selection effects
- ✅ **Visual Feedback** - Clear state indicators
- ✅ **Professional Polish** - Production-ready quality

### 🚀 **Performance**
- ✅ **Fast Loading** - Quick initial page load
- ✅ **Smooth Interactions** - Responsive user interface
- ✅ **Efficient Rendering** - Optimized skill tree updates
- ✅ **Memory Management** - Clean state management

---

## 🎉 **Conclusion**

The SWGDB Skill Calculator successfully replicates the SWGR.org functionality while providing a superior user experience with the authentic SWGDB theming. The tool is production-ready and provides a solid foundation for future enhancements and additional calculator tools.

**Ready for deployment and community use!** 🚀
