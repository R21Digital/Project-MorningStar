const fs = require('fs');
const path = require('path');

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      pagination: {
        data: "collections.lootBosses",
        size: 1,
        alias: "lootEntry"
      },
      permalink: function(data) {
        return `/heroics/${data.lootEntry.slug}/`;
      },
      eleventyComputed: {
        title: data => `${data.lootEntry.boss} – Heroic Info`
      }
    };
  }

  render({ lootEntry }) {
    return `
      <section class="py-12 px-6 max-w-4xl mx-auto">
        <a href="/heroics/" class="inline-flex items-center text-yellow-300 hover:text-white mb-6 font-semibold">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path>
          </svg>
          Back to Heroics
        </a>

        <h1 class="text-4xl font-bold text-yellow-300 mb-6">${lootEntry.boss}</h1>
        <div class="bg-gray-800 rounded-lg p-6 mb-8">
          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-yellow-300 mb-2">Instance</h3>
              <p class="text-gray-300">${lootEntry.instance}</p>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-yellow-300 mb-2">Location</h3>
              <p class="text-gray-300">${lootEntry.location}</p>
            </div>
          </div>
        </div>

        <div class="bg-gray-800 rounded-lg p-6 mb-8">
          <h2 class="text-2xl font-semibold text-white mb-4">Confirmed Drops</h2>
          <div class="grid md:grid-cols-2 gap-4">
            ${lootEntry.drops.map(item => `
              <div class="bg-gray-700 rounded-lg p-4 border-l-4 border-yellow-300">
                <div class="flex items-center">
                  <i class="fas fa-treasure-chest text-yellow-300 mr-3"></i>
                  <span class="text-white font-medium">${item}</span>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <div class="bg-gray-800 rounded-lg p-6 mb-8">
          <h2 class="text-2xl font-semibold text-white mb-4">Strategy Overview</h2>
          <p class="text-gray-300 mb-4">
            This encounter requires coordination and proper preparation. Study the mechanics and coordinate with your group for the best chance at rare drops.
          </p>
          <div class="bg-yellow-900 rounded-lg p-4 border-l-4 border-yellow-300">
            <h4 class="text-yellow-300 font-semibold mb-2">
              <i class="fas fa-lightbulb mr-2"></i>Pro Tip
            </h4>
            <p class="text-gray-300 text-sm">
              Drop rates vary based on group composition and encounter completion time. Higher difficulty encounters typically yield better rewards.
            </p>
          </div>
        </div>

        <div class="bg-gray-800 rounded-lg p-6">
          <h2 class="text-2xl font-semibold text-white mb-4">Community Data</h2>
          <p class="text-gray-300 mb-4">
            This loot data is maintained by the community. Help us keep it accurate by reporting your drops!
          </p>
          <div class="flex flex-wrap gap-4">
            <a href="/tools/loot-tracker/" class="text-yellow-400 hover:underline">
              ← Back to Loot Tracker
            </a>
            <a href="/report/" class="inline-block px-4 py-2 bg-green-500 text-black font-semibold rounded hover:bg-green-400 transition">
              Report Drop
            </a>
            <a href="/loot/${lootEntry.slug}/" class="inline-block px-4 py-2 bg-blue-500 text-white font-semibold rounded hover:bg-blue-400 transition">
              View Full Loot Table
            </a>
          </div>
        </div>
      </section>
    `;
  }
};