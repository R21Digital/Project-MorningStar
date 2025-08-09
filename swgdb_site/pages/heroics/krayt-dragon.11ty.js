module.exports = class {
  data() {
    return {
      title: "Ancient Krayt Dragon Heroic Guide - SWGDB",
      description: "Complete strategy guide for the Ancient Krayt Dragon raid encounter on Tatooine including boss mechanics, loot tables, and raid compositions for Star Wars Galaxies Restoration",
      layout: "base.njk",
      permalink: "/pages/heroics/krayt-dragon/"
    };
  }

  render(data) {
    return `
<section class="py-12 px-6 max-w-6xl mx-auto text-white">
    <!-- Back Link -->
    <a href="/pages/heroics/" class="inline-flex items-center text-yellow-300 hover:text-white mb-6 font-semibold">
        <i class="fas fa-arrow-left mr-2"></i>Back to Heroics
    </a>

    <!-- Hero Section -->
    <div class="bg-gradient-to-r from-orange-900 to-red-900 rounded-lg p-8 mb-8 text-center relative overflow-hidden">
        <div class="absolute inset-0 bg-black bg-opacity-20"></div>
        <div class="relative z-10">
            <h1 class="text-5xl font-bold mb-4 text-yellow-300">
                <i class="fas fa-dragon mr-3"></i>Ancient Krayt Dragon
            </h1>
            <span class="inline-block bg-red-600 text-white px-4 py-2 rounded-full font-bold mb-4">
                EXPERT LEVEL
            </span>
            <p class="text-xl text-gray-200">
                <i class="fas fa-map-marker-alt mr-2"></i>Tatooine - Dune Sea
            </p>
        </div>
    </div>

    <!-- Navigation -->
    <nav class="bg-gray-800 rounded-lg p-4 mb-8 sticky top-20 z-40">
        <div class="flex flex-wrap justify-center gap-4">
            <a href="#overview" class="nav-link px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-yellow-300 hover:text-gray-800 transition-all">
                <i class="fas fa-info-circle mr-2"></i>Overview
            </a>
            <a href="#requirements" class="nav-link px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-yellow-300 hover:text-gray-800 transition-all">
                <i class="fas fa-clipboard-check mr-2"></i>Requirements
            </a>
            <a href="#encounters" class="nav-link px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-yellow-300 hover:text-gray-800 transition-all">
                <i class="fas fa-sword mr-2"></i>Boss Encounters
            </a>
            <a href="#loot" class="nav-link px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-yellow-300 hover:text-gray-800 transition-all">
                <i class="fas fa-treasure-chest mr-2"></i>Loot Tables
            </a>
            <a href="#strategy" class="nav-link px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-yellow-300 hover:text-gray-800 transition-all">
                <i class="fas fa-chess mr-2"></i>Strategy Guide
            </a>
        </div>
    </nav>

    <!-- Overview Section -->
    <section id="overview" class="mb-12">
        <h2 class="text-3xl font-bold mb-6 text-white border-b border-gray-600 pb-2">
            <i class="fas fa-scroll mr-3"></i>Overview
        </h2>
        <div class="bg-gray-800 rounded-lg p-6">
            <p class="text-lg text-gray-300 leading-relaxed mb-6">
                The legendary Ancient Krayt Dragon is one of the most formidable creatures in the galaxy. Dwelling in the vast Dune Sea of Tatooine, this massive beast has terrorized travelers for millennia. Only the most skilled and coordinated raid groups can hope to defeat this apex predator.
            </p>
            
            <h3 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                <i class="fas fa-book mr-2"></i>Lore & Background
            </h3>
            <p class="text-gray-300 leading-relaxed">
                Ancient Krayt Dragons are the apex predators of Tatooine's desert ecosystem. These massive reptilian beasts can live for thousands of years, growing to enormous sizes. The pearl found within their gizzards is one of the most valuable materials in the galaxy, prized for its use in lightsaber construction and high-end technology.
            </p>
        </div>
    </section>

    <!-- Requirements Section -->
    <section id="requirements" class="mb-12">
        <h2 class="text-3xl font-bold mb-6 text-white border-b border-gray-600 pb-2">
            <i class="fas fa-clipboard-check mr-3"></i>Entry Requirements
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-gray-800 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-level-up-alt mr-2"></i>Character Level
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Minimum Level 80
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Recommended Level 85+
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Master combat skills required
                    </li>
                </ul>
            </div>

            <div class="bg-gray-800 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-users mr-2"></i>Raid Composition
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>8-12 Player Raid Group
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>2-3 Primary Tanks
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>3-4 Dedicated Healers
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>6-8 DPS Characters
                    </li>
                </ul>
            </div>

            <div class="bg-gray-800 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-key mr-2"></i>Prerequisites
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Tatooine Faction Standing
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Desert Survival Skills
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Advanced Equipment
                    </li>
                </ul>
            </div>

            <div class="bg-gray-800 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-graduation-cap mr-2"></i>Recommended Professions
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Bounty Hunter (Tank/DPS)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Commando (Heavy DPS)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Combat Medic (Healing)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Rifleman (Ranged DPS)
                    </li>
                </ul>
            </div>
        </div>
    </section>

    <!-- Boss Encounters Section -->
    <section id="encounters" class="mb-12">
        <h2 class="text-3xl font-bold mb-6 text-white border-b border-gray-600 pb-2">
            <i class="fas fa-sword mr-3"></i>Boss Encounters
        </h2>

        <!-- Canyon Krayt ---->
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <h3 class="text-2xl font-bold text-yellow-300 flex items-center">
                    <i class="fas fa-mountain mr-2"></i>Canyon Krayt
                </h3>
                <span class="bg-orange-600 text-white px-3 py-1 rounded-full font-bold text-sm mt-2 md:mt-0">
                    MINI BOSS
                </span>
            </div>
            
            <p class="text-gray-300 mb-4"><strong>Health:</strong> 1,200,000 HP</p>
            
            <h4 class="text-xl font-semibold text-white mb-3 flex items-center">
                <i class="fas fa-cogs mr-2"></i>Abilities & Mechanics
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-orange-500">
                    <strong class="text-orange-300">Rock Throw</strong>
                    <p class="text-gray-300 text-sm mt-1">Massive ranged damage to random target</p>
                </div>
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-orange-500">
                    <strong class="text-orange-300">Cave-In Attack</strong>
                    <p class="text-gray-300 text-sm mt-1">AoE damage in large circle</p>
                </div>
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-orange-500">
                    <strong class="text-orange-300">Territorial Rage</strong>
                    <p class="text-gray-300 text-sm mt-1">Damage and speed increase over time</p>
                </div>
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-orange-500">
                    <strong class="text-orange-300">Burrow Escape</strong>
                    <p class="text-gray-300 text-sm mt-1">Disappears underground temporarily</p>
                </div>
            </div>

            <div class="bg-green-900 rounded-lg p-4 border-l-4 border-green-400">
                <h5 class="text-green-300 font-semibold flex items-center mb-2">
                    <i class="fas fa-lightbulb mr-2"></i>Strategy Tips
                </h5>
                <p class="text-gray-300 text-sm">Watch for the Cave-In indicators and move quickly. When it burrows, spread out to avoid the surprise attack. Keep ranged DPS at maximum distance.</p>
            </div>
        </div>

        <!-- Ancient Krayt Dragon Final Boss -->
        <div class="bg-gray-800 rounded-lg p-6">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <h3 class="text-2xl font-bold text-yellow-300 flex items-center">
                    <i class="fas fa-dragon mr-2"></i>Ancient Krayt Dragon
                </h3>
                <span class="bg-red-600 text-white px-3 py-1 rounded-full font-bold text-sm mt-2 md:mt-0">
                    RAID BOSS
                </span>
            </div>
            
            <p class="text-gray-300 mb-6"><strong>Health:</strong> 5,000,000 HP</p>

            <!-- Phase 1 -->
            <div class="bg-gray-700 rounded-lg p-4 mb-4">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                    <h4 class="text-lg font-semibold text-orange-300">Phase 1: Awakening</h4>
                    <span class="bg-green-600 text-white px-2 py-1 rounded text-sm font-semibold">100% - 75%</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Tail Sweep</strong>
                        <p class="text-gray-300 text-sm">180-degree rear attack</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Sonic Roar</strong>
                        <p class="text-gray-300 text-sm">Stuns all players for 3 seconds</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Bite Attack</strong>
                        <p class="text-gray-300 text-sm">Massive single-target damage</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Ground Pound</strong>
                        <p class="text-gray-300 text-sm">AoE knockdown around dragon</p>
                    </div>
                </div>
                <div class="bg-green-800 rounded p-3">
                    <p class="text-green-200 text-sm"><strong>Strategy:</strong> Tanks position at head, DPS spread to sides. Healers stay at maximum range. Watch for tail sweep warnings.</p>
                </div>
            </div>

            <!-- Phase 2 -->
            <div class="bg-gray-700 rounded-lg p-4 mb-4">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                    <h4 class="text-lg font-semibold text-orange-300">Phase 2: Rage Mode</h4>
                    <span class="bg-yellow-600 text-white px-2 py-1 rounded text-sm font-semibold">75% - 40%</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Burrow Attack</strong>
                        <p class="text-gray-300 text-sm">Disappears and strikes from below</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Sand Storm</strong>
                        <p class="text-gray-300 text-sm">Arena-wide damage over time</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Young Krayt Summon</strong>
                        <p class="text-gray-300 text-sm">2-3 adds spawn every 60 seconds</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Acid Spit</strong>
                        <p class="text-gray-300 text-sm">DoT debuff on random players</p>
                    </div>
                </div>
                <div class="bg-green-800 rounded p-3">
                    <p class="text-green-200 text-sm"><strong>Strategy:</strong> Kill adds immediately. Use terrain to break line of sight during burrow attacks. Keep moving during sand storms.</p>
                </div>
            </div>

            <!-- Phase 3 -->
            <div class="bg-gray-700 rounded-lg p-4">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                    <h4 class="text-lg font-semibold text-orange-300">Phase 3: Ancient Fury</h4>
                    <span class="bg-red-600 text-white px-2 py-1 rounded text-sm font-semibold">40% - 0%</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Enrage</strong>
                        <p class="text-gray-300 text-sm">All abilities enhanced, faster attacks</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Death Roll</strong>
                        <p class="text-gray-300 text-sm">Instant kill if caught in roll</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Primal Scream</strong>
                        <p class="text-gray-300 text-sm">Fear effect, forces movement</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Final Burrow</strong>
                        <p class="text-gray-300 text-sm">Multiple emergence points</p>
                    </div>
                </div>
                <div class="bg-green-800 rounded p-3">
                    <p class="text-green-200 text-sm"><strong>Strategy:</strong> Burn phase - use all cooldowns. Stay mobile and avoid the death roll at all costs. Coordinate positioning for final burrow.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Loot Tables Section -->
    <section id="loot" class="mb-12">
        <h2 class="text-3xl font-bold mb-6 text-white border-b border-gray-600 pb-2">
            <i class="fas fa-treasure-chest mr-3"></i>Loot Tables & Drop Rates
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div class="bg-gradient-to-br from-yellow-800 to-orange-800 rounded-lg p-4 flex items-center">
                <div class="bg-yellow-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-gem text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Perfect Krayt Dragon Pearl</h4>
                    <p class="text-yellow-200 font-semibold">Drop Rate: 3% (Legendary)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-purple-800 to-indigo-800 rounded-lg p-4 flex items-center">
                <div class="bg-purple-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-shield-alt text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Dragon Bone Armor</h4>
                    <p class="text-purple-200 font-semibold">Drop Rate: 8% (Legendary)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-red-800 to-pink-800 rounded-lg p-4 flex items-center">
                <div class="bg-red-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-fire text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Ancient Dragon Scales</h4>
                    <p class="text-red-200 font-semibold">Drop Rate: 15% (Epic)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-blue-800 to-cyan-800 rounded-lg p-4 flex items-center">
                <div class="bg-blue-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-dna text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Krayt Dragon Tissue</h4>
                    <p class="text-blue-200 font-semibold">Drop Rate: 25% (Epic)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-green-800 to-teal-800 rounded-lg p-4 flex items-center">
                <div class="bg-green-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-tooth text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Dragon Fang Weapon Parts</h4>
                    <p class="text-green-200 font-semibold">Drop Rate: 40% (Rare)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg p-4 flex items-center">
                <div class="bg-gray-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-heart text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Dragon Blood Crystals</h4>
                    <p class="text-gray-200 font-semibold">Drop Rate: 60% (Uncommon)</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Strategy Guide Section -->
    <section id="strategy" class="mb-12">
        <h2 class="text-3xl font-bold mb-6 text-white border-b border-gray-600 pb-2">
            <i class="fas fa-chess mr-3"></i>Advanced Strategy Guide
        </h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-blue-900 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-blue-300 mb-4 flex items-center">
                    <i class="fas fa-flask mr-2"></i>Preparation
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Maximum stims and combat supplies
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Environmental protection gear
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Coordinate raid composition beforehand
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Establish clear communication channels
                    </li>
                </ul>
            </div>

            <div class="bg-green-900 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-green-300 mb-4 flex items-center">
                    <i class="fas fa-users mr-2"></i>Raid Composition
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>2-3 Tanks (BH Tank or Defensive builds)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>3-4 Healers (Combat Medic priority)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>6-8 DPS (mix of ranged and melee)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Dedicated add control specialists
                    </li>
                </ul>
            </div>

            <div class="bg-yellow-900 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-lightbulb mr-2"></i>Pro Tips
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Learn the burrow attack patterns
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Always prioritize add control in Phase 2
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Save heroics and specials for Phase 3
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Never stand still during sand storms
                    </li>
                </ul>
            </div>

            <div class="bg-purple-900 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-purple-300 mb-4 flex items-center">
                    <i class="fas fa-map-marker-alt mr-2"></i>Location Info
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Waypoint: /way tatooine 7307 4474
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Access: Deep Dune Sea expedition
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Travel Time: 25 minutes from Mos Eisley
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Bring speeders - long travel required
                    </li>
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