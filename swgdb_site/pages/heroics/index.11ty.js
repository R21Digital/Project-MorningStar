module.exports = class {
  data() {
    return {
      title: "Heroics - SWGDB",
      description: "Complete heroic instances database for Star Wars Galaxies Restoration with boss strategies, loot tables, and group compositions",
      layout: "base.njk",
      permalink: "/pages/heroics/"
    };
  }

  render(data) {
    return `
<section class="py-12 px-6 max-w-6xl mx-auto text-white">
    <h1 class="text-4xl font-bold mb-6 text-center">
        <i class="fas fa-shield-alt mr-3"></i>Heroic Instances
    </h1>
    <p class="text-xl text-gray-300 text-center mb-8 max-w-3xl mx-auto">
        Complete database of heroic encounters with boss strategies, loot tables, and group compositions for Star Wars Galaxies Restoration
    </p>

    <!-- Filter Section -->
    <div class="bg-gray-800 rounded-lg p-6 mb-8">
        <h3 class="text-xl font-semibold mb-4 text-white">
            <i class="fas fa-filter mr-2"></i>Filter by Difficulty
        </h3>
        <div class="flex flex-wrap gap-3">
            <button class="filter-btn px-4 py-2 rounded-full border-2 border-yellow-300 text-yellow-300 font-semibold hover:bg-yellow-300 hover:text-gray-800 transition-all active" data-filter="all">
                All Heroics
            </button>
            <button class="filter-btn px-4 py-2 rounded-full border-2 border-green-400 text-green-400 font-semibold hover:bg-green-400 hover:text-gray-800 transition-all" data-filter="easy">
                Easy
            </button>
            <button class="filter-btn px-4 py-2 rounded-full border-2 border-yellow-400 text-yellow-400 font-semibold hover:bg-yellow-400 hover:text-gray-800 transition-all" data-filter="medium">
                Medium
            </button>
            <button class="filter-btn px-4 py-2 rounded-full border-2 border-red-400 text-red-400 font-semibold hover:bg-red-400 hover:text-gray-800 transition-all" data-filter="hard">
                Hard
            </button>
            <button class="filter-btn px-4 py-2 rounded-full border-2 border-purple-400 text-purple-400 font-semibold hover:bg-purple-400 hover:text-gray-800 transition-all" data-filter="expert">
                Expert
            </button>
        </div>
    </div>

    <!-- Heroics Grid -->
    <div id="heroicGrid" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <!-- Heroic cards will be populated by JavaScript -->
    </div>
</section>

    .filter-btn.active { 
        @apply bg-yellow-300 text-gray-800; 
    }
</style>

    <script>
        // Comprehensive heroics data
        const heroicsData = [
            {
                id: "axkva-min",
                name: "Axkva Min",
                planet: "Dathomir",
                difficulty: "expert",
                entryRequirements: "Level 80+, elite group of 5-8",
                bosses: [
                    { name: "Axkva Min", mechanics: "Force lightning, teleportation, corruption aura, mind control" },
                    { name: "Nightsister Protectors", mechanics: "Healing spells, force barriers, coordinated attacks" },
                    { name: "Dark Side Spirits", mechanics: "Possession, life drain, phase through walls" }
                ],
                lootHighlights: [
                    "Axkva Min's Lightsaber",
                    "Ancient Nightsister Robe",
                    "Dark Side Force Crystals",
                    "Legendary Jewelry Sets"
                ],
                description: "The most challenging Nightsister encounter featuring the legendary fallen Jedi Axkva Min. This expert-level instance demands perfect coordination and advanced tactics."
            },
            {
                id: "nightsister-stronghold",
                name: "Nightsister Stronghold", 
                planet: "Dathomir",
                difficulty: "hard",
                entryRequirements: "Level 70+, group of 4-6",
                bosses: [
                    { name: "Sister V'aria", mechanics: "Force lightning, mind control, barrier spells" },
                    { name: "Matriarch Lishra", mechanics: "Elite guard summons, healing rituals" },
                    { name: "Nightsister Ritualists", mechanics: "Channeled spells, area attacks" }
                ],
                lootHighlights: [
                    "Nightsister Energy Lance",
                    "Ritualist Ceremonial Robes",
                    "Force Crystal Shards",
                    "Dathomir Artifacts"
                ],
                description: "Infiltrate the infamous Nightsister stronghold on Dathomir. Face powerful Force-wielding enemies in their sacred temple complex."
            },
            {
                id: "krayt-dragon",
                name: "Ancient Krayt Dragon",
                planet: "Tatooine", 
                difficulty: "expert",
                entryRequirements: "Level 80+, raid group of 8-12",
                bosses: [
                    { name: "Ancient Krayt Dragon", mechanics: "Burrow attacks, sonic roar, rage mode, tail sweep" },
                    { name: "Young Krayt Dragons", mechanics: "Pack hunting, flanking maneuvers, coordinated strikes" },
                    { name: "Canyon Krayt", mechanics: "Rock throw, cave-in attacks, territorial rage" }
                ],
                lootHighlights: [
                    "Perfect Krayt Dragon Pearl",
                    "Legendary Dragon Bone Armor",
                    "Ancient Dragon Scales", 
                    "Krayt Dragon Tissue"
                ],
                description: "Hunt the legendary Ancient Krayt Dragon in the vast Dune Sea. This massive beast requires a full raid group and flawless execution to defeat."
            },
            {
                id: "ig-88",
                name: "IG-88 Assassination",
                planet: "Tatooine",
                difficulty: "hard", 
                entryRequirements: "Level 70+, group of 4-6",
                bosses: [
                    { name: "IG-88", mechanics: "Precise targeting, advanced weapon systems, stealth mode" },
                    { name: "Security Droids", mechanics: "Shield generators, self-destruct sequences" },
                    { name: "Assassin Droids", mechanics: "Coordinated attacks, stun weapons" }
                ],
                lootHighlights: [
                    "IG-88's Custom Rifle",
                    "Advanced Droid Components", 
                    "Precision Targeting Computer",
                    "Bounty Hunter Equipment"
                ],
                description: "Infiltrate the notorious bounty hunter droid IG-88's heavily fortified compound. Expect cutting-edge technology and deadly precision."
            },
            {
                id: "geonosian-queen", 
                name: "Geonosian Queen's Hive",
                planet: "Geonosis",
                difficulty: "medium",
                entryRequirements: "Level 60+, group of 4-6",
                bosses: [
                    { name: "Geonosian Queen", mechanics: "Acid spit, swarm summoning, hive mind coordination" },
                    { name: "Royal Guards", mechanics: "Protective formation, sonic weapons, flight attacks" },
                    { name: "Worker Swarms", mechanics: "Overwhelming numbers, construction abilities" }
                ],
                lootHighlights: [
                    "Queen's Royal Staff",
                    "Geonosian Royal Armor",
                    "Sonic Weaponry",
                    "Rare Insectoid Artifacts"
                ],
                description: "Venture into the underground hive complex to face the Geonosian Queen. Navigate complex tunnel systems while battling swarms of defenders."
            },
            {
                id: "janta-blood-crisis",
                name: "Janta Blood Crisis", 
                planet: "Dantooine",
                difficulty: "easy",
                entryRequirements: "Level 25+, group of 3-4",
                bosses: [
                    { name: "Janta Blood Collectors", mechanics: "Basic melee combat, blood drain attacks" },
                    { name: "Blood Cult Leaders", mechanics: "Rally abilities, enhanced combat skills" },
                    { name: "Corrupted Shamans", mechanics: "Healing spells, curse abilities" }
                ],
                lootHighlights: [
                    "Blood Ritual Artifacts", 
                    "Primitive Weapons",
                    "Dantooine Relics",
                    "Basic Enhancement Components"
                ],
                description: "Stop the Janta Blood cult from terrorizing Dantooine settlements. A perfect introduction to heroic content for newer players."
            }
        ];

        // Filter functionality
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                // Update active button
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Filter heroics
                const filter = this.dataset.filter;
                filterHeroics(filter);
            });
        });

        function filterHeroics(difficulty) {
            const grid = document.getElementById('heroicGrid');
            grid.innerHTML = '';
            
            const filteredHeroics = difficulty === 'all' 
                ? heroicsData 
                : heroicsData.filter(heroic => heroic.difficulty === difficulty);
            
            filteredHeroics.forEach(heroic => {
                grid.appendChild(createHeroicCard(heroic));
            });
        }

        function createHeroicCard(heroic) {
            const card = document.createElement('div');
            card.className = 'bg-gray-800 rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2';
            
            const difficultyColors = {
                'easy': 'bg-green-500',
                'medium': 'bg-yellow-500',
                'hard': 'bg-red-500',
                'expert': 'bg-purple-500'
            };
            
            const difficultyColor = difficultyColors[heroic.difficulty] || 'bg-gray-500';
            const difficultyText = heroic.difficulty.charAt(0).toUpperCase() + heroic.difficulty.slice(1);
            
            card.innerHTML = \`
                <div class="bg-gradient-to-r from-primary to-secondary p-6 text-white relative">
                    <span class="absolute top-4 right-4 \${difficultyColor} text-white px-3 py-1 rounded-full text-sm font-bold">
                        \${difficultyText}
                    </span>
                    <h3 class="text-xl font-bold flex items-center">
                        <i class="fas fa-dragon mr-2"></i>
                        \${heroic.name}
                    </h3>
                </div>
                
                <div class="p-6">
                    <p class="text-gray-300 italic mb-4 leading-relaxed">\${heroic.description}</p>
                    
                    <div class="mb-4">
                        <h4 class="text-lg font-semibold text-white mb-2 flex items-center">
                            <i class="fas fa-globe text-yellow-300 mr-2"></i>Location
                        </h4>
                        <div class="bg-gray-700 rounded-lg p-3 flex items-center">
                            <i class="fas fa-map-marker-alt text-yellow-300 mr-2"></i>
                            <span class="text-gray-300">\${heroic.planet}</span>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <h4 class="text-lg font-semibold text-white mb-2 flex items-center">
                            <i class="fas fa-users text-yellow-300 mr-2"></i>Requirements
                        </h4>
                        <div class="bg-gray-700 rounded-lg p-3 flex items-center">
                            <i class="fas fa-sign-in-alt text-yellow-300 mr-2"></i>
                            <span class="text-gray-300">\${heroic.entryRequirements}</span>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <h4 class="text-lg font-semibold text-white mb-2 flex items-center">
                            <i class="fas fa-skull text-yellow-300 mr-2"></i>Boss Encounters
                        </h4>
                        <div class="space-y-2">
                            \${heroic.bosses.map(boss => \`
                                <div class="bg-gray-700 rounded-lg p-3 border-l-4 border-yellow-300">
                                    <span class="font-semibold text-yellow-300">\${boss.name}</span>
                                    <span class="text-gray-300">: \${boss.mechanics}</span>
                                </div>
                            \`).join('')}
                        </div>
                    </div>
                    
                    <div class="mb-6">
                        <h5 class="text-lg font-semibold text-white mb-2 flex items-center">
                            <i class="fas fa-treasure-chest text-yellow-300 mr-2"></i>Notable Loot
                        </h5>
                        <div class="bg-gradient-to-r from-yellow-900 to-orange-900 rounded-lg p-4 space-y-2">
                            \${heroic.lootHighlights.map(loot => \`
                                <div class="bg-yellow-100 text-yellow-900 px-3 py-1 rounded-md text-sm font-medium">
                                    \${loot}
                                </div>
                            \`).join('')}
                        </div>
                    </div>
                    
                    <a href="\${heroic.id}/" class="block w-full bg-gradient-to-r from-primary to-secondary text-white font-bold py-3 px-6 rounded-lg text-center hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                        <i class="fas fa-info-circle mr-2"></i>View Detailed Guide & Live Loot Tables
                    </a>
                </div>
            \`;
            
            return card;
        }

        // Initialize the page with all heroics
        document.addEventListener('DOMContentLoaded', function() {
            filterHeroics('all');
        });
    </script>
</body>
</html>
    `;
  }
};