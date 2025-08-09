// src/loot/index.11ty.js

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Loot Tables',
      eleventyNavigation: {
        key: 'Loot Tables',
        order: 5
      }
    };
  }

  render() {
    return `
<section class="max-w-6xl mx-auto px-4 py-12 text-white">
  <h1 class="text-4xl font-bold mb-6">Loot Tables</h1>
  <p class="mb-8 text-gray-400">Track which heroic or event drops the gear you're hunting. Data is updated regularly by the community and synced with SWGDB logs.</p>

  <div class="grid md:grid-cols-2 gap-8">
    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-green-400 mb-2">Exar Kun</h2>
      <p class="text-gray-300 mb-4">Rare Sith weapons, force relics, and high-end combat gear. Multiple bosses with unique loot pools.</p>
      <a href="/loot/exar-kun/" class="inline-block px-4 py-2 bg-green-500 text-black font-bold rounded hover:bg-green-400">View Loot Table</a>
    </div>

    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-green-400 mb-2">Axkva Min</h2>
      <p class="text-gray-300 mb-4">Rare Sith weapons, fallen Jedi artifacts, and high-end corruption crystals. Multiple phases with unique loot pools.</p>
      <a href="/loot/axkva-min/" class="inline-block px-4 py-2 bg-green-500 text-black font-bold rounded hover:bg-green-400">View Loot Table</a>
    </div>

    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-green-400 mb-2">Ancient Krayt Dragon</h2>
      <p class="text-gray-300 mb-4">Perfect Krayt Dragon Pearls, legendary dragon scale armor, and ancient bone weapons. Raid-tier rewards.</p>
      <a href="/loot/krayt-dragon/" class="inline-block px-4 py-2 bg-green-500 text-black font-bold rounded hover:bg-green-400">View Loot Table</a>
    </div>

    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-green-400 mb-2">IG-88</h2>
      <p class="text-gray-300 mb-4">Advanced droid components, precision targeting systems, and bounty hunter tech. High-tech equipment drops.</p>
      <a href="/loot/ig-88/" class="inline-block px-4 py-2 bg-green-500 text-black font-bold rounded hover:bg-green-400">View Loot Table</a>
    </div>

    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-green-400 mb-2">Nightsister Stronghold</h2>
      <p class="text-gray-300 mb-4">Nightsister energy weapons, ritualist robes, and Force crystal shards. Dark side artifacts and gear.</p>
      <a href="/loot/nightsister-stronghold/" class="inline-block px-4 py-2 bg-green-500 text-black font-bold rounded hover:bg-green-400">View Loot Table</a>
    </div>

    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-green-400 mb-2">Geonosian Queen's Hive</h2>
      <p class="text-gray-300 mb-4">Royal Geonosian staff, hive defender armor, and sonic weaponry. Insectoid technology and artifacts.</p>
      <a href="/loot/geonosian-queen/" class="inline-block px-4 py-2 bg-green-500 text-black font-bold rounded hover:bg-green-400">View Loot Table</a>
    </div>

    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition">
      <h2 class="text-2xl font-semibold text-green-400 mb-2">Janta Blood Crisis</h2>
      <p class="text-gray-300 mb-4">Blood ritual artifacts, primitive weapons, and Dantooine relics. Entry-level heroic rewards.</p>
      <a href="/loot/janta-blood-crisis/" class="inline-block px-4 py-2 bg-green-500 text-black font-bold rounded hover:bg-green-400">View Loot Table</a>
    </div>

    <!-- Community Loot Tracker -->
    <div class="bg-gray-900 rounded-lg border border-gray-700 p-6 shadow hover:shadow-lg transition md:col-span-2">
      <h2 class="text-2xl font-semibold text-blue-400 mb-2">Community Loot Tracker</h2>
      <p class="text-gray-300 mb-4">Real-time loot tracking system. Submit your drops to help the community track accurate drop rates and patterns.</p>
      <div class="flex flex-wrap gap-4">
        <a href="/tools/loot-tracker" class="inline-block px-4 py-2 bg-blue-500 text-black font-bold rounded hover:bg-blue-400">Submit Loot Drop</a>
        <a href="/loot/statistics/" class="inline-block px-4 py-2 bg-gray-700 text-white font-bold rounded hover:bg-gray-600">View Statistics</a>
      </div>
    </div>
  </div>
</section>
    `;
  }
};