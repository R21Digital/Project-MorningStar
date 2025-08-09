# 🚀 Export Build System - SWGDB Skill Calculator

## 📋 **Overview**

The Export Build System is a polished, feature-rich solution for sharing and saving character builds in the SWGDB Skill Calculator. It provides multiple export options including URL sharing, JSON downloads, and build snapshots with a modern, user-friendly interface.

## 🎯 **Key Features**

### ✅ **Core Functionality**
- **Floating Export Button** - Appears when skills are selected
- **Modern Modal Interface** - Clean, responsive design
- **URL Sharing** - Encoded build data in URL parameters
- **JSON Download** - Complete build data as downloadable file
- **Build Snapshot** - Visual summary of selected skills and stats
- **Copy to Clipboard** - One-click URL copying with feedback
- **Import from URL** - Load builds from shared URLs

### 🎨 **Design Features**
- **SWGDB Theming** - Consistent with dark sci-fi aesthetic
- **Responsive Design** - Works on all device sizes
- **Smooth Animations** - Professional transitions and effects
- **Accessibility** - Screen reader friendly with proper ARIA labels

## 📁 **File Structure**

```
src/
├── components/
│   ├── ExportBuildButton.jsx          # Floating export button
│   ├── ExportModal.jsx                # Main export modal
│   └── BuildSnapshot.jsx              # Build summary component
├── utils/
│   └── exportBuild.js                 # Core export utilities
└── pages/tools/skill-calculator.11ty.js  # Integrated implementation
```

## 🎮 **User Experience**

### **1. Floating Export Button**
- **Location**: Bottom-right corner of screen
- **Visibility**: Only appears when skills are selected
- **Design**: Gradient cyan-to-blue with hover effects
- **Functionality**: Opens export modal on click

### **2. Export Modal**
- **Layout**: Centered modal with backdrop blur
- **Content**: Build summary, URL sharing, download options
- **Actions**: Copy URL, Download JSON, Close
- **Responsive**: Adapts to mobile and desktop screens

### **3. Build Snapshot**
- **Display**: Grid layout with key statistics
- **Information**: Skill points, XP required, skills selected, profession
- **Visual**: Color-coded sections with icons

## ⚙️ **Technical Implementation**

### **Core Functions**

#### **URL Encoding/Decoding**
```javascript
// Encode build to shareable URL
function encodeBuildToURL(build) {
    const buildData = {
        profession: build.profession || 'None',
        skills: build.skills || [],
        pointsUsed: build.pointsUsed || 0,
        totalXP: build.totalXP || 0,
        timestamp: new Date().toISOString(),
        version: '1.0'
    };
    
    const base64 = btoa(JSON.stringify(buildData));
    return `${window.location.origin}${window.location.pathname}?build=${encodeURIComponent(base64)}`;
}

// Decode build from URL
function decodeBuildFromURL(encodedData) {
    const decoded = JSON.parse(atob(decodeURIComponent(encodedData)));
    return {
        profession: decoded.profession || 'None',
        skills: decoded.skills || [],
        pointsUsed: decoded.pointsUsed || 0,
        totalXP: decoded.totalXP || 0,
        timestamp: decoded.timestamp || new Date().toISOString()
    };
}
```

#### **JSON Download**
```javascript
function downloadBuildAsJSON(buildData) {
    const build = {
        profession: buildData.profession || 'None',
        skills: buildData.skills || [],
        pointsUsed: buildData.pointsUsed || 0,
        totalXP: buildData.totalXP || 0,
        timestamp: new Date().toISOString(),
        version: '1.0',
        metadata: {
            exportedFrom: 'SWGDB Skill Calculator',
            game: 'Star Wars Galaxies Restoration',
            tool: 'Skill Calculator'
        }
    };

    const blob = new Blob([JSON.stringify(build, null, 2)], { 
        type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `swgdb-build-${build.profession || 'unknown'}-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
}
```

### **Integration Points**

#### **Skill Calculator Integration**
```javascript
// Show/hide export button based on selected skills
function updateUI() {
    // ... existing UI updates ...
    
    // Show/hide export button based on selected skills
    const exportButton = document.getElementById('exportBuildButton');
    if (selectedSkills.size > 0) {
        exportButton.style.display = 'block';
    } else {
        exportButton.style.display = 'none';
    }
}

// Export build with enhanced data structure
function exportBuild() {
    const buildData = {
        profession: currentProfession ? currentProfession.name : 'None',
        skills: Array.from(selectedSkills),
        pointsUsed: skillPointsUsed,
        totalXP: totalXP,
        timestamp: new Date().toISOString()
    };
    
    showExportModal(buildData);
}
```

## 🎨 **Styling Details**

### **Floating Button**
```css
.fixed bottom-4 right-4 z-50 px-6 py-3 rounded-lg 
bg-gradient-to-r from-cyan-500 to-blue-500 
text-white font-semibold shadow-lg 
hover:scale-105 transition-all duration-300 
hover:shadow-cyan-500/25 border border-cyan-400/50
```

### **Modal Design**
```css
.fixed inset-0 z-50 flex items-center justify-center 
bg-black bg-opacity-70 backdrop-blur-sm

