// src/heroics/exar-kun.11ty.js

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Exar Kun Heroic',
      eleventyNavigation: {
        key: 'Exar Kun',
        parent: 'Heroics'
      }
    };
  }

  render() {
    return `
<section class="max-w-6xl mx-auto px-4 py-12 text-white">
  <h1 class="text-4xl font-bold mb-4">Exar Kun Heroic</h1>
  <p class="text-gray-400 mb-6">Journey deep into the Temple of Exar Kun on Yavin IV to face one of the galaxy's most dangerous Sith Lords.</p>

  <div class="bg-gray-900 p-6 rounded-lg border border-gray-700">
    <h2 class="text-2xl text-yellow-300 font-semibold mb-3">Overview</h2>
    <ul class="list-disc list-inside text-gray-300 space-y-2">
      <li>Location: Yavin IV</li>
      <li>Recommended Players: 6–8</li>
      <li>Boss Mechanics: AoE Force attacks, phase-based strategy</li>
      <li>Lockout: 24 hours</li>
    </ul>
  </div>

  <div class="mt-10 bg-gray-900 p-6 rounded-lg border border-gray-700">
    <h2 class="text-2xl text-yellow-300 font-semibold mb-3">Boss List</h2>
    <ol class="list-decimal list-inside text-gray-300 space-y-1">
      <li>Exar Kun's Ghost</li>
      <li>Dark Side Acolytes</li>
      <li>Ancient Sith Constructs</li>
    </ol>
  </div>

  <div class="mt-10 bg-gray-900 p-6 rounded-lg border border-gray-700">
    <h2 class="text-2xl text-yellow-300 font-semibold mb-3">Loot Preview</h2>
    <p class="text-gray-300 mb-2">See the full loot table <a class="text-yellow-400 underline" href="/loot/exar-kun/">here</a>.</p>
    <ul class="list-disc list-inside text-gray-300 space-y-1">
      <li>Sith Relic Lightsaber</li>
      <li>Force Crystal: Voidheart</li>
      <li>Ancient Robes of the Dark Side</li>
    </ul>
  </div>
</section>
    `;
  }
};