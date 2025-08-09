// src/guides.11ty.js

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Player Guides - SWGDB',
      permalink: '/guides/'
    };
  }

  render() {
    return `
<section class="max-w-6xl mx-auto px-4 py-12 text-white">
  <h1 class="text-4xl font-bold mb-6">Player Guides</h1>
  <p class="mb-8 text-gray-400">Comprehensive guides to help you master Star Wars Galaxies Restoration, from your first steps to advanced combat strategies.</p>

  <!-- Featured Guides -->
  <div class="grid md:grid-cols-2 gap-8 mb-12">
    <div class="bg-gradient-to-br from-green-800 to-blue-800 rounded-lg p-8 shadow-xl">
      <div class="text-center mb-6">
        <i class="fas fa-user-plus text-6xl text-green-400 mb-4"></i>
        <h2 class="text-2xl font-bold text-white">New Player Guide</h2>
      </div>
      <p class="text-gray-200 mb-6 text-center">Start your journey in the galaxy with this comprehensive beginner's guide covering character creation, professions, and your first steps.</p>
      <div class="text-center">
        <a href="/guides/new-player/" class="bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-8 rounded-lg inline-block transition">
          Get Started →
        </a>
      </div>
    </div>

    <div class="bg-gradient-to-br from-red-800 to-orange-800 rounded-lg p-8 shadow-xl">
      <div class="text-center mb-6">
        <i class="fas fa-crossed-swords text-6xl text-red-400 mb-4"></i>
        <h2 class="text-2xl font-bold text-white">Combat Build Guides</h2>
      </div>
      <p class="text-gray-200 mb-6 text-center">Master PvP and PvE combat with proven build strategies, skill combinations, and tactical advice for all playstyles.</p>
      <div class="text-center">
        <a href="/guides/combat-builds/" class="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-8 rounded-lg inline-block transition">
          View Builds →
        </a>
      </div>
    </div>
  </div>

  <!-- All Guides Grid -->
  <div class="bg-gray-800 rounded-lg p-8 mb-8">
    <h2 class="text-3xl font-bold text-white mb-8 text-center">All Guides</h2>
    
    <div class="grid md:grid-cols-3 gap-6">
      <div class="bg-gray-700 rounded-lg p-6 hover:shadow-lg transition">
        <div class="text-center mb-4">
          <i class="fas fa-rocket text-3xl text-blue-400 mb-2"></i>
          <h3 class="text-lg font-semibold text-yellow-300">Getting Started</h3>
        </div>
        <p class="text-gray-300 text-sm mb-4 text-center">Character creation, first profession choices, and essential early game tips.</p>
        <div class="text-center">
          <a href="/guides/new-player/" class="text-blue-400 hover:text-white font-semibold">Read Guide →</a>
        </div>
      </div>

      <div class="bg-gray-700 rounded-lg p-6 hover:shadow-lg transition">
        <div class="text-center mb-4">
          <i class="fas fa-sword text-3xl text-red-400 mb-2"></i>
          <h3 class="text-lg font-semibold text-yellow-300">Combat Builds</h3>
        </div>
        <p class="text-gray-300 text-sm mb-4 text-center">PvP and PvE builds for all combat professions with detailed skill breakdowns.</p>
        <div class="text-center">
          <a href="/guides/combat-builds/" class="text-red-400 hover:text-white font-semibold">View Builds →</a>
        </div>
      </div>

      <div class="bg-gray-700 rounded-lg p-6 hover:shadow-lg transition">
        <div class="text-center mb-4">
          <i class="fas fa-crosshairs text-3xl text-orange-400 mb-2"></i>
          <h3 class="text-lg font-semibold text-yellow-300">Bounty Hunting</h3>
        </div>
        <p class="text-gray-300 text-sm mb-4 text-center">Master the art of tracking and eliminating targets across the galaxy.</p>
        <div class="text-center">
          <a href="/guides/bounty-hunting/" class="text-orange-400 hover:text-white font-semibold">Learn More →</a>
        </div>
      </div>

      <div class="bg-gray-700 rounded-lg p-6 hover:shadow-lg transition opacity-75">
        <div class="text-center mb-4">
          <i class="fas fa-hammer text-3xl text-yellow-400 mb-2"></i>
          <h3 class="text-lg font-semibold text-gray-400">Crafting Mastery</h3>
        </div>
        <p class="text-gray-300 text-sm mb-4 text-center">Complete crafting guides for all professions (Coming Soon)</p>
        <div class="text-center">
          <span class="text-gray-500 font-semibold">Coming Soon</span>
        </div>
      </div>

      <div class="bg-gray-700 rounded-lg p-6 hover:shadow-lg transition opacity-75">
        <div class="text-center mb-4">
          <i class="fas fa-home text-3xl text-green-400 mb-2"></i>
          <h3 class="text-lg font-semibold text-gray-400">Player Housing</h3>
        </div>
        <p class="text-gray-300 text-sm mb-4 text-center">Housing, decoration, and city building guides (Coming Soon)</p>
        <div class="text-center">
          <span class="text-gray-500 font-semibold">Coming Soon</span>
        </div>
      </div>

      <div class="bg-gray-700 rounded-lg p-6 hover:shadow-lg transition opacity-75">
        <div class="text-center mb-4">
          <i class="fas fa-jedi text-3xl text-purple-400 mb-2"></i>
          <h3 class="text-lg font-semibold text-gray-400">Force Sensitive Path</h3>
        </div>
        <p class="text-gray-300 text-sm mb-4 text-center">Jedi unlock requirements and training guides (Coming Soon)</p>
        <div class="text-center">
          <span class="text-gray-500 font-semibold">Coming Soon</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Quick Access Tools -->
  <div class="bg-gradient-to-r from-purple-900 to-blue-900 rounded-lg p-8">
    <h2 class="text-2xl font-bold text-white mb-6 text-center">Helpful Tools</h2>
    <div class="flex flex-wrap justify-center gap-4">
      <a href="/tools/skill-calculator/" class="bg-yellow-500 hover:bg-yellow-600 text-black font-bold py-3 px-6 rounded-lg transition">
        <i class="fas fa-calculator mr-2"></i>Skill Calculator
      </a>
      <a href="/tools/gcw-calculator/" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg transition">
        <i class="fas fa-globe mr-2"></i>GCW Calculator
      </a>
      <a href="/heroics/" class="bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-lg transition">
        <i class="fas fa-dragon mr-2"></i>Heroic Guides
      </a>
      <a href="/tools/loot-tracker/" class="bg-purple-500 hover:bg-purple-600 text-white font-bold py-3 px-6 rounded-lg transition">
        <i class="fas fa-crosshairs mr-2"></i>Loot Tracker
      </a>
    </div>
    <p class="text-center text-gray-300 mt-4">Use these tools alongside the guides to optimize your gameplay</p>
  </div>
</section>
    `;
  }
};