.bg-gray-900 text-white rounded-lg p-6 max-w-md w-full 
shadow-xl border border-cyan-500 relative mx-4
```

### **Build Snapshot**
```css
.bg-gray-800 p-4 rounded-lg border border-gray-700
.grid grid-cols-2 gap-3 text-sm
```

## 🚀 **Usage Instructions**

### **For Users**

#### **Exporting a Build**
1. **Select Skills** - Choose skills in the skill calculator
2. **Export Button Appears** - Floating button appears in bottom-right
3. **Click Export** - Opens modal with export options
4. **Choose Method**:
   - **Copy URL** - Click copy button for shareable link
   - **Download JSON** - Click download for file
   - **Close** - Exit modal

#### **Importing a Build**
1. **Share URL** - Send the generated URL to others
2. **Open URL** - Recipient opens the URL
3. **Auto-Import** - Build automatically loads and applies
4. **Verify** - Check that skills are correctly selected

### **For Developers**

#### **Adding to Other Tools**
```javascript
// Import the export system
import { ExportBuildButton } from '../components/ExportBuildButton';
import { encodeBuildToURL, downloadBuildAsJSON } from '../utils/exportBuild';

// Use in your component
<ExportBuildButton buildData={currentBuild} />
```

#### **Customizing Build Data**
```javascript
const buildData = {
    profession: 'Rifleman',
    skills: ['rifle_accuracy_1', 'rifle_accuracy_2'],
    pointsUsed: 12,
    totalXP: 8000,
    timestamp: new Date().toISOString()
};
```

## 📊 **Data Structure**

### **Build Data Format**
```json
{
  "profession": "Rifleman",
  "skills": ["rifle_accuracy_1", "rifle_accuracy_2"],
  "pointsUsed": 12,
  "totalXP": 8000,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0",
  "metadata": {
    "exportedFrom": "SWGDB Skill Calculator",
    "game": "Star Wars Galaxies Restoration",
    "tool": "Skill Calculator"
  }
}
```

### **URL Format**
```
https://swgdb.com/tools/skill-calculator/?build=eyJwcm9mZXNzaW9uIjoiUmlmbGVtYW4iLCJza2lsbHMiOlsicmlmbGVfYWNjdXJhY3lfMSJdfQ==
```

## 🔧 **Configuration**

### **Environment Variables**
- **Base URL**: Automatically detected from `window.location`
- **Version**: Set to '1.0' for current implementation
- **Metadata**: Configurable in `exportBuild.js`

### **Styling Customization**
- **Colors**: Update Tailwind classes in components
- **Layout**: Modify CSS classes for different themes
- **Animations**: Adjust transition durations and effects

## ✅ **Implementation Status**

### **Completed Features**
- ✅ **Floating Export Button** - Appears when skills selected
- ✅ **Modern Modal Interface** - Clean, responsive design
- ✅ **URL Sharing** - Encoded build data in URLs
- ✅ **JSON Download** - Complete build data export
- ✅ **Build Snapshot** - Visual summary display
- ✅ **Copy to Clipboard** - One-click URL copying
- ✅ **Import from URL** - Load builds from shared URLs
- ✅ **SWGDB Theming** - Consistent dark sci-fi aesthetic
- ✅ **Responsive Design** - Mobile and desktop friendly
- ✅ **Error Handling** - Graceful error management
- ✅ **Accessibility** - Screen reader support

### **Future Enhancements**
- 🔄 **Build Templates** - Pre-made popular builds
- 🔄 **Community Sharing** - Public build library
- 🔄 **Build Comparison** - Side-by-side build analysis
- 🔄 **Build History** - Local storage for recent builds
- 🔄 **Advanced Filters** - Search and filter builds

## 🎉 **Benefits**

### **For Users**
- **Easy Sharing** - One-click URL generation
- **Portable Builds** - JSON files for offline storage
- **Visual Feedback** - Clear build summaries
- **Professional Interface** - Modern, polished design

### **For Developers**
- **Modular Design** - Reusable components
- **Extensible Architecture** - Easy to add new features
- **Clean Code** - Well-documented and organized
- **Performance Optimized** - Efficient data handling

## 🚀 **Ready for Production**

The Export Build System is now fully integrated into the SWGDB Skill Calculator and provides:

1. **Professional User Experience** - Modern, intuitive interface
2. **Comprehensive Functionality** - Multiple export options
3. **Robust Implementation** - Error handling and validation
4. **Extensible Architecture** - Easy to extend and customize
5. **Production Ready** - Tested and optimized for deployment

**Ready to enhance the SWGDB Skill Calculator with powerful build sharing capabilities!** 🎨✨
