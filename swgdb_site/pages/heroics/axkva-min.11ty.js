module.exports = class {
  data() {
    return {
      title: "Axkva Min Heroic Guide - SWGDB",
      description: "Complete strategy guide for the Axkva Min heroic encounter on Dathomir including boss mechanics, loot tables, and group compositions for Star Wars Galaxies Restoration",
      layout: "base.njk",
      permalink: "/pages/heroics/axkva-min/"
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
    <div class="bg-gradient-to-r from-purple-900 to-indigo-900 rounded-lg p-8 mb-8 text-center relative overflow-hidden">
        <div class="absolute inset-0 bg-black bg-opacity-20"></div>
        <div class="relative z-10">
            <h1 class="text-5xl font-bold mb-4 text-yellow-300">
                <i class="fas fa-mask mr-3"></i>Axkva Min
            </h1>
            <span class="inline-block bg-red-600 text-white px-4 py-2 rounded-full font-bold mb-4">
                EXPERT LEVEL
            </span>
            <p class="text-xl text-gray-200">
                <i class="fas fa-map-marker-alt mr-2"></i>Dathomir - Nightsister Stronghold
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
                The most challenging Nightsister encounter in the galaxy. Face the fallen Jedi Axkva Min in her dark domain, where corruption runs deep and the Force itself seems twisted. This encounter demands perfect coordination, advanced tactics, and the strongest warriors the galaxy has to offer.
            </p>
            
            <h3 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                <i class="fas fa-book mr-2"></i>Lore & Background
            </h3>
            <p class="text-gray-300 leading-relaxed">
                Once a promising Jedi Knight, Axkva Min fell to the dark side during the Clone Wars. Seduced by Nightsister magic and dark Force techniques, she became one of the most feared beings on Dathomir. Her stronghold is a testament to her power, filled with dark energy and guarded by loyal servants who share her corruption.
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
                        <i class="fas fa-check text-green-400 mr-2"></i>Elite combat skills
                    </li>
                </ul>
            </div>

            <div class="bg-gray-800 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-users mr-2"></i>Group Composition
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>5-8 Player Group
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>1 Primary Tank
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>2 Dedicated Healers
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>4-5 DPS Characters
                    </li>
                </ul>
            </div>

            <div class="bg-gray-800 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-key mr-2"></i>Prerequisites
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Mustafar Access
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Death Watch Bunker Complete
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Force Sensitive (Recommended)
                    </li>
                </ul>
            </div>

            <div class="bg-gray-800 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-graduation-cap mr-2"></i>Recommended Professions
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Jedi (Tank/DPS)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Bounty Hunter
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Commando
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Combat Medic
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

        <!-- Sister Vex'aria -->
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <h3 class="text-2xl font-bold text-yellow-300 flex items-center">
                    <i class="fas fa-user-ninja mr-2"></i>Sister Vex'aria
                </h3>
                <span class="bg-orange-600 text-white px-3 py-1 rounded-full font-bold text-sm mt-2 md:mt-0">
                    MINI BOSS
                </span>
            </div>
            
            <p class="text-gray-300 mb-4"><strong>Health:</strong> 850,000 HP</p>
            
            <h4 class="text-xl font-semibold text-white mb-3 flex items-center">
                <i class="fas fa-cogs mr-2"></i>Abilities & Mechanics
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-purple-500">
                    <strong class="text-purple-300">Force Lightning Chains</strong>
                    <p class="text-gray-300 text-sm mt-1">Jumps between nearby players causing massive damage</p>
                </div>
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-purple-500">
                    <strong class="text-purple-300">Mind Control</strong>
                    <p class="text-gray-300 text-sm mt-1">Takes control of 1 player for 15 seconds</p>
                </div>
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-purple-500">
                    <strong class="text-purple-300">Barrier Shield</strong>
                    <p class="text-gray-300 text-sm mt-1">75% damage reduction for 30 seconds</p>
                </div>
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-purple-500">
                    <strong class="text-purple-300">Nightsister Healing</strong>
                    <p class="text-gray-300 text-sm mt-1">Regenerates 50k health every 45 seconds</p>
                </div>
            </div>

            <div class="bg-green-900 rounded-lg p-4 border-l-4 border-green-400">
                <h5 class="text-green-300 font-semibold flex items-center mb-2">
                    <i class="fas fa-lightbulb mr-2"></i>Strategy Tips
                </h5>
                <p class="text-gray-300 text-sm">Interrupt healing at all costs. When a player is mind controlled, others must disable the affected player temporarily. Stack together during Force Lightning to minimize chain damage and share healing.</p>
            </div>
        </div>

        <!-- Axkva Min Final Boss -->
        <div class="bg-gray-800 rounded-lg p-6">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <h3 class="text-2xl font-bold text-yellow-300 flex items-center">
                    <i class="fas fa-mask mr-2"></i>Axkva Min
                </h3>
                <span class="bg-red-600 text-white px-3 py-1 rounded-full font-bold text-sm mt-2 md:mt-0">
                    FINAL BOSS
                </span>
            </div>
            
            <p class="text-gray-300 mb-6"><strong>Health:</strong> 2,500,000 HP</p>

            <!-- Phase 1 -->
            <div class="bg-gray-700 rounded-lg p-4 mb-4">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                    <h4 class="text-lg font-semibold text-purple-300">Phase 1: Corruption</h4>
                    <span class="bg-green-600 text-white px-2 py-1 rounded text-sm font-semibold">100% - 70%</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Corrupt Aura</strong>
                        <p class="text-gray-300 text-sm">Deals 2000 damage per second to all players</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Dark Force Lightning</strong>
                        <p class="text-gray-300 text-sm">Massive damage to primary target</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Teleportation</strong>
                        <p class="text-gray-300 text-sm">Randomly moves around the room</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Mind Twist</strong>
                        <p class="text-gray-300 text-sm">Confuses player controls for 10 seconds</p>
                    </div>
                </div>
                <div class="bg-green-800 rounded p-3">
                    <p class="text-green-200 text-sm"><strong>Strategy:</strong> Maintain maximum range when possible. Healers must work overtime to counter corruption damage. Tank positioning is crucial due to teleportation mechanics.</p>
                </div>
            </div>

            <!-- Phase 2 -->
            <div class="bg-gray-700 rounded-lg p-4 mb-4">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                    <h4 class="text-lg font-semibold text-purple-300">Phase 2: Nightsister Army</h4>
                    <span class="bg-yellow-600 text-white px-2 py-1 rounded text-sm font-semibold">70% - 40%</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Summon Guards</strong>
                        <p class="text-gray-300 text-sm">4 elite Nightsister adds spawn</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Force Storm</strong>
                        <p class="text-gray-300 text-sm">Room-wide AoE every 30 seconds</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Life Drain</strong>
                        <p class="text-gray-300 text-sm">Steals health from nearest player</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Dark Resurrection</strong>
                        <p class="text-gray-300 text-sm">Revives fallen adds with 50% health</p>
                    </div>
                </div>
                <div class="bg-green-800 rounded p-3">
                    <p class="text-green-200 text-sm"><strong>Strategy:</strong> Focus fire adds immediately when they spawn. Spread out for Force Storm to minimize damage. Assign one dedicated DPS to interrupt resurrection attempts.</p>
                </div>
            </div>

            <!-- Phase 3 -->
            <div class="bg-gray-700 rounded-lg p-4">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                    <h4 class="text-lg font-semibold text-purple-300">Phase 3: Final Corruption</h4>
                    <span class="bg-red-600 text-white px-2 py-1 rounded text-sm font-semibold">40% - 0%</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Rage Mode</strong>
                        <p class="text-gray-300 text-sm">All abilities enhanced and faster</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Corruption Nova</strong>
                        <p class="text-gray-300 text-sm">Massive damage if not interrupted</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Death Mark</strong>
                        <p class="text-gray-300 text-sm">Marks one player for death in 20 seconds</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Reality Tear</strong>
                        <p class="text-gray-300 text-sm">Creates zones of instant death</p>
                    </div>
                </div>
                <div class="bg-green-800 rounded p-3">
                    <p class="text-green-200 text-sm"><strong>Strategy:</strong> Full burn phase - use all consumables and special abilities. Death Mark requires focused group healing. Avoid tear zones at all costs - they mean instant death.</p>
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
                    <i class="fas fa-sword text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Axkva Min's Lightsaber</h4>
                    <p class="text-yellow-200 font-semibold">Drop Rate: 5% (Legendary)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-purple-800 to-indigo-800 rounded-lg p-4 flex items-center">
                <div class="bg-purple-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-tshirt text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Fallen Jedi Robes</h4>
                    <p class="text-purple-200 font-semibold">Drop Rate: 15% (Epic)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-red-800 to-pink-800 rounded-lg p-4 flex items-center">
                <div class="bg-red-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-gem text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Corruption Crystal</h4>
                    <p class="text-red-200 font-semibold">Drop Rate: 25% (Epic)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-blue-800 to-cyan-800 rounded-lg p-4 flex items-center">
                <div class="bg-blue-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-book text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Nightsister Spell Tome</h4>
                    <p class="text-blue-200 font-semibold">Drop Rate: 35% (Rare)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-green-800 to-teal-800 rounded-lg p-4 flex items-center">
                <div class="bg-green-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-certificate text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Ancient Force Relic</h4>
                    <p class="text-green-200 font-semibold">Drop Rate: 45% (Rare)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg p-4 flex items-center">
                <div class="bg-gray-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-circle text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Dark Side Meditation Crystal</h4>
                    <p class="text-gray-200 font-semibold">Drop Rate: 75% (Uncommon)</p>
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
                        <i class="fas fa-check text-green-400 mr-2"></i>Bring maximum stims and healing items
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Coordinate Force powers if using Jedi
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Assign specific roles before entering
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Practice target switching and positioning
                    </li>
                </ul>
            </div>

            <div class="bg-green-900 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-green-300 mb-4 flex items-center">
                    <i class="fas fa-users mr-2"></i>Team Composition
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>1 Tank (Jedi Guardian or BH Tank spec)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>2 Healers (Combat Medic or Jedi Healer)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>4-5 DPS (mixed ranged/melee)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>1 Dedicated Interrupter
                    </li>
                </ul>
            </div>

            <div class="bg-yellow-900 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-lightbulb mr-2"></i>Pro Tips
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Communication is absolutely critical
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Save special abilities for Phase 3
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Never fight alone - coordinate movements
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Practice escape routes for emergencies
                    </li>
                </ul>
            </div>

            <div class="bg-purple-900 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-purple-300 mb-4 flex items-center">
                    <i class="fas fa-map-marker-alt mr-2"></i>Location Info
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Waypoint: /way dathomir -4086 -1653
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Access: Researcher Kem'va at Research Outpost
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Travel Time: 15 minutes from starport
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Bring speeder or mount for travel
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