module.exports = class {
  data() {
    return {
      title: "IG-88 Assassination Heroic Guide - SWGDB",
      description: "Complete strategy guide for the IG-88 assassination mission on Tatooine including droid mechanics, loot tables, and group tactics for Star Wars Galaxies Restoration",
      layout: "base.njk",
      permalink: "/pages/heroics/ig-88/"
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
    <div class="bg-gradient-to-r from-gray-900 to-blue-900 rounded-lg p-8 mb-8 text-center relative overflow-hidden">
        <div class="absolute inset-0 bg-black bg-opacity-20"></div>
        <div class="relative z-10">
            <h1 class="text-5xl font-bold mb-4 text-yellow-300">
                <i class="fas fa-robot mr-3"></i>IG-88 Assassination
            </h1>
            <span class="inline-block bg-red-500 text-white px-4 py-2 rounded-full font-bold mb-4">
                HARD LEVEL
            </span>
            <p class="text-xl text-gray-200">
                <i class="fas fa-map-marker-alt mr-2"></i>Tatooine - Hidden Compound
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
                The notorious assassin droid IG-88 has established a heavily fortified compound on Tatooine. Known for its precision, advanced weaponry, and cold mechanical intelligence, this bounty hunter represents one of the most dangerous mechanical threats in the galaxy.
            </p>
            
            <h3 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                <i class="fas fa-book mr-2"></i>Mission Background
            </h3>
            <p class="text-gray-300 leading-relaxed">
                IG-88 is one of the most feared bounty hunters in the galaxy, a sophisticated assassin droid with advanced combat protocols and state-of-the-art weaponry. Its compound is filled with security systems, automated defenses, and loyal droid allies. Eliminating this threat requires tactical precision and superior firepower.
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
                        <i class="fas fa-check text-green-400 mr-2"></i>Minimum Level 70
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Recommended Level 75+
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Advanced combat skills
                    </li>
                </ul>
            </div>

            <div class="bg-gray-800 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-users mr-2"></i>Group Composition
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>4-6 Player Group
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>1 Tank Specialist
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>1-2 Healers
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>3-4 DPS Characters
                    </li>
                </ul>
            </div>

            <div class="bg-gray-800 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-key mr-2"></i>Prerequisites
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Bounty Hunter License
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Tech Specialist Skills
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Ion Resistance Gear
                    </li>
                </ul>
            </div>

            <div class="bg-gray-800 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-graduation-cap mr-2"></i>Recommended Professions
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Bounty Hunter
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Commando
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Combat Medic
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Smuggler (Tech Specialist)
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

        <!-- Security Protocol Droids -->
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <h3 class="text-2xl font-bold text-yellow-300 flex items-center">
                    <i class="fas fa-shield-alt mr-2"></i>Security Protocol Droids
                </h3>
                <span class="bg-orange-600 text-white px-3 py-1 rounded-full font-bold text-sm mt-2 md:mt-0">
                    ELITE GUARDS
                </span>
            </div>
            
            <p class="text-gray-300 mb-4"><strong>Health:</strong> 400,000 HP (each)</p>
            
            <h4 class="text-xl font-semibold text-white mb-3 flex items-center">
                <i class="fas fa-cogs mr-2"></i>Abilities & Mechanics
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500">
                    <strong class="text-blue-300">Shield Generator</strong>
                    <p class="text-gray-300 text-sm mt-1">Damage reduction field for nearby allies</p>
                </div>
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500">
                    <strong class="text-blue-300">Self-Destruct Protocol</strong>
                    <p class="text-gray-300 text-sm mt-1">Large AoE explosion when destroyed</p>
                </div>
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500">
                    <strong class="text-blue-300">Ion Burst</strong>
                    <p class="text-gray-300 text-sm mt-1">Disables player abilities temporarily</p>
                </div>
                <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500">
                    <strong class="text-blue-300">Coordinated Strike</strong>
                    <p class="text-gray-300 text-sm mt-1">Synchronized attacks with other droids</p>
                </div>
            </div>

            <div class="bg-green-900 rounded-lg p-4 border-l-4 border-green-400">
                <h5 class="text-green-300 font-semibold flex items-center mb-2">
                    <i class="fas fa-lightbulb mr-2"></i>Strategy Tips
                </h5>
                <p class="text-gray-300 text-sm">Target shield generators first. When a droid reaches low health, move away quickly to avoid self-destruct damage. Use ion resistance stims.</p>
            </div>
        </div>

        <!-- IG-88 Final Boss -->
        <div class="bg-gray-800 rounded-lg p-6">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <h3 class="text-2xl font-bold text-yellow-300 flex items-center">
                    <i class="fas fa-robot mr-2"></i>IG-88
                </h3>
                <span class="bg-red-600 text-white px-3 py-1 rounded-full font-bold text-sm mt-2 md:mt-0">
                    ASSASSINATION TARGET
                </span>
            </div>
            
            <p class="text-gray-300 mb-6"><strong>Health:</strong> 1,800,000 HP</p>

            <!-- Phase 1 -->
            <div class="bg-gray-700 rounded-lg p-4 mb-4">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                    <h4 class="text-lg font-semibold text-blue-300">Phase 1: Combat Protocols</h4>
                    <span class="bg-green-600 text-white px-2 py-1 rounded text-sm font-semibold">100% - 60%</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Precision Targeting</strong>
                        <p class="text-gray-300 text-sm">Increased accuracy and critical hits</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Blaster Volley</strong>
                        <p class="text-gray-300 text-sm">Multiple shots at different targets</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Thermal Detonator</strong>
                        <p class="text-gray-300 text-sm">Thrown explosive with large radius</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Combat Analysis</strong>
                        <p class="text-gray-300 text-sm">Adapts to player tactics over time</p>
                    </div>
                </div>
                <div class="bg-green-800 rounded p-3">
                    <p class="text-green-200 text-sm"><strong>Strategy:</strong> Keep mobile to avoid precision shots. Spread out to minimize thermal detonator damage. Focus consistent damage output.</p>
                </div>
            </div>

            <!-- Phase 2 -->
            <div class="bg-gray-700 rounded-lg p-4 mb-4">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                    <h4 class="text-lg font-semibold text-blue-300">Phase 2: Advanced Systems</h4>
                    <span class="bg-yellow-600 text-white px-2 py-1 rounded text-sm font-semibold">60% - 30%</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Stealth Mode</strong>
                        <p class="text-gray-300 text-sm">Becomes invisible for 10 seconds</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Assassin Droids</strong>
                        <p class="text-gray-300 text-sm">Summons 2 smaller assassin units</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Ion Cannon</strong>
                        <p class="text-gray-300 text-sm">Massive energy beam attack</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">System Override</strong>
                        <p class="text-gray-300 text-sm">Hacks player equipment temporarily</p>
                    </div>
                </div>
                <div class="bg-green-800 rounded p-3">
                    <p class="text-green-200 text-sm"><strong>Strategy:</strong> Use area attacks to damage cloaked IG-88. Kill assassin droids quickly. Watch for ion cannon charge-up indicators.</p>
                </div>
            </div>

            <!-- Phase 3 -->
            <div class="bg-gray-700 rounded-lg p-4">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                    <h4 class="text-lg font-semibold text-blue-300">Phase 3: Self-Preservation</h4>
                    <span class="bg-red-600 text-white px-2 py-1 rounded text-sm font-semibold">30% - 0%</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Emergency Protocols</strong>
                        <p class="text-gray-300 text-sm">All abilities enhanced and faster</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Compound Lockdown</strong>
                        <p class="text-gray-300 text-sm">Activates all security systems</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Final Gambit</strong>
                        <p class="text-gray-300 text-sm">Massive self-destruct if not killed quickly</p>
                    </div>
                    <div class="bg-gray-600 rounded p-3">
                        <strong class="text-red-300">Escape Attempt</strong>
                        <p class="text-gray-300 text-sm">Tries to flee at very low health</p>
                    </div>
                </div>
                <div class="bg-green-800 rounded p-3">
                    <p class="text-green-200 text-sm"><strong>Strategy:</strong> Maximum DPS burn phase. Don't let it escape - use stuns and slows. If self-destruct begins, either finish it quickly or evacuate.</p>
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
                    <i class="fas fa-crosshairs text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">IG-88's Custom Rifle</h4>
                    <p class="text-yellow-200 font-semibold">Drop Rate: 8% (Legendary)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-purple-800 to-indigo-800 rounded-lg p-4 flex items-center">
                <div class="bg-purple-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-microchip text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Advanced Droid Components</h4>
                    <p class="text-purple-200 font-semibold">Drop Rate: 15% (Epic)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-red-800 to-pink-800 rounded-lg p-4 flex items-center">
                <div class="bg-red-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-eye text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Precision Targeting Computer</h4>
                    <p class="text-red-200 font-semibold">Drop Rate: 20% (Epic)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-blue-800 to-cyan-800 rounded-lg p-4 flex items-center">
                <div class="bg-blue-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-vest text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Bounty Hunter Equipment</h4>
                    <p class="text-blue-200 font-semibold">Drop Rate: 30% (Rare)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-green-800 to-teal-800 rounded-lg p-4 flex items-center">
                <div class="bg-green-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-bolt text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Ion Weapon Modifications</h4>
                    <p class="text-green-200 font-semibold">Drop Rate: 45% (Rare)</p>
                </div>
            </div>

            <div class="bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg p-4 flex items-center">
                <div class="bg-gray-500 rounded-lg p-3 mr-4">
                    <i class="fas fa-cog text-2xl text-white"></i>
                </div>
                <div>
                    <h4 class="font-bold text-white">Droid Repair Kits</h4>
                    <p class="text-gray-200 font-semibold">Drop Rate: 70% (Common)</p>
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
                        <i class="fas fa-check text-green-400 mr-2"></i>Ion resistance stims and gear
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Tech specialist equipment
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>EMP grenades and ion weapons
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Coordinate timing for stealth phases
                    </li>
                </ul>
            </div>

            <div class="bg-green-900 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-green-300 mb-4 flex items-center">
                    <i class="fas fa-users mr-2"></i>Team Composition
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>1 Tech-spec Tank (BH preferred)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>1-2 Combat Medics
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>2-3 Ranged DPS (Commando/Rifleman)
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>1 Droid specialist (optional)
                    </li>
                </ul>
            </div>

            <div class="bg-yellow-900 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
                    <i class="fas fa-lightbulb mr-2"></i>Pro Tips
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Use terrain to break line of sight
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Prioritize add control in Phase 2
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Save interrupts for final gambit
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Never let IG-88 escape in Phase 3
                    </li>
                </ul>
            </div>

            <div class="bg-purple-900 rounded-lg p-6">
                <h4 class="text-xl font-semibold text-purple-300 mb-4 flex items-center">
                    <i class="fas fa-map-marker-alt mr-2"></i>Location Info
                </h4>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Waypoint: /way tatooine 1473 -7234
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Access: Hidden bounty hunter compound
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Travel Time: 12 minutes from Mos Eisley
                    </li>
                    <li class="flex items-center text-gray-300">
                        <i class="fas fa-check text-green-400 mr-2"></i>Requires bounty hunter terminal access
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