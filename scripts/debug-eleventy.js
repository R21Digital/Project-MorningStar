#!/usr/bin/env node

/**
 * Eleventy Debug Script
 * 
 * This script helps diagnose common Eleventy issues by checking:
 * - File structure
 * - Layout configurations
 * - Build output
 * - Common problems
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Eleventy Debug Script\n');

// Check 1: File structure
console.log('1. Checking file structure...');
const requiredDirs = [
  'src',
  'src/_includes',
  'src/_includes/layouts',
  '_site'
];

const missingDirs = [];
for (const dir of requiredDirs) {
  if (!fs.existsSync(dir)) {
    missingDirs.push(dir);
  }
}

if (missingDirs.length > 0) {
  console.log(`❌ Missing directories: ${missingDirs.join(', ')}`);
} else {
  console.log('✅ All required directories exist');
}

// Check 2: Layout files
console.log('\n2. Checking layout files...');
const layoutsDir = 'src/_includes/layouts';
if (fs.existsSync(layoutsDir)) {
  const layoutFiles = fs.readdirSync(layoutsDir).filter(f => f.endsWith('.11ty.js'));
  if (layoutFiles.length === 0) {
    console.log('❌ No layout files found in src/_includes/layouts/');
  } else {
    console.log(`✅ Found ${layoutFiles.length} layout file(s): ${layoutFiles.join(', ')}`);
    
    // Check for common layout issues
    for (const layoutFile of layoutFiles) {
      const layoutPath = path.join(layoutsDir, layoutFile);
      const content = fs.readFileSync(layoutPath, 'utf8');
      
      // Check for old syntax
      if (content.includes('module.exports = (content, data = {}) =>')) {
        console.log(`⚠️  ${layoutFile} uses old Eleventy 1.x syntax`);
      }
      
      // Check for proper function signature
      if (!content.includes('module.exports = function(data)') && 
          !content.includes('module.exports = (data) =>')) {
        console.log(`⚠️  ${layoutFile} may have incorrect function signature`);
      }
    }
  }
} else {
  console.log('❌ Layouts directory not found');
}

// Check 3: Build output
console.log('\n3. Checking build output...');
if (fs.existsSync('_site')) {
  const siteFiles = fs.readdirSync('_site');
  if (siteFiles.length === 0) {
    console.log('❌ _site directory is empty - build may have failed');
  } else {
    console.log(`✅ _site contains ${siteFiles.length} file(s)`);
    
    // Check for [object Object] in generated files
    const htmlFiles = siteFiles.filter(f => f.endsWith('.html'));
    for (const htmlFile of htmlFiles.slice(0, 3)) { // Check first 3 files
      const htmlPath = path.join('_site', htmlFile);
      const htmlContent = fs.readFileSync(htmlPath, 'utf8');
      
      if (htmlContent.includes('[object Object]')) {
        console.log(`❌ ${htmlFile} contains [object Object] - layout issue detected`);
      }
    }
  }
} else {
  console.log('❌ _site directory not found - run npm run build first');
}

// Check 4: Package.json scripts
console.log('\n4. Checking package.json scripts...');
if (fs.existsSync('package.json')) {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const scripts = packageJson.scripts || {};
  
  const requiredScripts = ['build', 'serve'];
  for (const script of requiredScripts) {
    if (scripts[script]) {
      console.log(`✅ ${script} script found: ${scripts[script]}`);
    } else {
      console.log(`❌ ${script} script missing`);
    }
  }
} else {
  console.log('❌ package.json not found');
}

// Check 5: Eleventy config
console.log('\n5. Checking Eleventy configuration...');
if (fs.existsSync('.eleventy.js')) {
  const configContent = fs.readFileSync('.eleventy.js', 'utf8');
  
  if (configContent.includes('addPassthroughCopy')) {
    console.log('✅ Passthrough copy configured');
  } else {
    console.log('⚠️  No passthrough copy configured');
  }
  
  if (configContent.includes('dir:')) {
    console.log('✅ Directory structure configured');
  } else {
    console.log('⚠️  Directory structure not explicitly configured');
  }
} else {
  console.log('❌ .eleventy.js not found');
}

// Check 6: Common issues
console.log('\n6. Checking for common issues...');

// Check for port conflicts
const { execSync } = require('child_process');
try {
  const portCheck = execSync('netstat -an | findstr :8080', { encoding: 'utf8' });
  if (portCheck.trim()) {
    console.log('⚠️  Port 8080 may be in use');
  } else {
    console.log('✅ Port 8080 appears to be free');
  }
} catch (error) {
  console.log('ℹ️  Could not check port status');
}

// Check for node processes
try {
  const nodeCheck = execSync('tasklist | findstr node.exe', { encoding: 'utf8' });
  const nodeCount = (nodeCheck.match(/node\.exe/g) || []).length;
  if (nodeCount > 0) {
    console.log(`⚠️  ${nodeCount} Node.js process(es) running`);
  } else {
    console.log('✅ No Node.js processes running');
  }
} catch (error) {
  console.log('ℹ️  Could not check Node.js processes');
}

console.log('\n🎯 Quick Fixes:');
console.log('1. If you see [object Object]: Update layout function signature');
console.log('2. If build fails: Run npm run clean && npm run build');
console.log('3. If server won\'t start: Kill existing processes with taskkill /F /IM node.exe');
console.log('4. If layouts not working: Check file paths and function signatures');

console.log('\n📚 For more help, see: docs/eleventy-troubleshooting.md');
