// src/heroics.11ty.js

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Heroic Encounters - SWGDB',
      permalink: '/heroics/'
    };
  }

  render() {
    return `
<section class="max-w-6xl mx-auto px-4 py-12 text-white">
  <h1 class="text-4xl font-bold mb-6">Heroic Encounters</h1>
  <p class="mb-8 text-gray-400">Explore high-stakes, high-reward missions across the galaxy. Each heroic instance offers rare loot, group-based mechanics, and faction prestige.</p>

  <div class="grid md:grid-cols-2 gap-8">
    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-yellow-300 mb-2">Exar Kun</h2>
      <p class="text-gray-300 mb-4">Face the ancient Sith Lord and his dark followers on Yavin IV. Requires coordinated group tactics.</p>
      <a href="/heroics/exar-kun/" class="inline-block px-4 py-2 bg-yellow-500 text-black font-bold rounded hover:bg-yellow-400">View Details & Live Loot</a>
    </div>

    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-yellow-300 mb-2">Axkva Min</h2>
      <p class="text-gray-300 mb-4">Face the fallen Jedi in her dark stronghold on Dathomir. Requires elite coordination and advanced tactics.</p>
      <a href="/heroics/axkva-min/" class="inline-block px-4 py-2 bg-yellow-500 text-black font-bold rounded hover:bg-yellow-400">View Details & Live Loot</a>
    </div>

    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-yellow-300 mb-2">Ancient Krayt Dragon</h2>
      <p class="text-gray-300 mb-4">Hunt the legendary beast of Tatooine's Dune Sea. Epic raid encounter requiring perfect coordination.</p>
      <a href="/heroics/krayt-dragon/" class="inline-block px-4 py-2 bg-yellow-500 text-black font-bold rounded hover:bg-yellow-400">View Details & Live Loot</a>
    </div>

    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-yellow-300 mb-2">IG-88</h2>
      <p class="text-gray-300 mb-4">Infiltrate the bounty hunter droid's compound. Advanced technology meets deadly precision.</p>
      <a href="/heroics/ig-88/" class="inline-block px-4 py-2 bg-yellow-500 text-black font-bold rounded hover:bg-yellow-400">View Details & Live Loot</a>
    </div>

    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-yellow-300 mb-2">Nightsister Stronghold</h2>
      <p class="text-gray-300 mb-4">Navigate the dark halls of the Nightsister fortress. Force-wielding enemies and ancient magic.</p>
      <a href="/heroics/nightsister-stronghold/" class="inline-block px-4 py-2 bg-yellow-500 text-black font-bold rounded hover:bg-yellow-400">View Details & Live Loot</a>
    </div>

    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-yellow-300 mb-2">Geonosian Queen's Hive</h2>
      <p class="text-gray-300 mb-4">Venture into the underground hive complex. Swarm tactics and coordinated insectoid attacks.</p>
      <a href="/heroics/geonosian-queen/" class="inline-block px-4 py-2 bg-yellow-500 text-black font-bold rounded hover:bg-yellow-400">View Details & Live Loot</a>
    </div>
  </div>

  <!-- Quick Access Section -->
  <div class="mt-12 bg-gray-800 rounded-lg p-8">
    <h2 class="text-2xl font-bold text-white mb-6 text-center">Quick Access</h2>
    <div class="flex flex-wrap justify-center gap-4">
      <a href="/tools/loot-tracker/" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-6 rounded-lg transition">
        <i class="fas fa-crosshairs mr-2"></i>Loot Tracker
      </a>
      <a href="/loot/" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-6 rounded-lg transition">
        <i class="fas fa-treasure-chest mr-2"></i>All Loot Tables
      </a>
      <a href="/guides/combat-builds/" class="bg-purple-500 hover:bg-purple-600 text-white font-bold py-2 px-6 rounded-lg transition">
        <i class="fas fa-sword mr-2"></i>Combat Build Guides
      </a>
    </div>
  </div>
</section>
    `;
  }
};