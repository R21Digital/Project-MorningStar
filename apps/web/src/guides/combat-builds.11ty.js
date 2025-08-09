// src/guides/combat-builds.11ty.js

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Combat Build Guides - SWGDB',
      permalink: '/guides/combat-builds/'
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

  <h1 class="text-4xl font-bold mb-6 text-yellow-300">Combat Build Guides</h1>
  <p class="mb-8 text-gray-400">Master the art of combat with these proven build strategies for PvP and PvE encounters.</p>

  <!-- PvP Builds Section -->
  <div class="bg-gray-800 rounded-lg p-8 mb-8">
    <h2 class="text-3xl font-bold text-white mb-6">
      <i class="fas fa-crossed-swords text-red-400 mr-3"></i>PvP Combat Builds
    </h2>
    
    <div class="grid md:grid-cols-2 gap-8">
      <div class="bg-gray-700 rounded-lg p-6">
        <h3 class="text-xl font-semibold text-yellow-300 mb-3">Jedi Guardian Build</h3>
        <div class="mb-4">
          <span class="bg-blue-500 text-white text-xs px-2 py-1 rounded">FORCE SENSITIVE</span>
          <span class="bg-red-500 text-white text-xs px-2 py-1 rounded ml-2">HIGH SURVIVABILITY</span>
        </div>
        <p class="text-gray-300 mb-4">Tank-focused Jedi build with heavy armor and defensive lightsaber techniques. Excellent for frontline combat and protecting allies.</p>
        <ul class="text-gray-300 text-sm space-y-1 mb-4">
          <li>• Enhanced Block and Parry chance</li>
          <li>• Force Armor for damage reduction</li>
          <li>• Lightsaber Defense mastery</li>
          <li>• Force Healing for sustainability</li>
        </ul>
        <a href="#jedi-guardian-detailed" class="text-yellow-300 hover:underline font-semibold">View Full Build →</a>
      </div>

      <div class="bg-gray-700 rounded-lg p-6">
        <h3 class="text-xl font-semibold text-yellow-300 mb-3">Bounty Hunter DPS</h3>
        <div class="mb-4">
          <span class="bg-green-500 text-white text-xs px-2 py-1 rounded">HIGH DPS</span>
          <span class="bg-purple-500 text-white text-xs px-2 py-1 rounded ml-2">RANGED</span>
        </div>
        <p class="text-gray-300 mb-4">Glass cannon build focused on maximum damage output with rifles and carbines. Perfect for picking off enemies from range.</p>
        <ul class="text-gray-300 text-sm space-y-1 mb-4">
          <li>• Rifle specialization and mastery</li>
          <li>• Advanced targeting systems</li>
          <li>• Explosive damage bonuses</li>
          <li>• Stealth and ambush tactics</li>
        </ul>
        <a href="#bounty-hunter-detailed" class="text-yellow-300 hover:underline font-semibold">View Full Build →</a>
      </div>

      <div class="bg-gray-700 rounded-lg p-6">
        <h3 class="text-xl font-semibold text-yellow-300 mb-3">Teras Kasi Master</h3>
        <div class="mb-4">
          <span class="bg-orange-500 text-white text-xs px-2 py-1 rounded">MELEE</span>
          <span class="bg-yellow-500 text-black text-xs px-2 py-1 rounded ml-2">MOBILE</span>
        </div>
        <p class="text-gray-300 mb-4">Mobile melee fighter with deadly unarmed combat techniques. Specializes in quick strikes and evasion.</p>
        <ul class="text-gray-300 text-sm space-y-1 mb-4">
          <li>• Unarmed combat mastery</li>
          <li>• Enhanced dodge and counter-attack</li>
          <li>• Stunning and disabling moves</li>
          <li>• High mobility and speed</li>
        </ul>
        <a href="#teras-kasi-detailed" class="text-yellow-300 hover:underline font-semibold">View Full Build →</a>
      </div>

      <div class="bg-gray-700 rounded-lg p-6">
        <h3 class="text-xl font-semibold text-yellow-300 mb-3">Commando Heavy Weapons</h3>
        <div class="mb-4">
          <span class="bg-red-600 text-white text-xs px-2 py-1 rounded">EXPLOSIVE</span>
          <span class="bg-gray-600 text-white text-xs px-2 py-1 rounded ml-2">AREA DAMAGE</span>
        </div>
        <p class="text-gray-300 mb-4">Heavy weapons specialist with rocket launchers and flamethowers. Dominates group combat scenarios.</p>
        <ul class="text-gray-300 text-sm space-y-1 mb-4">
          <li>• Heavy weapon proficiency</li>
          <li>• Area-of-effect damage specialization</li>
          <li>• Advanced targeting and accuracy</li>
          <li>• Explosive ammunition types</li>
        </ul>
        <a href="#commando-detailed" class="text-yellow-300 hover:underline font-semibold">View Full Build →</a>
      </div>
    </div>
  </div>

  <!-- PvE Builds Section -->
  <div class="bg-gray-800 rounded-lg p-8 mb-8">
    <h2 class="text-3xl font-bold text-white mb-6">
      <i class="fas fa-dragon text-green-400 mr-3"></i>PvE & Heroic Builds
    </h2>
    
    <div class="grid md:grid-cols-2 gap-8">
      <div class="bg-gray-700 rounded-lg p-6">
        <h3 class="text-xl font-semibold text-yellow-300 mb-3">Doctor/Medic Support</h3>
        <div class="mb-4">
          <span class="bg-blue-400 text-white text-xs px-2 py-1 rounded">SUPPORT</span>
          <span class="bg-green-400 text-black text-xs px-2 py-1 rounded ml-2">HEALING</span>
        </div>
        <p class="text-gray-300 mb-4">Essential support build for heroic encounters. Keeps the group alive with powerful healing and buffs.</p>
        <ul class="text-gray-300 text-sm space-y-1 mb-4">
          <li>• Advanced medical techniques</li>
          <li>• Group healing and resurrection</li>
          <li>• Stat enhancement and buffs</li>
          <li>• Poison and disease cure</li>
        </ul>
        <a href="#doctor-detailed" class="text-yellow-300 hover:underline font-semibold">View Full Build →</a>
      </div>

      <div class="bg-gray-700 rounded-lg p-6">
        <h3 class="text-xl font-semibold text-yellow-300 mb-3">Creature Handler Hybrid</h3>
        <div class="mb-4">
          <span class="bg-purple-600 text-white text-xs px-2 py-1 rounded">PETS</span>
          <span class="bg-orange-600 text-white text-xs px-2 py-1 rounded ml-2">UTILITY</span>
        </div>
        <p class="text-gray-300 mb-4">Unique build utilizing creature companions for both combat and utility in challenging encounters.</p>
        <ul class="text-gray-300 text-sm space-y-1 mb-4">
          <li>• Advanced creature taming</li>
          <li>• Pet combat training and commands</li>
          <li>• Creature stat enhancement</li>
          <li>• Multi-pet coordination</li>
        </ul>
        <a href="#creature-handler-detailed" class="text-yellow-300 hover:underline font-semibold">View Full Build →</a>
      </div>
    </div>
  </div>

  <!-- Build Tools Section -->
  <div class="bg-gradient-to-r from-purple-900 to-blue-900 rounded-lg p-8">
    <h2 class="text-2xl font-bold text-white mb-6 text-center">Build Planning Tools</h2>
    <div class="flex flex-wrap justify-center gap-4">
      <a href="/tools/skill-calculator/" class="bg-yellow-500 hover:bg-yellow-600 text-black font-bold py-3 px-6 rounded-lg transition">
        <i class="fas fa-calculator mr-2"></i>Skill Calculator
      </a>
      <a href="/tools/loot-tracker/" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg transition">
        <i class="fas fa-crosshairs mr-2"></i>Loot Tracker
      </a>
      <a href="/heroics/" class="bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-lg transition">
        <i class="fas fa-dragon mr-2"></i>Heroic Encounters
      </a>
    </div>
    <p class="text-center text-gray-300 mt-4">Use these tools to plan and optimize your combat builds</p>
  </div>
</section>
    `;
  }
};