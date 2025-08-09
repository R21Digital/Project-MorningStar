// src/pages/dev-tools/index.11ty.js

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Developer Tools - SWGDB',
      permalink: 'dev-tools/index.html'
    };
  }

  render() {
    return `
<section class="py-12 px-6 max-w-6xl mx-auto text-white">
  <div class="text-center mb-12">
    <h1 class="text-4xl font-bold mb-4 text-red-400">🛠️ Developer Tools</h1>
    <p class="text-xl text-gray-300">Access to hidden pages and development features</p>
    <div class="bg-red-900 bg-opacity-30 border border-red-500 rounded-lg p-4 mt-6">
      <p class="text-red-300 font-semibold">⚠️ For Development Use Only</p>
      <p class="text-red-200 text-sm">These pages are hidden from main navigation but accessible for testing</p>
    </div>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
    <!-- Hidden Pages Section -->
    <div class="bg-gray-800 rounded-lg p-6">
      <h2 class="text-2xl font-bold mb-4 text-yellow-300">📁 Hidden Pages</h2>
      <p class="text-gray-300 mb-4">Pages moved to _hidden/ directory but still accessible:</p>
      
      <div class="space-y-3">
        <a href="/heroics/" class="block bg-gray-700 hover:bg-gray-600 rounded p-3 transition-colors">
          <span class="font-semibold text-blue-400">🗡️ Heroics</span>
          <p class="text-sm text-gray-400">Heroic instance guides and strategies</p>
        </a>
        
        <a href="/loot/" class="block bg-gray-700 hover:bg-gray-600 rounded p-3 transition-colors">
          <span class="font-semibold text-green-400">💎 Loot Tracker</span>
          <p class="text-sm text-gray-400">Item drops and loot tables</p>
        </a>
        
        <a href="/mods/" class="block bg-gray-700 hover:bg-gray-600 rounded p-3 transition-colors">
          <span class="font-semibold text-purple-400">🔧 Mods Portal</span>
          <p class="text-sm text-gray-400">Community mods and modifications</p>
        </a>
        
        <a href="/guides/" class="block bg-gray-700 hover:bg-gray-600 rounded p-3 transition-colors">
          <span class="font-semibold text-orange-400">📚 Player Guides</span>
          <p class="text-sm text-gray-400">Comprehensive game guides</p>
        </a>
        
        <a href="/contribute/" class="block bg-gray-700 hover:bg-gray-600 rounded p-3 transition-colors">
          <span class="font-semibold text-cyan-400">🤝 Contribute</span>
          <p class="text-sm text-gray-400">Community contribution portal</p>
        </a>
        
        <a href="/legal/" class="block bg-gray-700 hover:bg-gray-600 rounded p-3 transition-colors">
          <span class="font-semibold text-yellow-400">⚖️ Legal</span>
          <p class="text-sm text-gray-400">Legal notices and compliance</p>
        </a>
        
        <a href="/credits/" class="block bg-gray-700 hover:bg-gray-600 rounded p-3 transition-colors">
          <span class="font-semibold text-pink-400">👥 Credits</span>
          <p class="text-sm text-gray-400">Contributors and acknowledgments</p>
        </a>
      </div>
    </div>

    <!-- Current Tools Section -->
    <div class="bg-gray-800 rounded-lg p-6">
      <h2 class="text-2xl font-bold mb-4 text-yellow-300">🧰 Active Tools</h2>
      <p class="text-gray-300 mb-4">Currently available in main navigation:</p>
      
      <div class="space-y-3">
        <a href="/tools/skill-calculator/" class="block bg-green-900 bg-opacity-50 border border-green-500 hover:bg-green-800 hover:bg-opacity-50 rounded p-3 transition-colors">
          <span class="font-semibold text-green-300">🧮 Skill Calculator</span>
          <p class="text-sm text-gray-400">Plan profession builds and skill trees</p>
        </a>
        
        <a href="/tools/gcw-calculator/" class="block bg-green-900 bg-opacity-50 border border-green-500 hover:bg-green-800 hover:bg-opacity-50 rounded p-3 transition-colors">
          <span class="font-semibold text-green-300">🌍 GCW Calculator</span>
          <p class="text-sm text-gray-400">Galactic Civil War planet control</p>
        </a>
        
        <a href="/tools/build-calculator/" class="block bg-green-900 bg-opacity-50 border border-green-500 hover:bg-green-800 hover:bg-opacity-50 rounded p-3 transition-colors">
          <span class="font-semibold text-green-300">⚡ Build Calculator</span>
          <p class="text-sm text-gray-400">Character build optimization</p>
        </a>
        
        <a href="/tools/gear-optimizer/" class="block bg-green-900 bg-opacity-50 border border-green-500 hover:bg-green-800 hover:bg-opacity-50 rounded p-3 transition-colors">
          <span class="font-semibold text-green-300">⚔️ Gear Optimizer</span>
          <p class="text-sm text-gray-400">Equipment and gear combinations</p>
        </a>
      </div>
    </div>
  </div>

  <div class="mt-12 bg-gray-800 rounded-lg p-6">
    <h2 class="text-2xl font-bold mb-4 text-yellow-300">🔧 Development Notes</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h3 class="text-lg font-semibold text-blue-400 mb-2">Site Structure</h3>
        <ul class="text-gray-300 text-sm space-y-1">
          <li>• Main tools are in <code class="bg-gray-700 px-1 rounded">src/pages/tools/</code></li>
          <li>• Hidden pages are in <code class="bg-gray-700 px-1 rounded">src/pages/_hidden/</code></li>
          <li>• Navigation simplified to 4 tools only</li>
          <li>• All old content preserved for future use</li>
        </ul>
      </div>
      <div>
        <h3 class="text-lg font-semibold text-red-400 mb-2">Access Notes</h3>
        <ul class="text-gray-300 text-sm space-y-1">
          <li>• Hidden pages still work via direct URL</li>
          <li>• No links in main navigation</li>
          <li>• Use this dev page to test hidden routes</li>
          <li>• Remove this page before production</li>
        </ul>
      </div>
    </div>
  </div>
</section>
    `;
  }
};