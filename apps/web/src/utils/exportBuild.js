/**
 * Export Build System for SWGDB Skill Calculator
 * Provides URL encoding and JSON download functionality
 */

/**
 * Encode build data to a shareable URL
 * @param {Object} build - Build data object
 * @returns {string} - Encoded URL with build data
 */
export function encodeBuildToURL(build) {
  try {
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
  } catch (error) {
    console.error('Error encoding build to URL:', error);
    return window.location.href;
  }
}

/**
 * Decode build data from URL parameters
 * @param {string} encodedData - Base64 encoded build data
 * @returns {Object|null} - Decoded build data or null if invalid
 */
export function decodeBuildFromURL(encodedData) {
  try {
    const decoded = JSON.parse(atob(decodeURIComponent(encodedData)));
    return {
      profession: decoded.profession || 'None',
      skills: decoded.skills || [],
      pointsUsed: decoded.pointsUsed || 0,
      totalXP: decoded.totalXP || 0,
      timestamp: decoded.timestamp || new Date().toISOString()
    };
  } catch (error) {
    console.error('Error decoding build from URL:', error);
    return null;
  }
}

/**
 * Download build data as JSON file
 * @param {Object} build - Build data object
 */
export function downloadBuildAsJSON(build) {
  try {
    const buildData = {
      profession: build.profession || 'None',
      skills: build.skills || [],
      pointsUsed: build.pointsUsed || 0,
      totalXP: build.totalXP || 0,
      timestamp: new Date().toISOString(),
      version: '1.0',
      metadata: {
        exportedFrom: 'SWGDB Skill Calculator',
        game: 'Star Wars Galaxies Restoration',
        tool: 'Skill Calculator'
      }
    };

    const blob = new Blob([JSON.stringify(buildData, null, 2)], { 
      type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `swgdb-build-${build.profession || 'unknown'}-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error downloading build as JSON:', error);
    alert('Failed to download build. Please try again.');
  }
}

/**
 * Import build data from JSON file
 * @param {File} file - JSON file to import
 * @returns {Promise<Object>} - Promise resolving to build data
 */
export function importBuildFromJSON(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const buildData = JSON.parse(e.target.result);
        resolve({
          profession: buildData.profession || 'None',
          skills: buildData.skills || [],
          pointsUsed: buildData.pointsUsed || 0,
          totalXP: buildData.totalXP || 0,
          timestamp: buildData.timestamp || new Date().toISOString()
        });
      } catch (error) {
        reject(new Error('Invalid build file format'));
      }
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}

/**
 * Validate build data structure
 * @param {Object} build - Build data to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export function validateBuildData(build) {
  return build && 
         typeof build === 'object' && 
         Array.isArray(build.skills) && 
         typeof build.pointsUsed === 'number' && 
         typeof build.totalXP === 'number';
}

/**
 * Get build summary for display
 * @param {Object} build - Build data object
 * @returns {Object} - Summary object with formatted data
 */
export function getBuildSummary(build) {
  return {
    profession: build.profession || 'None',
    skillCount: build.skills ? build.skills.length : 0,
    pointsUsed: build.pointsUsed || 0,
    pointsRemaining: 250 - (build.pointsUsed || 0),
    totalXP: build.totalXP || 0,
    formattedXP: (build.totalXP || 0).toLocaleString(),
    timestamp: build.timestamp || new Date().toISOString()
  };
}
