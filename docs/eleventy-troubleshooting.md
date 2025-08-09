# 🚨 Eleventy Troubleshooting Guide

## Common Issues and Solutions

### 1. Content Showing as `[object Object]`

**Problem:** Pages display `[object Object]` instead of actual content.

**Root Cause:** Layout function receiving content as an object instead of a string.

**Solution:**
```javascript
// ❌ WRONG - Old Eleventy 1.x syntax
module.exports = (content, data = {}) => {
  return `<html>${content}</html>`;
};

// ✅ CORRECT - Eleventy 2.x syntax
module.exports = function(data) {
  const { content, title = 'Default Title' } = data;
  
  // Handle content that might be an object or string
  let contentString = content;
  if (typeof content === 'object' && content !== null) {
    contentString = content.toString ? content.toString() : JSON.stringify(content);
  } else if (typeof content !== 'string') {
    contentString = String(content || '');
  }
  
  return `<html><title>${title}</title><body>${contentString}</body></html>`;
};
```

### 2. Layout Not Applying

**Problem:** Pages don't use the intended layout.

**Check:**
1. Verify layout path in front matter:
   ```javascript
   // ✅ Correct
   data() {
     return {
       layout: 'base.11ty.js',  // Must match filename exactly
       title: 'My Page'
     };
   }
   ```

2. Check layout file location:
   ```
   src/
   ├── _includes/
   │   └── layouts/
   │       └── base.11ty.js  // Layout files go here
   └── index.11ty.js
   ```

### 3. Development Server Issues

**Problem:** Changes not reflecting or server not starting.

**Solutions:**
```bash
# Clear cache and restart
npm run clean
npm run build
npm run serve

# Check if port is in use
netstat -an | findstr :8080  # Windows
lsof -i :8080                # macOS/Linux

# Kill existing processes
taskkill /F /IM node.exe     # Windows
pkill -f node                # macOS/Linux
```

### 4. Content Not Rendering

**Problem:** Pages appear empty or show errors.

**Debug Steps:**
1. Check browser console (F12) for JavaScript errors
2. Verify template syntax:
   ```javascript
   // ✅ Correct - Return string from render()
   render() {
     return `<h1>Hello World</h1>`;
   }
   
   // ❌ Wrong - Don't return objects
   render() {
     return { content: '<h1>Hello World</h1>' };
   }
   ```

3. Check layout function signature:
   ```javascript
   // ✅ Correct - Accept data object
   module.exports = function(data) {
     const { content, title } = data;
     return `<html>${content}</html>`;
   };
   ```

### 5. Static Assets Not Loading

**Problem:** CSS, JS, or images not found.

**Check:**
1. Verify passthrough copy in `.eleventy.js`:
   ```javascript
   eleventyConfig.addPassthroughCopy("src/assets");
   eleventyConfig.addPassthroughCopy("public");
   ```

2. Check file paths in templates:
   ```html
   <!-- ✅ Correct - Use relative paths -->
   <link href="/assets/style.css" rel="stylesheet">
   
   <!-- ❌ Wrong - Don't use absolute paths -->
   <link href="assets/style.css" rel="stylesheet">
   ```

## 🔍 Debugging Checklist

### Before Reporting Issues

1. **Check Eleventy Version:**
   ```bash
   npx @11ty/eleventy --version
   ```

2. **Verify File Structure:**
   ```
   src/
   ├── _includes/
   │   └── layouts/
   │       └── base.11ty.js
   ├── _data/
   ├── index.11ty.js
   └── pages/
   ```

3. **Test Build Process:**
   ```bash
   # Clean build
   npm run clean
   npm run build
   
   # Check output
   ls _site/
   ```

4. **Inspect Generated HTML:**
   ```bash
   # Look for [object Object] or other issues
   cat _site/index.html
   ```

5. **Check Console Output:**
   - Look for error messages during build
   - Check for missing files or dependencies

## 🛠️ Quick Fixes

### Emergency Reset
```bash
# 1. Stop all processes
taskkill /F /IM node.exe

# 2. Clear everything
rm -rf _site node_modules package-lock.json

# 3. Reinstall and rebuild
npm install
npm run build
npm run serve
```

### Common Layout Fix
```javascript
// Add this to any layout that's not working
module.exports = function(data) {
  const { content, title = 'Default Title' } = data;
  
  // Safely handle content
  let contentString = '';
  if (typeof content === 'string') {
    contentString = content;
  } else if (content && typeof content === 'object') {
    contentString = content.toString ? content.toString() : JSON.stringify(content);
  } else {
    contentString = String(content || '');
  }
  
  return `<!DOCTYPE html>
<html>
<head><title>${title}</title></head>
<body>${contentString}</body>
</html>`;
};
```

## 📞 When to Ask for Help

**Ask for help when:**
- ✅ You've tried all debugging steps above
- ✅ You can reproduce the issue consistently
- ✅ You have error messages or console output
- ✅ You've checked the Eleventy documentation

**Include in your request:**
1. Eleventy version (`npx @11ty/eleventy --version`)
2. Error messages or console output
3. Relevant code snippets
4. Steps to reproduce the issue
5. What you expected vs what happened

## 🎯 Prevention Tips

1. **Use TypeScript or JSDoc** for better type checking
2. **Test layouts independently** before using them
3. **Keep layouts simple** - avoid complex logic
4. **Use consistent naming** for layout files
5. **Document your layout structure** in comments

## 🔗 Useful Resources

- [Eleventy Documentation](https://www.11ty.dev/docs/)
- [Eleventy Layouts Guide](https://www.11ty.dev/docs/layouts/)
- [Eleventy Troubleshooting](https://www.11ty.dev/docs/debugging/)
- [Community Discord](https://discord.gg/eleventy)
