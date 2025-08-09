const fs = require('fs');
const path = require('path');

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Loot Tracker',
      permalink: '/tools/loot-tracker/',
      eleventyNavigation: {
        key: 'Loot Tracker',
        parent: 'Tools',
        order: 3
      }
    };
  }

  render() {
    const lootDir = path.join(__dirname, '../../data/loot');
    const files = fs.readdirSync(lootDir).filter(file => file.endsWith('.json'));
    const lootEntries = files.map(file => {
      const data = require(`../../data/loot/${file}`);
      const slug = file.replace('.json', '');
      return `
        <div class="bg-gray-800 rounded-lg shadow p-6 mb-6">
          <h2 class="text-2xl font-bold text-yellow-300 mb-2">${data.boss}</h2>
          <p class="text-gray-400 mb-2">${data.instance} – ${data.location}</p>
          <ul class="list-disc pl-6 text-white">
            ${data.drops.map(drop => `<li>${drop}</li>`).join('')}
          </ul>
          <a href="/heroics/${slug}/" class="inline-block mt-4 text-sm text-yellow-400 hover:underline">View Details & Live Loot</a>
        </div>
      `;
    }).join('');

    return `
      <section class="py-12 px-6 max-w-5xl mx-auto">
        <h1 class="text-4xl font-bold text-white mb-6">Heroic Loot Tracker</h1>
        <p class="text-gray-400 mb-10">Track rare drops from heroic encounters across the galaxy. Community-verified loot data updated regularly.</p>
        
        <div class="bg-gray-900 rounded-lg p-6 mb-8 border border-yellow-500">
          <h2 class="text-xl font-semibold text-yellow-300 mb-3">How to Use</h2>
          <ul class="list-disc pl-6 text-gray-300 space-y-1">
            <li>Browse confirmed drops from each heroic encounter</li>
            <li>Click "View Details & Live Loot" for complete encounter guides</li>
            <li>Submit your own drops to help the community</li>
            <li>Track your collection progress and rare finds</li>
          </ul>
        </div>

        ${lootEntries}
        
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <h3 class="text-xl font-bold text-green-400 mb-3">Submit Your Drops</h3>
          <p class="text-gray-300 mb-4">Help the community by reporting your loot drops! Your submissions help verify drop rates and discover new items.</p>
          <a href="/report/" class="inline-block px-6 py-3 bg-green-500 text-black font-bold rounded hover:bg-green-400 transition">
            Report Loot Drop
          </a>
        </div>
      </section>
    `;
  }
};