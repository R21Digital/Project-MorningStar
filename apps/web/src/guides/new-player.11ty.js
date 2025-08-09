// src/guides/new-player.11ty.js

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'New Player Guide - SWGDB',
      permalink: '/guides/new-player/'
    };
  }

  render() {
    return `
<section class="max-w-6xl mx-auto px-4 py-12 text-white">
  <a href="/guides/" class="inline-flex items-center text-yellow-300 hover:text-white mb-6 font-semibold">
    <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path>
    </svg>
    Back to Guides
  </a>

  <h1 class="text-4xl font-bold mb-6 text-yellow-300">New Player Guide</h1>
  <p class="mb-8 text-gray-400">Welcome to Star Wars Galaxies Restoration! This comprehensive guide will help you get started on your journey in the galaxy far, far away.</p>

  <!-- Getting Started Section -->
  <div class="bg-gradient-to-r from-green-900 to-blue-900 rounded-lg p-8 mb-8">
    <h2 class="text-3xl font-bold text-white mb-6">
      <i class="fas fa-rocket text-green-400 mr-3"></i>Getting Started
    </h2>
    
    <div class="grid md:grid-cols-2 gap-8">
      <div>
        <h3 class="text-xl font-semibold text-yellow-300 mb-4">Character Creation</h3>
        <ul class="space-y-3 text-gray-300">
          <li class="flex items-start">
            <i class="fas fa-check-circle text-green-400 mr-3 mt-1"></i>
            <span>Choose your starting planet carefully - each offers unique opportunities</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-check-circle text-green-400 mr-3 mt-1"></i>
            <span>Your starting profession isn't permanent - you can change later</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-check-circle text-green-400 mr-3 mt-1"></i>
            <span>Species choice affects some stats but isn't game-breaking</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-check-circle text-green-400 mr-3 mt-1"></i>
            <span>Take time to create a character you'll enjoy looking at</span>
          </li>
        </ul>
      </div>
      
      <div>
        <h3 class="text-xl font-semibold text-yellow-300 mb-4">First Steps</h3>
        <ol class="space-y-3 text-gray-300 list-decimal list-inside">
          <li>Complete the tutorial missions to learn basic controls</li>
          <li>Visit the local starport and cantina to meet other players</li>
          <li>Start training your first profession skills</li>
          <li>Explore the starter town and nearby areas</li>
          <li>Join a guild for support and community</li>
        </ol>
      </div>
    </div>
  </div>

  <!-- Profession System -->
  <div class="bg-gray-800 rounded-lg p-8 mb-8">
    <h2 class="text-3xl font-bold text-white mb-6">
      <i class="fas fa-graduation-cap text-blue-400 mr-3"></i>Understanding Professions
    </h2>
    
    <div class="mb-6">
      <p class="text-gray-300 mb-4">SWG features a unique skill-based progression system. You can learn multiple professions and create hybrid builds.</p>
    </div>

    <div class="grid md:grid-cols-3 gap-6">
      <div class="bg-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-yellow-300 mb-3">
          <i class="fas fa-sword mr-2"></i>Combat Professions
        </h3>
        <ul class="text-gray-300 text-sm space-y-2">
          <li>• <strong>Marksman:</strong> Ranged weapons specialist</li>
          <li>• <strong>Brawler:</strong> Unarmed and melee combat</li>
          <li>• <strong>Jedi:</strong> Force-sensitive warrior (unlock required)</li>
          <li>• <strong>Bounty Hunter:</strong> Advanced tracking and combat</li>
        </ul>
      </div>

      <div class="bg-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-yellow-300 mb-3">
          <i class="fas fa-hammer mr-2"></i>Crafting Professions
        </h3>
        <ul class="text-gray-300 text-sm space-y-2">
          <li>• <strong>Artisan:</strong> Basic crafting foundation</li>
          <li>• <strong>Weaponsmith:</strong> Create weapons and ammunition</li>
          <li>• <strong>Armorsmith:</strong> Craft protective gear</li>
          <li>• <strong>Chef:</strong> Prepare food and drinks</li>
        </ul>
      </div>

      <div class="bg-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-yellow-300 mb-3">
          <i class="fas fa-heart mr-2"></i>Support Professions
        </h3>
        <ul class="text-gray-300 text-sm space-y-2">
          <li>• <strong>Medic:</strong> Healing and buffing others</li>
          <li>• <strong>Entertainer:</strong> Inspire and heal fatigue</li>
          <li>• <strong>Scout:</strong> Exploration and survival</li>
          <li>• <strong>Creature Handler:</strong> Tame and train pets</li>
        </ul>
      </div>
    </div>

    <div class="mt-6 bg-blue-900 rounded-lg p-4">
      <p class="text-blue-200 text-center">
        <i class="fas fa-lightbulb mr-2"></i>
        <strong>Pro Tip:</strong> Start with Artisan to unlock crafting options, then branch into specializations that interest you.
      </p>
    </div>
  </div>

  <!-- Economy and Credits -->
  <div class="bg-gray-800 rounded-lg p-8 mb-8">
    <h2 class="text-3xl font-bold text-white mb-6">
      <i class="fas fa-coins text-yellow-400 mr-3"></i>Economy & Making Credits
    </h2>
    
    <div class="grid md:grid-cols-2 gap-8">
      <div>
        <h3 class="text-xl font-semibold text-yellow-300 mb-4">Early Credit Sources</h3>
        <ul class="space-y-3 text-gray-300">
          <li class="flex items-start">
            <i class="fas fa-arrow-right text-yellow-400 mr-3 mt-1"></i>
            <span><strong>Mission Terminals:</strong> Quick credits for simple tasks</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-arrow-right text-yellow-400 mr-3 mt-1"></i>
            <span><strong>Resource Harvesting:</strong> Sell raw materials to crafters</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-arrow-right text-yellow-400 mr-3 mt-1"></i>
            <span><strong>Creature Hunting:</strong> Sell hides and meat to NPCs</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-arrow-right text-yellow-400 mr-3 mt-1"></i>
            <span><strong>Entertainer Tips:</strong> Perform for other players</span>
          </li>
        </ul>
      </div>

      <div>
        <h3 class="text-xl font-semibold text-yellow-300 mb-4">Advanced Income</h3>
        <ul class="space-y-3 text-gray-300">
          <li class="flex items-start">
            <i class="fas fa-arrow-right text-yellow-400 mr-3 mt-1"></i>
            <span><strong>Player Vendors:</strong> Set up shop to sell items</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-arrow-right text-yellow-400 mr-3 mt-1"></i>
            <span><strong>Crafting Business:</strong> Create in-demand items</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-arrow-right text-yellow-400 mr-3 mt-1"></i>
            <span><strong>Heroic Encounters:</strong> Rare loot for high-level players</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-arrow-right text-yellow-400 mr-3 mt-1"></i>
            <span><strong>Bounty Hunting:</strong> Track and eliminate player targets</span>
          </li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Community and Social -->
  <div class="bg-gray-800 rounded-lg p-8 mb-8">
    <h2 class="text-3xl font-bold text-white mb-6">
      <i class="fas fa-users text-purple-400 mr-3"></i>Community & Social Features
    </h2>
    
    <div class="grid md:grid-cols-2 gap-8">
      <div>
        <h3 class="text-xl font-semibold text-yellow-300 mb-4">Finding Your Place</h3>
        <ul class="space-y-3 text-gray-300">
          <li class="flex items-start">
            <i class="fas fa-guild text-purple-400 mr-3 mt-1"></i>
            <span><strong>Join a Guild:</strong> Find community, support, and shared goals</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-home text-purple-400 mr-3 mt-1"></i>
            <span><strong>Player Cities:</strong> Live in thriving player communities</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-comments text-purple-400 mr-3 mt-1"></i>
            <span><strong>Chat Channels:</strong> Join planet and help channels</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-handshake text-purple-400 mr-3 mt-1"></i>
            <span><strong>Player Events:</strong> Participate in community activities</span>
          </li>
        </ul>
      </div>

      <div>
        <h3 class="text-xl font-semibold text-yellow-300 mb-4">Social Activities</h3>
        <ul class="space-y-3 text-gray-300">
          <li class="flex items-start">
            <i class="fas fa-music text-purple-400 mr-3 mt-1"></i>
            <span><strong>Cantina Entertainment:</strong> Watch and tip performers</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-store text-purple-400 mr-3 mt-1"></i>
            <span><strong>Player Markets:</strong> Browse and trade with others</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-flag text-purple-400 mr-3 mt-1"></i>
            <span><strong>Faction Warfare:</strong> Join Imperial or Rebel forces</span>
          </li>
          <li class="flex items-start">
            <i class="fas fa-trophy text-purple-400 mr-3 mt-1"></i>
            <span><strong>Competitions:</strong> Racing, combat tournaments, etc.</span>
          </li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Next Steps -->
  <div class="bg-gradient-to-r from-purple-900 to-blue-900 rounded-lg p-8">
    <h2 class="text-2xl font-bold text-white mb-6 text-center">Ready for More?</h2>
    <div class="flex flex-wrap justify-center gap-4">
      <a href="/guides/combat-builds/" class="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-lg transition">
        <i class="fas fa-sword mr-2"></i>Combat Builds
      </a>
      <a href="/tools/skill-calculator/" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg transition">
        <i class="fas fa-calculator mr-2"></i>Skill Calculator
      </a>
      <a href="/heroics/" class="bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-lg transition">
        <i class="fas fa-dragon mr-2"></i>Heroic Content
      </a>
    </div>
    <p class="text-center text-gray-300 mt-4">Continue your journey with advanced guides and tools</p>
  </div>
</section>
    `;
  }
};