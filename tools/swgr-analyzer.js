/**
 * SWGR.org Skill Calculator Analysis Script
 * 
 * Instructions:
 * 1. Open https://swgr.org/skill-calculator/ in your browser
 * 2. Open Developer Tools (F12)
 * 3. Go to Console tab
 * 4. Copy and paste this entire script
 * 5. Press Enter to run the analysis
 * 
 * This will analyze their implementation and provide detailed insights.
 */

(function() {
    console.log('🔍 SWGR.org Skill Calculator Analysis Starting...');
    console.log('================================================');
    
    // Analysis results object
    const analysis = {
        timestamp: new Date().toISOString(),
        url: window.location.href,
        findings: {}
    };
    
    // 1. Analyze global variables
    console.log('\n📊 1. Analyzing Global Variables...');
    const globalVars = Object.keys(window).filter(key => 
        key.includes('skill') || 
        key.includes('profession') || 
        key.includes('build') ||
        key.includes('calculator')
    );
    analysis.findings.globalVariables = globalVars;
    console.log('Global variables found:', globalVars);
    
    // 2. Analyze DOM structure
    console.log('\n🏗️ 2. Analyzing DOM Structure...');
    
    // Find skill calculator container
    const calculatorContainer = document.querySelector('.skill-calculator, [class*="calculator"], [class*="skill"]');
    if (calculatorContainer) {
        analysis.findings.calculatorContainer = {
            className: calculatorContainer.className,
            id: calculatorContainer.id,
            children: Array.from(calculatorContainer.children).map(child => ({
                tagName: child.tagName,
                className: child.className,
                id: child.id
            }))
        };
        console.log('Calculator container found:', analysis.findings.calculatorContainer);
    } else {
        console.log('❌ No calculator container found');
    }
    
    // Find profession selector
    const professionSelector = document.querySelector('select, [class*="profession"], [class*="dropdown"]');
    if (professionSelector) {
        analysis.findings.professionSelector = {
            tagName: professionSelector.tagName,
            className: professionSelector.className,
            options: Array.from(professionSelector.options || []).map(option => ({
                value: option.value,
                text: option.textContent
            }))
        };
        console.log('Profession selector found:', analysis.findings.professionSelector);
    } else {
        console.log('❌ No profession selector found');
    }
    
    // Find skill tree
    const skillTree = document.querySelector('[class*="skill-tree"], [class*="tree"], [class*="skills"]');
    if (skillTree) {
        analysis.findings.skillTree = {
            className: skillTree.className,
            children: Array.from(skillTree.children).map(child => ({
                tagName: child.tagName,
                className: child.className,
                textContent: child.textContent?.substring(0, 50)
            }))
        };
        console.log('Skill tree found:', analysis.findings.skillTree);
    } else {
        console.log('❌ No skill tree found');
    }
    
    // Find skill boxes
    const skillBoxes = document.querySelectorAll('[class*="skill"], [class*="box"], [class*="item"]');
    if (skillBoxes.length > 0) {
        analysis.findings.skillBoxes = Array.from(skillBoxes).slice(0, 5).map(box => ({
            className: box.className,
            textContent: box.textContent?.substring(0, 100),
            style: {
                backgroundColor: getComputedStyle(box).backgroundColor,
                borderColor: getComputedStyle(box).borderColor,
                color: getComputedStyle(box).color
            }
        }));
        console.log('Skill boxes found:', skillBoxes.length, 'items');
        console.log('Sample skill boxes:', analysis.findings.skillBoxes);
    } else {
        console.log('❌ No skill boxes found');
    }
    
    // 3. Analyze CSS styles
    console.log('\n🎨 3. Analyzing CSS Styles...');
    
    const computedStyles = {};
    if (skillBoxes.length > 0) {
        const sampleBox = skillBoxes[0];
        const styles = getComputedStyle(sampleBox);
        computedStyles.skillBox = {
            backgroundColor: styles.backgroundColor,
            borderColor: styles.borderColor,
            color: styles.color,
            fontSize: styles.fontSize,
            fontWeight: styles.fontWeight,
            padding: styles.padding,
            margin: styles.margin,
            borderRadius: styles.borderRadius,
            boxShadow: styles.boxShadow
        };
        console.log('Sample skill box styles:', computedStyles.skillBox);
    }
    
    // 4. Analyze JavaScript functions
    console.log('\n⚙️ 4. Analyzing JavaScript Functions...');
    
    const functions = Object.keys(window).filter(key => {
        const value = window[key];
        return typeof value === 'function' && (
            key.includes('skill') || 
            key.includes('profession') || 
            key.includes('build') ||
            key.includes('calculator') ||
            key.includes('select') ||
            key.includes('toggle')
        );
    });
    
    analysis.findings.functions = functions;
    console.log('Relevant functions found:', functions);
    
    // 5. Analyze network requests (if possible)
    console.log('\n🌐 5. Analyzing Network Requests...');
    
    // Check for any data in localStorage or sessionStorage
    const localStorageData = {};
    const sessionStorageData = {};
    
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.includes('skill') || key.includes('profession') || key.includes('build'))) {
            try {
                localStorageData[key] = JSON.parse(localStorage.getItem(key));
            } catch {
                localStorageData[key] = localStorage.getItem(key);
            }
        }
    }
    
    for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && (key.includes('skill') || key.includes('profession') || key.includes('build'))) {
            try {
                sessionStorageData[key] = JSON.parse(sessionStorage.getItem(key));
            } catch {
                sessionStorageData[key] = sessionStorage.getItem(key);
            }
        }
    }
    
    if (Object.keys(localStorageData).length > 0) {
        analysis.findings.localStorage = localStorageData;
        console.log('LocalStorage data found:', localStorageData);
    }
    
    if (Object.keys(sessionStorageData).length > 0) {
        analysis.findings.sessionStorage = sessionStorageData;
        console.log('SessionStorage data found:', sessionStorageData);
    }
    
    // 6. Analyze page structure
    console.log('\n📄 6. Analyzing Page Structure...');
    
    const pageStructure = {
        title: document.title,
        metaDescription: document.querySelector('meta[name="description"]')?.content,
        headScripts: Array.from(document.head.querySelectorAll('script')).map(script => ({
            src: script.src,
            type: script.type,
            content: script.textContent?.substring(0, 100)
        })),
        bodyScripts: Array.from(document.body.querySelectorAll('script')).map(script => ({
            src: script.src,
            type: script.type,
            content: script.textContent?.substring(0, 100)
        }))
    };
    
    analysis.findings.pageStructure = pageStructure;
    console.log('Page structure:', pageStructure);
    
    // 7. Generate recommendations
    console.log('\n💡 7. Generating Recommendations...');
    
    const recommendations = [];
    
    if (analysis.findings.skillBoxes && analysis.findings.skillBoxes.length > 0) {
        recommendations.push('✅ Skill boxes found - analyze their structure and styling');
    } else {
        recommendations.push('❌ No skill boxes found - check for different class names');
    }
    
    if (analysis.findings.professionSelector) {
        recommendations.push('✅ Profession selector found - analyze dropdown structure');
    } else {
        recommendations.push('❌ No profession selector found - check for different selectors');
    }
    
    if (analysis.findings.skillTree) {
        recommendations.push('✅ Skill tree found - analyze tree structure and organization');
    } else {
        recommendations.push('❌ No skill tree found - check for different container names');
    }
    
    if (analysis.findings.functions.length > 0) {
        recommendations.push('✅ JavaScript functions found - analyze their functionality');
    } else {
        recommendations.push('❌ No relevant functions found - check for minified code');
    }
    
    // 8. Export analysis
    console.log('\n📋 8. Analysis Complete!');
    console.log('================================================');
    console.log('📊 Full Analysis Results:');
    console.log(JSON.stringify(analysis, null, 2));
    
    // Create downloadable analysis
    const analysisBlob = new Blob([JSON.stringify(analysis, null, 2)], { type: 'application/json' });
    const analysisUrl = URL.createObjectURL(analysisBlob);
    
    console.log('\n💾 To download the analysis:');
    console.log('1. Copy this URL:', analysisUrl);
    console.log('2. Open in a new tab to download the JSON file');
    
    // Store analysis in localStorage for later use
    localStorage.setItem('swgr_analysis_' + Date.now(), JSON.stringify(analysis));
    
    console.log('\n🎯 Next Steps:');
    console.log('1. Review the analysis results above');
    console.log('2. Download the JSON file for detailed analysis');
    console.log('3. Use the findings to improve our SWGDB implementation');
    console.log('4. Focus on the identified structure and styling patterns');
    
    return analysis;
})();
