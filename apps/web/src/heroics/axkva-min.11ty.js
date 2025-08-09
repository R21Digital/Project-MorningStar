// src/heroics/axkva-min.11ty.js

const heroics = require('../../public/data/heroics.json');

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Axkva Min - Heroic Guide',
      permalink: '/heroics/axkva-min/',
    };
  }

  render() {
    const heroic = heroics.find(h => h.id === 'axkva-min');
    
    return `
<section class="py-12 px-6 max-w-6xl mx-auto text-white">
  <!-- Back Link -->
  <a href="/heroics" class="inline-flex items-center text-yellow-300 hover:text-white mb-6 font-semibold">
    <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path>
    </svg>
    Back to Heroics
  </a>

  <!-- Hero Section -->
  <div class="bg-gradient-to-r from-purple-900 to-indigo-900 rounded-lg p-8 mb-8 text-center relative overflow-hidden">
    <div class="absolute inset-0 bg-black bg-opacity-20"></div>
    <div class="relative z-10">
      <h1 class="text-5xl font-bold mb-4 text-yellow-300">
        ${heroic.name}
      </h1>
      <span class="inline-block bg-red-600 text-white px-4 py-2 rounded-full font-bold mb-4">
        ${heroic.difficulty.toUpperCase()} LEVEL
      </span>
      <p class="text-xl text-gray-200">
        📍 ${heroic.planet} - Nightsister Stronghold
      </p>
    </div>
  </div>

  <!-- Navigation -->
  <nav class="bg-gray-800 rounded-lg p-4 mb-8 sticky top-4 z-40">
    <div class="flex flex-wrap justify-center gap-4">
      <a href="#overview" class="nav-link px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-yellow-300 hover:text-gray-800 transition-all">
        ℹ️ Overview
      </a>
      <a href="#requirements" class="nav-link px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-yellow-300 hover:text-gray-800 transition-all">
        ✅ Requirements
      </a>
      <a href="#encounters" class="nav-link px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-yellow-300 hover:text-gray-800 transition-all">
        ⚔️ Boss Encounters
      </a>
      <a href="#loot" class="nav-link px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-yellow-300 hover:text-gray-800 transition-all">
        🏆 Loot Tables
      </a>
      <a href="#strategy" class="nav-link px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-yellow-300 hover:text-gray-800 transition-all">
        🎯 Strategy Guide
      </a>
    </div>
  </nav>

  <!-- Overview Section -->
  <section id="overview" class="mb-12">
    <h2 class="text-3xl font-bold mb-6 text-white border-b border-gray-600 pb-2">
      📜 Overview
    </h2>
    <div class="bg-gray-800 rounded-lg p-6">
      <p class="text-lg text-gray-300 leading-relaxed mb-6">
        ${heroic.description} This expert-level encounter demands perfect coordination, advanced tactics, and the strongest warriors the galaxy has to offer.
      </p>
      
      <h3 class="text-xl font-semibold text-yellow-300 mb-4">
        📖 Lore & Background
      </h3>
      <p class="text-gray-300 leading-relaxed">
        Once a promising Jedi Knight, Axkva Min fell to the dark side during the Clone Wars. Seduced by Nightsister magic and dark Force techniques, she became one of the most feared beings on Dathomir. Her stronghold is a testament to her power, filled with dark energy and guarded by loyal servants who share her corruption.
      </p>
    </div>
  </section>

  <!-- Requirements Section -->
  <section id="requirements" class="mb-12">
    <h2 class="text-3xl font-bold mb-6 text-white border-b border-gray-600 pb-2">
      ✅ Entry Requirements
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-gray-800 rounded-lg p-6">
        <h4 class="text-xl font-semibold text-yellow-300 mb-4">
          📈 Character Level
        </h4>
        <ul class="space-y-2">
          <li class="flex items-center text-gray-300">
            ✅ Minimum Level ${heroic.minLevel}
          </li>
          <li class="flex items-center text-gray-300">
            ✅ Recommended Level 85+
          </li>
          <li class="flex items-center text-gray-300">
            ✅ Elite combat skills
          </li>
        </ul>
      </div>

      <div class="bg-gray-800 rounded-lg p-6">
        <h4 class="text-xl font-semibold text-yellow-300 mb-4">
          👥 Group Composition
        </h4>
        <ul class="space-y-2">
          <li class="flex items-center text-gray-300">
            ✅ ${heroic.groupSize}
          </li>
          <li class="flex items-center text-gray-300">
            ✅ 1 Primary Tank
          </li>
          <li class="flex items-center text-gray-300">
            ✅ 2 Dedicated Healers
          </li>
          <li class="flex items-center text-gray-300">
            ✅ 4-5 DPS Characters
          </li>
        </ul>
      </div>
    </div>
  </section>

  <!-- Boss Encounters Section -->
  <section id="encounters" class="mb-12">
    <h2 class="text-3xl font-bold mb-6 text-white border-b border-gray-600 pb-2">
      ⚔️ Boss Encounters
    </h2>

    <!-- Sister Vex'aria -->
    <div class="bg-gray-800 rounded-lg p-6 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
        <h3 class="text-2xl font-bold text-yellow-300">
          🥷 Sister Vex'aria
        </h3>
        <span class="bg-orange-600 text-white px-3 py-1 rounded-full font-bold text-sm mt-2 md:mt-0">
          MINI BOSS
        </span>
      </div>
      
      <p class="text-gray-300 mb-4"><strong>Health:</strong> 850,000 HP</p>
      
      <h4 class="text-xl font-semibold text-white mb-3">
        ⚙️ Key Mechanics
      </h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        ${heroic.mechanics.map(mechanic => `
          <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-purple-500">
            <strong class="text-purple-300">${mechanic}</strong>
            <p class="text-gray-300 text-sm mt-1">Advanced ${mechanic.toLowerCase()} abilities</p>
          </div>
        `).join('')}
      </div>

      <div class="bg-green-900 rounded-lg p-4 border-l-4 border-green-400">
        <h5 class="text-green-300 font-semibold mb-2">
          💡 Strategy Tips
        </h5>
        <p class="text-gray-300 text-sm">Interrupt healing at all costs. When a player is mind controlled, others must disable the affected player temporarily. Stack together during Force Lightning to minimize chain damage and share healing.</p>
      </div>
    </div>

    <!-- Axkva Min Final Boss -->
    <div class="bg-gray-800 rounded-lg p-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
        <h3 class="text-2xl font-bold text-yellow-300">
          👹 Axkva Min
        </h3>
        <span class="bg-red-600 text-white px-3 py-1 rounded-full font-bold text-sm mt-2 md:mt-0">
          FINAL BOSS
        </span>
      </div>
      
      <p class="text-gray-300 mb-6"><strong>Health:</strong> 2,500,000 HP</p>

      <!-- Phase Information -->
      <div class="space-y-4">
        <div class="bg-gray-700 rounded-lg p-4">
          <h4 class="text-lg font-semibold text-purple-300 mb-2">Phase 1: Corruption (100% - 70%)</h4>
          <p class="text-gray-300 text-sm">Corrupt Aura deals constant damage. Maintain maximum range and coordinate healing rotations.</p>
        </div>
        
        <div class="bg-gray-700 rounded-lg p-4">
          <h4 class="text-lg font-semibold text-purple-300 mb-2">Phase 2: Nightsister Army (70% - 40%)</h4>
          <p class="text-gray-300 text-sm">Elite adds spawn. Focus fire adds immediately and spread out for Force Storm.</p>
        </div>
        
        <div class="bg-gray-700 rounded-lg p-4">
          <h4 class="text-lg font-semibold text-purple-300 mb-2">Phase 3: Final Corruption (40% - 0%)</h4>
          <p class="text-gray-300 text-sm">Full burn phase with enhanced abilities. Use all consumables and avoid Reality Tear zones.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Loot Tables Section -->
  <section id="loot" class="mb-12">
    <h2 class="text-3xl font-bold mb-6 text-white border-b border-gray-600 pb-2">
      🏆 Loot Tables & Drop Rates
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      ${heroic.loot.map((item, index) => `
        <div class="bg-gradient-to-br from-yellow-800 to-orange-800 rounded-lg p-4 flex items-center">
          <div class="bg-yellow-500 rounded-lg p-3 mr-4">
            <span class="text-2xl">🎯</span>
          </div>
          <div>
            <h4 class="font-bold text-white">${item}</h4>
            <p class="text-yellow-200 font-semibold">Drop Rate: ${index === 0 ? '5%' : index === 1 ? '15%' : '25%'} (${index === 0 ? 'Legendary' : index === 1 ? 'Epic' : 'Rare'})</p>
          </div>
        </div>
      `).join('')}
    </div>
  </section>

  <!-- Strategy Guide Section -->
  <section id="strategy" class="mb-12">
    <h2 class="text-3xl font-bold mb-6 text-white border-b border-gray-600 pb-2">
      🎯 Advanced Strategy Guide
    </h2>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-blue-900 rounded-lg p-6">
        <h4 class="text-xl font-semibold text-blue-300 mb-4">
          🧪 Preparation
        </h4>
        <ul class="space-y-2">
          <li class="text-gray-300">✅ Bring maximum stims and healing items</li>
          <li class="text-gray-300">✅ Coordinate Force powers if using Jedi</li>
          <li class="text-gray-300">✅ Assign specific roles before entering</li>
          <li class="text-gray-300">✅ Practice target switching and positioning</li>
        </ul>
      </div>

      <div class="bg-green-900 rounded-lg p-6">
        <h4 class="text-xl font-semibold text-green-300 mb-4">
          👥 Team Composition
        </h4>
        <ul class="space-y-2">
          <li class="text-gray-300">✅ 1 Tank (Jedi Guardian or BH Tank spec)</li>
          <li class="text-gray-300">✅ 2 Healers (Combat Medic or Jedi Healer)</li>
          <li class="text-gray-300">✅ 4-5 DPS (mixed ranged/melee)</li>
          <li class="text-gray-300">✅ 1 Dedicated Interrupter</li>
        </ul>
      </div>

      <div class="bg-yellow-900 rounded-lg p-6">
        <h4 class="text-xl font-semibold text-yellow-300 mb-4">
          💡 Pro Tips
        </h4>
        <ul class="space-y-2">
          <li class="text-gray-300">✅ Communication is absolutely critical</li>
          <li class="text-gray-300">✅ Save special abilities for Phase 3</li>
          <li class="text-gray-300">✅ Never fight alone - coordinate movements</li>
          <li class="text-gray-300">✅ Practice escape routes for emergencies</li>
        </ul>
      </div>

      <div class="bg-purple-900 rounded-lg p-6">
        <h4 class="text-xl font-semibold text-purple-300 mb-4">
          📍 Location Info
        </h4>
        <ul class="space-y-2">
          <li class="text-gray-300">✅ Waypoint: /way dathomir -4086 -1653</li>
          <li class="text-gray-300">✅ Access: Researcher Kem'va at Research Outpost</li>
          <li class="text-gray-300">✅ Travel Time: 15 minutes from starport</li>
          <li class="text-gray-300">✅ Bring speeder or mount for travel</li>
        </ul>
      </div>
    </div>
  </section>
</section>

<script>
// Smooth scrolling for navigation links
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});
</script>
    `;
  }
};