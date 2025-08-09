module.exports = class {
  data() {
    return {
      title: "Tools Hub - SWGDB",
      description: "Interactive tools and utilities for Star Wars Galaxies Restoration including skill calculators, loot trackers, and community-built resources",
      layout: "base.njk",
      permalink: "/pages/tools/"
    };
  }

  render(data) {
    return `
<section class="py-12 px-6 max-w-6xl mx-auto text-white">
    <!-- Hero Section -->
    <div class="bg-gradient-to-r from-purple-900 to-blue-900 rounded-lg p-12 mb-12 text-center">
        <h1 class="text-5xl font-bold mb-4 text-yellow-300">
            <i class="fas fa-tools mr-3"></i>Tools Hub
        </h1>
        <p class="text-xl text-gray-200 max-w-2xl mx-auto">
            Interactive tools and utilities built by the community, for the community
        </p>
    </div>

    <!-- Character & Build Tools -->
    <div class="mb-12">
        <div class="text-center mb-8">
            <h2 class="text-3xl font-bold mb-4 text-white flex items-center justify-center gap-3">
                <i class="fas fa-user"></i>Character & Build Tools
            </h2>
            <p class="text-lg text-gray-300">Plan, optimize, and perfect your character builds</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <a href="/pages/tools/skill-calculator/" class="bg-gray-800 rounded-lg overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-2 block">
                <div class="bg-gradient-to-r from-primary to-secondary p-6 text-white">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <div class="bg-white bg-opacity-20 rounded-lg p-3">
                                <i class="fas fa-calculator text-2xl"></i>
                            </div>
                            <div>
                                <h3 class="text-xl font-bold">Skill Calculator</h3>
                                <span class="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-bold">LIVE</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="p-6">
                    <p class="text-gray-300 mb-4 leading-relaxed">
                        Interactive skill calculator for planning profession builds with automatic dependency tracking, point management, and build export functionality.
                    </p>
                    <div class="flex flex-wrap gap-2 mb-4">
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">5 Professions</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Auto Dependencies</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Point Tracking</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Export Builds</span>
                    </div>
                    <div class="bg-gradient-to-r from-primary to-secondary text-white font-bold py-3 px-6 rounded-lg text-center">
                        <i class="fas fa-play mr-2"></i>Launch Tool
                    </div>
                </div>
            </a>

            <a href="/pages/tools/gcw-calculator/" class="bg-gray-800 rounded-lg overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-2 block">
                <div class="bg-gradient-to-r from-primary to-secondary p-6 text-white">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <div class="bg-white bg-opacity-20 rounded-lg p-3">
                                <i class="fas fa-globe text-2xl"></i>
                            </div>
                            <div>
                                <h3 class="text-xl font-bold">GCW Calculator</h3>
                                <span class="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-bold">LIVE</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="p-6">
                    <p class="text-gray-300 mb-4 leading-relaxed">
                        Simulate Galactic Civil War planet control across the galaxy. Adjust faction percentages and visualize Imperial vs Rebel dominance.
                    </p>
                    <div class="flex flex-wrap gap-2 mb-4">
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">12 Planets</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Live Updates</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Faction Balance</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Visual Charts</span>
                    </div>
                    <div class="bg-gradient-to-r from-primary to-secondary text-white font-bold py-3 px-6 rounded-lg text-center">
                        <i class="fas fa-play mr-2"></i>Launch Tool
                    </div>
                </div>
            </a>
        </div>
    </div>

    <!-- Loot & Tracking Tools -->
    <div class="mb-12">
        <div class="text-center mb-8">
            <h2 class="text-3xl font-bold mb-4 text-white flex items-center justify-center gap-3">
                <i class="fas fa-treasure-chest"></i>Loot & Tracking Tools
            </h2>
            <p class="text-lg text-gray-300">Track drops, analyze loot tables, and manage collections</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <a href="/pages/tools/loot-tracker.html" class="bg-gray-800 rounded-lg overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-2 block">
                <div class="bg-gradient-to-r from-primary to-secondary p-6 text-white">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <div class="bg-white bg-opacity-20 rounded-lg p-3">
                                <i class="fas fa-crosshairs text-2xl"></i>
                            </div>
                            <div>
                                <h3 class="text-xl font-bold">Loot Tracker</h3>
                                <span class="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-bold">LIVE</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="p-6">
                    <p class="text-gray-300 mb-4 leading-relaxed">
                        Track your rare loot drops and farming progress. Set goals, monitor collection growth, and share achievements with the community.
                    </p>
                    <div class="flex flex-wrap gap-2 mb-4">
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Drop Tracking</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Goal Setting</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Progress Stats</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Community Share</span>
                    </div>
                    <div class="bg-gradient-to-r from-primary to-secondary text-white font-bold py-3 px-6 rounded-lg text-center">
                        <i class="fas fa-play mr-2"></i>Launch Tool
                    </div>
                </div>
            </a>

            <a href="/pages/tools/loot-memory.html" class="bg-gray-800 rounded-lg overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-2 block">
                <div class="bg-gradient-to-r from-primary to-secondary p-6 text-white">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <div class="bg-white bg-opacity-20 rounded-lg p-3">
                                <i class="fas fa-brain text-2xl"></i>
                            </div>
                            <div>
                                <h3 class="text-xl font-bold">Loot Memory</h3>
                                <span class="bg-yellow-500 text-white px-3 py-1 rounded-full text-sm font-bold">BETA</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="p-6">
                    <p class="text-gray-300 mb-4 leading-relaxed">
                        Advanced loot tracking with memory features. Remember where you found items, track farming locations, and optimize your routes.
                    </p>
                    <div class="flex flex-wrap gap-2 mb-4">
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Location Memory</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Route Planning</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">Smart Suggestions</span>
                        <span class="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">AI Learning</span>
                    </div>
                    <div class="bg-gradient-to-r from-primary to-secondary text-white font-bold py-3 px-6 rounded-lg text-center">
                        <i class="fas fa-flask mr-2"></i>Try Beta
                    </div>
                </div>
            </a>
        </div>
    </div>

    <!-- Community Favorites -->
    <div class="bg-gray-800 rounded-lg p-8">
        <h3 class="text-2xl font-bold text-center mb-8 text-white flex items-center justify-center gap-3">
            <i class="fas fa-star text-yellow-300"></i>Community Favorites
        </h3>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <a href="/pages/tools/skill-calculator/" class="bg-gray-700 rounded-lg p-4 text-center hover:bg-gray-600 transition-all duration-300 hover:-translate-y-1 block">
                <i class="fas fa-calculator text-3xl text-yellow-300 mb-3 block"></i>
                <h4 class="font-semibold text-white text-sm mb-1">Skill Calculator</h4>
                <p class="text-xs text-gray-400">Most used tool for build planning</p>
            </a>
            <a href="/pages/heroics/" class="bg-gray-700 rounded-lg p-4 text-center hover:bg-gray-600 transition-all duration-300 hover:-translate-y-1 block">
                <i class="fas fa-dragon text-3xl text-yellow-300 mb-3 block"></i>
                <h4 class="font-semibold text-white text-sm mb-1">Heroic Guides</h4>
                <p class="text-xs text-gray-400">Complete instance strategies</p>
            </a>
            <a href="/pages/tools/loot-tracker.html" class="bg-gray-700 rounded-lg p-4 text-center hover:bg-gray-600 transition-all duration-300 hover:-translate-y-1 block">
                <i class="fas fa-crosshairs text-3xl text-yellow-300 mb-3 block"></i>
                <h4 class="font-semibold text-white text-sm mb-1">Loot Tracker</h4>
                <p class="text-xs text-gray-400">Track your rare collections</p>
            </a>
            <a href="/pages/tools/gcw-calculator/" class="bg-gray-700 rounded-lg p-4 text-center hover:bg-gray-600 transition-all duration-300 hover:-translate-y-1 block">
                <i class="fas fa-globe text-3xl text-yellow-300 mb-3 block"></i>
                <h4 class="font-semibold text-white text-sm mb-1">GCW Calculator</h4>
                <p class="text-xs text-gray-400">Planet control simulation</p>
            </a>
            <a href="/pages/guides/" class="bg-gray-700 rounded-lg p-4 text-center hover:bg-gray-600 transition-all duration-300 hover:-translate-y-1 block">
                <i class="fas fa-book text-3xl text-yellow-300 mb-3 block"></i>
                <h4 class="font-semibold text-white text-sm mb-1">Build Guides</h4>
                <p class="text-xs text-gray-400">Expert build tutorials</p>
            </a>
            <a href="/pages/leaderboard/" class="bg-gray-700 rounded-lg p-4 text-center hover:bg-gray-600 transition-all duration-300 hover:-translate-y-1 block">
                <i class="fas fa-trophy text-3xl text-yellow-300 mb-3 block"></i>
                <h4 class="font-semibold text-white text-sm mb-1">Rankings</h4>
                <p class="text-xs text-gray-400">Community leaderboards</p>
            </a>
        </div>
    </div>
</section>
    `;
  }
};