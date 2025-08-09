// src/heroics/geonosian-queen.11ty.js

const heroics = require('../../public/data/heroics.json');

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Geonosian Queen\'s Hive - Heroic Guide',
      permalink: 'heroics/geonosian-queen/index.html',
    };
  }

  render() {
    const heroic = heroics.find(h => h.slug === 'geonosian-queen');
    
    return `
<section class="py-12 px-6 max-w-6xl mx-auto text-white">
  <h1 class="text-4xl font-bold mb-4 text-yellow-300">${heroic.name}</h1>
  <p class="text-gray-400 mb-6">${heroic.summary}</p>

  <h2 class="text-2xl font-semibold mt-8 mb-2">Loot Table</h2>
  <ul class="list-disc list-inside text-yellow-200">
    ${heroic.loot.map(item => `<li>${item}</li>`).join('')}
  </ul>

  <h2 class="text-2xl font-semibold mt-8 mb-2">Strategy Tips</h2>
  <p class="text-gray-300">${heroic.strategy}</p>
</section>
    `;
  }
};