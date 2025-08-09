// src/loot/exar-kun.11ty.js

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Exar Kun Loot Table',
      eleventyNavigation: {
        key: 'Exar Kun',
        parent: 'Loot Tables'
      }
    };
  }

  render() {
    return `
<section class="max-w-6xl mx-auto px-4 py-12 text-white">
  <h1 class="text-4xl font-bold mb-4">Exar Kun Loot Table</h1>
  <p class="text-gray-400 mb-6">Drops from the Exar Kun heroic instance. Community-verified data based on multiple runs.</p>

  <div class="bg-gray-900 p-6 rounded-lg border border-gray-700">
    <h2 class="text-2xl text-green-400 font-semibold mb-3">Legendary Drops</h2>
    <ul class="list-disc list-inside text-gray-300 space-y-1">
      <li>Sith Relic Lightsaber (Ultra Rare)</li>
      <li>Voidheart Force Crystal</li>
      <li>Darkside Mastery Ring</li>
    </ul>
  </div>

  <div class="mt-8 bg-gray-900 p-6 rounded-lg border border-gray-700">
    <h2 class="text-2xl text-green-400 font-semibold mb-3">Rare Drops</h2>
    <ul class="list-disc list-inside text-gray-300 space-y-1">
      <li>Force-sensitive Necklace</li>
      <li>Ancient Robes</li>
      <li>Enhanced Sith Holocron</li>
    </ul>
  </div>

  <div class="mt-8 bg-gray-900 p-6 rounded-lg border border-gray-700">
    <h2 class="text-2xl text-green-400 font-semibold mb-3">Common Drops</h2>
    <ul class="list-disc list-inside text-gray-300 space-y-1">
      <li>Credits (10k–30k)</li>
      <li>Sith Themed Cosmetics</li>
      <li>Basic Buff Consumables</li>
    </ul>
  </div>

  <div class="mt-8">
    <a href="/heroics/exar-kun/" class="text-yellow-400 underline">← Back to Exar Kun Heroic Overview</a>
  </div>
</section>
    `;
  }
};